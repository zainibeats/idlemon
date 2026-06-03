"""Shared Qt stylesheet helpers for IdleMon."""

from ui_colors import UIColors


def transparent_label_style(
    color=UIColors.TEXT_PRIMARY,
    font_size=11,
    *,
    bold=False,
    padding=5,
    extra="",
):
    """Return a transparent QLabel style."""
    font_weight = "font-weight: bold;" if bold else ""
    return f"""
        QLabel {{
            color: {color};
            font-size: {font_size}px;
            {font_weight}
            background: transparent;
            padding: {padding}px;
            {extra}
        }}
    """


def button_style(
    background_color,
    hover_color,
    *,
    pressed_color=None,
    pressed_opacity=None,
    font_size=None,
    border_radius=5,
    padding="8px 20px",
    min_width=None,
    bold=True,
):
    """Return a QPushButton style with consistent hover and pressed states."""
    font_size_rule = f"font-size: {font_size}px;" if font_size is not None else ""
    min_width_rule = f"min-width: {min_width}px;" if min_width is not None else ""
    font_weight = "font-weight: bold;" if bold else ""
    pressed = ""
    if pressed_color is not None:
        opacity_rule = f"opacity: {pressed_opacity};" if pressed_opacity is not None else ""
        pressed = f"""
        QPushButton:pressed {{
            background-color: {pressed_color};
            {opacity_rule}
        }}
        """

    return f"""
        QPushButton {{
            background-color: {background_color};
            color: {UIColors.TEXT_PRIMARY};
            {font_size_rule}
            {font_weight}
            border: none;
            border-radius: {border_radius}px;
            padding: {padding};
            {min_width_rule}
        }}
        QPushButton:hover {{
            background-color: {hover_color};
        }}
        {pressed}
    """


def group_box_style(border_color):
    """Return a QGroupBox style for settings sections."""
    return f"""
        QGroupBox {{
            font-weight: bold;
            color: {UIColors.TEXT_PRIMARY};
            border: 2px solid {border_color};
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }}
    """


def line_edit_style():
    """Return the standard QLineEdit style."""
    return f"""
        QLineEdit {{
            background-color: {UIColors.BG_LIGHT};
            color: {UIColors.TEXT_DARK};
            border: 2px solid {UIColors.BORDER_DEFAULT};
            border-radius: 5px;
            padding: 8px;
            font-size: 12px;
        }}
        QLineEdit:focus {{
            border: 2px solid {UIColors.BORDER_FOCUS};
        }}
    """


def combo_box_style():
    """Return the standard QComboBox style."""
    return f"""
        QComboBox {{
            background-color: {UIColors.BG_LIGHT};
            color: {UIColors.TEXT_DARK};
            border: 2px solid {UIColors.BORDER_DEFAULT};
            border-radius: 5px;
            padding: 8px;
            font-size: 12px;
        }}
        QComboBox::drop-down {{
            border: none;
        }}
        QComboBox QAbstractItemView {{
            background-color: {UIColors.BG_LIGHT};
            color: {UIColors.TEXT_DARK};
            selection-background-color: {UIColors.BUTTON_SECONDARY};
            selection-color: {UIColors.TEXT_PRIMARY};
        }}
    """
