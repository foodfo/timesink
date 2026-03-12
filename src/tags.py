import dearpygui.dearpygui as dpg

class Tags:

    @staticmethod
    def generate() -> int:
        return dpg.generate_uuid()

    @staticmethod
    def init_tags() -> None:
        Tags.source_config = Tags.generate()
        Tags.main_window = Tags.generate()
        Tags.primary_tab = Tags.generate()
        # Tags.tabs = Tags.generate()
        Tags.sidebar = Tags.generate()
        Tags.options_window = Tags.generate()
        Tags.managers_window = Tags.generate()
        Tags.data_manager_tab = Tags.generate()
        Tags.plot_manager_tab = Tags.generate()
        Tags.plot_window = Tags.generate()
        Tags.import_config = Tags.generate()
        Tags.manipulate = Tags.generate()
        Tags.input_window = Tags.generate()
        Tags.data_window = Tags.generate()
        Tags.output_window = Tags.generate()
        Tags.draggables = Tags.generate()