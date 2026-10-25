import numpy as np

from predwinner.metrics import classification_report, national_share


def test_national_share_is_vote_weighted():
    assert national_share([1.0, 0.0], [3, 1]) == 0.75


def test_classification_report_perfect_predictions():
    r = classification_report(np.array([0, 1, 1]), np.array([0.1, 0.9, 0.8]))
    assert r["accuracy"] == 1.0
    assert r["auc"] == 1.0


def test_classification_report_handles_hard_probabilities():
    r = classification_report(np.array([0, 1]), np.array([1.0, 0.0]))
    assert np.isfinite(r["log_loss"])
