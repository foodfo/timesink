from multiprocessing.process import parent_process

import dearpygui.dearpygui as dpg
import pandas as pd
import numpy as np
from dearpygui.dearpygui import mvPlotScale_Linear, mvPlotScale_Log10, mvPlotScale_SymLog

from src.data_instance import DataInstance
from utils import plots, data
from utils import * # TODO: temporary until I manage Globals better
import tags
from typing import Dict

from dataclasses import dataclass




class PlotInstance:

    def __init__(self,instance_tag, manager_tag,graph_tag, y1_tag):
        self.instance_tag = instance_tag
        self.manager_tag = manager_tag
        self.graph_tag = graph_tag
        self.series_list: Dict[int, SeriesInstance] = {}
        self.global_style: str = 'Line Plot'
        self.x_axis_tags = [dpg.generate_uuid(), dpg.generate_uuid()] #, dpg.generate_uuid()] # can enable a 3rd x-axis possibly
        self.y_axis_tags = [dpg.generate_uuid(), dpg.generate_uuid(), dpg.generate_uuid()]

    # TODO: decide if these shallow methods are better than direct access
    # def set_graph_tag(self, tag):
    #     self.graph_tag = tag
    #
    # def set_manager_tag(self, tag):
    #     self.manager_tag = tag

    # def set_global_style(self, style: str) -> None:
    #     self.global_style = style

    def set_style(self, sr_tag: int, style: str) -> None:
        self.series_list[sr_tag].style = style # TODO: consider whether or not this should have a dedicated accessor or just modify it directly

    def get_style(self, sr_tag):
        return self.series_list[sr_tag].style

    def add_series(self, sr_tag, series):
        self.series_list[sr_tag] = series

    def delete_series(self, sr_tag):
        sr = self.series_list.pop(sr_tag)
        dpg.delete_item(sr.mvseries_tag)

    def draw_series(self, sr_tag, style, parent_axis_tag):

        sr = self.series_list[sr_tag]
        # sr.axis_tag = parent_axis_tag
        if style is None: style = sr.style # TODO: is there another way to do default input? style=None in fn declaration?

        # legend = f'{sr.file_alias}_{sr.y_alias}'  # TODO: make filename alias easier to get
        legend = sr.y_alias

        if style == 'Line Plot': # old: line # TODO: can i abstract away the text some how? maybe with enum>
            dpg.add_line_series(sr.x_vals, sr.y_vals, label=legend, parent=parent_axis_tag, tag=sr.mvseries_tag)
        elif style == 'Scatter Plot': # old scatter
            dpg.add_scatter_series(sr.x_vals, sr.y_vals, label=legend, parent=parent_axis_tag, tag=sr.mvseries_tag)
        elif style == 'Histogram':
            num_bins = sr.n_bins
            dpg.add_histogram_series(sr.y_vals, bins = sr.n_bins, label=legend, parent=parent_axis_tag, tag=sr.mvseries_tag)
        elif style == 'area':
            pass
        elif style == 'bar':
            pass
        elif style == 'histogram':
            sr.to_histogram()
            dpg.add_scatter_series(sr.h_bins,sr.h_mags, label=legend, parent=parent_axis_tag, tag=sr.mvseries_tag)
            pass
        elif style == 'fft':
            pass

    def delete_line(self, sr_tag):
        dpg.delete_item(self.series_list[sr_tag].mvseries_tag)

    def change_plot_style(self, sr_tag, style): # TODO: consider generalizing thsi to just (style, tag), and wrap the callback in a helper
        # FIRST DELETE, THEN REDRAW
        sr = self.series_list[sr_tag]
        sr.style = style
        target_axis_tag = sr.parent_axis_tag # TODO: decide if parent or sender, check drawseries and callback root and clean up language

        self.delete_line(sr_tag)
        self.draw_series(sr_tag, style, target_axis_tag)


