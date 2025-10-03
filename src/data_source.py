from pathlib import Path
import numpy as np
import pandas as pd


class DataSource:
    def __init__(self, file_path, tag):
        self.file_path = file_path
        self.file_name = Path(file_path).stem
        self.tag = tag
        self.df = self._convert_to_dataframe(file_path)
        self.alias = self._init_alias_dict(self.df, self.file_name)
        self.x_axis = None # consider making _x_axis marked private

    def set_alias(self, alias): # alias is dict with key=colname, val=user_data
        self.alias.update(alias)

    def get_column_aliases(self, skip_first=True):
        """
        Returns a list of (key, value) tuples for all columns.
        Optionally skip the first alias (usually the filename).
        """
        aliases = list(self.alias.items())
        if skip_first:
            return aliases[1:]
        return aliases

    # probably break out to file_name and file_alias and col_name and col_alias
    # maybe each ds is called a series?
    def get_filename_alias(self):
        """
        Returns the first alias (usually the filename).
        """
        first_key, first_val = next(iter(self.alias.items()))
        return first_key, first_val

    def set_x_axis(self, col_name):
        if self.x_axis is None:
            self.x_axis = np.array(self.df[col_name], dtype=float)
        else:
            raise ValueError('X AXIS ALREADY ASSIGNED')  # TODO: somehow figure out how to manage series with more than 1 x axis. i think x axis needs to be assigned as a property of the plot, not of the data Y vals

    def get_x_axis(self):
        if self.x_axis is None: # TODO: make sure this actually works
            return np.array(self.df['_index'], dtype=float)
        return self.x_axis

    def get_y_axis(self, col_name):
        return np.array(self.df[col_name], dtype=float)

    # TODO: make the aliases the keys that way you can aliases.key to get the corresponding col_name
    @staticmethod
    def _init_alias_dict(df, file_name):
        alias_dict = {file_name: file_name}
        for header in df.columns:
            alias_dict[header] = header
        return alias_dict

    @staticmethod
    def _convert_to_dataframe(file_path):
        df = pd.read_csv(file_path)
        df.insert(0, '_index', df.index)
        return df