import logging
from collections import defaultdict
from typing import List

from simstring.database.base import BaseDatabase


class FeatureSizeMemoizer:
    def __init__(self):

        self.memory = defaultdict(dict)

    def get(
        self, db: BaseDatabase = None, size: int = None, feature: str = None
    ):

        if feature not in self.memory[size]:
            self.memory[size][
                feature
            ] = db.lookup_strings_by_feature_set_size_and_feature(
                size=size, feature=feature
            )

        return self.memory[size][feature]

    def load_bulk(
        self,
        db: BaseDatabase = None,
        size: int = None,
        features: List[str] = None,
    ):

        logging.info("bulk")
        for feat, result in zip(
            features,
            db.lookup_strings_by_feature_set_size_and_feature_bulk(
                size=size, features=features
            ),
        ):
            self.memory[size][feat] = result

    def clear(self):

        self.memory = defaultdict(dict)
