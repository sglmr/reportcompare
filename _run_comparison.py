from compare_reports import ReportCompare
from pathlib import Path


def main():

    file_1 = Path(__file__).resolve().parent / "File_1.csv"
    file_2 = Path(__file__).resolve().parent / "File_2.csv"
    results_file = Path(__file__).resolve().parent / "COMPARE_RESULTS.xlsx"

    compare = ReportCompare(
        file1=file_1,
        file1_name=file_1.name,
        file2=file_2,
        file2_name=file_2.name,
        key="Unique_ID",
    )

    compare.compare_files()
    compare.build_summary()
    compare.write_to_excel(results_file=results_file)


if __name__ == "__main__":
    main()
