from pathlib import Path
import numpy as np
import pandas as pd
import dearpygui.dearpygui as dpg
import random


class DataInstance:
    def __init__(self, file_path, instance_tag, manager_tag, quick_format_options=None):
        self.file_path = file_path
        self.file_name = Path(file_path).stem
        self.instance_tag = instance_tag
        self.manager_tag = manager_tag
        self.df = self._convert_to_dataframe(file_path, quick_format_options)
        # self.alias = self._init_alias_dict(self.df, self.file_name)
        self.x_axis = None # consider making _x_axis marked private


        self.file_alias = self.file_name
        self.col_names = tuple(self.df.columns)
        self.col_aliases = self.col_names # initialize them the same
        self.col_names_map = self._init_names_to_alias_map(self.col_names) # key=name, val=alias
        self.col_aliases_map = reverse_dict_mapping(self.col_names_map) # key=alias, val=name
        self.preferred_x_axis = self.df.columns[0]



    def get_alias_from_name(self, name):
        return self.col_names_map[name]

    def get_name_from_alias(self, alias):
        return self.col_aliases_map[alias]

    def get_column(self, name_or_alias):  # first index: column name, second index: data
        if name_or_alias in self.col_names:
            col_name = name_or_alias
        elif name_or_alias in self.col_aliases:
            col_name = self.get_name_from_alias(name_or_alias)
        else:
            return None # TODO decide if this is enough protection

        return (col_name, self.df[col_name])

    def update_alias_list(self):
        self.col_aliases = (key for key in self.col_aliases_map.keys()) # TODO: decide if should be arr or tuple

    def set_file_alias(self,text):
        self.file_alias = text

    def set_col_alias(self, header, alias):
        # oldAlias = next((key for key, val in self.col_aliases_map.items() if val == header), None)
        old_alias = self.get_alias_from_name(header)
        if alias == '' or None:
            self.col_aliases_map[header] = self.col_aliases_map.pop(old_alias)
        else:
            self.col_aliases_map[alias] = self.col_aliases_map.pop(old_alias)

        # IMPORTANT: regenerate the alias list and regenerate the column names mapping as theyre used by internal class logic
        self.update_alias_list()
        self.col_names_map = reverse_dict_mapping(self.col_aliases_map)


    def set_preferred_x_axis(self, col_name):
        self.preferred_x_axis = col_name


    # def set_alias(self, alias): # alias is dict with key=colname, val=user_data
    #     self.alias.update(alias)
    #
    # def get_column_aliases(self, skip_first=True):
    #     """
    #     Returns a list of (key, value) tuples for all columns.
    #     Optionally skip the first alias (usually the filename).
    #     """
    #     aliases = list(self.alias.items())
    #     if skip_first:
    #         return aliases[1:]
    #     return aliases
    #
    # # probably break out to file_name and file_alias and col_name and col_alias
    # # maybe each ds is called a series?
    # def get_filename_alias(self):
    #     """
    #     Returns the first alias (usually the filename).
    #     """
    #     first_key, first_val = next(iter(self.alias.items()))
    #     return first_key, first_val

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

    # # TODO: make the aliases the keys that way you can aliases.key to get the corresponding col_name
    # @staticmethod
    # def _init_alias_dict(df, file_name):
    #     alias_dict = {file_name: file_name}
    #     for header in df.columns:
    #         alias_dict[header] = header
    #     return alias_dict

    @staticmethod
    def _convert_to_dataframe(file_path, quick_format_options): # TODO add quick format processing to drop rows, rename df, set datetimee, rename headers
        df = pd.read_csv(file_path)
        df.insert(0, '_index', df.index)
        return df

    #
    # @staticmethod
    # def _init_alias_dict2(df):
    #
    #     header_to_alias = {header: header for header in df.columns}
    #     alias_to_header = {val: key for key, val in header_to_alias.items()}
    #
    #     return alias_to_header

    @staticmethod
    def _init_names_to_alias_map(col_names):
        return {name: name for name in col_names}


def reverse_dict_mapping(dict):
    return({val: key for key, val in dict.items()})


