from typing import List

from simstring.feature_extractor.base import BaseFeatureExtractor


class BaseDatabase:
    def __init__(self, feature_extractor: BaseFeatureExtractor = None):
        self.feature_extractor = feature_extractor

    def add(self, string: str = None):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def add_bulk(self, simstring_file: str = None):
        raise NotImplementedError

    def min_feature_size(self):
        raise NotImplementedError

    def max_feature_size(self):
        raise NotImplementedError

    def lookup_strings_by_feature_set_size_and_feature(
        self, size: int = None, feature: str = None
    ):
        raise NotImplementedError

    def lookup_strings_by_feature_set_size_and_feature_bulk(
        self, size: int, features: List[str]
    ):
        raise NotImplementedError
