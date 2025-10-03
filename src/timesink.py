
import dearpygui.dearpygui as dpg
import pandas as pd
import numpy as np
from dearpygui.dearpygui import set_item_label, get_item_label

from data_source import DataSource
from src.plot_instance import PlotInstance

# put into utils
WINDOW_TITLE = "TIMESINK"
VIEWPORT_HEIGHT = 1080
VIEWPORT_WIDTH = 1920
# VIEWPORT_HEIGHT = 700
# VIEWPORT_WIDTH = 1200
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
    dpg.configure_item('Source_Config',show=True)



with dpg.window(#width = dpg.get_viewport_width(), height = dpg.get_viewport_height(),pos=[0,MENU_BAR_HEIGHT+40],no_move=True,no_title_bar=True
                ) as mainwin:
    with dpg.menu_bar(tag='vp_bar', show=False):
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
#         pass
#
# with dpg.window(label=WINDOW_TITLE, width=600, height=300):
#     pass

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

    # num_plots = len(plots) if len(plots) else 1

    for tag in plots.keys():
        # dpg.set_item_height(tag, calculate_plot_height())
        dpg.set_item_height(plots[tag].child, calculate_plot_height())



def add_to_plot(sender, app_data, user_data):
    parent_tag = app_data['parent_tag']
    col_name = app_data['col_name']
    col_alias = app_data['col_alias']
    print(parent_tag)
    print(col_name)
    print(data[parent_tag])
    x_axis = data[parent_tag].get_x_axis()
    y_axis = data[parent_tag].get_y_axis(col_name)
    legend = data[parent_tag].get_filename_alias()[1] + '_' + col_alias # TODO: make filename alias easier to get

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


def get_plot_number(tag):
    return list(plots.keys()).index(tag) + 1 # 1 indexed rather than 0 indexed

def rename_plot(sender,app_data):
    tag = dpg.get_item_parent(sender)
    plot_number = get_plot_number(tag)
    set_item_label(tag,f'{app_data} {plot_number}')

def show_plot_options(sender, app_data):
    dpg.add_button(label='set x-axis', parent=sender)

def delete_plot_instance(sender, app_data): #delete the last added plot # TODO make a way to delete any plot
    # delete data from dict and also ge the tag of the collapsable window
    tag, pi = plots.popitem() # key, val # TODO: should probably made a plots.delete(tag) function and make plots a class that way logic is abstracted away from the functions
    dpg.delete_item(tag) # delete the options window
    dpg.delete_item(pi.child) #delete the plot
    set_all_plot_heights()

def select_plot_type(sender, app_data, user_data):
    print(sender)
    print(app_data)
    rename_plot(sender,app_data)
    show_plot_options(sender, app_data)

def add_new_plot_instance():
    pi = PlotInstance(tag=dpg.generate_uuid())

    plots[pi.tag] = pi

    plot_number = get_plot_number(pi.tag)

    pi.set_child_tag(f'{pi.tag},{plot_number}')

    plot_types = ('Line Plot', 'Scatter Plot', 'Histogram', 'Heatmap', 'Log Plot', 'Stem Plot')

    # with dpg.collapsing_header(parent=plot_list,default_open=True, tag=pi.tag):
    with dpg.collapsing_header(parent=plot_list, default_open=True, tag=pi.tag):


        dpg.add_combo(plot_types, default_value=plot_types[0],callback=select_plot_type)
        dpg.set_item_label(dpg.last_container(), label=f'{plot_types[0]} {plot_number}')

    # with dpg.plot(width=-1, height=calculate_plot_height(), parent = plot_window, tag=(pi.tag, plot_number)): # TODO: consider either making this dpg.uuid or wrap into a class to handle tags directly
    with dpg.plot(width=-1, height=calculate_plot_height(), parent=plot_window, tag=pi.child):  # TODO: consider either making this dpg.uuid or wrap into a class to handle tags directly

        dpg.add_plot_legend()
        dpg.add_plot_axis(dpg.mvXAxis, label="x")
        dpg.add_plot_axis(dpg.mvYAxis, label="y", drop_callback=add_to_plot) # TODO: really hard to figure out where the appdata comes from. I think this is what PAYLOAD TYPE is for so you can easily search around to see the payload source
        print(dpg.last_container()) # TODO: figure out if y axis and x axis need thier own uuids as well then figure out how to access them
        print(get_item_label(dpg.last_container()))

    set_all_plot_heights()