# configure options for data instance (alias, preferred x axis, axis manipulation) # TODO: should probably live in data_instance.py
def configure_data(sender, app_data, user_data) -> None:

    ds = user_data
    table_column_headers = ('Header', 'Alias','Set X-Axis')
    COLS = len(table_column_headers)
    ROWS = len(ds.col_aliases_map)
    print(COLS)
    print(ROWS)
    table_tags = [[None for _ in range(COLS)] for _ in range(ROWS)]
    TEXT_BOX_WIDTH = 150
    COLUMN_RENAME_HEIGHT = 150

    renamed_list = []

    def renamed_columns_callback(sender):
        renamed_list.append(sender)

    def set_x_axis_callback(sender):
        ds.set_preferred_x_axis(dpg.get_value(sender))

    def show_preview(sender, app_data, user_data):

        alias = user_data[0]
        append = user_data[1]

        random_col = random.choice(ds.col_aliases)

        if append:
            dpg.set_item_label(preview, f'{alias}_{random_col}')
        else:
            dpg.set_item_label(preview,f'{random_col}')

    def print_table():
        out = []
        for r in range(ROWS):
            arr = []
            for c in range(COLS):
                arr.append(dpg.get_value(table_tags[r][c]))
            out.append(arr)
        print(out)

        for r in range(ROWS):
            header_cell_tag=table_tags[r][0]
            alias_cell_tag=table_tags[r][1]
            xaxis_cell_tag=table_tags[r][2]

            header = dpg.get_value(header_cell_tag)
            alias = dpg.get_value(alias_cell_tag)
            set_x_axis = dpg.get_value(xaxis_cell_tag)


            ds.set_col_alias(header, alias)

            print(ds.col_aliases_map)

            print(renamed_list)
            print(ds.preferred_x_axis)

            if set_x_axis:
                ds.set_preferred_x_axis(header)

    with dpg.theme() as delete_theme:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (180, 60, 60))  # neutral red
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (200, 80, 80))  # lighter red
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (160, 40, 40))  # darker red
            # dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
            # dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 6, 4)


    with dpg.window(label=f'Configure {ds.file_name}', modal=True, autosize=True, pos=(200,25)) as source_config:
        # with dpg.tab_bar():
        # with dpg.tab(label='Fields'):
        dpg.add_separator(label='Rename File')
        with dpg.group(horizontal=True):
            alias = dpg.add_input_text(label=ds.file_name,width=TEXT_BOX_WIDTH, default_value=ds.file_alias)
            dpg.add_spacer(width=25)
            append = dpg.add_checkbox(label='Append', default_value=True)
            with dpg.tooltip(dpg.last_item()):
                dpg.add_text('Add File Alias to Column Alias in Plot Legend')
        with dpg.group(horizontal=True):
            dpg.add_button(label='Preview:',callback=show_preview, user_data=[alias,append])
            dpg.add_spacer(width=15)
            preview = dpg.add_text()
        dpg.add_separator(label='Set Source X-Axis')
        with dpg.group(horizontal=True):
            dpg.add_combo(ds.col_names,label='Set X-Axis',width=TEXT_BOX_WIDTH, default_value=ds.preferred_x_axis, callback=set_x_axis_callback)
            dpg.add_spacer(width=25)
            dpg.add_checkbox(label='DateTime?', default_value=False) # TODO: change this to degault_option
        with dpg.group(horizontal=True):
            dpg.add_text('Scalar Operation')
            dpg.add_combo(('None', 'Multiply', 'Divide'), default_value='None', width=80) # TODO: change this to default_option
            dpg.add_input_float(step=0, step_fast=0, width=50,  format="%.1f")
        dpg.add_separator(label='Rename Columns')
        with dpg.child_window(height=COLUMN_RENAME_HEIGHT, border=False, auto_resize_x=True):
            for name in ds.col_names:
                alias = ds.get_alias_from_name(name)
                dpg.add_input_text(label=name, default_value=alias, width=TEXT_BOX_WIDTH, no_spaces=True, auto_select_all=True, callback=renamed_columns_callback)

            # with dpg.tab(label='Edit X-Axis'):
            #     dpg.add_listbox(("AAAA", "BBBB", "CCCC", "DDDD"), label='ALTERNATE X-AXIS SOURCE')
            #     dpg.add_checkbox(label='Re-base axis')
            #     dpg.add_text('scalar')
            #     dpg.add_text('time')
            #     dpg.add_text('UTC offset')
        dpg.add_separator()
        with dpg.group(horizontal=True):
            dpg.add_button(label="Cancel")
            dpg.add_button(label="OK", callback=print_table)
            dpg.add_spacer(width=170)
            dpg.add_button(label="Delete Series")
            dpg.bind_item_theme(dpg.last_item(), delete_theme)

        # with dpg.table(header_row=False, borders_innerH=False, borders_innerV=False, borders_outerH=False, borders_outerV=False):
        #     dpg.add_table_column()
        #     dpg.add_table_column()
        #     dpg.add_table_column()
        #     with dpg.table_row():
        #         dpg.add_button(label="OK", callback=print_table)
        #         dpg.add_button(label="Cancel")
        #         dpg.add_button(label="Delete Series")
        #         dpg.bind_item_theme(dpg.last_item(), delete_theme)

        # with dpg.group(horizontal=True):
        #     dpg.add_button(label="OK", callback=print_table)
        #     dpg.add_button(label="Cancel")
        #     dpg.add_spacer(width=-1)  # stretch spacer (acts like glue)
        #     btn = dpg.add_button(label="Delete Series")
        #     dpg.bind_item_theme(btn, delete_theme)

#
# with dpg.table(header_row=True, borders_innerH=True,
#                borders_outerH=True, borders_innerV=True, borders_outerV=True):
#     for c in range(COLS):
#         dpg.add_table_column(label=table_column_headers[c])
#
#     for r in range(ROWS):
#         # for header in ds.col_aliases.values():
#         with dpg.table_row():
#             header_cell_tag = dpg.add_text(list(ds.col_aliases_map.values())[
#                                                r])  # get vals is aliases (df headers), convert to list, and get index to get headers TODO: consider just exposing headers as private variable
#             alias_cell_tag = dpg.add_input_text(no_spaces=True, width=100)
#             xaxis_cell_tag = dpg.add_checkbox()
#             table_tags[r] = [header_cell_tag, alias_cell_tag, xaxis_cell_tag]
