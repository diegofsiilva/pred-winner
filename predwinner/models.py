"""Modelos que estimam P(PT vence no município)."""
import numpy as np
from scipy.stats import norm
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
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


def gradient_boosting():
    return SklearnClassifier(
        HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, random_state=0)
    )


class Fundamentals:
    """Estilo Abramowitz: share do PT ~ voto anterior + incumbência + economia.

    A probabilidade de vitória vem de assumir erro normal em torno do share previsto.
    """

    features = ["share_pt_ant", "pt_incumbente", "crescimento_rel", "crescimento_x_incumbente"]

    def fit(self, df):
        self.reg = LinearRegression().fit(df[self.features], df.share_pt, sample_weight=df.votos_validos)
        resid = df.share_pt - self.reg.predict(df[self.features])
        self.sigma = np.sqrt(np.average(resid**2, weights=df.votos_validos))
        return self

    def predict_share(self, df):
        return self.reg.predict(df[self.features])

    def predict_proba(self, df):
        return norm.cdf((self.predict_share(df) - 0.5) / self.sigma)


def fundamentals():
    return Fundamentals()


class Ensemble:
    """Média simples das probabilidades dos modelos componentes."""

    def __init__(self, members):
        self.members = members

    def fit(self, df):
        for m in self.members:
            m.fit(df)
        return self

    def predict_proba(self, df):
        return np.mean([m.predict_proba(df) for m in self.members], axis=0)


def ensemble():
    return Ensemble([logistic(), random_forest(), gradient_boosting(), fundamentals()])


class Persistence:
    """Baseline: o município repete o resultado da eleição anterior."""

    def fit(self, df):
        return self

    def predict_proba(self, df):
        return (df.share_pt_ant > 0.5).astype(float).to_numpy()


MODELS = {
    "persistencia": Persistence,
    "logistica": logistic,
    "random_forest": random_forest,
    "gradient_boosting": gradient_boosting,
    "fundamentals": fundamentals,
    "ensemble": ensemble,
}