# everything that sits in a single tab instance
with dpg.child_window(parent=primary_tab, border=False):
    with dpg.group(horizontal=True):
        with dpg.child_window(resizable_x=True, width=SIDEBAR_WIDTH, border=False) as sidebar:
            with dpg.child_window(label="Options",autosize_x=True, tag='Options', auto_resize_y=True):
                with dpg.collapsing_header(label="Options",default_open=True):
                    dpg.add_text(f'Downsample %: {downsample_percent}%')
                    dpg.add_checkbox(label='Downsample Data')
                    dpg.add_checkbox(label='Unlock X-Axis')
                    # with dpg.group(horizontal=True):
                    #     dpg.add_button(label='+ Plot')
                    #     dpg.add_button(label='- Plot')
                    dpg.add_separator()
                    dpg.add_button(label='Add Parse Line')
                    dpg.add_button(label='Find Peak on Screen')
                    dpg.add_button(label='Add Annotation')

            with dpg.child_window(label="Plot Controller",autosize_x=True, autosize_y=True, tag='Plot Controller'):
                with dpg.tab_bar():
                    with dpg.tab(label='DATA') as data_list:
                        dpg.add_button(label="ADD DATA", callback=lambda: dpg.show_item("file_dialog") )
                    with dpg.tab(label='PLOTS') as plot_list:
                        with dpg.group(horizontal=True):
                            dpg.add_button(label="- Plot", callback=delete_plot_instance)
                            dpg.add_button(label="+ Plot", callback=add_new_plot_instance)
                        dpg.add_separator()
                        dpg.add_spacer(height=10)
                    # with dpg.tab(label='CUSTOM FORMULAS'):
                    #     pass
                    # with dpg.tab(label='PRESETS'):
                    #     pass
    # with dpg.child_window(pos=(SIDEBAR_WIDTH+10,0), autosize_x=True, autosize_y=True) as plot_window:
        with dpg.child_window(autosize_x=True, autosize_y=True, border=False) as plot_window:
            for i in range(NUM_PLOTS_ON_STARTUP):
                add_new_plot_instance()
            # for i in range(20):
            #     dpg.add_text("TEST TEST TEST")
            # TODO: periodically poll the width of the sidebar and adjust plot size accordingly. do the same for viewport height/width? or just run callback on viewport resize?
            # with dpg.plot(width=-1, height=calculate_plot_height(), tag='plot1'):
            #     dpg.add_plot_legend(parent='plot1')
            #     dpg.add_plot_axis(dpg.mvXAxis, label="x",parent='plot1')
            #     dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="y_axis1",parent='plot1',drop_callback=add_to_plot)
            # with dpg.plot(width=dpg.get_viewport_width() - dpg.get_item_width(sidebar) - 40, height=-1, tag='plot2'):
            #     dpg.add_plot_legend(parent='plot2')
            #     dpg.add_plot_axis(dpg.mvXAxis, label="x", parent='plot2')
            #     dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="y_axis2", parent='plot2', drop_callback=add_to_plot)
            # with dpg.plot():
            #     pass


with dpg.window(label='Configure Data Source', modal=True, height=500, width=500, show=False, tag='Source_Config'):
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





def add_new_data_source(sender,app_data,user_data):
    ds = DataSource(file_path=app_data['file_path_name'],tag=dpg.generate_uuid())

    data[ds.tag] = ds

    with dpg.collapsing_header(label=list(ds.alias.values())[0], default_open=True,tag=ds.tag, parent=data_list):

        aliases = ds.get_column_aliases()

        dpg.add_button(label='Configure', callback=show_source_config)
        dpg.add_button(label='Set X-Axis', drop_callback=set_x_axis)
        dpg.add_separator()
        with dpg.child_window(height=100):
            for key, val in aliases: # skip the first alias since thats the filename. consider splitting these up
                dpg.add_button(label=val)
                with dpg.drag_payload(label=val,parent=dpg.last_item(),drag_data={'parent_tag':ds.tag,'col_name':key,'col_alias':val}): # TODO: really hard to figure out what this points to. I think this is what PAYLOAD TYPE is for so you can easily search around to see the payload source
                    dpg.add_text(val)





with dpg.file_dialog(directory_selector=False,show=False,width=400,height=400, tag="file_dialog",callback=add_new_data_source, default_path='/Users/tyler/Downloads'):
    dpg.add_file_extension('.csv',color=(150, 255, 150, 255))



dpg.set_viewport_resize_callback(set_all_plot_heights)
# dpg.show_item_registry()
dpg.set_primary_window(mainwin,True)
dpg.start_dearpygui()
dpg.destroy_context()