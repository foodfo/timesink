from multiprocessing.process import parent_process
from tkinter import Label

import dearpygui.dearpygui as dpg
import pandas as pd
import numpy as np
from dearpygui.dearpygui import mvPlotScale_Linear, mvPlotScale_Log10, mvPlotScale_SymLog, set_item_label, \
    mvPlotScale_Time, get_item_user_data

from src.data_instance import DataInstance
from utils import plots, data
from utils import * # TODO: temporary until I manage Globals better
import tags
from typing import Dict

from dataclasses import dataclass




class PlotInstance:

    def __init__(self,instance_tag, manager_tag,graph_tag, legend_tag):
        self.instance_tag = instance_tag
        self.manager_tag = manager_tag
        self.graph_tag = graph_tag
        self.legend_tag = legend_tag
        self.series_list: Dict[int, SeriesInstance] = {}
        self.global_style: str = 'Line Plot'
        self.x_axis_tags = [dpg.generate_uuid(), dpg.generate_uuid()] #, dpg.generate_uuid()] # can enable a 3rd x-axis possibly
        self.y_axis_tags = [dpg.generate_uuid(), dpg.generate_uuid(), dpg.generate_uuid()]
        self.plot_name = None # gets init just after creation after getting index
        self.options = self._init_options()
        self.plot_name_visible = False

    # TODO: decide if these shallow methods are better than direct access
    # def set_graph_tag(self, tag):
    #     self.graph_tag = tag
    #
    # def set_manager_tag(self, tag):
    #     self.manager_tag = tag

    # def set_global_style(self, style: str) -> None:
    #     self.global_style = style
    def get_plot_name(self):
        if self.options['show_plot_name']:
            return self.plot_name
        else:
            return ''

    def _init_options(self):
        options = {
            'show_plot_name':False,
            'show_legend': True,
            'highlight_axis_on_hover':False,
        }
        return options

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

        legend = sr.y_alias

        if style == 'Line Plot': # old: line # TODO: can i abstract away the text some how? maybe with enum>
            dpg.add_line_series(sr.x_vals, sr.y_vals, label=legend, parent=parent_axis_tag, tag=sr.mvseries_tag)
        elif style == 'Scatter Plot': # old scatter
            dpg.add_scatter_series(sr.x_vals, sr.y_vals, label=legend, parent=parent_axis_tag, tag=sr.mvseries_tag)
        elif style == 'Histogram':
            num_bins = sr.h_bins
            dpg.add_histogram_series(sr.y_vals, bins = sr.h_bins, label=legend, parent=parent_axis_tag, tag=sr.mvseries_tag)
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
                 x_name: str,
                 y_name: str,
                 x_alias: str,
                 y_alias: str,
                 x_df: pd.Series,
                 y_df: pd.Series,
                 style: str,
                 h_bins: int,
                 fft_mag: list,
                 fft_freq: list):
        self.data_instance_tag = data_instance_tag # tag of the source DataInstance
        self.instance_tag: int =  instance_tag # tag for this SeriesInstance
        self.parent_axis_tag = parent_axis_tag # tag for the parent Axis the series was dragged to
        self.mvseries_tag = mvseries_tag # tag for the actual line object that dpg will render to
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
        self.h_mags = self.y_vals
        self.h_bins = h_bins
        self.fft_mag = fft_mag # TODO: make sure this doenst need to be converted from a df
        self.fft_freq = fft_freq

    def to_histogram(self):
        pass

    def to_fft(self):
        pass

    @classmethod
    def create_object(cls, ds, drag_data, global_style, parent_axis_tag): # make series instance WAY easier to set up
        parent_axis_tag = parent_axis_tag
        data_instance_tag = drag_data['instance_tag']
        col_name = drag_data['col_name']
        params = drag_data['extra_params']  # TODO: decide if/how to implement params. setting new x axis with FFT will cuase issues when we call get_prepended_alias. maybe guard this get fn to just pass any results not in the source

        source_x_axis_name = params.get('alt_x_axis') or ds.source_x_axis_name
        style = params.get('axis_style') or global_style
        h_bins = params.get('histogram_bins') or 10
        fft_mag = params.get('FFT_magnitudes_arr')  or None
        fft_freq = params.get('FFT_frequencies_arr') or None

        y_name, y_alias, y_df = ds.get_column(col_name)
        x_name, x_alias, x_df = ds.get_column(source_x_axis_name)

        y_alias = ds.get_prepended_alias(y_alias)
        x_alias = ds.get_prepended_alias(x_alias)

        sr_instance_tag = dpg.generate_uuid()  # used in series_list dict
        mvseries_tag = dpg.generate_uuid()  # the dpg tag for the actual lines on the graph

        return cls(
            data_instance_tag = data_instance_tag,
            instance_tag = sr_instance_tag,
            parent_axis_tag = parent_axis_tag,
            mvseries_tag = mvseries_tag,
            x_name = x_name,
            y_name = y_name,
            x_alias = x_alias,
            y_alias = y_alias,
            x_df = x_df,
            y_df = y_df,
            style = style,
            h_bins = h_bins,
            fft_mag = fft_mag,
            fft_freq = fft_freq
        )


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

    # DEFAULT_HISTOGRAM_BINS = 10 # TODO: decide where this should go

    print(dpg.get_item_label(sender))
    # print(app_data)
    print(f'tag passed OUT from user_data: {user_data}')

    user_data = dpg.get_item_user_data(sender)
    parent_axis_tag = sender
    print(f'RETRY USER DATA GET: {user_data}')

    # 1.
    plot_instance_tag = user_data
    data_instance_tag = app_data['instance_tag']
    # col_name = app_data['col_name']
    # extra_params = app_data['extra_params']
    # params = {k:v for k,v in extra_params.items() if v is not None}
    drag_data = app_data


    pi = plots[plot_instance_tag]
    ds: DataInstance = data[data_instance_tag]

    #2. Process Params for alternate inputs

    # print(plots)

    #3.
    # sr = SeriesInstance(data_instance_tag, sr_instance_tag, parent_axis_tag, mvseries_tag, file_alias, x_name, x_alias, x_df, y_name, y_alias, y_df, style)
    sr = SeriesInstance.create_object(ds, drag_data, pi.global_style, parent_axis_tag)
    #4.
    pi.add_series(sr.instance_tag, sr) # TODO: once again, could direct access
    #5.
    pi.draw_series(sr.instance_tag, sr.style, sr.parent_axis_tag)



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

