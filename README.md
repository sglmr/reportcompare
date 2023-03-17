![Logo](logo.png)
Compare two similar CSV or Excel Reports. Particularly useful for testing before and after changes.

---
# Quickstart
1. Specify paths to `before`, `after`, and `compare results` files
2. Specify the key/id field that uniquely identifies records between the two files
3. Run and review the differences

```python
from pathlib import Path

from compare_reports import ReportCompare

# Specify file paths
file_1 = Path.cwd() / "before_csv.csv"
file_2 = Path.cwd() / "after_csv.csv"
results_file = Path.cwd() / "COMPARE_RESULTS.xlsx"

# Create ReportCompare Object
compare = ReportCompare(
    file1=file_1,
    file1_name=file_1.name,
    file2=file_2,
    file2_name=file_2.name,
    key="eid",
)

# Execute Report Compare Steps
compare.compare_files()
compare.build_summary()

# Export Summary of Report Compare Results
compare.write_to_excel(results_file=results_file)
```

---
# How does it work?
1. Script ensures it can read both of the input files.
2. Script "normalizes" the data
  - Identification, removal, and reporting of column differences between the files.
  - Identification, removal, and reporting of duplicate records on the files.
  - Identification, removal, and reporting of missing records between the files.
3. Script completes a field by field, record by record comparison
4. Script creates an XLSX report of the results.
  - Summary tab of the findings for each step
  - One tab for each type of mismatch found.