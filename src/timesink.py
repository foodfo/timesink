
import dearpygui.dearpygui as dpg
import pandas as pd
import numpy as np

import data_instance # TODO: collapse this to preserve namespace
import plot_instance
from data_instance import DataInstance, add_new_data_instance
from plot_instance import PlotInstance, delete_last_plot_instance, add_new_plot_instance, set_all_plot_heights
from utils import data, plots # TODO: see if theres a better way to store data and plots. Should they be classeS?
from utils import * # TODO: temporary until I manage Globals better
import tags


global showSide
showSide = False
downsample_percent = 100


# region Feature Extraction
test=5
# endregion

# data = {} # key = UUID tag, value = DataSource
# plots = {} # key = UUID tag, value = PlotInstance
# graphs = [] # TODO: temporary just to get plots adding. consider putting plot manager and plot viewer TAGS in PI then reference PI by TAG
#
# class DataSourceRegistry:
#     def __init__(self):
#         self.sources = {}
#
#     def add(self, ds):
#         self.sources[ds.tag] = ds
#
#     def get(self, tag):
#         return self.sources[tag]
#
# registry = DataSourceRegistry()


dpg.create_context()
dpg.create_viewport(title=WINDOW_TITLE,width=VIEWPORT_WIDTH,height=VIEWPORT_HEIGHT)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.show_debug()

tags.init_tags()
tags.print_tags()


# ---------- Helper Functions ----------

def hide_sidebar():

    global showSide

    if showSide:
        direction = '<<'
    else:
        direction = '>>'
    dpg.configure_item('Options', show=showSide)
    dpg.configure_item('Plot Controller', show=showSide)
    dpg.configure_item('hide_sidebar', label=direction)
    showSide = not showSide


def show_source_config():
    dpg.configure_item(tags.source_config,show=True)



def set_x_axis(sender, app_data, user_data):
    parent_tag = app_data['parent_tag']
    col_name = app_data['col_name']
    col_alias = app_data['col_alias']

    data[parent_tag].set_x_axis(col_name)

    print(f'AXIS SET TO {col_alias}')


def show_file_dialog(sender, app_data, user_data):
    # dpg.show_item("file_dialog")
    dpg.configure_item(item='file_dialog',user_data=user_data,show=True) #TODO: consider moving tags into utils so they can be referenced globally rather than being passed through as user data





# main window with menu bar and tab instance containers
with dpg.window(tag=tags.mainwin):
    with dpg.menu_bar(show=False):
        with dpg.menu(label="File",): # not sure what to put here
            pass
        with dpg.menu(label="Options"): # some options and config maybe?
            pass
        with dpg.menu(label="Plot"): # plot options like crosshairs, num plots
            pass
        with dpg.menu(label="Export"): # export options:
            dpg.add_menu_item(label="Truncate to View")
            dpg.add_menu_item(label="Truncate between parsers")
            dpg.add_menu_item(label="Truncate between every other parser")
        with dpg.menu(label="Help"):
            pass
    with dpg.tab_bar(label = "test", tag=tags.tabs):
        dpg.add_tab_button(label="<<", tag="hide_sidebar",callback=hide_sidebar)
        with dpg.tab(label="Tab 1", tag=tags.primary_tab):
            pass
        with dpg.tab(label="Tab 2"):
            pass
        dpg.add_tab_button(label="+")


# everything that sits in a single tab instance
with dpg.child_window(parent=tags.primary_tab, border=False):
    with dpg.group(horizontal=True):
        with dpg.child_window(resizable_x=True, width=SIDEBAR_WIDTH, border=False, tag=tags.sidebar):
            with dpg.child_window(label="Options",autosize_x=True, auto_resize_y=True, tag=tags.options_window):
                with dpg.collapsing_header(label="Options",default_open=True):
                    dpg.add_text(f'Downsample %: {downsample_percent}%')
                    dpg.add_checkbox(label='Downsample Data')
                    dpg.add_checkbox(label='Unlock X-Axis')
                    dpg.add_checkbox(label='Bind cursor to screen')
                    dpg.add_checkbox(label='Bind cursor to axis')
                    dpg.add_separator(label='draggables')
                    dpg.add_button(label='Add Parse Line')
                    dpg.add_button(label='Find Peak on Screen')
                    dpg.add_button(label='Add Annotation')

            with dpg.child_window(label="managers",autosize_x=True, autosize_y=True, tag=tags.managers_window):
                with dpg.tab_bar():
                    with dpg.tab(label='DATA', tag=tags.data_manager_tab):
                        # dpg.add_button(label="ADD DATA", callback=lambda: dpg.show_item("file_dialog"), user_data=dpg.last_item())
                        dpg.add_button(label="ADD DATA", callback=show_file_dialog, user_data=dpg.last_container())
                        dpg.add_separator()
                        dpg.add_spacer(height=10)

                    with dpg.tab(label='PLOTS', tag=tags.plot_manager_tab):
                        with dpg.group(horizontal=True):
                            dpg.add_button(label="- Plot", callback=delete_last_plot_instance)
                            dpg.add_button(label="+ Plot", callback=add_new_plot_instance)
                        dpg.add_separator()
                        dpg.add_spacer(height=10)

        # this is the actual plot area
        with dpg.child_window(autosize_x=True, autosize_y=True, border=False, tag=tags.plot_window):
            for i in range(NUM_PLOTS_ON_STARTUP):
                add_new_plot_instance()