class SeriesInstance:
    def __init__(self,
                 data_instance_tag: int,
                 instance_tag: int,
                 parent_axis_tag: int,
                 mvseries_tag: int,
                 file_alias: str,
                 x_name: str,
                 x_alias: str,
                 x_df: pd.Series,
                 y_name: str,
                 y_alias: str,
                 y_df: pd.Series,
                 style: str, ):
        self.data_instance_tag = data_instance_tag
        self.instance_tag: int =  instance_tag
        self.parent_axis_tag = parent_axis_tag
        self.mvseries_tag = mvseries_tag
        self.file_alias = file_alias
        self.x_name = x_name
        self.y_name = y_name
        self.x_alias = x_alias
        self.y_alias = y_alias
        self.x_df = x_df
        self.y_df = y_df
        self.style = style
        self.x_vals = self.x_df.tolist()  # Convert DataFrame/Series columns to Python lists
        self.y_vals = self.y_df.tolist()
        self.style = style
        self.n_bins = 10
        self.h_mags = None
        self.h_bins = None
        self.fft_mag = None
        self.fft_freq = None


    def to_histogram():
        pass



def calculate_plot_height():
    num_plots = max(1, min(len(plots), MAX_PLOTS_ON_SCREEN)) # protect divide by zero and clamp to maximum plots set in "options"
    # TODO: make config and button in options set the max plots on screen. changing this should also trigger the callback to update all plot sizes
    return int((dpg.get_viewport_client_height()-TAB_BAR_HEIGHT) / num_plots)

def set_all_plot_heights():
    for instance_tag in plots.keys():
        dpg.set_item_height(plots[instance_tag].graph_tag, calculate_plot_height())

# ---------- Helper Functions ----------

def add_to_plot(sender, app_data, user_data):

    # add axis to current plot instance
    # 1. get data to add to PlotData
    # 2. process params for alternate inputs
    # 3. create PlotAxes which holds plot type and tags, defining the x and y axis for plotting - alos handles converting axes around for different plot types (FFT, Histogram)
    # 4. add PlotAxes to PlotInstance
    # 5. plot line with selected style

    DEFAULT_HISTOGRAM_BINS = 10 # TODO: decide where this should go

    print(dpg.get_item_label(sender))
    # print(app_data)
    print(f'tag passed OUT from user_data: {user_data}')

    user_data = dpg.get_item_user_data(sender)
    parent_axis_tag = sender
    print(f'RETRY USER DATA GET: {user_data}')

    # 1.
    plot_instance_tag = user_data # TODO: decide if theres an easier way to init the PlotSeries
    data_instance_tag = app_data['instance_tag']
    col_name = app_data['col_name']
    extra_params = app_data['extra_params'] # TODO: decide if/how to implement params. setting new x axis with FFT will cuase issues when we call get_prepended_alias. maybe guard this get fn to just pass any results not in the source
    params = {k:v for k,v in extra_params.items() if v is not None}


    pi = plots[plot_instance_tag]
    ds: DataInstance = data[data_instance_tag]

    #2. Process Params for alternate inputs
    if params.get('alt_x_axis'):
        source_x_axis_name = params['alt_x_axis']
    else:
        source_x_axis_name = ds.source_x_axis_name

    if params.get('axis_style'):
        style = params['axis_style']
    else:
        style = pi.global_style

    if params.get('histogram_bins'):
        h_bins = params['histogram_bins']
    else:
        h_bins = DEFAULT_HISTOGRAM_BINS

    if params.get('FFT_magnitudes_arr'):
        fft_mag = params['FFT_magnitudes_arr']
    else:
        fft_mag = None

    if params.get('FFT_frequencies_arr'):
        fft_freq = params['FFT_frequencies_arr']
    else:
        fft_freq = None




    y_name, y_alias, y_df = ds.get_column(col_name)
    x_name, x_alias, x_df = ds.get_column(source_x_axis_name)

    y_alias = ds.get_prepended_alias(y_alias)
    x_alias = ds.get_prepended_alias(x_alias)

    file_alias = ds.file_alias
    sr_instance_tag = dpg.generate_uuid() # used in serie_list dict
    mvseries_tag = dpg.generate_uuid() # the dpg tag for the actual lines on the graph
    # print(plots)

    #3.
    sr = SeriesInstance(data_instance_tag, sr_instance_tag, parent_axis_tag, mvseries_tag, file_alias, x_name, x_alias, x_df, y_name, y_alias, y_df, style)
    #4.
    pi.add_series(sr_instance_tag, sr) # TODO: once again, could direct access
    #5.
    pi.draw_series(sr_instance_tag, style, parent_axis_tag)



    # print(parent_tag)
    # print(col_name)
    # print(data[parent_tag])
    # x_axis = data[parent_tag].get_x_axis()
    # y_axis = data[parent_tag].get_y_axis(col_name)
    # legend = data[parent_tag].file_alias + '_' + col_alias # TODO: make filename alias easier to get
    #
    # dpg.add_line_series(x_axis, y_axis, label=legend, parent=sender)
    # print(f'sender: {sender}')
    # print(f'app_Data: {app_data}')
    # print(f'parent: {dpg.get_item_parent(sender)}')
    # print(f'children: {dpg.get_item_children(dpg.get_item_parent(sender),slot=1)}')
    #
    # axes_tags = dpg.get_item_children(dpg.get_item_parent(sender),slot=1) # slot 1 holds axis information # TODO: figure out what to do if theres more than 2 axis
    # for i in axes_tags:
    #     dpg.fit_axis_data(i) # TODO: consider not doing this if there is already a series present
    #                         # TODO: what happens if you only do one axis?


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
    # print(sender)
    # print(app_data)
    rename_manager(sender, app_data, user_data)
    show_plot_options(sender, app_data)

