from pathlib import Path

import pytest

from compare_reports import ReportCompare


@pytest.fixture
def same_xlsx():
    same_xlsx_1 = Path(__file__).resolve().parent / "test_files" / "same_xlsx.xlsx"
    same_xlsx_2 = Path(__file__).resolve().parent / "test_files" / "same_xlsx.xlsx"

    return ReportCompare(
        file1=same_xlsx_1,
        file1_name="file_1.xlsx",
        file2=same_xlsx_2,
        file2_name="file_2.xlsx",
        key="eid",
    )


def test_xlsx_df_shape(same_xlsx):
    """Test the shape of the dataframes to ensure they imported everything"""

    # set up test case
    rc = same_xlsx

    # test
    assert rc.df1.shape == (3, 4)
    assert rc.df1.shape == rc.df2.shape


def test_xlsx_df_keys(same_xlsx):
    """Test the shape of the dataframes to ensure they imported everything"""

    # set up test case
    rc = same_xlsx

    # etst
    assert rc.df1.index.name == "eid"
    assert rc.df2.index.name == "eid"


def test_compare_xlsx_summary(same_xlsx):
    """Summary len should be 1, 'No mismatches...'"""

    # set up test case
    rc = same_xlsx
    rc.compare_files()

    # test
    assert len(rc.summary) == 1
    assert "No mismatches" in rc.summary.iloc[0, 0]
