from pathlib import Path
import pandas as pd
from typing import Dict
from dataclasses import dataclass
import dearpygui.dearpygui as dpg
from themes import Themes
from tags import Tags
from utils import sources, DragItemType

@dataclass
class ColumnParams: # addition attributes can be assigned to any column
    alt_x_axis: str | None = None
    axis_style: str | None = None
    histogram_bins: int = None
    fft_magnitudes_arr: list | None = None
    fft_frequencies_arr: list | None = None

@dataclass
class DragPayloadColumn:
    ds: 'DataInstance'
    col_header_to_plot: str
    params: ColumnParams
    type: DragItemType

class DataInstance:
    def __init__(self, file_path: str, quick_format_options: Dict = None):

        self.file_name = Path(file_path).stem
        self.file_alias = self.file_name # initialize them the same
        self.self_tag = Tags.generate()
        self.button_tag = Tags.generate()
        self.content_tag = Tags.generate() # TODO: this is a stub from changing from collapsible header to button. decide if it should exist
        self.df = self._create_dataframe(file_path, quick_format_options)
        self.x_axis_header = self.df.columns[0]
        self._header_to_alias: Dict[str,str] = {header: header for header in self.df.columns}
        self._all_column_params: Dict[str, ColumnParams] = {name: ColumnParams() for name in self.df.columns}


    @property
    def col_headers(self) -> tuple:
        return tuple(self._header_to_alias.keys())

    @property
    def col_aliases(self) -> tuple:
        return tuple(self._header_to_alias.values())

    def delete(self) -> None:
        dpg.delete_item(self.button_tag)
        dpg.delete_item(self.content_tag)  #TODO: this is a stub from changing from collapsible header to button. decide if it should exist

    def get_alias_from_header(self, name) -> str:
        return self._header_to_alias[name]

    def set_file_alias(self, text) -> None:
        if text == '' or text is None:
            self.file_alias = self.file_name
        else:
            self.file_alias = text

    # REFACTOR: THIS IS THE MAIN ENTRY POINT FOR MANIPULATE. MAYBE CLEAN THIS UP FOR BETTER ACCESS. USE DRAG PAYLOAD CLASS INSTEAD?
    def get_column(self, header_or_alias) -> tuple|None:
        if header_or_alias in self.col_headers:
            header = header_or_alias
        else:
            header = next((h for h, a in self._header_to_alias.items() if a == header_or_alias), None)
        if header is None:
            return None # TODO decide if this is enough protection
        return (header, self.get_alias_from_header(header), self.df[header]) # (header, alias, df[data]) # TODO: decide if tuple is better than dict. will need to change in plot instance initializer to .values()

    def set_col_alias(self, header, alias) -> None:
        if alias in self.col_aliases:
            raise ValueError("ALIAS ALREADY USED, CHOOSE ANOTHER ALIAS")
        if alias == '' or alias is None:
            alias = header
        self._header_to_alias[header] = alias

    def add_new_column(self, values: pd.DataFrame, header, alias, params: 'ColumnParams') -> None:
        if header in self.col_headers:
            raise ValueError('COLUMN NAME ALREADY PRESENT IN DATA')
        if alias is None:
            alias = header
        self.df[header] = values
        self._header_to_alias[header] = alias
        self._all_column_params[header] = params if params is not None else ColumnParams()

    def set_column_params(self, col_header, params: ColumnParams) -> None:
        self._all_column_params[col_header] = params

    def drag_and_drop_column(self, col_header) -> DragPayloadColumn:
        return DragPayloadColumn(ds=self,
                                 col_header_to_plot=col_header,
                                 params=self._all_column_params[col_header],
                                 type=DragItemType.DATA)

    @staticmethod
    def _create_dataframe(file_path, quick_format_options) -> pd.DataFrame: # FEATURE add quick format processing to drop rows, rename df, set datetimee, rename headers
        ext = Path(file_path).suffix
        if ext == '.txt':
            df = pd.read_csv(file_path, sep="\t")
        else:
            df = pd.read_csv(file_path)
        df.insert(0, '_index', df.index)
        return df

