import dearpygui.dearpygui as dpg
from utils import *
import tags






def open_trim_window_export(sender, app_data, user_data):

    output_selector = dpg.generate_uuid()
    loc = dpg.generate_uuid()
    option_tag = dpg.generate_uuid()
    normalize_tag = dpg.generate_uuid()
    reimport_tag = dpg.generate_uuid()
    out_name = dpg.generate_uuid()



    def export_trim_window():
        print(dpg.get_value(option_tag))
        print(dpg.get_value(normalize_tag))
        print(dpg.get_value(reimport_tag))
        print(dpg.get_value(loc))
        print(dpg.get_value(out_name))


    with dpg.window(label='Export', autosize=True,pos=(300,300)):
        options = ('Trim Windows as Separate Columns','Trim Windows Concatenated','Trim Windows as Separate Files')


        dpg.add_radio_button(options, tag=option_tag)
        dpg.add_checkbox(label='Re-Index / Normalize Axis', tag=normalize_tag) # TODO: clean up this language
        dpg.add_checkbox(label='Re-Import to Current Tab', tag=reimport_tag) # TODO: change language
        dpg.add_button(label='Output Location', callback=lambda: dpg.show_item(output_selector)) # TODO: decide if theres a better way
        dpg.add_text(tag=loc)

        with dpg.file_dialog(label='Output Location', directory_selector=True, tag=output_selector, show=False, callback= lambda s,a,u: dpg.set_value(loc,a['file_path_name'])):
            pass

        dpg.add_input_text(label='filename', tag=out_name)
        dpg.add_button(label='EXPORT', callback=export_trim_window)