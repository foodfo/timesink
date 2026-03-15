from asyncio import create_eager_task_factory

import dearpygui.dearpygui as dpg
import pandas as pd
import numpy as np

import data_instance # TODO: collapse this to preserve namespace
import plot_instance
from data_instance import DataInstance, add_data_to_sources
from plot_instance import PlotInstance, add_new_plot_instance, set_all_plot_heights, change_num_visible_plots
from utils import sources, plots # TODO: see if theres a better way to store data and plots. Should they be classeS?
from utils import * # TODO: temporary until I manage Globals better
from tags import Tags
from themes import Themes
from manipulate import manipulation_options
from draggables import draggable_options
import export


global showSide
showSide = False
downsample_percent = 100

#TODO: todo lists
#FEATURE: new features to add to code
#BUG: Known issue
#REFACTOR: rework this chunk of code

#region Feature Extraction
    # test=5
#endregion

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
# dpg.show_debug()

Tags.init_tags()
Themes.init_themes()
# Tags.print_tags()


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
    dpg.configure_item(Tags.source_config, show=True)



def set_x_axis(sender, app_data, user_data):
    parent_tag = app_data['parent_tag']
    col_name = app_data['col_name']
    col_alias = app_data['col_alias']

    data[parent_tag].set_x_axis(col_name)

    print(f'AXIS SET TO {col_alias}')


def show_file_dialog(sender, app_data, user_data):
    # dpg.show_item("file_dialog")
    dpg.configure_item(item='file_dialog',user_data=user_data,show=True) #TODO: consider moving Tags into utils so they can be referenced globally rather than being passed through as user data





# main window with menu bar and tab instance containers
with dpg.window(tag=Tags.main_window):
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
            dpg.add_menu_item(label='Export Trim Window', callback=export.open_trim_window_export)
        with dpg.menu(label="Help"):
            pass
    # with dpg.tab_bar(label = "test", tag=Tags.tabs):
    #     dpg.add_tab_button(label="<<", tag="hide_sidebar",callback=hide_sidebar)
    #     with dpg.tab(label="Tab 1", tag=Tags.primary_tab):
    #         pass
    #     with dpg.tab(label="Tab 2"):
    #         pass
    #     dpg.add_tab_button(label="+")


#
# with dpg.theme() as blue_header_theme:
#     with dpg.theme_component(dpg.mvCollapsingHeader):
#         dpg.add_theme_color(dpg.mvThemeCol_Header, (45, 95, 180, 150), category=dpg.mvThemeCat_Core)          # closed
#         dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (70, 120, 220, 200), category=dpg.mvThemeCat_Core)  # hover
#         dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (40, 90, 200, 255), category=dpg.mvThemeCat_Core)    # open

# with dpg.theme() as blue_header_theme:
#     with dpg.theme_component(dpg.mvCollapsingHeader):
#         dpg.add_theme_color(dpg.mvThemeCol_Header, (45, 95, 180, 150))          # closed
#         dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (70, 120, 220, 200))  # hover
#         dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (40, 90, 200, 255))    # open

# with dpg.theme() as blue_header_theme:  # CUTOM BLUE HEADEr THEME
#     with dpg.theme_component(dpg.mvCollapsingHeader):
#         dpg.add_theme_color(dpg.mvThemeCol_Header, (0, 119, 200, 153))          # closed
#         dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (29, 151, 236, 103))  # hover
#         dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (0, 119, 200, 153))

with dpg.theme() as blue_header_theme: # TEAL THEME
    with dpg.theme_component(dpg.mvCollapsingHeader):
        dpg.add_theme_color(dpg.mvThemeCol_Header, (10, 100,100, 200))          # closed
        dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (10, 100,100, 170))  # hover
        dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (10, 100,100, 200))

# with dpg.theme() as neutral_theme:
#     pass