# def rename_manager(sender, app_data, user_data):
#     dropdown_selection = app_data
#     manager_tag=user_data['manager_tag'] # is there a better way to do this than  passing the user_data?
#     instance_tag=user_data['instance_tag']
#     # manager_tag = dpg.get_item_parent(sender)
#     plot_number = get_plot_instance_number(instance_tag)
#     dpg.set_item_label(manager_tag,f'{dropdown_selection} {plot_number}')


def delete_last_plot_instance(sender, app_data): #delete the last added plot instance, manager, and graph # TODO make a way to delete any plot
    # delete data from dict and also ge the tag of the collapsable window
    instance_tag, pi = plots.popitem() # key, val # TODO: should probably made a plots.delete(tag) function and make plots a class that way logic is abstracted away from the functions
    dpg.delete_item(pi.manager_tag) # delete the options window
    dpg.delete_item(pi.graph_tag) #delete the plot
    set_all_plot_heights()

# def select_plot_type(sender, app_data, user_data):
#     # print(sender)
#     # print(app_data)
#     rename_manager(sender, app_data, user_data)
#     show_plot_options(sender, app_data)

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
    plot_legend_tag =  dpg.generate_uuid()

    pi = PlotInstance(instance_tag=plot_instance_tag, manager_tag=plot_manager_tag,graph_tag=plot_graph_tag, legend_tag=plot_legend_tag)

    plots[pi.instance_tag] = pi

    instance_number = get_plot_instance_number(pi.instance_tag)

    pi.plot_name = f'Plot {instance_number}'

    user_data = {'instance_tag':plot_instance_tag,'manager_tag':plot_manager_tag,'graph_tag':plot_graph_tag} # there has to be a better way than sending the whole tree. If manager_tag and instance_tag are the same itll work though

    plot_types = ('Line Plot', 'Scatter Plot', 'Histogram', 'Heatmap', 'Log Plot', 'Stem Plot')

    dpg.add_button(label=pi.plot_name, width=-1, parent=tags.plot_manager_tab, tag=pi.manager_tag, callback=configure_plot, user_data=pi)
    #
    # with dpg.collapsing_header(parent=tags.plot_manager_tab, default_open=True, tag=pi.manager_tag):
    #     dpg.add_combo(plot_types, default_value=plot_types[0],callback=select_plot_type, user_data=user_data) # TODO: see if theres a better way to do this now that everything is a class
    #     dpg.set_item_label(dpg.last_container(), label=f'{plot_types[0]} {instance_number}')

    with dpg.plot(width=-1, parent=tags.plot_window, tag=pi.graph_tag, no_frame=True):  # TODO: consider either making this dpg.uuid or wrap into a class to handle tags directly
        dpg.add_plot_legend(tag=pi.legend_tag, no_highlight_axis=not pi.options['highlight_axis_on_hover']) # TODO: amake this a config option globally in menubar
        dpg.add_plot_axis(dpg.mvXAxis, label="x")
        # dpg.add_plot_axis(dpg.mvYAxis, label="y", drop_callback=add_to_plot, user_data=pi.instance_tag, tag=y1_tag) # TODO: really hard to figure out where the appdata comes from. I think this is what PAYLOAD TYPE is for so you can easily search around to see the payload source
        # print(dpg.last_container()) # TODO: figure out if y axis and x axis need thier own uuids as well then figure out how to access them
        # print(dpg.get_item_label(dpg.last_container()))

        add_axis(None,None,user_data={'instance_tag':pi.instance_tag,'axis':'x'})
        add_axis(None,None,user_data={'instance_tag':pi.instance_tag,'axis':'y'})

    set_all_plot_heights()




