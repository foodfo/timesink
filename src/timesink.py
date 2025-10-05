from ctypes.wintypes import HINSTANCE

import dearpygui.dearpygui as dpg
import pandas as pd
import numpy as np

import data_instance
from data_instance import DataInstance
from src.plot_instance import PlotInstance

# put into utils
WINDOW_TITLE = "TIMESINK"
# VIEWPORT_HEIGHT = 1080
# VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 700
VIEWPORT_WIDTH = 1200
WINDOW_PADDING = 8
MENU_BAR_HEIGHT : int = 18
SIDEBAR_WIDTH = 150
OPTIONS_HEIGHT = 200
TAB_BAR_HEIGHT = 60 # TODO: tune this up a bit
MAX_PLOTS_ON_SCREEN = 4
NUM_PLOTS_ON_STARTUP = 2

global showSide
showSide = False
downsample_percent = 100


# region Feature Extraction
test=5
# endregion

data = {} # key = UUID tag, value = DataSource
plots = {} # key = UUID tag, value = PlotInstance
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
    dpg.configure_item(source_config,show=True)



def set_x_axis(sender, app_data, user_data):
    parent_tag = app_data['parent_tag']
    col_name = app_data['col_name']
    col_alias = app_data['col_alias']

    data[parent_tag].set_x_axis(col_name)

    print(f'AXIS SET TO {col_alias}')

def calculate_plot_height():
    num_plots = max(1, min(len(plots), MAX_PLOTS_ON_SCREEN)) # protect divide by zero and clamp to maximum plots set in "options"
    # TODO: make config and button in options set the max plots on screen. changing this should also trigger the callback to update all plot sizes
    return int((dpg.get_viewport_client_height()-TAB_BAR_HEIGHT) / num_plots)

def set_all_plot_heights():
    for instance_tag in plots.keys():
        dpg.set_item_height(plots[instance_tag].graph_tag, calculate_plot_height())

# ---------- Helper Functions ----------

def add_to_plot(sender, app_data, user_data):
    parent_tag = app_data['parent_tag']
    col_name = app_data['col_name']
    col_alias = app_data['col_alias']
    print(parent_tag)
    print(col_name)
    print(data[parent_tag])
    x_axis = data[parent_tag].get_x_axis()
    y_axis = data[parent_tag].get_y_axis(col_name)
    legend = data[parent_tag].file_alias + '_' + col_alias # TODO: make filename alias easier to get

    dpg.add_line_series(x_axis, y_axis, label=legend, parent=sender)
    print(f'sender: {sender}')
    print(f'app_Data: {app_data}')
    print(f'parent: {dpg.get_item_parent(sender)}')
    print(f'children: {dpg.get_item_children(dpg.get_item_parent(sender),slot=1)}')

    axes_tags = dpg.get_item_children(dpg.get_item_parent(sender),slot=1) # slot 1 holds axis information # TODO: figure out what to do if theres more than 2 axis
    for i in axes_tags:
        dpg.fit_axis_data(i) # TODO: consider not doing this if there is already a series present
                            # TODO: what happens if you only do one axis?


def add_line_plot(sender, app_data, user_data):
    parent_tag = app_data['parent_tag']


def get_plot_instance_number(instance_tag):
    return list(plots.keys()).index(instance_tag) + 1 # 1 indexed rather than 0 indexed

def rename_manager(sender, app_data, user_data):
    dropdown_selection = app_data
    manager_tag=user_data['manager_tag'] # is there a better way to do this than  passing the user_data?
    instance_tag=user_data['instance_tag']
    # manager_tag = dpg.get_item_parent(sender)
    plot_number = get_plot_instance_number(instance_tag)
    dpg.set_item_label(manager_tag,f'{dropdown_selection} {plot_number}')

def show_plot_options(sender, app_data):
    dpg.add_button(label='set x-axis', parent=sender)

def delete_last_plot_instance(sender, app_data): #delete the last added plot instance, manager, and graph # TODO make a way to delete any plot
    # delete data from dict and also ge the tag of the collapsable window
    instance_tag, pi = plots.popitem() # key, val # TODO: should probably made a plots.delete(tag) function and make plots a class that way logic is abstracted away from the functions
    dpg.delete_item(pi.manager_tag) # delete the options window
    dpg.delete_item(pi.graph_tag) #delete the plot
    set_all_plot_heights()

def select_plot_type(sender, app_data, user_data):
    print(sender)
    print(app_data)
    rename_manager(sender, app_data, user_data)
    show_plot_options(sender, app_data)


