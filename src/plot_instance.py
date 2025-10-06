
import dearpygui.dearpygui as dpg
import pandas as pd
import numpy as np
from utils import plots, data
from utils import * # TODO: temporary until I manage Globals better
import tags
from typing import Dict

from dataclasses import dataclass




class PlotInstance:

    def __init__(self,instance_tag, manager_tag,graph_tag):
        self.instance_tag = instance_tag
        self.manager_tag = manager_tag
        self.graph_tag = graph_tag
        self.series_list: Dict[int, PlotSeries] = {}
        self.global_style: str = 'line'

    # TODO: decide if these shallow methods are better than direct access
    # def set_graph_tag(self, tag):
    #     self.graph_tag = tag
    #
    # def set_manager_tag(self, tag):
    #     self.manager_tag = tag

    # def set_global_style(self, style: str) -> None:
    #     self.global_style = style

    def set_style(self, series_tag: int, style: str) -> None:
        self.series_list[series_tag].style = style # TODO: consider whether or not this should have a dedicated accessor or just modify it directly

    def get_series_style(self, series_tag):
        return self.series_list[series_tag].style

    def add_series(self, series_tag, series):
        self.series_list[series_tag] = series

    def delete_series(self, series_tag):
        self.series_list.pop(series_tag)

    def draw_series(self, series_tag, style, sender):

        sr = self.series_list[series_tag]
        if style is None: style = sr.style # TODO: is there another way to do default input? style=None in fn declaration?

        legend = f'{sr.file_alias}_{sr.y_alias}'  # TODO: make filename alias easier to get

        if style == 'line':
            dpg.add_line_series(sr.x_vals, sr.y_vals, label=legend, parent=sender)
        elif style == 'scatter':
            pass
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


class PlotSeries:
    def __init__(self,
                 data_instance_tag: int,
                 series_tag: int,
                 file_alias: str,
                 x_name: str,
                 x_alias: str,
                 x_df: pd.Series,
                 y_name: str,
                 y_alias: str,
                 y_df: pd.Series,
                 style: str,):
        self.data_instance_tag = data_instance_tag
        self.series_tag: series_tag
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
    print(f'RETRY USER DATA GET: {user_data}')

    # 1.
    plot_instance_tag = user_data # TODO: decide if theres an easier way to init the PlotSeries
    data_instance_tag = app_data['instance_tag']
    col_name = app_data['col_name']
    ds = data[data_instance_tag]
    y_name, y_alias, y_df = ds.get_column(col_name)
    x_name, x_alias, x_df = ds.get_column(ds.source_x_axis)
    file_alias = ds.file_alias
    series_tag = dpg.generate_uuid()
    # print(plots)
    style = plots[plot_instance_tag].global_style
    #2.
    sr = PlotSeries(data_instance_tag,series_tag,file_alias,x_name,x_alias,x_df,y_name,y_alias,y_df, style)
    #3.
    plots[plot_instance_tag].add_series(series_tag, sr) # TODO: once again, could direct access
    #4.
    plots[plot_instance_tag].draw_series(series_tag, None, sender)



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
    # print(sender)
    # print(app_data)
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

    with dpg.collapsing_header(parent=tags.plot_manager_tab, default_open=True, tag=pi.manager_tag):
        dpg.add_combo(plot_types, default_value=plot_types[0],callback=select_plot_type, user_data=user_data) # TODO: see if theres a better way to do this now that everything is a class
        dpg.set_item_label(dpg.last_container(), label=f'{plot_types[0]} {instance_number}')

    with dpg.plot(width=-1, parent=tags.plot_window, tag=pi.graph_tag):  # TODO: consider either making this dpg.uuid or wrap into a class to handle tags directly
        dpg.add_plot_legend()
        dpg.add_plot_axis(dpg.mvXAxis, label="x")
        dpg.add_plot_axis(dpg.mvYAxis, label="y", drop_callback=add_to_plot, user_data=pi.instance_tag) # TODO: really hard to figure out where the appdata comes from. I think this is what PAYLOAD TYPE is for so you can easily search around to see the payload source
        # print(dpg.last_container()) # TODO: figure out if y axis and x axis need thier own uuids as well then figure out how to access them
        # print(dpg.get_item_label(dpg.last_container()))

    set_all_plot_heights()









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