def quick_set_x_axis(sender, app_data: DragPayloadColumn):
    ds = dpg.get_item_user_data(sender) # user data is not passed with drop_callback so we fetch it manually
    ds.x_axis_header = app_data.col_header_to_plot
    populate_data_manager(ds) # TODO: seems a bit brute force to regenerate the entire data manager window, but this has the benefit of regenerating the config window during callback creation so it doesnt open empty after changes like with the line above. Previously just tried configureitemlabel

def populate_data_manager(ds: DataInstance) -> None:
    # if dpg.does_item_exist(ds.manager_tag): #TODO: this is a stub from changing from collapsible header to button. decide if it should exist
    #     dpg.delete_item(ds.manager_tag,children_only=True)

    if dpg.does_item_exist(ds.content_tag):
        dpg.delete_item(ds.content_tag, children_only=True)

    with dpg.child_window(parent=Tags.data_manager_tab, tag=ds.content_tag, show=True, border=False, auto_resize_y=True, autosize_y=True): #TODO: this is a stub from changing from collapsible header to button. decide if it should exist
    # with dpg.group(parent=ds.manager_tag): # parent is the collapsing header window
        # dpg.add_button(label='Configure', callback=configure_data_window, user_data=ds) # TODO: decide to keep or remove this. if remove consider cleanidng up the "right click" functions and rolling them into thier children
        dpg.add_text(default_value=f'X-Axis: {ds.get_alias_from_header(ds.x_axis_header)}', drop_callback=quick_set_x_axis, user_data=ds)
        dpg.add_separator()
        with dpg.child_window(height=130, resizable_y=True, border=False):
            for header in ds.col_headers:  # keys are aliases, cols are df headers
                alias = ds.get_alias_from_header(header)
                dpg.add_button(label=alias)
                # CREATE DRAG AND DROP COLUMN PAYLOAD - drag_data becomes app_data in callback
                with dpg.drag_payload(label=alias, parent=dpg.last_item(), # TODO: is parent required here?
                                      drag_data=ds.drag_and_drop_column(header)):  # TODO: really hard to figure out what this points to. I think this is what PAYLOAD TYPE is for so you can easily search around to see the payload source
                    dpg.add_text(alias)

def add_data_to_sources(_, app_data: Dict[str,str]) -> None:
    ds = DataInstance(file_path=app_data['file_path_name'])
    sources.add(ds)

    # with dpg.collapsing_header(label=ds.file_alias, default_open=True, tag=ds.manager_tag, parent=Tags.data_manager_tab):
    #     dpg.bind_item_theme(dpg.last_item(), Themes.collapsing_header) # TODO: check this I believe it is the DEFAULT theme. consider renaming it for clarity
    dpg.add_button(label=ds.file_alias, tag=ds.button_tag, parent=Tags.data_manager_tab, width=-1, callback=toggle_content_visibility_callback, user_data=ds)
    # BUG: for some reason the first time the popup is triggered, it renders at screen loc 0,0. I had minimal luck fixing it. it appears this is only a bug when loading in data very early. when its called in timesink directly
    with dpg.popup(dpg.last_item(),min_size=(50,50)):
        dpg.add_selectable(label="Edit", callback=right_click_configure, user_data=ds)
        dpg.add_spacer(height=2)
        dpg.add_separator()
        dpg.add_spacer(height=2)  # add space so you don't accidentally hit delete
        dpg.add_selectable(label='Delete', callback=right_click_delete, user_data=ds)
        dpg.bind_item_theme(dpg.last_item(), Themes.red_selectable)

    populate_data_manager(ds)

def toggle_content_visibility_callback(sender, app_data, user_data: DataInstance) -> None:
    ds = user_data
    dpg.hide_item(ds.content_tag) if dpg.is_item_shown(ds.content_tag) else dpg.show_item(ds.content_tag)

