"""Centralized UI color palette for IdleMon"""

class UIColors:
    """
    Pokemon-inspired color palette with muted tones.
    Designed to work with green backgrounds while maintaining good visibility.
    """
    # Primary colors - Bold and saturated
    PRIMARY_BLUE = "#2196F3"      # Bright blue

    # Background colors
    BG_DARK = "rgba(30, 30, 40, 200)"       # Deep dark blue-gray
    BG_DARKER = "rgba(20, 20, 30, 220)"     # Even darker variant
    BG_LIGHT = "rgba(255, 255, 255, 200)"   # Clean white for inputs

    # Text colors
    TEXT_PRIMARY = "#FFFFFF"      # Pure white for main text
    TEXT_SECONDARY = "#B0B0B0"    # Light gray for secondary text
    TEXT_DARK = "#212121"         # Strong dark text for light backgrounds
    TEXT_SHINY = "#FFD700"        # Bright gold for shiny Pokemon

    # Accent colors
    ACCENT_HOVER = "#66BB6A"      # Lighter green for hover
    ACCENT_PRESSED = "#388E3C"    # Darker green for pressed

    # Border colors
    BORDER_DEFAULT = "#757575"    # Medium gray border
    BORDER_FOCUS = "#2196F3"      # Bright blue for focused elements
    BORDER_SHINY = "#FFD700"      # Bright gold for shiny items

    # Scrollbar colors
    SCROLLBAR_BG = "#424242"      # Dark gray background
    SCROLLBAR_HANDLE = "#757575"  # Medium gray handle
    SCROLLBAR_HOVER = "#9E9E9E"   # Light gray on hover

    # Button colors
    BUTTON_PRIMARY = "#4CAF50"    # Vibrant green for primary actions
    BUTTON_SECONDARY = "#2196F3"  # Bright blue for secondary actions
    BUTTON_CANCEL = "#757575"     # Gray for cancel/neutral

    # Count badge
    BADGE_BG = "#66BB6A"          # Lighter green for duplicate count badges

    # Group box borders (for settings)
    GROUP_DISPLAY = "#8B7BA8"     # Muted purple for display settings
    GROUP_VISUAL = "#FFD700"      # Gold for visual settings