# everything that sits in a single tab instance
# with dpg.child_window(parent=Tags.primary_tab, border=False):
with dpg.child_window(parent=Tags.main_window, border=False):
    # dpg.add_spacer(height = 5)
    with dpg.group(horizontal=True):
            # with dpg.child_window(label="Options",autosize_x=True, auto_resize_y=True, tag=Tags.options_window):
        with dpg.child_window(resizable_x=True, width=SIDEBAR_WIDTH, border=False, tag=Tags.sidebar):
            with dpg.collapsing_header(label="Options",default_open=False):
                dpg.bind_item_theme(dpg.last_item(), blue_header_theme)
                with dpg.child_window(auto_resize_y=True):
                    dpg.add_text(f'Downsample %: {downsample_percent}%')
                    dpg.add_checkbox(label='Downsample Data')
                    dpg.add_checkbox(label='Unlock X-Axis')
                    dpg.add_checkbox(label='Bind cursor to screen')
                    dpg.add_checkbox(label='Bind cursor to axis')

        # with dpg.child_window(label="Options", autosize_x=True, auto_resize_y=True, border=False, always_use_window_padding=True):
            with dpg.collapsing_header(label="Draggables", default_open=True):
                dpg.bind_item_theme(dpg.last_item(), blue_header_theme)
                with dpg.child_window(auto_resize_y=True, tag=Tags.draggables):
                    draggable_options()


            with dpg.collapsing_header(label="Manipulations", default_open=True):
                dpg.bind_item_theme(dpg.last_item(), blue_header_theme)
                with dpg.child_window(auto_resize_y=True, tag=Tags.manipulate):
                    manipulation_options()


            # with dpg.child_window(label="managers",autosize_x=True, autosize_y=True, tag=Tags.managers_window):
            #     with dpg.tab_bar():
            #         with dpg.tab(label='DATA', tag=Tags.data_manager_tab):

            with dpg.collapsing_header(label='PLOTS', default_open=False):
                dpg.bind_item_theme(dpg.last_item(), blue_header_theme)
                with dpg.child_window(auto_resize_y=True, tag=Tags.plot_manager_tab):
                    # with dpg.tab(label='PLOTS', tag=Tags.plot_manager_tab):

                    with dpg.group(horizontal=True):
                        dpg.add_button(label="ADD PLOT", callback=add_new_plot_instance) # TODO: make add plot and add data centered on column
                        dpg.add_input_int(default_value=MAX_PLOTS_ON_SCREEN, callback=change_num_visible_plots, width=65, min_value=1,max_value=10, min_clamped=True, max_clamped=True)
                        with dpg.tooltip(parent=dpg.last_item(), delay=.01):
                            dpg.add_text('Max Visible Plots')


                    # with dpg.group(horizontal=True):
                    #     dpg.add_button(label="- Plot", callback=delete_last_plot_instance) # TODO: add right click button to quicklly delete plots and ddata
                    #     dpg.add_button(label="+ Plot", callback=add_new_plot_instance)
                    dpg.add_separator()
                dpg.add_spacer(height=10)

            with dpg.collapsing_header(label='DATA', default_open=True):
                dpg.bind_item_theme(dpg.last_item(), blue_header_theme)
                with dpg.child_window(auto_resize_y=True, tag = Tags.data_manager_tab):
                    # dpg.add_button(label="ADD DATA", callback=lambda: dpg.show_item("file_dialog"), user_data=dpg.last_item())
                    dpg.add_button(label="IMPORT DATA", callback=show_file_dialog, user_data=dpg.last_container())
                    dpg.add_separator()
                    dpg.add_spacer(height=3) # TODO: decide to keep or delete the spacer


            # this is the actual plot area
        with dpg.child_window(autosize_x=True, autosize_y=True, border=False, tag=Tags.plot_window):
            for i in range(NUM_PLOTS_ON_STARTUP):
                add_new_plot_instance()
                # add_new_plot_instance()


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


with dpg.file_dialog(directory_selector=False, show=False, width=400, height=400, tag="file_dialog", callback=add_data_to_sources, default_path='/Users/tyler/Downloads'):
    dpg.add_file_extension('.csv',color=(150, 255, 150, 255))
    dpg.add_file_extension('.txt',color=(150, 150, 255, 255))

    # dpg.add_user_data(dpg.last_container)

    # with dpg.group():
    #     dpg.add_checkbox(label="Set Current Path as Default")
    #     with dpg.group(horizontal=True):
    #         dpg.add_combo(default_axis_choices,default_value = default_axis_choices[0])
    #         dpg.add_checkbox(label='Set Default')
    #     dpg.add_combo(quick_format_choices, default_value = quick_format_choices[0],label='Quick-Format Data')
    #     dpg.add_combo(preprocessor_choices,default_value = preprocessor_choices[0]) # TODO: selecting a preproccessor should pop up a text box to request input. Ideally this would run the script to get a list of inputs to display
    #     dpg.add_checkbox(label='Launch Import Configurator', callback = lambda: dpg.show_item(import_config))


with dpg.window(label='Import Configurator', width=500, height=700, modal=True, show=False, tag=Tags.import_config):
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
        dpg.add_button(label="IMPORT", callback=lambda: dpg.hide_item(Tags.import_config))
        dpg.add_button(label="Cancel")

# add_data_to_sources(None, app_data = {'file_path_name': 'C:\\Users\\tyler\\Downloads\\exampleData1.csv'})
# add_data_to_sources(None, {'file_path_name': '/Users/tyler/Downloads/test_data2.csv'})
add_data_to_sources(None, {'file_path_name': '/Users/tyler/Documents/repos/timesink/test_data1.csv'})

# dpg.show_debug()
dpg.set_viewport_resize_callback(set_all_plot_heights)
# dpg.show_style_editor()
dpg.show_item_registry()
dpg.set_primary_window(Tags.main_window, True)
dpg.start_dearpygui()
dpg.destroy_context()