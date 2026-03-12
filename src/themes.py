import dearpygui.dearpygui as dpg

class Themes:
    collapsing_header = None
    red_button = None
    blue_button = None
    red_text = None

    @classmethod
    def init_themes(cls):

        # LIST OF THEMES
        with dpg.theme() as blue_dropdown:
            with dpg.theme_component(dpg.mvCollapsingHeader):
                dpg.add_theme_color(dpg.mvThemeCol_Header, (51, 51, 55, 255))  # closed
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (29, 151, 236, 103))  # hover
                dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (0, 119, 200, 153))

        with dpg.theme() as black_sub_dropdown:
            with dpg.theme_component(dpg.mvCollapsingHeader):
                dpg.add_theme_color(dpg.mvThemeCol_Header, (10, 10, 10, 150))  # closed
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (10, 100,100, 200))  # hover
                dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (10, 10, 10, 255))  # open

        with dpg.theme() as red_text_theme:
            with dpg.theme_component(dpg.mvText):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 0, 0, 255))  # RGBA

        with dpg.theme() as delete_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (180, 60, 60))  # neutral red
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (200, 80, 80))  # lighter red
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (160, 40, 40))  # darker red
                # dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
                # dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 6, 4)

        # THEME ASSIGNMENT MAPPING
        cls.collapsing_header = blue_dropdown
        # cls.collapsing_header = black_sub_dropdown
        cls.red_button = delete_theme
        cls.red_text = red_text_theme




# class Themes:
#
#     @staticmethod
#     def init_themes():
#         pass
#
#     @staticmethod
#     def collapsing_header() -> int:
#         with dpg.theme() as blue_dropdown:
#             with dpg.theme_component(dpg.mvCollapsingHeader):
#                 dpg.add_theme_color(dpg.mvThemeCol_Header, (51, 51, 55, 255))  # closed
#                 dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (29, 151, 236, 103))  # hover
#                 dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (0, 119, 200, 153))
#         return blue_dropdown

        # with dpg.theme() as other_theme:
        #     with dpg.theme_component(dpg.mvCollapsingHeader):
        #         dpg.add_theme_color(dpg.mvThemeCol_Header, (10, 10, 10, 150))  # closed
        #         dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (10, 100,100, 200))  # hover
        #         dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (10, 10, 10, 255))  # open
        #
        # with dpg.theme() as red_text_theme:
        #     with dpg.theme_component(dpg.mvText):
        #         dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 0, 0, 255))  # RGBA
        #
        # with dpg.theme() as delete_theme:
        #     with dpg.theme_component(dpg.mvButton):
        #         dpg.add_theme_color(dpg.mvThemeCol_Button, (180, 60, 60))  # neutral red
        #         dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (200, 80, 80))  # lighter red
        #         dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (160, 40, 40))  # darker red
        #         # dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
        #         # dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 6, 4)
        #
        # # THEME ASSIGNMENT MAPPING
        # cls.collapsing_header = blue_dropdown
        # cls.red_button = delete_theme
        # cls.red_text = red_text_theme