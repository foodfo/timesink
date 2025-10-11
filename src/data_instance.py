from pathlib import Path
import numpy as np
import pandas as pd
import dearpygui.dearpygui as dpg
import tags
from utils import data


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
        self.source_x_axis_name = self.df.columns[0]
        self.is_prepended_alias = True # TODO: auto mark prepend True once there is more than one DataInstance and flip back to false when deleting down to just one
        self._extra_drag_payload_params = self._init_extra_drag_payload_params(None)
        # self.source_x_axis = self.get_column(self.df.columns[0])
        # self.x_alias = self.source_x_axis[1]



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

        # return {
        #         "name": col_name,
        #         "alias": self.get_alias_from_name(col_name),
        #         "data": self.df[col_name]
        #     }# (name, alias, df[data])

        return (col_name,self.get_alias_from_name(col_name),self.df[col_name]) # (name, alias, df[data]) # TODO: decide if tuple is better than dict. will need to change in plot instance initializer to .values()

    def update_alias_list(self):
        self.col_aliases = (key for key in self.col_aliases_map.keys()) # TODO: decide if should be arr or tuple

    def set_file_alias(self,text):
        if text == '' or None:
            self.file_alias = self.file_name
        else:
            self.file_alias = text

        # if self._is_prepended_alias:
        #     for alias in self.col_aliases:
        #         self.prepend_file_alias(alias)

    def set_col_alias(self, name, alias): # set new column alias for column that already exists
        # oldAlias = next((key for key, val in self.col_aliases_map.items() if val == name), None)
        if alias in self.col_aliases:
            raise ValueError("ALIAS ALREADY USED, CHOOSE ANOTHER ALIAS")
            # return

        old_alias = self.get_alias_from_name(name)
        if alias == '' or None:
            self.col_aliases_map[name] = self.col_aliases_map.pop(old_alias)
        else:
            self.col_aliases_map[alias] = self.col_aliases_map.pop(old_alias)

        # IMPORTANT: regenerate the alias list and regenerate the column names mapping as they're used by internal class logic
        self.update_alias_list()
        self.col_names_map = reverse_dict_mapping(self.col_aliases_map)

    def set_source_x_axis(self, col_name):
        # self.source_x_axis = (col_name, self.get_alias_from_name(col_name), self.df[col_name])
        self.source_x_axis_name = col_name

    def add_new_column(self, data, col_name,col_alias):

        if col_name in self.col_names:
            raise ValueError('COLUMN NAME ALREADY PRESENT IN DATA')

        if col_alias is None:
            col_alias = col_name


        self.df[col_name] = data
        self.col_names_map[col_name] = col_alias

        # IMPORTANT: regenerate the alias list and regenerate the column names mapping as they're used by internal class logic
        self.col_aliases_map = reverse_dict_mapping((self.col_names_map))
        self.update_alias_list()
        self.col_names=tuple(self.df.columns)  # TODO: there MUST be a smoother way to update all of these items
        self._init_extra_drag_payload_params(col_name)

    def get_prepended_alias(self, alias):
        if self.is_prepended_alias:
            return self.file_alias + '_' + alias
        else:
            return alias



    def set_extra_drag_payload_params(self, col_name, user_params):
        self._extra_drag_payload_params[col_name] = user_params

    def get_drag_payload_data(self, col_name):
        return {'instance_tag':self.instance_tag, 'col_name':col_name, 'extra_params':self._extra_drag_payload_params[col_name]}

    # def prepend_file_alias(self, col_alias):
    #     col_name = self.get_name_from_alias(col_alias)
    #     prepended_col_alias = self.file_alias + '_' + col_alias
    #     self.set_col_alias(col_name, prepended_col_alias)
    #
    #
    # def undo_prepend_file_alias(self, col_alias):
    #     col_name = self.get_name_from_alias(col_alias):
    #     undo_prepend_col_alias = col_alias.strip(self.file_alias + '_')
    #     self.set_col_alias(col_name, undo_prepend_col_alias)

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

    # def set_x_axis(self, col_name):
    #     if self.x_axis is None:
    #         self.x_axis = np.array(self.df[col_name], dtype=float)
    #     else:
    #         raise ValueError('X AXIS ALREADY ASSIGNED')  # TODO: somehow figure out how to manage series with more than 1 x axis. i think x axis needs to be assigned as a property of the plot, not of the data Y vals
    #
    # def get_x_axis(self):
    #     if self.x_axis is None: # TODO: make sure this actually works
    #         return np.array(self.df['_index'], dtype=float)
    #     return self.x_axis
    #
    # def get_y_axis(self, col_name):
    #     return np.array(self.df[col_name], dtype=float)

    # # TODO: make the aliases the keys that way you can aliases.key to get the corresponding col_name
    # @staticmethod
    # def _init_alias_dict(df, file_name):
    #     alias_dict = {file_name: file_name}
    #     for header in df.columns:
    #         alias_dict[header] = header
    #     return alias_dict

    def _init_extra_drag_payload_params(self, col_name=None):
        params = {
            'alt_x_axis': None,
            'axis_style': None,
            'histogram_bins': None,
            'FFT_magnitudes_arr': None,
            'FFT_frequencies_arr': None
        }

        if col_name is None:
            all_params_dict = {}
            for name in self.col_names:

                all_params_dict[name] = dict(params) # wrap in dict() to make a copy to pass values rather than a reference to params
            return all_params_dict
        else:
            self._extra_drag_payload_params[col_name] = dict(params)
            return None

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

