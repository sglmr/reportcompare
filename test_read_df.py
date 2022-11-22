import pytest
from pathlib import Path
from compare_reports import ReportCompare
import pandas


@pytest.fixture
def same_csv():
    # Read in test files
    same_csv_1 = Path(__file__).resolve().parent / "test_files" / "same_xlsx.xlsx"
    same_csv_2 = Path(__file__).resolve().parent / "test_files" / "same_xlsx.xlsx"

    # create data frames
    same_df_1 = pandas.read_excel(same_csv_1)
    same_df_2 = pandas.read_excel(same_csv_2)

    return ReportCompare(
        file1=same_df_1,
        file1_name="file_1",
        file2=same_df_2,
        file2_name="file_2",
        key="eid",
    )


def test_df_immport_df_shape(same_csv):
    """Test the shape of the dataframes to ensure they imported everything"""

    # set up test case
    rc = same_csv

    # test
    assert rc.df1.shape == (3, 4)
    assert rc.df1.shape == rc.df2.shape


def test_compare_df_summary(same_csv):
    """Summary len should be 1, 'No mismatches...'"""

    # set up test case
    rc = same_csv
    rc.compare_files()

    # test
    assert len(rc.summary) == 1
    assert "No mismatches" in rc.summary.iloc[0, 0]
