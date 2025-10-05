import dearpygui.dearpygui as dpg

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()
dpg.show_viewport()



ROWS = 3
COLS = 3

# store references so we can read them later
cell_tags = [[None for _ in range(COLS)] for _ in range(ROWS)]

def print_table_data():
    """Extract current state of table to 2D list."""
    data = []
    for r in range(ROWS):
        row_data = []
        for c in range(COLS):
            text_tag, checkbox_tag = cell_tags[r][c]
            text_value = dpg.get_value(text_tag)
            check_value = dpg.get_value(checkbox_tag)
            row_data.append((text_value, check_value))
        data.append(row_data)
    print("TABLE DATA:", data)

with dpg.window(label="Table Example", width=600, height=400):
    with dpg.table(header_row=True, resizable=True, policy=dpg.mvTable_SizingStretchProp):
        # Add columns
        for c in range(COLS):
            dpg.add_table_column(label=f"Col {c+1}")

        # Add rows
        for r in range(ROWS):
            with dpg.table_row():
                for c in range(COLS):
                    with dpg.group(horizontal=True):
                        text_tag = dpg.add_input_text(width=80, default_value=f"R{r}C{c}")
                        checkbox_tag = dpg.add_checkbox(default_value=False)
                        cell_tags[r][c] = (text_tag, checkbox_tag)

    dpg.add_button(label="Print Table Data", callback=print_table_data)

# dpg.set_viewport_resize_callback(set_all_plot_heights)
# dpg.show_item_registry()
# dpg.set_primary_window(mainwin,True)
dpg.start_dearpygui()
dpg.destroy_context()
