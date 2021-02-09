from collections import defaultdict

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

    def lookup_strings_by_feature_set_size_and_feature(
        self, size: int = None, feature: str = None
    ):
        return self.feature_set_size_and_feature_to_string_map[size][feature]

    def min_feature_size(self):
        return min(self.feature_set_size_and_feature_to_string_map.keys())

    def max_feature_size(self):
        return max(self.feature_set_size_and_feature_to_string_map.keys())