def create_data_manager_items(ds):
    if dpg.does_item_exist(ds.manager_tag):  # TODO: this feels like a really crude way to do this. consider something better
        dpg.delete_item(ds.manager_tag,children_only=True)

    with dpg.group(parent=ds.manager_tag):
        dpg.add_button(label='Configure', callback=configure_data, user_data=ds)
        dpg.add_text(f'X-Axis: {ds.get_alias_from_name(ds.source_x_axis_name)}')
        # dpg.configure_item(source_config, show=True)
        # dpg.add_button(label='Set X-Axis', drop_callback=set_x_axis)
        dpg.add_separator()
        with dpg.child_window(height=130, resizable_y=True):
            for name in ds.col_names:  # keys are aliasees, cols are df headers
                alias = ds.get_alias_from_name(name)
                dpg.add_button(label=alias)
                with dpg.drag_payload(label=alias, parent=dpg.last_item(), # TODO: is parent required here?
                                      drag_data=ds.get_drag_payload_data(name)):  # TODO: really hard to figure out what this points to. I think this is what PAYLOAD TYPE is for so you can easily search around to see the payload source

                    if ds.is_prepended_alias:
                        dragged_object_name = ds.file_alias + '_' + alias
                    else:
                        dragged_object_name = alias
                    dpg.add_text(dragged_object_name)
                    # THIS IS MAPPED INTO PLOT INSTANCE
                    # drag_data in payload becomes app_data in callback - kinda strange

# def update_data_instance_columns(ds):
#
#     if dpg.does_item_exist(ds.column_window_tag): # TODO: this feels like a really crude way to do this. consider something better
#         print('DELETING ITEM')
#         dpg.delete_item(ds.column_window_tag)
#
#     with dpg.child_window(height=100, parent=ds.manager_tag, tag=ds.column_window_tag):
#         for name in ds.col_names:  # keys are aliasees, cols are df headers
#             alias = ds.get_alias_from_name(name)
#             dpg.add_button(label=alias)
#             with dpg.drag_payload(label=alias, parent=dpg.last_item(),drag_data={'parent_tag': ds.instance_tag, 'col_name': name,'col_alias': alias}):  # TODO: really hard to figure out what this points to. I think this is what PAYLOAD TYPE is for so you can easily search around to see the payload source
#                 dpg.add_text(alias)




