from collections import defaultdict

from simstring.memoize import FeatureSizeMemoizer


class Searcher:
    def __init__(self, db, measure):
        self.db = db
        self.measure = measure
        self.feature_extractor = db.feature_extractor
        self.memoizer = FeatureSizeMemoizer()

    def search(self, query_string, alpha):
        features = self.feature_extractor.features(query_string)
        min_feature_size = self.measure.min_feature_size(len(features), alpha)
        max_feature_size = self.measure.max_feature_size(len(features), alpha)
        results = []

        for candidate_feature_size in range(
            min_feature_size, max_feature_size + 1
        ):
            tau = self._min_overlap(
                len(features), candidate_feature_size, alpha
            )
            results.extend(
                self._overlap_join(features, tau, candidate_feature_size)
            )

        return results

    def ranked_search(self, query_string, alpha):
        results = self.search(query_string, alpha)
        features = self.feature_extractor.features(query_string)
        results_with_score = list(
            map(
                lambda x: [
                    self.measure.similarity(
                        features, self.feature_extractor.features(x)
                    ),
                    x,
                ],
                results,
            )
        )
        return sorted(results_with_score, key=lambda x: (-x[0], x[1]))

    def _min_overlap(self, query_size, candidate_feature_size, alpha):
        return self.measure.minimum_common_feature_count(
            query_size, candidate_feature_size, alpha
        )

    def _overlap_join(self, features, tau, candidate_feature_size):

        self.memoizer.load_bulk(
            db=self.db, size=candidate_feature_size, features=features
        )

        query_feature_size = len(features)
        sorted_features = sorted(
            features,
            key=lambda x: len(
                self.memoizer.get(
                    size=candidate_feature_size, feature=x, db=self.db
                )
            ),
        )

        candidate_string_to_matched_count = defaultdict(int)
        results = []

        for feature in sorted_features[0 : query_feature_size - tau + 1]:
            for s in self.memoizer.get(
                size=candidate_feature_size, feature=feature, db=self.db
            ):
                candidate_string_to_matched_count[s] += 1

        for s in candidate_string_to_matched_count.keys():
            for i in range(query_feature_size - tau + 1, query_feature_size):
                feature = sorted_features[i]
                if s in self.memoizer.get(
                    size=candidate_feature_size, feature=feature, db=self.db
                ):
                    candidate_string_to_matched_count[s] += 1
                if candidate_string_to_matched_count[s] >= tau:
                    results.append(s)
                    break
                remaining_feature_count = query_feature_size - i - 1
                if (
                    candidate_string_to_matched_count[s]
                    + remaining_feature_count
                    < tau
                ):
                    break

        self.memoizer.clear()

        return results
