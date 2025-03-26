# coding: utf-8
from enum import Enum

from qfluentwidgets import StyleSheetBase, Theme, isDarkTheme, qconfig


class StyleSheet(StyleSheetBase, Enum):
    """ Style sheet  """

    # TODO: Add your qss here
    LINK_CARD = "link_card"
    SAMPLE_CARD = "sample_card"
    SETTING_INTERFACE = "setting_interface"
    VIEW_INTERFACE = "view_interface"
    DISPLAY_INTERFACE = "display_interface"
    HOME_INTERFACE = "home_interface"
    ADDITIONAL_FEATURES_INTERFACE = "additional_features_interface"
    HELP_INTERFACE = "help_interface"
    OCR_TABLE = "ocr_table"

    def path(self, theme=Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        return f":/app/resource/qss/{theme.value.lower()}/{self.value}.qss"
