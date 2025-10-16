from importlib.metadata import pass_none

import dearpygui.dearpygui as dpg
import pandas as pd
import numpy as np
import tags
from utils import *



def transform_axis_to_screen_coordinates(source, destination):
    pass



def add_annotation(sender, app_data, user_data):

    text, plot_coords, parent_tag, offset = user_data
    text = dpg.get_value(text)
    color = dpg.get_item_label(sender)
    offset = dpg.get_value(offset) # TODO: clean these functinos up to make variable names clearere

    # TODO: fine tune color options
    if color=='Red': # TODO: consider chaning the variable name for type safety
        color = [255, 0, 0, 255]
    elif color=='Green':
        color = [0, 255, 0, 255]
    elif color=='Yellow':
        color = [255, 255, 0, 255]
    elif color=='Blue':
        color = [0, 0, 255, 255]
    else:
        color = [255, 255, 0, 255] # DEFAULT VALUE IF NO COLOR IS CHOSEN (pressing enter on text box)

    if offset == 'TR':
        offset = [15,-15]
    elif offset == 'TL':
        offset = [-15,-15]
    elif offset == 'BR':
        offset = [15,15]
    elif offset == 'BL':
        offset = [-15,15]
    else:
        offset = [15,-15]

    dpg.add_plot_annotation(label=text, default_value=plot_coords, parent=parent_tag, color=color, offset=offset, clamped=False)
    dpg.delete_item(dpg.last_root()) # TODO: thsi works but consider tag explicit to avoid accidentally deleting the wrong root
def add_annotation_to_plot(sender, app_data, user_data):
    print(app_data['draggable'])
    user_data = dpg.get_item_user_data(sender)
    plot_instance_tag = user_data
    pi = plots[plot_instance_tag]

    dpg.split_frame() # required to force update dpg renderer to compute correct coords. TODO: if we do this a lot, consider putting it in a function that returns coords after a split frame
    mouse_coords = dpg.get_plot_mouse_pos()
    mouse_screen_coords = dpg.get_mouse_pos()

    # pregen the tags to use them in user data
    offset = dpg.generate_uuid()
    default_color = dpg.generate_uuid()
    txt = dpg.generate_uuid()

    with dpg.theme() as activated_axis: # TODO: create themes.py and put them all in there
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (10, 100, 100, 200))  # closed
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (10, 100, 100, 170))  # hover
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (10, 100, 100, 200))

    with dpg.window(label='Annotation', modal=True, autosize=True, pos=mouse_screen_coords, no_title_bar=True):
        dpg.add_input_text(default_value='Text Here', auto_select_all=True, width=150, on_enter=True, tag=txt, callback=add_annotation, user_data=[txt,mouse_coords, pi.graph_tag, offset])
        dpg.focus_item(txt)

        with dpg.group(horizontal=True):
            dpg.add_radio_button(('TR','BR','BL','TL'), horizontal=True, default_value='TR', tag=offset)

        user_data = [txt, mouse_coords, pi.graph_tag, offset]

        with dpg.group(horizontal=True):
            dpg.add_button(label='Yellow', user_data=user_data, callback=add_annotation, tag=default_color) # TODO: default color didnt seem to work? kept going black so had to add else clause
            dpg.bind_item_theme(dpg.last_item(), activated_axis) # TODO: consider if there is a better way to show default value
            dpg.add_button(label='Red', user_data=user_data, callback=add_annotation)
            dpg.add_button(label='Green', user_data=user_data, callback=add_annotation)
            dpg.add_button(label='Blue', user_data=user_data, callback=add_annotation)

# TODO: PARSE LINES MUST BE A CLASS. also rethink the name
def add_parse_line(sender, app_data, user_data):
    user_data = dpg.get_item_user_data(sender)
    plot_instance_tag = user_data
    pi = plots[plot_instance_tag]

    dpg.split_frame()  # required to force update dpg renderer to compute correct coords. TODO: if we do this a lot, consider putting it in a function that returns coords after a split frame
    mouse_coords = dpg.get_plot_mouse_pos()
    mouse_screen_coords = dpg.get_mouse_pos()

    dpg.add_drag_line(label="LINE # 1", parent=pi.graph_tag,default_value=mouse_coords[0])
    dpg.add_drag_line(label="LINE # 1", parent=pi.graph_tag, default_value=mouse_coords[0]+3000) # TODO: make this a % of plot size. maybe 10% would feel OK?



def tansform_axis_to_axis_coordinates(source, destination):
    pass
























def draggable_options():
    with dpg.group(parent=tags.draggables):
        dpg.add_button(label='Annotation') #TODO: add some text explaining function when enter pressed.  also consider a way to manage annotations later
        with dpg.drag_payload(parent=dpg.last_item(),drag_data={'draggable':'Annotation'}):
            dpg.add_text('Annotation')
        dpg.add_button(label='Parse Line')
        with dpg.drag_payload(parent=dpg.last_item(),drag_data={'draggable':'Parse Line'}):
            dpg.add_text('Parse Line')
        dpg.add_button(label='Peak on Screen')