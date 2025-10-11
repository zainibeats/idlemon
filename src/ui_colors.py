"""Centralized UI color palette for IdleMon"""

class UIColors:
    """
    Pokemon-inspired color palette with muted tones.
    Designed to work with green backgrounds while maintaining good visibility.
    """

    # Primary colors - muted Pokemon-inspired palette
    PRIMARY_BLUE = "#5B8FA3"      # Soft blue (Water-type inspired)
    PRIMARY_RED = "#C65D5D"       # Muted red (Fire-type inspired)
    PRIMARY_YELLOW = "#D4AF6A"    # Muted gold (Electric-type inspired)

    # Background colors
    BG_DARK = "rgba(45, 55, 65, 200)"      # Dark semi-transparent background
    BG_DARKER = "rgba(30, 40, 50, 220)"    # Darker variant for emphasis
    BG_LIGHT = "rgba(240, 240, 235, 200)"  # Light background for inputs

    # Text colors
    TEXT_PRIMARY = "#F5F5F0"      # Off-white for main text
    TEXT_SECONDARY = "#B8B8B0"    # Muted gray for secondary text
    TEXT_DARK = "#3A3A3A"         # Dark text for light backgrounds
    TEXT_SHINY = "#D4AF6A"        # Gold for shiny Pokemon

    # Accent colors
    ACCENT_SUCCESS = "#6B9F7F"    # Muted green (Grass-type inspired)
    ACCENT_HOVER = "#7BA895"      # Lighter green for hover states
    ACCENT_PRESSED = "#5A8570"    # Darker green for pressed states

    # Border colors
    BORDER_DEFAULT = "#8B9B9F"    # Neutral gray-blue border
    BORDER_FOCUS = "#D4AF6A"      # Gold border for focused elements
    BORDER_SHINY = "#D4AF6A"      # Gold border for shiny items

    # Scrollbar colors
    SCROLLBAR_BG = "#4A5A6A"      # Scrollbar background
    SCROLLBAR_HANDLE = "#6B7B8B"  # Scrollbar handle
    SCROLLBAR_HOVER = "#7B8B9B"   # Scrollbar handle on hover

    # Button colors
    BUTTON_PRIMARY = "#6B9F7F"    # Primary action button
    BUTTON_SECONDARY = "#5B8FA3"  # Secondary action button
    BUTTON_CANCEL = "#8B9B9F"     # Cancel/neutral button
    BUTTON_DANGER = "#C65D5D"     # Destructive action

    # Count badge
    BADGE_BG = "#C65D5D"          # Badge background (muted red)

    # Group box borders (for settings)
    GROUP_DISPLAY = "#8B7BA8"     # Purple-gray for display settings
    GROUP_VISUAL = "#B8956A"      # Brown-tan for visual settings
