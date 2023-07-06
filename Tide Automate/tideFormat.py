import pandas as pd
import numpy as np

class FilerTide():
    def __init__(self, downloads, gene) -> None:
        self._downloads = downloads
        self._gene = gene

    def _filterRows(self, df):
        ovarian_df = df[df.iloc[:, 1] == "Ovarian"]
        ovary_df = df[df.iloc[:, 1] == "Ovary"]
        return pd.concat([ovarian_df, ovary_df])
    
    def _filterColumns(self, df):
        # List of column indices to remove
        columns_to_remove = [1, 2, 3, 4, 6, 7, 8]
        df = df.drop(df.columns[columns_to_remove], axis=1)
        df.reset_index(drop=True, inplace=True)
        df['Gene'] = self._gene
        return df
    
    def _tryAddExclusion(self, df):
        try:
            exclusion_df = pd.read_csv(f"{self._downloads}/{self._gene}_exclusion.csv")
            return_df = pd.concat([df, exclusion_df], axis=1, ignore_index=True)
            return return_df
        except FileNotFoundError as error:
            print(f"Cannot Find Exclusion File \n {error}")
            return df

    def filterData(self):
        df = pd.read_csv(f"{self._downloads}/{self._gene}.csv")
        rows_df = self._filterRows(df)
        column_df = self._filterColumns(rows_df)
        return self._tryAddExclusion(column_df)

class FormatTide():
    def __init__(self, filename, columns) -> None:
        self._filename = filename
        self._columns = columns
        self.Tcga1 = True
        self.genes = []
        self.complete_rows = []
        self.current_row = np.zeros(len(columns))

    def _sortColumns(self, df):
        og_columns = ["Cohort", "T Dysfunction", "Gene", "Condition", "Z score"]
        if len(df.columns) != len(og_columns):
            difference = len(df.columns) - len(og_columns)
            for missing in range(difference):
                og_columns.append(str(missing))
        df.columns = og_columns
        return df.sort_values('Gene')
    
    def _resetCurretRow(self, current_gene):
        if len(self.genes) != 0:
            if current_gene != self.genes[-1]:
                append_row = self.current_row.tolist()
                append_row[0] = self.genes[-1]
                self.complete_rows.append(append_row)
                self.current_row = np.zeros(len(self._columns))
    
    def _tcgaFlip(self, cohort):
        if cohort == 'TCGA':
            if self.Tcga1:
                cohort = 'TCGA1'
                self.Tcga1 = False
            else:
                cohort = 'TCGA2'
                self.Tcga1 = True

    def _getValues(self, cohort, row):
        for index, column in enumerate(self._columns):
            if cohort == column:
                self.current_row[index] = row['T Dysfunction'] 
            elif row['Condition'] == column:
                self.current_row[index] = row['Z score']

    def formatTide(self):
        df = pd.read_csv(self._filename)
        df_sorted = self._sortColumns(df)

        for i, row in df_sorted.iterrows(): #For each row, need i to get row
            current_gene = row['Gene']
            self._resetCurretRow(current_gene)
            cohort = row['Cohort']
            self._tcgaFlip(cohort)

            self._getValues(cohort, row)
            self.genes.append(current_gene)

        output_df = pd.DataFrame(self.complete_rows, columns=self._columns)
        output_df.replace(to_replace = 0, value = '', inplace=True)
        return output_df