def add_axis(sender, app_data, user_data):
    pi = plots[user_data['instance_tag']]
    axis = user_data['axis']

    DEFAULT_Y_AXIS_LABELS = ['y1', 'y2', 'y3']
    DEFAULT_X_AXIS_LABELS = ['x1', 'x2', 'x3']
    DEFAULT_Y_AXIS_POSITION = [False,True,True]
    DEFAULT_X_AXIS_POSITION = [False,False,False]
    x_axis_constants = [dpg.mvXAxis, dpg.mvXAxis2, dpg.mvXAxis3]
    y_axis_constants = [dpg.mvYAxis, dpg.mvYAxis2, dpg.mvYAxis3]
    x_tags = pi.x_axis_tags
    y_tags = pi.y_axis_tags

    if axis == 'y':
        labels= DEFAULT_Y_AXIS_LABELS
        tags = y_tags
        axis_constants  = y_axis_constants
        position = DEFAULT_Y_AXIS_POSITION
    else:
        labels = DEFAULT_X_AXIS_LABELS
        tags = x_tags
        axis_constants  = x_axis_constants
        position = DEFAULT_X_AXIS_POSITION


    i = next((i for i,tag in enumerate(tags) if not dpg.does_item_exist(tag)), None) # todo: consider for loop instead of a generator link remove_last_axis
    if i is None:
        return
    dpg.add_plot_axis(axis_constants[i], label=labels[i],tag=tags[i],opposite=position[i], parent = pi.graph_tag, drop_callback=add_to_plot,user_data=pi.instance_tag, scale=mvPlotScale_Linear, no_side_switch=True, no_highlight=True) # TODO: really hard to figure out where the appdata comes from. I think this is what PAYLOAD TYPE is for so you can easily search around to see the payload source
    # TODO: expose no-highlight in main options bar to change global behavior


        # dpg.add_plot_axis(dpg.mvYAxis, label="y", drop_callback=add_to_plot, user_data=pi.instance_tag,
        #                   tag=y1_tag)  # TODO: really hard to figure out where the appdata comes from. I think this is what PAYLOAD TYPE is for so you can easily search around to see the payload source

def remove_last_axis(sender, app_data, user_data):
    pi = plots[user_data['instance_tag']]
    axis = user_data['axis']

    if axis == 'y':
        tags = pi.y_axis_tags
    else:
        tags = pi.x_axis_tags

    for tag in reversed(tags):
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)
            break