#
# # configure options for data instance (alias, preferred x axis, axis manipulation) # TODO: should probably live in plot_instance.py
# with dpg.window(label='Configure Data Source', modal=True, height=500, width=500, show=False) as source_config:
#     with dpg.tab_bar():
#         with dpg.tab(label='Fields'):
#             dpg.add_input_text(label='File Label')
#             dpg.add_checkbox(label='Append Data Name tp Column Names', default_value=True)
#             dpg.add_separator()
#
#             with dpg.table(header_row=True, borders_innerH=True,
#                            borders_outerH=True, borders_innerV=True, borders_outerV=True):
#                 dpg.add_table_column(label='Source Col Name')
#                 dpg.add_table_column(label='Visible Name')
#                 dpg.add_table_column(label='Set X-Axis')
#
#                 with dpg.table_row():
#                     dpg.add_text('_index')
#                     dpg.add_input_text(no_spaces=True, width=100)
#                     dpg.add_checkbox()
#
#                 with dpg.table_row():
#                     dpg.add_text('time')
#                     dpg.add_input_text(no_spaces=True, width=100)
#                     dpg.add_checkbox()
#
#                 with dpg.table_row():
#                     dpg.add_text('SAMPLE 1')
#                     dpg.add_input_text(no_spaces=True, width=100)
#                     dpg.add_checkbox()
#                 with dpg.table_row():
#                     dpg.add_text('Voltage (mV)')
#                     dpg.add_input_text(no_spaces=True, width=100)
#                     dpg.add_checkbox()
#                 with dpg.table_row():
#                     dpg.add_text('aceleration_z')
#                     dpg.add_input_text(no_spaces=True, width=100)
#                     dpg.add_checkbox()
#                     dpg.add_checkbox()
#
#         with dpg.tab(label='Edit X-Axis'):
#             dpg.add_listbox(("AAAA", "BBBB", "CCCC", "DDDD"), label='ALTERNATE X-AXIS SOURCE')
#             dpg.add_checkbox(label='Re-base axis')
#             dpg.add_text('scalar')
#             dpg.add_text('time')
#             dpg.add_text('UTC offset')
#
#     dpg.add_spacer(height=50)
#     dpg.add_separator()
#     with dpg.group(horizontal=True, horizontal_spacing=100):
#         dpg.add_button(label="Cancel")
#         dpg.add_button(label="OK")
#         dpg.add_button(label="Delete Series")
#         # with dpg.theme_component(dpg.mvButton):
#         #     dpg.add_theme_color(dpg.mvThemeCol_Button, (7.0, 0.6, 0.6))
#         #     dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ( 7.0, 0.8, 0.8))
#         #     dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (7.0, 0.7, 0.7))
#         #     dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3 * 5)
#         #     dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 3 * 3, 3 * 3)
#






# opens importer file dialog and impor configurator. also will handle plugins/preprocessors - TODO: should probably move to its own file

default_axis_choices = ('Indexes','First Column')
quick_format_choices = ('None','OmegaTempLogger','ConvergenceInstruments')
preprocessor_choices = ('None','WDH.py','WingTester.py','RainflowCounting.py')


with dpg.file_dialog(directory_selector=False, show=False, width=400, height=400, tag="file_dialog", callback=add_new_data_instance, default_path='/Users/tyler/Downloads'):
    dpg.add_file_extension('.csv',color=(150, 255, 150, 255))
    # dpg.add_user_data(dpg.last_container)

    # with dpg.group():
    #     dpg.add_checkbox(label="Set Current Path as Default")
    #     with dpg.group(horizontal=True):
    #         dpg.add_combo(default_axis_choices,default_value = default_axis_choices[0])
    #         dpg.add_checkbox(label='Set Default')
    #     dpg.add_combo(quick_format_choices, default_value = quick_format_choices[0],label='Quick-Format Data')
    #     dpg.add_combo(preprocessor_choices,default_value = preprocessor_choices[0]) # TODO: selecting a preproccessor should pop up a text box to request input. Ideally this would run the script to get a list of inputs to display
    #     dpg.add_checkbox(label='Launch Import Configurator', callback = lambda: dpg.show_item(import_config))


with dpg.window(label='Import Configurator',width=500, height=700, modal=True, show=False, tag=tags.import_config):
    dpg.add_input_int(label='Header Row Index') # check options and make type safe for int only
    dpg.add_input_text(label='Drop Rows') # hint explains that this is an array that is later parsed
    dpg.add_separator()

    options = ['','Header','Rename','X-Axis Vals','To DateTime','Op 1', 'Op 2', 'Disable']

    with dpg.table(header_row=True, borders_innerH=True,
                   borders_outerH=True, borders_innerV=True, borders_outerV=True):
        for i in options:
            dpg.add_table_column(label=i) # TODO: figure out row sizing

        for i in range(20): # TODO: have this be the count of columns
            with dpg.table_row():
                dpg.add_text(i)
                dpg.add_text(f'_index #{i}') # TODO: get column header from file - use Header Row Index
                dpg.add_input_text(no_spaces=True, width=100)
                dpg.add_checkbox()
                dpg.add_checkbox()
                dpg.add_input_text(no_spaces=True, width=100)
                dpg.add_input_text(no_spaces=True, width=100)
                dpg.add_checkbox()

    with dpg.group(horizontal=True):
        dpg.add_button(label="IMPORT", callback=lambda: dpg.hide_item(tags.import_config))
        dpg.add_button(label="Cancel")

add_new_data_instance(None, {'file_path_name': 'C:\\Users\\tyler\\Downloads\\exampleData1.csv'}, tags.data_manager_tab)
# add_new_data_ instance(None, {'file_path_name': '/Users/tyler/Downloads/test_data1.csv'}, tags.data_manager_tab)

dpg.show_debug()
dpg.set_viewport_resize_callback(set_all_plot_heights)
# dpg.show_item_registry()
dpg.set_primary_window(tags.mainwin,True)
dpg.start_dearpygui()
dpg.destroy_context()