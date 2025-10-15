import dearpygui.dearpygui as dpg

dpg.create_context()

# Sample data
x = [0, 1, 2, 3, 4, 5]
y_primary = [0, 1, 0, 1, 0, 1]
y_secondary = [0, 100, 200, 300, 400, 500]

with dpg.window(label="Dual Axis Plot", width=600, height=400):
    with dpg.plot(label="My Plot", height=350, width=550) as plot_tag:
        # Primary axis
        x_axis = dpg.add_plot_axis(dpg.mvXAxis, label="X Axis")
        y_axis1 = dpg.add_plot_axis(dpg.mvYAxis, label="Left Y Axis")
        y_axis2 = dpg.add_plot_axis(dpg.mvYAxis2, label="Right Y Axis")

        # Add series
        dpg.add_line_series(x, y_primary, label="Primary Series", parent=y_axis1)
        sec_series = dpg.add_line_series(x, y_secondary, label="Secondary Series", parent=y_axis2)

        # Create annotation on secondary Y axis
        y_sec_value = y_secondary[2]  # pick a Y value to annotate (e.g., 200)
        ann_tag = dpg.add_plot_annotation(
            label="Peak",
            default_value=(x[2],y_sec_value),  # initially raw value
            parent=plot_tag,
            color=(255,0,0,255)
        )

    # Function to transform secondary Y to primary Y coordinates
    def transform_secondary_to_primary(y_sec, sec_axis, prim_axis):
        sec_info = dpg.get_plot_axis_limits(sec_axis)
        prim_info = dpg.get_plot_axis_limits(prim_axis)
        sec_min, sec_max = sec_info[0], sec_info[1]
        prim_min, prim_max = prim_info[0], prim_info[1]

        # linear mapping
        normalized = (y_sec - sec_min) / (sec_max - sec_min)
        y_prim = prim_min + normalized * (prim_max - prim_min)
        return y_prim

    # Update annotation to follow secondary Y axis
    def update_annotation(sender, app_data, user_data):
        new_y = transform_secondary_to_primary(
            y_sec_value,
            sec_axis=y_axis2,
            prim_axis=y_axis1
        )
        dpg.configure_item(ann_tag, y=new_y)

    # Add a button to simulate axis zoom/pan and update annotation
    dpg.add_button(label="Update Annotation", callback=update_annotation)

dpg.create_viewport(title='Dual Axis Plot Example', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
