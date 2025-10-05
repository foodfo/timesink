import dearpygui.dearpygui as dpg
import pandas as pd
import numpy as np



class PlotInstance:

    def __init__(self,instance_tag, manager_tag,graph_tag):
        self.instance_tag = instance_tag
        self.manager_tag = manager_tag
        self.graph_tag = graph_tag


    def set_graph_tag(self, tag):
        self.graph_tag = tag

    def set_manager_tag(self, tag):
        self.manager_tag = tag