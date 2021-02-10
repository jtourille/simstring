from collections import defaultdict

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

    def clear(self):

        self.memory = defaultdict(dict)
