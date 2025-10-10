import dearpygui.dearpygui as dpg
import pandas as pd
import numpy as np
from dearpygui.dearpygui import show_item, drag_payload

from data_instance import create_data_manager_items # todo: consider not importing this and access it thru dot operator instead

import tags
from data_instance import DataInstance
from utils import data

INPUT_WINDOW_WIDTH = 150
DATA_WINDOW_WIDTH = 350

one_window_only='onewindow'
output_name = 'output_name'
output_draggable = 'output_draggable'
test='scalar'



supported_manipulations = ('Scalar','Algebra','Calculus', 'Compare','Convert','Histogram','FFT','SRS')

def placeholder(sender, app_data, user_data):

    window_name = dpg.get_item_label(sender)

    instance_tag = app_data['instance_tag']
    col_name = app_data['col_name']
    ds: DataInstance = data[instance_tag]
    col_alias = ds.get_alias_from_name(col_name)


    with dpg.window(label=window_name, autosize=True, pos=(100,100)):
        with dpg.group(horizontal=True):
            with dpg.child_window(width = INPUT_WINDOW_WIDTH, autosize_y=True):
                dpg.add_text('INPUTS')
                dpg.add_separator()
                dpg.add_button(label=col_alias, enabled=False)
            with dpg.child_window(auto_resize_x=True, auto_resize_y=True, border=False):
                with dpg.child_window(auto_resize_y=True, auto_resize_x=True) as win:
                    dpg.add_text('What scalar would you like to apply to the selected column?')
                    dpg.add_input_text()
                with dpg.child_window(height = 50, autosize_x=True):
                    with dpg.group(horizontal=True):
                        dpg.add_input_text(label='New Column Name', width=150) # TODO: width should probably be a variable
                        dpg.add_button(label='Calculate')

            with dpg.child_window(width=INPUT_WINDOW_WIDTH, autosize_y=True):
                dpg.add_text('OUTPUTS')
                dpg.add_separator()
                dpg.add_button(label=col_alias)

def ok_to_compute(): # TODO: consider protecting this more by referencing the column in the parent dataframe to ensure no duplicate names
    name = dpg.get_value(output_name)
    if name.strip() != "":
        return True
    else:
        return False

def rebuild_input_button(sender, app_data, user_data):
    button_tag = sender
    instance_tag = app_data['instance_tag']
    col_name = app_data['col_name']
    ds: DataInstance = data[instance_tag]
    col_alias = ds.get_alias_from_name(col_name)

    dpg.configure_item(sender, label=col_alias, user_data=app_data,drop_callback=rebuild_input_button)
    # dpg.add_button(label=col_alias, user_data=app_data, tag=button_tag, drop_callback=rebuild_input_button, parent=tags.input_window)


def populate_scalar():
    dpg.add_button(label='Drag Column Here', drop_callback=rebuild_input_button, parent=tags.input_window, user_data={}, tag='scalar')
    dpg.add_input_float(label='Scalar', parent=tags.data_window, tag='input', width=150) # TODO: make width a variable


# def load_scalar_data(sender, app_data):
#     instance_tag = app_data['instance_tag']
#     col_name = app_data['col_name']
#     ds: DataInstance = data[instance_tag]
#     col_alias = ds.get_alias_from_name(col_name)
#
#     # dpg.set_item_label(sender, col_alias)
#     # dpg.set_item_user_data(sender, app_data)
#     print(dpg.get_item_label(sender))
#
#     rebuild_button(sender, col_alias, app_data, tag='scalar')
#
#     # dpg.configure_item(sender, label=col_alias, user_data=app_data, tag=test)
#     # print(dpg.get_item_label(sender))
#     print('ITEM INFO LOADED')
#     print(dpg.get_item_label(test))

def compute_scalar():

    if not ok_to_compute():
        return

    out_name = dpg.get_value(output_name)



    app_data = dpg.get_item_user_data('scalar') # TODO: clean up these variable names

    instance_tag = app_data['instance_tag']
    col_name = app_data['col_name']
    ds: DataInstance = data[instance_tag]


    scalar = dpg.get_value('input') # TODO: protect this for simple cases, letters, divide by zero

    output_data = ds.df[col_name] * scalar

    ds.add_new_column(output_data,out_name,None) # required to update ds instnace appropriately
    out_alias = ds.get_alias_from_name(out_name)

    alias = ds.get_prepended_alias(out_alias)


    # print('CONVERSION COMPLETE')
    # print(alias)
    # print(ds.df[col_name])
    # print(ds.df[out_name])

    # TODO: consider wrapping this in a function to abstract sending the data so compute_ can have narrow scope
    dpg.configure_item(output_draggable, label=out_alias, show=True)
    dpg.add_drag_payload(label=alias, parent=output_draggable,drag_data=ds.get_drag_payload_data(out_name)) # TODO: consider making this output something that the ds object creates for consistency

    create_data_manager_items(ds) # required to update ds manager appropriately



