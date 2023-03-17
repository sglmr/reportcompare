from pathlib import Path

import pandas as pd
import pytest

from compare_reports import ReportCompare


@pytest.fixture
def same_csv():
    same_csv_1 = Path(__file__).resolve().parent / "test_files" / "same_csv.csv"
    same_csv_2 = Path(__file__).resolve().parent / "test_files" / "same_csv.csv"

    return ReportCompare(
        file1=same_csv_1,
        file1_name="file_1.csv",
        file2=same_csv_2,
        file2_name="file_2.csv",
        key="eid",
    )


def test_filenames(same_csv):
    rc = same_csv
    assert rc.f1_name == "file_1.csv"
    assert rc.f2_name == "file_2.csv"


def test_df_exists(same_csv):
    rc = same_csv
    assert type(rc.df1) == pd.DataFrame
    assert type(rc.df2) == pd.DataFrame


def test_find_extra_columns(same_csv):

    # set up test case
    rc = same_csv
    ex_cols = rc.find_extra_columns()

    # test
    assert rc.extra_columns.empty
    assert ex_cols.empty


def test_drop_extra_columns(same_csv):
    """Count of dropped columns should be 0"""

    # set up test case
    rc = same_csv
    rc.find_extra_columns()
    dropped_cols = rc.drop_extra_columns()

    # Test
    assert dropped_cols == 0
    assert len(rc.extra_columns) == dropped_cols


def test_deduplicate_files(same_csv):
    """count of duplicate records should be 0"""

    # set up test case
    rc = same_csv
    rc.find_extra_columns()
    rc.drop_extra_columns()
    dropped_dupes = rc.deduplicate_files()

    # test
    assert len(dropped_dupes) == 0


def test_drop_missing_records(same_csv):
    """dropped records should be 0"""

    # set up test case
    rc = same_csv
    rc.find_extra_columns()
    rc.drop_extra_columns()
    rc.deduplicate_files()
    missing_records = rc.drop_missing_records()

    # test
    assert len(missing_records) == 0


def test_pandas_compare(same_csv):
    # set up test case
    rc = same_csv
    rc.find_extra_columns()
    rc.drop_extra_columns()
    rc.deduplicate_files()
    rc.drop_missing_records()
    compare = rc.pandas_compare()

    assert len(compare) == 0


def test_build_summary(same_csv):
    """Summary len should be 1, 'No mismatches...'"""

    # set up test case
    rc = same_csv
    rc.find_extra_columns()
    rc.drop_extra_columns()
    rc.deduplicate_files()
    rc.drop_missing_records()
    rc.pandas_compare()

    summary = rc.build_summary()

    # test
    assert len(summary) == 1
    assert "No mismatches" in summary.iloc[0, 0]
