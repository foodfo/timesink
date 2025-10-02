import dearpygui.dearpygui as dpg
dpg.create_context()

def drag_cb(sender, app_data, user_data):
    # sender is btn_drag
    # app_data is btn_drag (value from drag_data)
    # do some configure(drawing_item), animation
    ...

def drop_cb(sender, app_data, user_data):
    # sender is group, app_data is btn_drag
    dpg.move_item(app_data, parent=sender)

with dpg.window():
    with dpg.group(horizontal=True):

        with dpg.group(width=300, drop_callback=drop_cb, payload_type="int"):  # user_data=??
            dpg.add_text("Group left")
            dpg.add_button(label="not drag this")

        with dpg.group(width=300, drop_callback=drop_cb, payload_type="int"):
            dpg.add_text("Group right")
            dpg.add_button(label="not drag this")
            btn_drag = dpg.add_button(label="drag me to another group then drop", drag_callback=drag_cb)

        with dpg.drag_payload(parent=btn_drag, drag_data=btn_drag, payload_type="int"):
            dpg.add_text("dragging a button")

            # parent=btn_drag     --> this playload will appear if dragged from the btn_drag
            # drag_data=btn_drag  --> btn_drag will be app_data in the above drag_cb and drop_cb
            # payload_type="int"  --> btn_drag is an int, specified in this playload and drop target - two group above

dpg.create_viewport()
dpg.setup_dearpygui()
dpg.show_viewport()
while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()
dpg.destroy_context()