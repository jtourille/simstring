import re
from collections import defaultdict
from typing import List

from simstring.database.base import BaseDatabase


class DictDatabase(BaseDatabase):
    def __init__(self, feature_extractor):
        super().__init__(feature_extractor=feature_extractor)

        self.feature_extractor = feature_extractor
        self.feature_set_size_and_feature_to_string_map = defaultdict(
            lambda: defaultdict(set)
        )

    def add(self, string: str = None):
        features = self.feature_extractor.features(string)
        size = len(features)

        for feature in features:
            self.feature_set_size_and_feature_to_string_map[size][feature].add(
                string
            )

    def add_bulk(self, simstring_file: str = None, **kwargs):

        with open(simstring_file, "r", encoding="UTF-8") as input_file:
            for line in input_file:
                if re.match("^$", line):
                    continue

                term = line.rstrip("\n")
                features = self.feature_extractor.features(term)
                size = len(features)
                for feat in features:
                    self.feature_set_size_and_feature_to_string_map[size][
                        feat
                    ].add(term)

    def clear(self):
        self.feature_set_size_and_feature_to_string_map = defaultdict(
            lambda: defaultdict(set)
        )

    def lookup_strings_by_feature_set_size_and_feature(
        self, size: int = None, feature: str = None
    ):
        return self.feature_set_size_and_feature_to_string_map[size][feature]

    def lookup_strings_by_feature_set_size_and_feature_bulk(
        self, size: int = None, features: List[str] = None
    ):

        return [
            self.lookup_strings_by_feature_set_size_and_feature(
                size=size, feature=feat
            )
            for feat in features
        ]

    def min_feature_size(self):
        return min(self.feature_set_size_and_feature_to_string_map.keys())

    def max_feature_size(self):
        return max(self.feature_set_size_and_feature_to_string_map.keys())
