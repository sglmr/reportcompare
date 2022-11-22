import pandas


class ReportCompare:
    def __init__(self, file1, file1_name, file2, file2_name, key, results_file=None):

        # Set the key/index field to match on
        self.key = key
        self.results_file = results_file

        assert type(file1) == type(file2), "File types are not the same"

        # Get the filenames
        self.f1_name = file1_name
        self.f2_name = file2_name

        # Read the files into a dataframe
        if type(file1) == pandas.DataFrame:
            self.df1 = file1.set_index(self.key)
            self.df2 = file2.set_index(self.key)
        elif ".csv" in self.f1_name:
            self.df1 = pandas.read_csv(file1, index_col=self.key)
            self.df2 = pandas.read_csv(file2, index_col=self.key)
        elif ".xls" in self.f1_name:
            self.df1 = pandas.read_excel(file1, index_col=self.key)
            self.df2 = pandas.read_excel(file2, index_col=self.key)
        else:
            raise ValueError

    def compare_files(self):

        # Find extra columns on each file
        self.find_extra_columns()

        # Drop extra columns from each file
        self.drop_extra_columns()

        # Remove duplicate records
        self.deduplicate_files()

        # Remove records that don't match between files
        self.drop_missing_records()

        # Run Pandas comparison
        self.pandas_compare()

        # Buld summary dataframe
        self.build_summary()

    def pandas_compare(self):
        self.compare = self.df1.compare(
            self.df2,
            result_names=(f"{self.f1_name}", f"{self.f2_name}"),
            align_axis=0,
        )
        return self.compare

    def write_to_excel(self):
        with pandas.ExcelWriter(self.results_file, mode="w") as writer:
            if len(self.summary) > 0:
                self.summary.to_excel(
                    writer,
                    sheet_name="Summary",
                    index=False,
                )
            if len(self.compare) > 0:
                self.compare.to_excel(
                    writer,
                    sheet_name="Mismatches",
                    freeze_panes=(1, 2),
                    merge_cells=False,
                )
            if len(self.extra_columns) > 0:
                self.extra_columns.to_excel(
                    writer,
                    sheet_name="Extra Columns",
                    index=False,
                )
            if len(self.duplicates) > 0:
                self.duplicates.to_excel(
                    writer,
                    sheet_name="Duplicates",
                    freeze_panes=(1, 2),
                )
            if len(self.missing) > 0:
                self.missing.to_excel(
                    writer,
                    sheet_name="Missing Records",
                    freeze_panes=(1, 2),
                )

    def build_summary(self) -> pandas.DataFrame:
        """Put together a summary dataframe of the results"""

        summary = list()

        if len(self.extra_columns) > 0:
            summary.append(["Extra columns", "", len(self.extra_columns)])

        if len(self.duplicates) > 0:
            summary.append(["Duplicate records", "", int(len(self.duplicates) / 2)])

        if len(self.missing) > 0:
            summary.append(["Missing records from files", "", len(self.missing)])

        for x in self.compare:
            summary.append(["Compare mismatch", x, int(self.compare[x].count() / 2)])

        # If no issues, note that in the summary
        if len(summary) == 0:
            msg = [f"No mismatches comparing {self.f1_name} to {self.f2_name}", "", ""]
            summary.append(msg)

        self.summary = pandas.DataFrame(
            summary, columns=["Description", "Field", "Count"]
        )

        return self.summary

    def drop_missing_records(self) -> pandas.DataFrame:
        """Remove records that don't match between the two files"""

        # find a unique list of keys shared between the two files
        unique_keys = self.df1.index.intersection(self.df2.index)

        # find the rows in file 1 that aren't in file 2
        df1_ex_rows = self.df1[~self.df1.index.isin(self.df2.index)]
        df1_ex_rows.insert(0, "file", f"{self.f1_name}")
        df1_ex_rows.insert(1, "err_msg", f"Missing from {self.f2_name}")

        # find the rows in file 2 that aren't in file 1
        df2_ex_rows = self.df2[~self.df2.index.isin(self.df1.index)]
        df2_ex_rows.insert(0, "file", f"{self.f2_name}")
        df2_ex_rows.insert(1, "err_msg", f"Missing from {self.f1_name}")

        # Create a dataframe of the missing records
        self.missing = pandas.concat([df1_ex_rows, df2_ex_rows])

        # Drop the missing records
        self.df1 = self.df1[self.df1.index.isin(unique_keys)]
        self.df2 = self.df2[self.df2.index.isin(unique_keys)]

        # Return the df of missing records
        return self.missing

    def deduplicate_files(self) -> pandas.DataFrame:
        """Find the duplicate records in each file"""

        # Find File 1 Duplicates
        df1_dupes = self.df1[self.df1.index.duplicated(keep=False)]
        df1_dupes.insert(0, "file", f"{self.f1_name}")
        df1_dupes.insert(1, "err_msg", "Duplicate record")

        # Find File 2 Duplicates
        df2_dupes = self.df2[self.df2.index.duplicated(keep=False)]
        df2_dupes.insert(0, "file", f"{self.f2_name}")
        df2_dupes.insert(1, "err_msg", "Duplicate record")

        # Create a dataframe of the duplicates
        self.duplicates = pandas.concat([df1_dupes, df2_dupes])

        # Delete the duplicate records from the original files
        self.df1 = self.df1[~self.df1.index.duplicated(keep="first")]
        self.df2 = self.df2[~self.df2.index.duplicated(keep="first")]

        return self.duplicates

    def _label_list(self, label: str, items: list) -> list[list]:
        """Labels a list of items to be turned into a dataframe"""
        return [[label, x] for x in items]

    def find_shared_columns(self) -> pandas.Index:
        """Create an Index (list) of the shared columns in the files"""

        return self.og_df1.columns.intersection(self.og_df2.columns)

    def drop_extra_columns(self):
        """Deletes extra columns that aren't in both files.
        Returns an integer of the number of columns dropped."""

        start_len = len(self.df1.columns) + len(self.df2.columns)

        # Drop columns that don't match
        self.df1.drop(labels=self.f1_ex_cols, axis=1, inplace=True)
        self.df2.drop(labels=self.f2_ex_cols, axis=1, inplace=True)

        # Count of dropped columns
        c = start_len - len(self.df1.columns) - len(self.df1.columns)

        return c

    def find_extra_columns(self) -> pandas.DataFrame:
        """Compares the two files and identifies columns
        that don't exist in both files."""

        # Find the columns that don't match between the two data frames
        self.f1_ex_cols = self.df1.columns.difference(self.df2.columns)
        self.f2_ex_cols = self.df2.columns.difference(self.df1.columns)

        self.extra_columns = pandas.concat(
            [
                pandas.DataFrame(
                    self._label_list(f"{self.f1_name}", self.f1_ex_cols),
                    columns=["Source", "Extra Column"],
                ),
                pandas.DataFrame(
                    self._label_list(f"{self.f2_name}", self.f2_ex_cols),
                    columns=["Source", "Extra Column"],
                ),
            ]
        )

        return self.extra_columns
