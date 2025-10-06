import dearpygui.dearpygui as dpg
# TODO: audit this list to make sure it has the minimum required tags for best encapsulation
source_config = None
mainwin = None
primary_tab = None
tabs = None
sidebar = None
options_window = None
managers_window = None
data_manager_tab = None
plot_manager_tab = None
plot_window = None
import_config = None

def init_tags():
    global source_config
    global mainwin
    global primary_tab
    global tabs
    global sidebar
    global options_window
    global managers_window
    global data_manager_tab
    global plot_manager_tab
    global plot_window
    global import_config

    source_config = dpg.generate_uuid()
    mainwin = dpg.generate_uuid()
    primary_tab = dpg.generate_uuid()
    tabs = dpg.generate_uuid()
    sidebar = dpg.generate_uuid()
    options_window = dpg.generate_uuid()
    managers_window = dpg.generate_uuid()
    data_manager_tab = dpg.generate_uuid()
    plot_manager_tab = dpg.generate_uuid()
    plot_window = dpg.generate_uuid()
    import_config = dpg.generate_uuid()

def print_tags():
    print(source_config)
    print(mainwin)
    print(primary_tab)
    print(tabs)
    print(sidebar)
    print(options_window)
    print(managers_window)
    print(data_manager_tab)
    print(plot_manager_tab)
    print(plot_window)
    print(import_config)