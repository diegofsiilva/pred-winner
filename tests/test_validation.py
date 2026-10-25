import pandas as pd

from predwinner.validation import expanding_splits


def test_expanding_splits_never_train_on_future():
    df = pd.DataFrame({"ano": [2006, 2010, 2014, 2018]})
    splits = list(expanding_splits(df))
    assert [y for y, _, _ in splits] == [2010, 2014, 2018]
    for year, train, test in splits:
        assert train.ano.max() < year
        assert set(test.ano) == {year}
