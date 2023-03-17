from pathlib import Path

import pytest

from compare_reports import ReportCompare


@pytest.fixture
def comparison():
    file_1 = Path(__file__).resolve().parent / "test_files" / "before_csv.csv"
    file_2 = Path(__file__).resolve().parent / "test_files" / "after_csv.csv"

    return ReportCompare(
        file1=file_1,
        file1_name=file_1.name,
        file2=file_2,
        file2_name=file_2.name,
        key="eid",
    )


def test_sanity_check(comparison):
    """Sanity check that the right files were picked up for the test"""

    # set up test case
    rc = comparison

    # test key
    assert rc.f1_name == "before_csv.csv"
    assert rc.f2_name == "after_csv.csv"

    # test key
    assert rc.df1.index.name == "eid"
    assert rc.df2.index.name == "eid"

    # test record count
    assert len(rc.df1) == 6
    assert len(rc.df2) == 6


def test_find_extra_columns(comparison):
    """Test that the correct extra columns were found."""

    # Set up test case
    rc = comparison
    extra_columns = rc.find_extra_columns()

    # Count of extra columns
    assert len(extra_columns) == 2

    # File 1 extra column(s)
    ex_cols = extra_columns[extra_columns["Source"] == rc.f1_name]["Extra Column"]
    assert "extra_col_1" in ex_cols.values
    assert "extra_col_2" not in ex_cols.values

    # File 2 extra column(s)
    ex_cols = extra_columns[extra_columns["Source"] == rc.f2_name]["Extra Column"]
    assert "extra_col_1" not in ex_cols.values
    assert "extra_col_2" in ex_cols.values


def test_drop_extra_columns(comparison):
    """Test that the correct extra columns were dropped."""

    # Set up test case
    rc = comparison
    rc.find_extra_columns()
    dropped_columns = rc.drop_extra_columns()

    # Dropped count should be the length of extra columns found
    count_of_extra_columns = len(rc.extra_columns)
    assert dropped_columns == count_of_extra_columns

    # Another search for extra columns should return nothing.
    rc.find_extra_columns()
    assert len(rc.extra_columns) == 0


def test_deduplicate_files(comparison):
    # Set up test case
    rc = comparison
    rc.find_extra_columns()
    rc.drop_extra_columns()
    dupes = rc.deduplicate_files()

    # File 1 duplicates
    f1_dupes = dupes[dupes["file"] == rc.f1_name]
    assert len(f1_dupes) == 2

    # File 1 found the correct duplicate
    assert 113 in f1_dupes.index.values
    assert 114 not in f1_dupes.index.values

    # Results has all of the fields from the original file
    for col in rc.df1.columns:
        assert col in f1_dupes.columns

    # File 2 duplicates
    f2_dupes = dupes[dupes["file"] == rc.f2_name]
    assert len(f2_dupes) == 2

    # File 1 found the correct duplicate
    assert 113 not in f2_dupes.index.values
    assert 114 in f2_dupes.index.values

    # Results has all of the fields from the original file
    for col in rc.df2.columns:
        assert col in f2_dupes.columns

    # Test number of duplicates removed
    assert len(dupes) == 2 * 2


def test_missing_records(comparison):
    """Test functionality to identify records that exist in one file but not the other"""
    # Set up test case
    rc = comparison
    rc.find_extra_columns()
    rc.drop_extra_columns()
    rc.deduplicate_files()

    start_len = len(rc.df1) + len(rc.df2)
    missing = rc.drop_missing_records()

    # Test file 1 missing records
    f1_ = missing[missing["file"] == rc.f1_name]
    assert 115 in f1_.index.values
    assert 117 not in f1_.index.values
    assert len(f1_) == 1

    # Test file 2 missing records
    f2_ = missing[missing["file"] == rc.f2_name]
    assert 115 not in f2_.index.values
    assert 117 in f2_.index.values
    assert len(f2_) == 1

    # Results has all of the fields from the original file
    for col in rc.df1.columns:
        assert col in missing.columns

    # Test missing record count
    assert len(missing) == 2
    assert start_len - len(rc.df1) - len(rc.df2) == len(missing)


def test_pandas_compare(comparison):
    """Basic sanity check on pandas compare. Assuming pandas has plenty of tests for this."""

    # Set up test case
    rc = comparison
    rc.find_extra_columns()
    rc.drop_extra_columns()
    rc.deduplicate_files()
    rc.drop_missing_records()
    compare = rc.pandas_compare()

    # Test the correct workers were found
    eids = [x for x, y in compare.index.values]
    assert 112 in eids
    assert 113 in eids
    assert 114 not in eids

    # Test record count is what's expected
    assert len(compare) == 4


def test_build_summary(comparison):
    # Set up test case
    rc = comparison
    rc.find_extra_columns()
    rc.drop_extra_columns()
    rc.deduplicate_files()
    rc.drop_missing_records()
    rc.pandas_compare()
    summary = rc.build_summary()

    # Test column values
    for col in summary.columns.values:
        assert col in ["Description", "Field", "Count"]

    # Test extra columns count
    extra_columns = summary[summary["Description"] == "Extra columns"]
    assert extra_columns["Count"].values[0] == 2

    # Test duplicate records count
    dupe_records = summary[summary["Description"] == "Duplicate records"]
    assert dupe_records["Count"].values[0] == 2

    # Test missing records count
    missing_records = summary[summary["Description"] == "Missing records from files"]
    assert missing_records["Count"].values[0] == 2

    # Test pandas compare count
    compares = summary[summary["Description"] == "Compare mismatch"]

    # shape of the result is as expected
    assert compares.shape == (2, 3)

    # found the right fields/columns for the changes
    for field in compares["Field"]:
        assert field in ["start_year", "department"]

    # summary count matches the pandas_compare() function count
    compares["Count"].sum() == len(rc.compare)


def test_write_to_excel(comparison):

    results_file = Path(__file__).resolve().parent / "test_files" / "test_results.xlsx"

    # Results file should not exist yet
    assert results_file.exists is not True

    rc = comparison
    rc.compare_files()
    rc.build_summary()
    rc.write_to_excel(results_file=results_file)

    # Results file should exist
    assert results_file.exists

    # TODO: Should add more test for the contents of the results file
    #  - check tabs
    #  - check rows in each tab

    # Remove file & assert it no longer exists
    results_file.unlink()
    assert results_file.exists is not True
