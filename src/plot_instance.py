import dearpygui.dearpygui as dpg
import pandas as pd
import numpy as np



class PlotInstance:

    def __init__(self,tag):
        self.tag = tag
        self.child = None


    def set_child_tag(self, text):
        self.child = text