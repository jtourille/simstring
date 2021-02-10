import math
import re
import unicodedata
from typing import List

import redis
from joblib import Parallel, delayed

from simstring.database.base import BaseDatabase
from simstring.feature_extractor.base import BaseFeatureExtractor


def _add_terms_to_redis(
    simstring_file: str = None,
    start: int = None,
    end: int = None,
    redis_host: str = None,
    redis_port: int = None,
    redis_prefix: str = None,
    feature_extractor: BaseFeatureExtractor = None,
):
    r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    buffer_counter = 0

    with r.pipeline() as pipe:
        with open(simstring_file, "r", encoding="UTF-8") as input_file:
            for i, line in enumerate(input_file):
                if i < start or i > end:
                    continue

                if re.match("^$", line):
                    continue

                term = unicodedata.normalize("NFKD", line.rstrip("\n"))
                features = feature_extractor.features(term)
                size = len(features)

                for feat in features:
                    key = "{}:#S{}#F{}".format(redis_prefix, size, feat)
                    pipe.rpush(key, term)
                    buffer_counter += 1

                if buffer_counter >= 1000:
                    buffer_counter = 0
                    pipe.execute()

            if buffer_counter > 0:
                pipe.execute()


class RedisDatabase(BaseDatabase):
    def __init__(
        self,
        feature_extractor: BaseFeatureExtractor = None,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_prefix: str = "simstringdb",
    ):

        super().__init__(feature_extractor=feature_extractor)
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_prefix = redis_prefix

        self.min_size = None
        self.max_size = None

        self.r = redis.Redis(
            host=self.redis_host, port=self.redis_port, decode_responses=True
        )

    def clear(self):
        for key in self.r.scan_iter("{}:*".format(self.redis_prefix)):
            self.r.delete(key)

    def add_bulk(self, simstring_file: str = None, n_jobs: int = 1):

        count = 0

        with open(simstring_file, "r", encoding="UTF-8") as input_file:
            for _ in input_file:
                count += 1

        chunk_size = math.ceil(count / n_jobs)

        start = 0
        indices = list()
        for i in range(n_jobs):
            indices.append((start, start + chunk_size - 1))
            start += chunk_size

        _ = Parallel(n_jobs=n_jobs)(
            delayed(_add_terms_to_redis)(
                simstring_file=simstring_file,
                start=start,
                end=end,
                redis_host=self.redis_host,
                redis_port=self.redis_port,
                redis_prefix=self.redis_prefix,
                feature_extractor=self.feature_extractor,
            )
            for start, end in indices
        )

    def add(self, string: str = None):
        features = self.feature_extractor.features(string)
        size = len(features)

        with self.r.pipeline() as pipe:
            for feat in features:
                key = "{}:#S{}#F{}".format(self.redis_prefix, size, feat)
                pipe.rpush(key, string)

            pipe.execute()

    def lookup_strings_by_feature_set_size_and_feature(
        self, size: int = None, feature: str = None
    ):

        key = "{}:#S{}#F{}".format(self.redis_prefix, size, feature)

        return self.r.lrange(key, 0, -1)

    def lookup_strings_by_feature_set_size_and_feature_bulk(
        self, size: int = None, features: List[str] = None
    ):

        with self.r.pipeline() as pipe:
            for feat in features:
                key = "{}:#S{}#F{}".format(self.redis_prefix, size, feat)
                pipe.lrange(key, 0, -1)

            return pipe.execute()

    def min_feature_size(self):

        if self.min_size is None:
            self.extract_min_max_sizes()

        return self.min_size

    def max_feature_size(self):

        if self.max_size is None:
            self.extract_min_max_sizes()

        return self.max_size

    def extract_min_max_sizes(self):
        all_sizes = set()

        for key in self.r.scan_iter("{}:*".format(self.redis_prefix)):
            match = re.match(
                r"^{}:#S(\d+)#F(.*)$".format(self.redis_prefix), key
            )
            all_sizes.add(int(match.group(1)))

        self.min_size = min(all_sizes)
        self.max_size = min(all_sizes)