def populate_algebra():
    with dpg.group(horizontal=True,parent=tags.input_window):
        dpg.add_text('X: ')
        dpg.add_button(label='Drag X Val', drop_callback=rebuild_input_button, user_data={}, tag='x')
    with dpg.group(horizontal=True,parent=tags.input_window):
        dpg.add_text('Y: ')
        dpg.add_button(label='Drag Y Val', drop_callback=rebuild_input_button, user_data={}, tag='y')
    with dpg.group(horizontal=True,parent=tags.input_window):
        dpg.add_text('Z: ')
        dpg.add_button(label='Drag Z Val', drop_callback=rebuild_input_button, user_data={}, tag='z')

    with dpg.group(parent=tags.data_window):
        dpg.add_text('Algebraic Expression:')
        with dpg.tooltip(dpg.last_item()):
            dpg.add_text('X, Y, and Z will be mapped to selected columns')
            dpg.add_text('Output value will be truncated to shortest column')
            dpg.add_text('Supported operations: \n PEMDAS \n sin, cos, tan \n sqrt, pi \n e, ln, log10 \n max, min, abs')
        dpg.add_separator()
        dpg.add_input_text(tag='input')

def compute_algebra():
    if not ok_to_compute():
        return

    out_name = dpg.get_value(output_name)

    # input and format user algebraic expression
    user_expression = dpg.get_value('input').lower().strip()
    if user_expression == "":
        return

    # get x,y,z if user_data exists
    if dpg.get_item_user_data('x'):
        (_,_,x) = data[dpg.get_item_user_data('x')['instance_tag']].get_column(dpg.get_item_user_data('x')['col_name'])
    else:
        x=None
    if dpg.get_item_user_data('y'):
        (_,_,y) = data[dpg.get_item_user_data('y')['instance_tag']].get_column(dpg.get_item_user_data('y')['col_name'])
    else:
        y = None
    if dpg.get_item_user_data('z'):
        (_,_,z) = data[dpg.get_item_user_data('z')['instance_tag']].get_column(dpg.get_item_user_data('z')['col_name'])
    else:
        z = None

    if x is None:
        raise ValueError('X MUST BE DEFINED')

    # get min column length and truncate other values to min length
    min_length = min(len(var) for var in (x,y,z) if var is not None)

    x = x[:min_length]
    if y is not None:
        y = y[:min_length]
    if z is not None:
        z = z[:min_length]

    math_dict = {
        'sin': np.sin,
        'cos': np.cos,
        'tan': np.tan,
        'sqrt': np.sqrt,
        'pi': np.pi,
        'e': np.e,
        'ln': np.log,
        'log10': np.log10,
        'max': np.max,
        'min': np.min,
        'abs': np.abs,
    }

    var_dict = {
        'x': x,
        'y': y,
        'z': z
    }


    output_data = pd.eval(user_expression, local_dict={**math_dict, **var_dict})

    # append data to x-value source
    ds = data[dpg.get_item_user_data('x')['instance_tag']]

    ds.add_new_column(output_data,out_name,None) # required to update ds instnace appropriately
    out_alias = ds.get_alias_from_name(out_name)

    alias = ds.get_prepended_alias(out_alias)

    # TODO: consider wrapping this in a function to abstract sending the data so compute_ can have narrow scope
    dpg.configure_item(output_draggable, label=out_alias, show=True)
    dpg.add_drag_payload(label=alias, parent=output_draggable,drag_data=ds.get_drag_payload_data(out_name)) # TODO: consider making this output something that the ds object creates for consistency

    create_data_manager_items(ds) # required to update ds manager appropriately


def populate_window_handler(which):
    print(which)
    if which == 'Scalar':
        print('passed')
        populate_scalar()
    elif which == 'Algebra':
        populate_algebra()
    else:
        print('tripped')
        raise NotImplementedError

def compute_results_handler(sender, app_data, user_data):
    which = user_data
    if which == 'Scalar':
        print('passed')
        compute_scalar()
    elif which == 'Algebra':
        compute_algebra()
    else:
        print('tripped')
        raise NotImplementedError


def open_manipulate_window(sender, app_data, user_data):
    if dpg.does_item_exist(one_window_only):
        dpg.delete_item(one_window_only)

    which_manipulation = dpg.get_item_label(sender)
    window_name = which_manipulation
    with dpg.window(label=window_name, autosize=True, pos=(100, 100), tag=one_window_only):
        with dpg.group(horizontal=True):
            with dpg.child_window(width=INPUT_WINDOW_WIDTH, autosize_y=True, tag=tags.input_window):
                dpg.add_text('INPUTS')
                dpg.add_separator()
            with dpg.child_window(width=DATA_WINDOW_WIDTH, auto_resize_y=True, border=False):
                with dpg.child_window(auto_resize_y=True,width=DATA_WINDOW_WIDTH , tag=tags.data_window):
                    pass
                with dpg.child_window(height=50, width=DATA_WINDOW_WIDTH, auto_resize_x=True):
                    with dpg.group(horizontal=True):
                        dpg.add_input_text(label='Output Column Name',width=100,tag=output_name)  # TODO: width should probably be a variable
                        dpg.add_button(label='GENERATE', width=100, height=30, callback=compute_results_handler, user_data=which_manipulation)
            with dpg.child_window(width=INPUT_WINDOW_WIDTH, autosize_y=True, tag=tags.output_window):
                dpg.add_text('OUTPUTS')
                dpg.add_separator()
                dpg.add_button(label=window_name, show=False, tag=output_draggable)

    populate_window_handler(which_manipulation)

def manipulation_options():
    with dpg.group(parent = tags.manipulate):
        for option in supported_manipulations:
            dpg.add_button(label=option, drop_callback=placeholder, width=-1, callback=open_manipulate_window)



