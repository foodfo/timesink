import dearpygui.dearpygui as dpg

dpg.create_context()
dpg.create_viewport(title="Modal with Popup", width=800, height=600)
dpg.setup_dearpygui()

def show_inner_popup(sender, app_data, user_data):
    with dpg.popup(parent=user_data, mousebutton=dpg.mvMouseButton_Left, tag="inner_popup"):
        dpg.add_text("This is a popup over the modal!")
        dpg.add_button(label="Close Inner Popup", callback=lambda: dpg.delete_item("inner_popup"))

with dpg.window(label="Main Window"):
    dpg.add_button(label="Open Modal", callback=lambda: dpg.show_item("my_modal"))

with dpg.window(label="My Modal", modal=True, show=False, tag="my_modal"):
    dpg.add_text("This is a modal window.")
    dpg.add_button(label="Open Popup", callback=show_inner_popup, user_data=dpg.last_item()) # Parent the popup to the button
    dpg.add_button(label="Close Modal", callback=lambda: dpg.hide_item("my_modal"))

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()