def add_new_plot_instance():

    plot_instance_tag = dpg.generate_uuid()
    plot_manager_tag = dpg.generate_uuid()
    plot_graph_tag = dpg.generate_uuid()

    pi = PlotInstance(instance_tag=plot_instance_tag, manager_tag=plot_manager_tag,graph_tag=plot_graph_tag)

    plots[pi.instance_tag] = pi

    instance_number = get_plot_instance_number(pi.instance_tag)

    user_data = {'instance_tag':plot_instance_tag,'manager_tag':plot_manager_tag,'graph_tag':plot_graph_tag} # there has to be a better way than sending the whole tree. If manager_tag and instance_tag are the same itll work though

    plot_types = ('Line Plot', 'Scatter Plot', 'Histogram', 'Heatmap', 'Log Plot', 'Stem Plot')

    with dpg.collapsing_header(parent=plot_manager_tab, default_open=True, tag=pi.manager_tag):
        dpg.add_combo(plot_types, default_value=plot_types[0],callback=select_plot_type, user_data=user_data)
        dpg.set_item_label(dpg.last_container(), label=f'{plot_types[0]} {instance_number}')

    with dpg.plot(width=-1, parent=plot_window, tag=pi.graph_tag):  # TODO: consider either making this dpg.uuid or wrap into a class to handle tags directly
        dpg.add_plot_legend()
        dpg.add_plot_axis(dpg.mvXAxis, label="x")
        dpg.add_plot_axis(dpg.mvYAxis, label="y", drop_callback=add_to_plot) # TODO: really hard to figure out where the appdata comes from. I think this is what PAYLOAD TYPE is for so you can easily search around to see the payload source
        print(dpg.last_container()) # TODO: figure out if y axis and x axis need thier own uuids as well then figure out how to access them
        print(dpg.get_item_label(dpg.last_container()))

    set_all_plot_heights()

def add_new_data_instance(sender, app_data, user_data):

    data_instance_tag = dpg.generate_uuid()
    data_manager_tag = dpg.generate_uuid()

    ds = DataInstance(file_path=app_data['file_path_name'], instance_tag=data_instance_tag, manager_tag=data_manager_tag)

    data[ds.instance_tag] = ds

    with dpg.collapsing_header(label=ds.file_alias, default_open=True, tag=ds.manager_tag, parent=data_manager_tab):

        dpg.add_button(label='Configure', callback=data_instance.configure_data, user_data=ds)
        # dpg.configure_item(source_config, show=True)

        dpg.add_button(label='Set X-Axis', drop_callback=set_x_axis)
        dpg.add_separator()
        with dpg.child_window(height=100):
            for name in ds.col_names: # keys are aliasees, cols are df headers
                alias = ds.get_alias_from_name(name)
                dpg.add_button(label=alias)
                with dpg.drag_payload(label=alias,parent=dpg.last_item(),drag_data={'parent_tag':ds.instance_tag,'col_name':name,'col_alias':alias}): # TODO: really hard to figure out what this points to. I think this is what PAYLOAD TYPE is for so you can easily search around to see the payload source
                    dpg.add_text(alias)




# main window with menu bar and tab instance containers
with dpg.window() as mainwin:
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
    with dpg.tab_bar(label = "test") as tabs:
        dpg.add_tab_button(label="<<", tag="hide_sidebar",callback=hide_sidebar)
        with dpg.tab(label="Tab 1", tag="tab1") as primary_tab:
            pass
        with dpg.tab(label="Tab 2", tag="tab2"):
            pass
        dpg.add_tab_button(label="+", tag="add_tab")


# everything that sits in a single tab instance
with dpg.child_window(parent=primary_tab, border=False):
    with dpg.group(horizontal=True):
        with dpg.child_window(resizable_x=True, width=SIDEBAR_WIDTH, border=False) as sidebar:
            with dpg.child_window(label="Options",autosize_x=True, auto_resize_y=True) as options_window:
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

            with dpg.child_window(label="managers",autosize_x=True, autosize_y=True) as managers_window:
                with dpg.tab_bar():
                    with dpg.tab(label='DATA') as data_manager_tab:
                        dpg.add_button(label="ADD DATA", callback=lambda: dpg.show_item("file_dialog") )
                    with dpg.tab(label='PLOTS') as plot_manager_tab:
                        with dpg.group(horizontal=True):
                            dpg.add_button(label="- Plot", callback=delete_last_plot_instance)
                            dpg.add_button(label="+ Plot", callback=add_new_plot_instance)
                        dpg.add_separator()
                        dpg.add_spacer(height=10)

        # this is the actual plot area
        with dpg.child_window(autosize_x=True, autosize_y=True, border=False) as plot_window:
            for i in range(NUM_PLOTS_ON_STARTUP):
                add_new_plot_instance()