def right_click_configure(sender, app_data, user_data: DataInstance) -> None:
    dpg.set_value(sender, False)
    configure_data_window(None, None, user_data)

def right_click_delete(sender, app_data, user_data: DataInstance) -> None:
    sources.delete(user_data)

def configure_data_window(_, __, user_data: DataInstance) -> None:

    TEXT_BOX_WIDTH = 150 # REFACTOR: MOVE THESE TO UTILS.PY OR OPTIONS.PY probably make into an ENUM
    COLUMN_RENAME_HEIGHT = 150

    ds = user_data
    renamed_aliases = []

    def remove_data_from_sources() -> None:
        dpg.delete_item(Tags.source_config)  # BUG: This may error out when adding delete on right click menu
        sources.delete(ds)

    def save_and_close() -> None:
        # FEATURE: implement the other config options at some point
        ds.x_axis_header = dpg.get_value(choose_x_axis_header)

        new_alias = dpg.get_value(choose_file_alias)
        if new_alias:
            ds.set_file_alias(new_alias)
            dpg.set_item_label(ds.button_tag, new_alias)

        for tag in renamed_aliases:
            col_alias = dpg.get_value(tag)
            col_name = dpg.get_item_label(tag)
            original_alias = ds.get_alias_from_header(col_name)
            if col_alias == original_alias:
                continue
            if col_alias != original_alias and col_alias in ds.col_aliases:
                dpg.show_item(duplicate_error)
                return
            if col_alias:
                ds.set_col_alias(col_name, col_alias)

        populate_data_manager(ds)
        dpg.delete_item(Tags.source_config)

    with dpg.window(label=f'Configure {ds.file_name}', modal=True, autosize=True, pos=(200,25), tag=Tags.source_config): #TODO: make window position based on window size
        dpg.add_separator(label='Rename File')
        with dpg.group(horizontal=True):
            choose_file_alias = dpg.add_input_text(label=ds.file_name,width=TEXT_BOX_WIDTH, default_value=ds.file_alias, no_spaces=True)
            dpg.add_spacer(width=25)
        dpg.add_separator(label='Set Source X-Axis')
        with dpg.group(horizontal=True):
            choose_x_axis_header = dpg.add_combo(ds.col_headers, label='Set X-Axis', width=TEXT_BOX_WIDTH, default_value=ds.x_axis_header)
            dpg.add_spacer(width=25)
            choose_datetime = dpg.add_checkbox(label='DateTime?', default_value=False) # FEATURE: change this to degault_option. DECIDE IF DATETIME needs to be selected here or if it should be done with date dropdown in config plot
        dpg.add_separator(label='Rename Columns')
        with dpg.child_window(height=COLUMN_RENAME_HEIGHT, border=False, auto_resize_x=True):
            for name in ds.col_headers:
                alias = ds.get_alias_from_header(name)
                tag = Tags.generate()
                renamed_aliases.append(tag)
                dpg.add_input_text(label=name, default_value=alias, width=TEXT_BOX_WIDTH, no_spaces=True, auto_select_all=True, tag=tag)
        dpg.add_separator()
        with dpg.group(horizontal=True):
            dpg.add_button(label="Cancel", callback=lambda: dpg.delete_item(Tags.source_config))
            dpg.add_button(label="OK", callback=save_and_close)
            duplicate_error = dpg.add_text(default_value='NO DUPLICATE ALIAS ALLOWED', show=False) # BUG: make this not resize the window when it pops up. Unfortunately popups over modal does not seem possible
            dpg.bind_item_theme(dpg.last_item(), Themes.red_text)
            # TODO: decide to keep or remove this. if remove consider cleanidng up the "right click" functions and rolling them into thier children
            # dpg.add_spacer(width=190)
            # dpg.add_button(label="DELETE DATA", callback=remove_data_from_sources)
            # dpg.bind_item_theme(dpg.last_item(), Themes.red_button)