def add_new_plot_instance():

    plot_instance_tag = dpg.generate_uuid()
    plot_manager_tag = dpg.generate_uuid()
    plot_graph_tag = dpg.generate_uuid()
    y1_tag = dpg.generate_uuid()

    pi = PlotInstance(instance_tag=plot_instance_tag, manager_tag=plot_manager_tag,graph_tag=plot_graph_tag, y1_tag=y1_tag)

    plots[pi.instance_tag] = pi

    instance_number = get_plot_instance_number(pi.instance_tag)

    user_data = {'instance_tag':plot_instance_tag,'manager_tag':plot_manager_tag,'graph_tag':plot_graph_tag} # there has to be a better way than sending the whole tree. If manager_tag and instance_tag are the same itll work though

    plot_types = ('Line Plot', 'Scatter Plot', 'Histogram', 'Heatmap', 'Log Plot', 'Stem Plot')

    dpg.add_button(label=f'Plot {instance_number}', width=-1, parent=tags.plot_manager_tab, tag=pi.manager_tag, callback=configure_plot, user_data=pi)
    #
    # with dpg.collapsing_header(parent=tags.plot_manager_tab, default_open=True, tag=pi.manager_tag):
    #     dpg.add_combo(plot_types, default_value=plot_types[0],callback=select_plot_type, user_data=user_data) # TODO: see if theres a better way to do this now that everything is a class
    #     dpg.set_item_label(dpg.last_container(), label=f'{plot_types[0]} {instance_number}')

    with dpg.plot(width=-1, parent=tags.plot_window, tag=pi.graph_tag, no_frame=True):  # TODO: consider either making this dpg.uuid or wrap into a class to handle tags directly
        dpg.add_plot_legend()
        dpg.add_plot_axis(dpg.mvXAxis, label="x")
        # dpg.add_plot_axis(dpg.mvYAxis, label="y", drop_callback=add_to_plot, user_data=pi.instance_tag, tag=y1_tag) # TODO: really hard to figure out where the appdata comes from. I think this is what PAYLOAD TYPE is for so you can easily search around to see the payload source
        # print(dpg.last_container()) # TODO: figure out if y axis and x axis need thier own uuids as well then figure out how to access them
        # print(dpg.get_item_label(dpg.last_container()))

        add_axis(None,None,user_data={'instance_tag':pi.instance_tag,'axis':'x'})
        add_axis(None,None,user_data={'instance_tag':pi.instance_tag,'axis':'y'})

    set_all_plot_heights()