def add_new_data_instance(sender, app_data, user_data):

    target_container_tag = user_data #TODO: consider moving tags into utils so they can be referenced globally rather than being passed through as user data
    data_instance_tag = dpg.generate_uuid()
    data_manager_tag = dpg.generate_uuid()
    column_window_tag = dpg.generate_uuid()

    # print(app_data)

    # with dpg.theme() as other_theme:
    #     with dpg.theme_component(dpg.mvCollapsingHeader):
    #         dpg.add_theme_color(dpg.mvThemeCol_Header, (10, 10, 10, 150))  # closed
    #         dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (10, 100,100, 200))  # hover
    #         dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (10, 10, 10, 255))  # open
    with dpg.theme() as other_theme:
            with dpg.theme_component(dpg.mvCollapsingHeader):
                dpg.add_theme_color(dpg.mvThemeCol_Header, (51,51,55,255))          # closed
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (29, 151, 236, 103))  # hover
                dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (0, 119, 200, 153))

    # with dpg.theme() as other_theme:
    #     with dpg.theme_component(dpg.mvCollapsingHeader):
    #         pass  # empty for all buttons

    ds = DataInstance(file_path=app_data['file_path_name'], instance_tag=data_instance_tag, manager_tag=data_manager_tag)

    data[ds.instance_tag] = ds

    with dpg.collapsing_header(label=ds.file_alias, default_open=True, tag=ds.manager_tag, parent=target_container_tag): # TODO: plot_instance just uses tag.parent instead. consider that here
        dpg.bind_item_theme(dpg.last_item(), other_theme)
        # dpg.bind_item_theme(dpg.last_item(), 0)


    create_data_manager_items(ds)

    # with dpg.collapsing_header(label=ds.file_alias, default_open=True, tag=ds.manager_tag, parent=target_container_tag):
    #
    #     dpg.add_button(label='Configure', callback=configure_data, user_data=ds)
    #     # dpg.configure_item(source_config, show=True)
    #     # dpg.add_button(label='Set X-Axis', drop_callback=set_x_axis)
    #     dpg.add_separator()
    #     update_data_instance_columns(ds)
        # with dpg.child_window(height=100):
        #     for name in ds.col_names: # keys are aliasees, cols are df headers
        #         alias = ds.get_alias_from_name(name)
        #         dpg.add_button(label=alias)
        #         with dpg.drag_payload(label=alias,parent=dpg.last_item(),drag_data={'parent_tag':ds.instance_tag,'col_name':name,'col_alias':alias}): # TODO: really hard to figure out what this points to. I think this is what PAYLOAD TYPE is for so you can easily search around to see the payload source
        #             dpg.add_text(alias)