def configure_plot(sender, app_data, user_data):
    pi: PlotInstance = user_data
    # TODO: delete window if it already exists. similar to earlier window whihc makes sure its the only one of its type. right now you can make 2 config windows
    # plot_name = pi.plot_name # get name for window regardless of visile status


    # plot_types = ('Line Plot', 'Scatter Plot', 'Histogram', 'Heatmap', 'Log Plot', 'Stem Plot') # TODO Rename plot_styles but this should move somewhere else

    line_style = ('Line', 'Scatter', 'Segmented Line', 'Area Fill')

    with dpg.theme() as activated_axis:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (10, 100, 100, 200))  # closed
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (10, 100, 100, 170))  # hover
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (10, 100, 100, 200))

    with dpg.theme() as deactivated_axis:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (51, 51, 55, 255))  # closed
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (10, 100, 100, 170))  # hover
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (10, 100, 100, 200))

    def change_plot_name_callback(sender, app_data):
        pi.plot_name = app_data
        set_item_label(pi.graph_tag, pi.get_plot_name())
        set_item_label(pi.manager_tag, pi.plot_name)

    def set_plot_name_visibility(sender, app_data):
        pi.options['show_plot_name'] = app_data
        pi.plot_name_visible =  pi.options['show_plot_name']
        set_item_label(pi.graph_tag, pi.get_plot_name())

    def show_legend_callback(sender, app_data):
        pi.options['show_legend'] = app_data
        dpg.configure_item(pi.legend_tag, show=pi.options['show_legend'])

    def highlight_axis_callback(sender, app_data): # TODO: consider making this global instead of local to each plot
        pi.options['highlight_axis_on_hover'] = app_data
        dpg.configure_item(pi.legend_tag, no_highlight_axis=not pi.options['highlight_axis_on_hover'])

    def change_enable_theme(sender,app_data, user_data):
        if dpg.get_item_theme(sender) == activated_axis:
            dpg.bind_item_theme(sender, deactivated_axis)
            # dpg.set_item_user_data(sender, False)
            user_data['enable']=False
            show_rest_of_table(user_data)
        else:
            dpg.bind_item_theme(sender, activated_axis)
            # dpg.set_item_user_data(sender, True)
            user_data['enable']=True

            show_rest_of_table(user_data)



    def change_plot_style_callback(sender, app_data, user_data):
        style = app_data
        sr_tag = user_data
        print(style, sr_tag)
        pi.change_plot_style(sr_tag, style)

    def get_list_of_series_in_axis(tag):
        series_list = [sr for sr in pi.series_list.values() if sr.parent_axis_tag == tag]

        if tag in pi.y_axis_tags: # get x or y alias depending on source tag
            names = [sr.y_alias for sr in series_list]
        else:
            names = [sr.x_alias for sr in series_list]

        if len(names) == 0:
            return ()
        return names

    axis_scale = {'Linear':mvPlotScale_Linear, 'Log':mvPlotScale_Log10, 'Date':mvPlotScale_Time}

    def get_current_axis_scale(tag):
        if not dpg.does_item_exist(tag):
            return None
        current_scale = dpg.get_item_configuration(tag)['scale']
        return next((label for label, scale in axis_scale.items() if scale == current_scale), None)

    def set_axis_scale(sender, app_data, user_data):
        dpg.configure_item(user_data, scale=axis_scale[app_data])

    def set_axis_alias(sender, app_data, user_data):
        dpg.configure_item(user_data, label=app_data)

    def edit_series_style_callback(sender, app_data, user_data):
        line_color = ('Red', 'Yellow', 'Blue')
        line_weight = ('Thin', 'Medium', 'Thick')
        marker_style = ('None', 'Circle', 'Square')
        marker_fill = ('Fill', 'Empty')

        with dpg.window(label='Line Style Editor', autosize=True):

            dpg.add_combo(line_color, label='Line Color')
            dpg.add_combo(line_style, label='Line Style')
            dpg.add_combo(line_weight, label='Line Weight')
            dpg.add_combo(marker_style, label='Marker')
            dpg.add_combo(marker_fill, label='Marker Fill')

    def show_rest_of_table(user_data):
        # name = user_data['name']
        tag = user_data['tag']
        enable = user_data['enable']

        dpg.add_input_text(width=TEXT_BOX_WIDTH, callback=set_axis_alias, user_data=tag, show=enable, parent=tag)
        series_names = get_list_of_series_in_axis(tag)
        if series_names:
            with dpg.tooltip(
                    dpg.last_item()):  # TODO: this tooltip is great but add a right cliclk menu to auto populate an input from selection. do not go back to combo input
                for name in series_names:
                    dpg.add_text(name)
        dpg.add_combo(list(axis_scale.keys()), width=50, callback=set_axis_scale, user_data=tag, default_value=get_current_axis_scale(tag), show=enable)
        # dpg.add_checkbox()
        dpg.add_checkbox(indent=25,show=enable)
        dpg.add_checkbox(indent=25,show=enable)



    with dpg.window(label=f'Configure {pi.plot_name}',pos=(50,200), autosize=True): #,no_move=True,modal=True):

        TEXT_BOX_WIDTH = 125 # TODO: consider making this global
        CHECK_BOX_WIDTH = 50

        with dpg.tab_bar():
            with dpg.tab(label='Global'):
                dpg.add_separator(label='Plot')
                with dpg.group(horizontal=True):
                    dpg.add_input_text(label='Plot Name', width=TEXT_BOX_WIDTH, default_value=pi.plot_name, callback=change_plot_name_callback)
                    dpg.add_checkbox(label='Show Plot Name', default_value=pi.options['show_plot_name'], callback=set_plot_name_visibility)
                dpg.add_separator(label="Legend")
                with dpg.group(horizontal=True):
                    dpg.add_checkbox(label='Show legend', default_value=pi.options['show_legend'], callback=show_legend_callback)
                    dpg.add_checkbox(label='Highlight Axis on Hover', default_value=pi.options['highlight_axis_on_hover'], callback=highlight_axis_callback)
                # dpg.add_combo(plot_types, default_value=plot_types[0],callback=select_plot_type, width=TEXT_BOX_WIDTH) # TODO: see if theres a better way to do this now that everything is a class
                dpg.add_separator(label='Axes')

                with dpg.table(header_row=True, borders_innerH=True,borders_outerH=True) as table:
                    dpg.add_table_column(label='Enable Axis', width_fixed=True)
                    # dpg.add_table_column(label='Axis Label', width_fixed=True)
                    dpg.add_table_column(label='Axis Alias', width_fixed=True)
                    dpg.add_table_column(label='Scale', width_fixed=True)
                    # dpg.add_table_column(label='Invert',width_fixed=True,width=20) $ TODO: decide if this adds value or not
                    dpg.add_table_column(label='Hide Label',width_fixed=True,width=20)
                    dpg.add_table_column(label='Hide Axis',width_fixed=True,width=20)

                    axis_list = {'Y Axis 1':pi.y_axis_tags[0],'Y Axis 2':pi.y_axis_tags[1],'Y Axis 3':pi.y_axis_tags[2],'X Axis 1':pi.x_axis_tags[0],'X Axis 2':pi.x_axis_tags[1]}


                    for name, tag in axis_list.items():
                        # axis_dropdowns = get_list_of_series_in_axis(tag)
                        with dpg.table_row(user_data=tag):
                            dpg.add_button(label=name, width=100, callback=change_enable_theme, user_data={'enable':True,'name':name,'tag':tag})
                            dpg.bind_item_theme(dpg.last_item(), deactivated_axis)
                            # print(dpg.get_item_label(button))
                            show_rest_of_table(get_item_user_data(dpg.last_item()))
                                # dpg.add_combo(axis_dropdowns, width=75, callback=set_axis_name)
                                # dpg.add_input_text(width=TEXT_BOX_WIDTH, callback=set_axis_alias, user_data=tag)
                                # series_names = get_list_of_series_in_axis(tag)
                                # if series_names:
                                #     with dpg.tooltip(dpg.last_item()): # TODO: this tooltip is great but add a right cliclk menu to auto populate an input from selection. do not go back to combo input
                                #         for name in series_names:
                                #             dpg.add_text(name)
                                # dpg.add_combo(list(axis_scale.keys()), width=50, callback=set_axis_scale, user_data=tag, default_value=get_current_axis_scale(tag))
                                # # dpg.add_checkbox()
                                # dpg.add_checkbox(indent=25)
                                # dpg.add_checkbox(indent=25)


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
                        dpg.add_combo(line_style, default_value=sr.style,callback=change_plot_style_callback, user_data=sr.instance_tag)
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