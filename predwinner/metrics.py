"""Métricas de classificação por município e de acerto do resultado nacional."""
import numpy as np
from sklearn.metrics import accuracy_score, brier_score_loss, f1_score, log_loss, roc_auc_score


def classification_report(y_true, proba) -> dict:
    proba = np.clip(proba, 1e-6, 1 - 1e-6)
    pred = (proba > 0.5).astype(int)
    return {
        "accuracy": accuracy_score(y_true, pred),
        "f1": f1_score(y_true, pred),
        "auc": roc_auc_score(y_true, proba),
        "brier": brier_score_loss(y_true, proba),
        "log_loss": log_loss(y_true, proba),
    }


def national_share(share, votes) -> float:
    """Share nacional do PT como média dos shares municipais ponderada pelos votos válidos."""
    return float(np.average(share, weights=votes))
