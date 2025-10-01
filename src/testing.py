import dearpygui.dearpygui as dpg

dpg.create_context()
dpg.create_viewport(title="Primary Window Below Viewport Menu Bar", width=800, height=600)

with dpg.viewport_menu_bar():
    with dpg.menu(label="File"):
        dpg.add_menu_item(label="New")
        dpg.add_menu_item(label="Open")
    with dpg.menu(label="Edit"):
        dpg.add_menu_item(label="Cut")
        dpg.add_menu_item(label="Copy")

with dpg.window(label="My Primary Window", tag="PrimaryWindow"):
    dpg.add_text("This is content within the primary window.")
    dpg.add_button(label="Click Me")

dpg.set_primary_window("PrimaryWindow", True)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()