from zipfile import sizeEndCentDir

import dearpygui.dearpygui as dpg

# put into utils
WINDOW_TITLE = "TIMESINK"
VIEWPORT_HEIGHT = 1080
VIEWPORT_WIDTH = 1920
WINDOW_PADDING = 8
MENU_BAR_HEIGHT : int = 18


dpg.create_context()
dpg.create_viewport(title=WINDOW_TITLE,width=VIEWPORT_WIDTH,height=VIEWPORT_HEIGHT)
# dpg.set_primary_window(tabs, WINDOW_TITLE)
dpg.setup_dearpygui()
dpg.show_viewport()



with dpg.viewport_menu_bar():
    with dpg.menu(label="File",): # not sure what to put here
        pass
    with dpg.menu(label="Options"): # some options and config maybe?
        pass
    with dpg.menu(label="Plot"): # plot options like crosshairs, num plots
        pass
    with dpg.menu(label="Export"): # export options:
        dpg.add_menu_item(label="Truncate to View")
        dpg.add_menu_item(label="Truncate between parsers")
        dpg.add_menu_item(label="Truncate between every other parser")
    with dpg.menu(label="Help"):
        pass

with dpg.window(width = dpg.get_viewport_width(), height = dpg.get_viewport_height(),
                pos=[0,MENU_BAR_HEIGHT],
                no_move=True,
                no_title_bar=True) as mainwin:
    with dpg.tab_bar(label = "test") as tabs:
        with dpg.tab(label="Tab 1", tag="tab1"):
            pass
        with dpg.tab(label="Tab 2", tag="tab2"):
            pass
        dpg.add_tab_button(label="+", tag="add_tab")
#         pass
#
# with dpg.window(label=WINDOW_TITLE, width=600, height=300):
#     pass




dpg.start_dearpygui()
dpg.destroy_context()