# configure options for data instance (alias, preferred x axis, axis manipulation) # TODO: should probably live in plot_instance.py
with dpg.window(label='Configure Data Source', modal=True, height=500, width=500, show=False) as source_config:
    with dpg.tab_bar():
        with dpg.tab(label='Fields'):
            dpg.add_input_text(label='File Label')
            dpg.add_checkbox(label='Append Data Name tp Column Names', default_value=True)
            dpg.add_separator()

            with dpg.table(header_row=True, borders_innerH=True,
                           borders_outerH=True, borders_innerV=True, borders_outerV=True):
                dpg.add_table_column(label='Source Col Name')
                dpg.add_table_column(label='Visible Name')
                dpg.add_table_column(label='Set X-Axis')

                with dpg.table_row():
                    dpg.add_text('_index')
                    dpg.add_input_text(no_spaces=True, width=100)
                    dpg.add_checkbox()

                with dpg.table_row():
                    dpg.add_text('time')
                    dpg.add_input_text(no_spaces=True, width=100)
                    dpg.add_checkbox()

                with dpg.table_row():
                    dpg.add_text('SAMPLE 1')
                    dpg.add_input_text(no_spaces=True, width=100)
                    dpg.add_checkbox()
                with dpg.table_row():
                    dpg.add_text('Voltage (mV)')
                    dpg.add_input_text(no_spaces=True, width=100)
                    dpg.add_checkbox()
                with dpg.table_row():
                    dpg.add_text('aceleration_z')
                    dpg.add_input_text(no_spaces=True, width=100)
                    dpg.add_checkbox()
                    dpg.add_checkbox()

        with dpg.tab(label='Edit X-Axis'):
            dpg.add_listbox(("AAAA", "BBBB", "CCCC", "DDDD"), label='ALTERNATE X-AXIS SOURCE')
            dpg.add_checkbox(label='Re-base axis')
            dpg.add_text('scalar')
            dpg.add_text('time')
            dpg.add_text('UTC offset')

    dpg.add_spacer(height=50)
    dpg.add_separator()
    with dpg.group(horizontal=True, horizontal_spacing=100):
        dpg.add_button(label="Cancel")
        dpg.add_button(label="OK")
        dpg.add_button(label="Delete Series")
        # with dpg.theme_component(dpg.mvButton):
        #     dpg.add_theme_color(dpg.mvThemeCol_Button, (7.0, 0.6, 0.6))
        #     dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ( 7.0, 0.8, 0.8))
        #     dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (7.0, 0.7, 0.7))
        #     dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3 * 5)
        #     dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 3 * 3, 3 * 3)







# opens importer file dialog and impor configurator. also will handle plugins/preprocessors - TODO: should probably move to its own file

default_axis_choices = ('Indexes','First Column')
quick_format_choices = ('None','OmegaTempLogger','ConvergenceInstruments')
preprocessor_choices = ('None','WDH.py','WingTester.py','RainflowCounting.py')


with dpg.file_dialog(directory_selector=False, show=False, width=400, height=400, tag="file_dialog", callback=add_new_data_instance, default_path='/Users/tyler/Downloads'):
    dpg.add_file_extension('.csv',color=(150, 255, 150, 255))
    # with dpg.group():
    #     dpg.add_checkbox(label="Set Current Path as Default")
    #     with dpg.group(horizontal=True):
    #         dpg.add_combo(default_axis_choices,default_value = default_axis_choices[0])
    #         dpg.add_checkbox(label='Set Default')
    #     dpg.add_combo(quick_format_choices, default_value = quick_format_choices[0],label='Quick-Format Data')
    #     dpg.add_combo(preprocessor_choices,default_value = preprocessor_choices[0]) # TODO: selecting a preproccessor should pop up a text box to request input. Ideally this would run the script to get a list of inputs to display
    #     dpg.add_checkbox(label='Launch Import Configurator', callback = lambda: dpg.show_item(import_config))


with dpg.window(label='Import Configurator',width=500, height=700, modal=True, show=False) as import_config:
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
        dpg.add_button(label="IMPORT", callback=lambda: dpg.hide_item(import_config))
        dpg.add_button(label="Cancel")




dpg.set_viewport_resize_callback(set_all_plot_heights)
# dpg.show_item_registry()
dpg.set_primary_window(mainwin,True)
dpg.start_dearpygui()
dpg.destroy_context()