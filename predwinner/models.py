"""Modelos que estimam P(PT vence no município)."""
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from predwinner.features import FEATURES


class SklearnClassifier:
    def __init__(self, estimator):
        self.estimator = estimator

    def fit(self, df):
        self.estimator.fit(df[FEATURES], df.pt_venceu)
        return self

    def predict_proba(self, df):
        return self.estimator.predict_proba(df[FEATURES])[:, 1]


def logistic():
    return SklearnClassifier(make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)))


def random_forest():
    return SklearnClassifier(
        RandomForestClassifier(n_estimators=300, min_samples_leaf=5, n_jobs=-1, random_state=0)
    )
