from importlib.metadata import pass_none

import dearpygui.dearpygui as dpg
import pandas as pd
import numpy as np
import tags
from utils import *


def transform_axis_to_screen_coordinates(source, destination):
    pass





def tansform_axis_to_axis_coordinates(source, destination):
    pass
























def draggable_options():
    with dpg.group(parent=tags.draggables):
        dpg.add_button(label='Annotation')
        dpg.add_button(label='Parse Line')
        dpg.add_button(label='Peak on Screen')