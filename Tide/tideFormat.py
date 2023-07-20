import pandas as pd
import numpy as np

class FilerTide():
    def __init__(self, downloads: str, gene: str, exclusion: bool, cancers: list[str]) -> None:
        self._downloads = downloads
        self._gene = gene
        self._exclusion = exclusion
        self._cancers = cancers

    def _filterRows(self, df):
        final_dfs = []
        for cancer in self._cancers:
            filter_df = df[df.iloc[:, 1] == cancer]
            final_dfs.append(filter_df)
        return pd.concat(final_dfs)
    
    def _mergeCancerSubtype(self, df):
        def mergeNonNaRow(row):
            if pd.notna(row['Subtype']):
                    return row['Cohort'] + ' ' + row['Subtype']
            return row['Cohort']
        
        df['MergedColumn'] = df.apply(mergeNonNaRow, axis=1)
        return df
        
    def _filterColumns(self, df):
        # List of column indices to remove
        columns_to_remove = [0, 1, 2, 3, 4, 6, 7, 8]
        df = df.drop(df.columns[columns_to_remove], axis=1)
        df.reset_index(drop=True, inplace=True)
        df['Gene'] = self._gene
        return df
    
    def _tryAddExclusion(self, df):
        try:
            if not self._exclusion: #If exclusion false
                raise EnvironmentError("Exclusion data not wanted.")
            exclusion_df = pd.read_csv(f"{self._downloads}/{self._gene}_exclusion.csv")
            return_df = pd.concat([df, exclusion_df], axis=1, ignore_index=False)
            return return_df #Remove left over labels
        except FileNotFoundError as error:
            print(f"Cannot Find Exclusion File \n {error}")
            return df
        except EnvironmentError:
            return df

    def filterData(self):
        df = pd.read_csv(f"{self._downloads}/{self._gene}.csv")
        rows_df = self._filterRows(df)
        named_df = self._mergeCancerSubtype(rows_df)
        column_df = self._filterColumns(named_df)
        return self._tryAddExclusion(column_df)

class FormatTide():
    def __init__(self, filename, columns, exclusion: bool) -> None:
        self._filename = filename
        self._exclusion = exclusion
        self.genes = []
        self.complete_rows = []
        self.Tcga1 = True
        self._columns = self._prepColumns(columns)
        self.current_row = np.zeros(len(columns) + 1) # +1 for TCGA 1 and 2

    def _prepColumns(self, columns: list[str]):
        columns.insert(0, "Gene")
        if self._exclusion:
            columns.extend(['CAF FAP', 'MDSC', 'TAM M2'])
        return columns

    def _sortColumns(self, df):
        og_columns = ["T Dysfunction", "Cohort", "Gene", "Condition", "Z score"]
        difference = abs(len(df.columns) - len(og_columns))
        if len(df.columns) < len(og_columns):
            for missing in range(difference):
                df[missing] = ''
        elif len(df.columns) > len(og_columns):
            for missing in range(difference):
                og_columns.append(str(missing))
        df.columns = og_columns
        return df.sort_values('Gene')
    
    def _resetCurretRow(self, current_gene):
        if len(self.genes) != 0 and current_gene != self.genes[-1]:
                append_row = self.current_row.tolist()
                append_row[0] = self.genes[-1]
                self.complete_rows.append(append_row)
                self.current_row = np.zeros(len(self._columns) + 1) # +1 for TCGA 1 and 2

    def addTCGAcols(self):
        try:
            self._columns.index("TCGA1")
        except ValueError:
            #Don't need try called in if block for TCGA
            index = self._columns.index('TCGA') 
            self._columns.pop(index)
            self._columns.insert(index, 'TCGA1')
            self._columns.insert(index + 1, 'TCGA2')

    def _tcgaFlip(self, cohort):
        if cohort == 'TCGA':
            self.addTCGAcols()
            if self.Tcga1:
                cohort = 'TCGA1'
                self.Tcga1 = False
            else:
                cohort = 'TCGA2'
                self.Tcga1 = True
        return cohort

    def _getValues(self, cohort, row):
        for index, column in enumerate(self._columns):
            if cohort == column: #Split the whitespace to remove subtype
                self.current_row[index] = row['T Dysfunction'] 
            elif self._exclusion and row['Condition'] == column:
                self.current_row[index] = row['Z score']

    def _correctArraySize(self):
        #Drop the difference from the right for every row in array
        for i, row in enumerate(self.complete_rows): #Index each array in list
            #If len of row greater than column length
            if len(self.complete_rows[i]) > len(self._columns): 
                #Go into row and take up to the length of wanted row
                self.complete_rows[i] = self.complete_rows[i][:len(self._columns)] 

    def _mergeTCGA(self, df):
        # Merge values from Column1 into Column2, but only overwrite if the value is empty in Column2
        df['TCGA1'] = df['TCGA1'].fillna(df['TCGA2']) 
        # If the number of Na
        tcga2_na = df['TCGA2'].isna().sum()
        if len(df['TCGA1']) / 1.1 < 2 * tcga2_na * 1.1:
            df = df.drop('TCGA2', axis=1)
        return df

    def _outputDf(self):
        output_df = pd.DataFrame(self.complete_rows, columns=self._columns)
        output_df.replace(to_replace = 0, value = np.NaN, inplace=True)
        output_df = self._mergeTCGA(output_df)
        output_df.fillna('', inplace=True) #Replace remaining NaN
        return output_df

    def formatTide(self):
        df = pd.read_csv(self._filename)
        df_sorted = self._sortColumns(df)

        for i, row in df_sorted.iterrows(): #For each row, need i to get row
            current_gene = row['Gene']
            self._resetCurretRow(current_gene) #Reset all vars for next row

            cohort = row['Cohort']
            cohort = self._tcgaFlip(cohort)
            self._getValues(cohort, row)
            self.genes.append(current_gene)

        self._correctArraySize()
        return self._outputDf()
