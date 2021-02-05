from collections import Counter

from .base import BaseFeatureExtractor

SENTINAL_CHAR = "\xa0"  # non breaking space


class CharacterNgramFeatureExtractor(BaseFeatureExtractor):
    def __init__(self, n: int = 3, be: bool = False):
        self.n = n
        self.be = be

    def features(self, string):
        if self.be:
            string = (
                SENTINAL_CHAR * (self.n - 1)
                + string
                + SENTINAL_CHAR * (self.n - 1)
            )

        features = self._each_cons(
            SENTINAL_CHAR + string + SENTINAL_CHAR, self.n
        )
        feature_count = Counter(features)

        final_features = set()
        for k, v in feature_count.items():
            if v > 1:
                final_features.add("{}{}".format(k, v))
            else:
                final_features.add(k)

        return final_features