# configure options for data instance (alias, preferred x axis, axis manipulation) # TODO: should probably live in data_instance.py
def configure_data(sender, app_data, user_data) -> None:

    parent_tag = dpg.get_item_parent(sender) # TODO consider wrapping this in user data for consistency?
    ds = user_data # TODO: consider passing tag in instead of the full object. does it matter?
    table_column_headers = ('Header', 'Alias','Set X-Axis')
    TEXT_BOX_WIDTH = 150
    COLUMN_RENAME_HEIGHT = 150

    # init tags
    file_alias_choice = None
    prepend_alias_choice = None
    x_axis_choice = None
    datetime_choice = None
    operation_choice = None
    scalar_choice = None
    duplicate_error = None

    renamed_list = set() # TODO: rename these for clarity
    stored_choices = set()

    # stage changes for OK
    def renamed_columns_callback(sender):
        renamed_list.add(sender)

    def store_choices_callback(sender, app_data, user_data):
        # stored_choices[sender] = app_data
        stored_choices.add(sender)

    # send changes on OK
    def save_config_choices_callback(sender):

        if file_alias_choice in stored_choices and dpg.get_value(file_alias_choice): # skip if " "
            ds.set_file_alias(dpg.get_value(file_alias_choice))
            dpg.set_item_label(ds.manager_tag, ds.file_alias) # TODO: maybe need to make an updater function that does the whole configurator manager in one place

        if x_axis_choice in stored_choices:
            if ds.source_x_axis_name != dpg.get_value(x_axis_choice): # skip if its the same text
                ds.set_source_x_axis(dpg.get_value(x_axis_choice)) # TODO: review source_x_axis logic in this project and decide if it makes more sense for it to be an alias or a name

        if prepend_alias_choice in stored_choices:
            if dpg.get_value(prepend_alias_choice):
                ds.is_prepended_alias = True
            else:
                ds.is_prepended_alias = False

        # TODO: implement the other config options at some point

        for tag in renamed_list:
            col_alias = dpg.get_value(tag)
            col_name = dpg.get_item_label(tag)

            if col_alias in ds.col_aliases:
                dpg.show_item(duplicate_error)
                return

            if col_alias:
                dpg.hide_item(duplicate_error)
                ds.set_col_alias(col_name, col_alias)

        # update_data_instance_columns(ds)
        create_data_manager_items(ds)
        dpg.delete_item(tags.source_config)

        print(ds.file_alias)
        print(ds.source_x_axis_name)
        print(ds.col_aliases_map)

    def delete_config_window():
        dpg.delete_item(tags.source_config)


    def delete_data_callback():
        delete_config_window()
        dpg.delete_item(ds.manager_tag) # delete manager
        data.pop(ds.instance_tag) # TODO: see if theres a better way than storing the data in UTILS


    with dpg.theme() as red_text_theme:
        with dpg.theme_component(dpg.mvText):
            dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 0, 0, 255))  # RGBA

    with dpg.theme() as delete_theme:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (180, 60, 60))  # neutral red
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (200, 80, 80))  # lighter red
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (160, 40, 40))  # darker red
            # dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
            # dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 6, 4)


    with dpg.window(label=f'Configure {ds.file_name}', modal=True, autosize=True, pos=(200,25), tag=tags.source_config):
        # with dpg.tab_bar():
        # with dpg.tab(label='Fields'):
        dpg.add_separator(label='Rename File')
        with dpg.group(horizontal=True):
            file_alias_choice = dpg.add_input_text(label=ds.file_name,width=TEXT_BOX_WIDTH, default_value=ds.file_alias, no_spaces=True, callback=store_choices_callback)
            dpg.add_spacer(width=25)
            prepend_alias_choice = dpg.add_checkbox(label='Prepend', default_value=ds.is_prepended_alias, callback=store_choices_callback)
            with dpg.tooltip(dpg.last_item()):
                dpg.add_text('Add File Alias to Column Alias in Plot Legend')
        dpg.add_separator(label='Set Source X-Axis')
        with dpg.group(horizontal=True):
            x_axis_choice = dpg.add_combo(ds.col_names, label='Set X-Axis', width=TEXT_BOX_WIDTH, default_value=ds.source_x_axis_name, callback=store_choices_callback) # choices are names, not aliases. this will return a name and it must be converted back to an alias
            dpg.add_spacer(width=25)
            datetime_choice = dpg.add_checkbox(label='DateTime?', default_value=False, callback=store_choices_callback) # TODO: change this to degault_option
        with dpg.group(horizontal=True):
            dpg.add_text('Scalar Operation')
            operation_choice = dpg.add_combo(('None', 'Multiply', 'Divide'), default_value='None', width=80, callback=store_choices_callback) # TODO: change this to default_option
            scalar_choice = dpg.add_input_float(step=0, step_fast=0, width=50,  format="%.1f", callback=store_choices_callback)
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
            dpg.add_button(label="Cancel", callback=delete_config_window)
            dpg.add_button(label="OK", callback=save_config_choices_callback)
            duplicate_error = dpg.add_text('NO DUPLICATE ALIAS ALLOWED', show=False) # TODO: make this not resize the window when it pops up. Unfortunately popups over modal does not seem possible
            dpg.bind_item_theme(dpg.last_item(), red_text_theme)
            dpg.add_spacer(width=170)
            dpg.add_button(label="Delete Series", callback=delete_data_callback)
            dpg.bind_item_theme(dpg.last_item(), delete_theme)































################################################################


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
#     def print_table():
#         out = []
#         for r in range(ROWS):
#             arr = []
#             for c in range(COLS):
#                 arr.append(dpg.get_value(table_tags[r][c]))
#             out.append(arr)
#         print(out)
#
#         for r in range(ROWS):
#             header_cell_tag=table_tags[r][0]
#             alias_cell_tag=table_tags[r][1]
#             xaxis_cell_tag=table_tags[r][2]
#
#             header = dpg.get_value(header_cell_tag)
#             alias = dpg.get_value(alias_cell_tag)
#             set_x_axis = dpg.get_value(xaxis_cell_tag)
#
#
#             ds.set_col_alias(header, alias)
#
#             print(ds.col_aliases_map)
#
#             print(renamed_list)
#             print(ds.source_x_axis)
#
#             if set_x_axis:
#                 ds.set_preferred_x_axis(header)