def configure_plot(sender, app_data, user_data):
    pi: PlotInstance = user_data
    plot_name: str = dpg.get_item_label(sender)


    plot_types = ('Line Plot', 'Scatter Plot', 'Histogram', 'Heatmap', 'Log Plot', 'Stem Plot') # TODO Rename plot_styles but this should move somewhere else



    def change_plot_style_callback(sender, app_data, user_data):
        style = app_data
        sr_tag = user_data
        print(style, sr_tag)
        pi.change_plot_style(sr_tag, style)


    def edit_series_style_callback(sender, app_data, user_data):
        line_color = ('Red', 'Yellow', 'Blue')
        line_style = ('Line', 'Dashed', 'Dotted')
        line_weight = ('Thin', 'Medium', 'Thick')
        marker_style = ('None', 'Circle', 'Square')
        marker_fill = ('Fill', 'Empty')

        with dpg.window(label='Line Style Editor', autosize=True):

            dpg.add_combo(line_color, label='Line Color')
            dpg.add_combo(line_style, label='Line Style')
            dpg.add_combo(line_weight, label='Line Weight')
            dpg.add_combo(marker_style, label='Marker')
            dpg.add_combo(marker_fill, label='Marker Fill')



    with dpg.window(label=f'Configure {plot_name}',pos=(50,200), autosize=True): #,no_move=True,modal=True):

        TEXT_BOX_WIDTH = 150 # TODO: consider making this global
        CHECK_BOX_WIDTH = 50

        with dpg.tab_bar():
            with dpg.tab(label='Global'):
                dpg.add_separator(label='Plot')
                with dpg.group(horizontal=True):
                    dpg.add_input_text(label='Plot Name', width=TEXT_BOX_WIDTH)
                    dpg.add_checkbox(label='Hide Plot Name')
                    dpg.add_checkbox(label='Hide legend')
                dpg.add_separator(label="Global Style")
                dpg.add_combo(plot_types, default_value=plot_types[0],callback=select_plot_type, width=TEXT_BOX_WIDTH) # TODO: see if theres a better way to do this now that everything is a class
                dpg.add_separator(label='Axes')

                with dpg.table(header_row=True, borders_innerH=True,borders_outerH=True) as table:
                    dpg.add_table_column(label='Enable Axis', width_fixed=True)
                    dpg.add_table_column(label='Axis Label', width_fixed=True)
                    dpg.add_table_column(label='Axis Alias', width_fixed=True)
                    dpg.add_table_column(label='Scale', width_fixed=True)
                    # dpg.add_table_column(label='Invert',width_fixed=True,width=20) $ TODO: decide if this adds value or not
                    dpg.add_table_column(label='Hide Label',width_fixed=True,width=20)
                    dpg.add_table_column(label='Hide Axis',width_fixed=True,width=20)

                    plot_scale = ('Linear','Log','Date')
                    axis_list = ('Y Axis 1','Y Axis 2','X Axis 1','X Axis 2','X Axis 3')

                    for ax in axis_list:
                        with dpg.table_row(user_data=ax):
                            dpg.add_button(label=ax, width=100)
                            dpg.add_combo(('_index', 'time'), width=75)
                            dpg.add_input_text(width=TEXT_BOX_WIDTH)
                            dpg.add_combo(plot_scale, width=50)
                            # dpg.add_checkbox()
                            dpg.add_checkbox(indent=25)
                            dpg.add_checkbox(indent=25)


                with dpg.group(horizontal=True):
                    dpg.add_button(label='+Y', callback=add_axis, user_data={'instance_tag':pi.instance_tag,'axis':'y'})
                    dpg.add_button(label='-Y', callback=remove_last_axis, user_data={'instance_tag':pi.instance_tag,'axis':'y'})
                with dpg.group(horizontal=True):
                    dpg.add_button(label='+X', callback=add_axis,user_data={'instance_tag': pi.instance_tag, 'axis': 'x'})
                    dpg.add_button(label='-X', callback=remove_last_axis,user_data={'instance_tag': pi.instance_tag, 'axis': 'x'})
            with dpg.tab(label='Per Series'):
                for tag, sr in pi.series_list.items():
                    with dpg.group(horizontal=True):
                        dpg.add_button(label=sr.y_alias, callback=edit_series_style_callback)
                        dpg.add_combo(plot_types, default_value=sr.style,callback=change_plot_style_callback, user_data=sr.instance_tag)
                        dpg.add_text(f'Source X-Axis: {sr.x_alias}')

        with dpg.group(horizontal=True):
            dpg.add_button(label='Cancel')
            dpg.add_button(label='OK')
            dpg.add_spacer(width=170)
            dpg.add_button(label='Delete Plot')






    #########################################################################
    # def add_to_plot(sender, app_data, user_data):
    #     print(sender)
    #     print(app_data)
    #     print(user_data)
    #
    #     instancd_tag = app_data['instance_tag']
    #     col_name = app_data['col_name']
    #     ds = data[instancd_tag]
    #     y_name, y_alias, y_df = ds.get_column(col_name)
    #     x_name, x_alias, x_df = ds.get_column(ds.source_x_axis)
    #
    #     print(parent_tag)
    #     print(col_name)
    #     print(data[parent_tag])
    #     x_axis = data[parent_tag].get_x_axis()
    #     y_axis = data[parent_tag].get_y_axis(col_name)
    #     legend = data[parent_tag].file_alias + '_' + col_alias  # TODO: make filename alias easier to get
    #
    #     dpg.add_line_series(x_axis, y_axis, label=legend, parent=sender)
    #     print(f'sender: {sender}')
    #     print(f'app_Data: {app_data}')
    #     print(f'parent: {dpg.get_item_parent(sender)}')
    #     print(f'children: {dpg.get_item_children(dpg.get_item_parent(sender), slot=1)}')
    #
    #     axes_tags = dpg.get_item_children(dpg.get_item_parent(sender),
    #                                       slot=1)  # slot 1 holds axis information # TODO: figure out what to do if theres more than 2 axis
    #     for i in axes_tags:
    #         dpg.fit_axis_data(i)  # TODO: consider not doing this if there is already a series present
    #         # TODO: what happens if you only do one axis?