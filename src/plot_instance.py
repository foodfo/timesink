from multiprocessing.process import parent_process

import dearpygui.dearpygui as dpg
import pandas as pd
import numpy as np
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
        dpg.delete_item(sr.axis_tag)

    def draw_series(self, sr_tag, style, parent_axis_tag):

        sr = self.series_list[sr_tag]
        # sr.axis_tag = parent_axis_tag
        if style is None: style = sr.style # TODO: is there another way to do default input? style=None in fn declaration?

        legend = f'{sr.file_alias}_{sr.y_alias}'  # TODO: make filename alias easier to get

        if style == 'Line Plot': # old: line # TODO: can i abstract away the text some how? maybe with enum>
            dpg.add_line_series(sr.x_vals, sr.y_vals, label=legend, parent=parent_axis_tag, tag=sr.mvseries_tag)
        elif style == 'Scatter Plot': # old scatter
            dpg.add_scatter_series(sr.x_vals, sr.y_vals, label=legend, parent=parent_axis_tag, tag=sr.mvseries_tag)
        elif style == 'stem':
            pass
        elif style == 'area':
            pass
        elif style == 'bar':
            pass
        elif style == 'histogram':
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
        self.h_mag = None
        self.h_bins = None
        self.fft_mag = None
        self.fft_freq = None



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
    # 2. create PlotAxes which holds plot type and tags, defining the x and y axis for plotting - alos handles converting axes around for different plot types (FFT, Histogram)
    # 3. add PlotAxes to PlotInstance
    # 4. plot line with selected style



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
    pi = plots[plot_instance_tag]
    ds = data[data_instance_tag]
    y_name, y_alias, y_df = ds.get_column(col_name)
    x_name, x_alias, x_df = ds.get_column(ds.source_x_axis_name)
    file_alias = ds.file_alias
    sr_instance_tag = dpg.generate_uuid() # used in serie_list dict
    mvseries_tag = dpg.generate_uuid() # the dpg tag for the actual lines on the graph
    # print(plots)
    style = pi.global_style
    #2.
    sr = SeriesInstance(data_instance_tag, sr_instance_tag, parent_axis_tag, mvseries_tag, file_alias, x_name, x_alias, x_df, y_name, y_alias, y_df, style)
    #3.
    pi.add_series(sr_instance_tag, sr) # TODO: once again, could direct access
    #4.
    # pi.draw_series(series_tag, None, sender)
    pi.draw_series(sr_instance_tag, None, parent_axis_tag)



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
    dpg.add_plot_axis(axis_constants[i], label=labels[i],tag=tags[i],opposite=position[i], parent = pi.graph_tag, drop_callback=add_to_plot,user_data=pi.instance_tag) # TODO: really hard to figure out where the appdata comes from. I think this is what PAYLOAD TYPE is for so you can easily search around to see the payload source



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

    with dpg.plot(width=-1, parent=tags.plot_window, tag=pi.graph_tag):  # TODO: consider either making this dpg.uuid or wrap into a class to handle tags directly
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



    with dpg.window(label=f'Configure {plot_name}',pos=(50,200),width=300, height=300): #,no_move=True,modal=True):
        with dpg.tab_bar():
            with dpg.tab(label='Global'):
                dpg.add_combo(plot_types, default_value=plot_types[0],callback=select_plot_type) # TODO: see if theres a better way to do this now that everything is a class
                with dpg.group(horizontal=True):
                    dpg.add_button(label='+Y', callback=add_axis, user_data={'instance_tag':pi.instance_tag,'axis':'y'})
                    dpg.add_button(label='-Y', callback=remove_last_axis, user_data={'instance_tag':pi.instance_tag,'axis':'y'})
                with dpg.group(horizontal=True):
                    dpg.add_button(label='+X', callback=add_axis,user_data={'instance_tag': pi.instance_tag, 'axis': 'x'})
                    dpg.add_button(label='-X', callback=remove_last_axis,user_data={'instance_tag': pi.instance_tag, 'axis': 'x'})
            with dpg.tab(label='Series'):
                for tag, sr in pi.series_list.items():
                    with dpg.group(horizontal=True):
                        dpg.add_text(sr.y_alias)
                        dpg.add_combo(plot_types, default_value=sr.style,callback=change_plot_style_callback, user_data=sr.instance_tag)
                        dpg.add_combo(('Y1','Y2','Y3'),label='Y-Axis')
                        dpg.add_combo(('X1','X2'),label='X-Axis')
                        dpg.add_text(sr.x_alias) # TODO: change this to dropdown to choose x axis
            with dpg.tab(label='X-Axis'):
                pass
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