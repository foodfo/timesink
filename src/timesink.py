from zipfile import sizeEndCentDir

import dearpygui.dearpygui as dpg
from dearpygui.dearpygui import collapsing_header, hide_item, add_button, group

# put into utils
WINDOW_TITLE = "TIMESINK"
# VIEWPORT_HEIGHT = 1080
# VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 700
VIEWPORT_WIDTH = 1200
WINDOW_PADDING = 8
MENU_BAR_HEIGHT : int = 18
SIDEBAR_WIDTH = 150
OPTIONS_HIEGHT = 200

global showSide
showSide = False
downsample_percent = 100


dpg.create_context()
dpg.create_viewport(title=WINDOW_TITLE,width=VIEWPORT_WIDTH,height=VIEWPORT_HEIGHT)
dpg.setup_dearpygui()
dpg.show_viewport()

def hide_sidebar():

    global showSide

    if showSide:
        direction = '<<'
    else:
        direction = '>>'
    dpg.configure_item('Options', show=showSide)
    dpg.configure_item('Plot Controller', show=showSide)
    dpg.configure_item('hide_sidebar', label=direction)
    showSide = not showSide


def show_source_config():
    dpg.configure_item('Source_Config',show=True)



with dpg.window(#width = dpg.get_viewport_width(), height = dpg.get_viewport_height(),pos=[0,MENU_BAR_HEIGHT+40],no_move=True,no_title_bar=True
                ) as mainwin:
    with dpg.menu_bar(tag='vp_bar', show=False):
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

    with dpg.tab_bar(label = "test") as tabs:

        dpg.add_tab_button(label="<<", tag="hide_sidebar",callback=hide_sidebar)
        with dpg.tab(label="Tab 1", tag="tab1") as primary_tab:
            pass
        with dpg.tab(label="Tab 2", tag="tab2"):
            pass
        dpg.add_tab_button(label="+", tag="add_tab")
#         pass
#
# with dpg.window(label=WINDOW_TITLE, width=600, height=300):
#     pass

# everything that sits in a single tab instance
with dpg.child_window(parent=primary_tab, border=False):
    with dpg.group(horizontal=True):
        with dpg.child_window(resizable_x=True, width=SIDEBAR_WIDTH, border=False) as sidebar:
            with dpg.child_window(label="Options",autosize_x=True, tag='Options', auto_resize_y=True):
                with dpg.collapsing_header(label="Options",default_open=True):
                    dpg.add_text(f'Downsample %: {downsample_percent}%')
                    dpg.add_checkbox(label='Downsample Data')
                    dpg.add_checkbox(label='Unlock X-Axis')
                    with dpg.group(horizontal=True):
                        dpg.add_button(label='+ Plot')
                        dpg,add_button(label='- Plot')
                    dpg.add_separator()
                    dpg.add_button(label='Add Parse Line')
                    dpg.add_button(label='Find Peak on Screen')
                    dpg.add_button(label='Add Annotation')

            with dpg.child_window(label="Plot Controller",autosize_x=True, autosize_y=True, tag='Plot Controller'):
                with dpg.tab_bar():
                    with dpg.tab(label='PLOTS') as plot_list:
                        dpg.add_button(label="ADD DATA")
                        with dpg.collapsing_header(label="Source 1",default_open=True):
                            dpg.add_button(label='Configure', callback=show_source_config)
                            dpg.add_button(label='Set X-Axis')
                            dpg.add_separator()
                            with dpg.child_window(height=100):
                                dpg.add_button(label="time")
                                dpg.add_button(label="count")
                                dpg.add_button(label="temp1")
                                dpg.add_button(label="temp2")
                                dpg.add_button(label="temp3")

                    with dpg.tab(label='CUSTOM FORMULAS'):
                        pass
                    with dpg.tab(label='PRESETS'):
                        pass
    # with dpg.child_window(pos=(SIDEBAR_WIDTH+10,0), autosize_x=True, autosize_y=True) as plot_window:
        with dpg.child_window(autosize_x=True, autosize_y=True, border=False) as plot_window:
            # for i in range(20):
            #     dpg.add_text("TEST TEST TEST")
            # TODO: periodically poll the width of the sidebar and adjust plot size accordingly. do the same for viewport height/width? or just run callback on viewport resize?
            with dpg.plot(width=dpg.get_viewport_width()-dpg.get_item_width(sidebar)-40):
                pass
            with dpg.plot():
                pass
            with dpg.plot():
                pass


with dpg.window(label='Configure Data Source', modal=True, height=500, width=500, show=False, tag='Source_Config'):
    with dpg.tab_bar():
        with dpg.tab(label='Fields'):
            dpg.add_input_text(label='File Label')
            dpg.add_separator()

            with dpg.table(header_row=True, borders_innerH=True,
                           borders_outerH=True, borders_innerV=True, borders_outerV=True):
                dpg.add_table_column(label='Source Col Name')
                dpg.add_table_column(label='Visible Name')
                dpg.add_table_column(label='Set X-Axis')

                with dpg.table_row():
                    dpg.add_text('_index')
                    dpg.add_input_text(no_spaces=True, width=100)
                    dpg.add_checkbox()

                with dpg.table_row():
                    dpg.add_text('time')
                    dpg.add_input_text(no_spaces=True, width=100)
                    dpg.add_checkbox()

                with dpg.table_row():
                    dpg.add_text('SAMPLE 1')
                    dpg.add_input_text(no_spaces=True, width=100)
                    dpg.add_checkbox()
                with dpg.table_row():
                    dpg.add_text('Voltage (mV)')
                    dpg.add_input_text(no_spaces=True, width=100)
                    dpg.add_checkbox()
                with dpg.table_row():
                    dpg.add_text('aceleration_z')
                    dpg.add_input_text(no_spaces=True, width=100)
                    dpg.add_checkbox()

        with dpg.tab(label='Edit X-Axis'):
            dpg.add_listbox(("AAAA", "BBBB", "CCCC", "DDDD"), label='ALTERNATE X-AXIS SOURCE')
            dpg.add_checkbox(label='Re-base axis')
            dpg.add_text('scalar')
            dpg.add_text('time')
            dpg.add_text('UTC offset')

    dpg.add_spacing(count=50)
    dpg.add_separator()
    with dpg.group(horizontal=True, horizontal_spacing=100):
        dpg.add_button(label="Cancel")
        dpg.add_button(label="OK")
        dpg.add_button(label="Delete Series")
        # with dpg.theme_component(dpg.mvButton):
        #     dpg.add_theme_color(dpg.mvThemeCol_Button, (7.0, 0.6, 0.6))
        #     dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ( 7.0, 0.8, 0.8))
        #     dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (7.0, 0.7, 0.7))
        #     dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3 * 5)
        #     dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 3 * 3, 3 * 3)

# dpg.configure_item("vp_bar",show=False)

dpg.show_item_registry()
dpg.set_primary_window(mainwin,True)
dpg.start_dearpygui()
dpg.destroy_context()