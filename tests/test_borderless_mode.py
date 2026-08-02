"""Tests for borderless desktop pet mode.

A translucent window is only click-through on Windows, where transparent pixels of a
layered window pass clicks to the desktop. On X11 and Wayland the whole window
rectangle swallows input regardless of transparency, so the canvas is masked down to
the sprite. These tests pin the mask geometry that makes that work.
"""
import pytest

pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtCore import QPoint, QSize  # noqa: E402
from PySide6.QtWidgets import QMainWindow  # noqa: E402

import paths  # noqa: E402
from ui_manager import (  # noqa: E402
    BORDERLESS_CANVAS_SIZE,
    BORDERLESS_GRAB_PADDING,
    GIF_SCALE_FACTOR,
    UIManager,
)

# Extremes of the bundled sprite set, and a small sprite for contrast.
WIDEST = "Lugia"
TALLEST = "Growlithe"
SMALL = "Diglett"


class StubPetWindow(QMainWindow):
    """Minimal stand-in exposing the callbacks the context menu connects to."""

    def __init__(self):
        super().__init__()
        self.shiny_paused = False

    def continue_hunt(self):
        pass

    def open_collection_window(self):
        pass

    def open_settings(self):
        pass


@pytest.fixture
def pet(qapp):
    window = StubPetWindow()
    manager = UIManager(window, paths.asset_path("images", "default_background.jpg"),
                        borderless_mode=True)
    manager.setup_ui()
    yield manager
    window.close()


def test_canvas_is_fixed_so_the_pet_does_not_jump(pet):
    assert pet.window.size() == BORDERLESS_CANVAS_SIZE
    assert pet.window.minimumSize() == pet.window.maximumSize()


def test_nothing_is_grabbable_before_the_first_sprite(pet):
    assert pet.window.mask().isEmpty()


@pytest.mark.parametrize("pokemon", [WIDEST, TALLEST, SMALL, "Bulbasaur", "Froslass"])
def test_grab_region_hugs_the_sprite_and_stays_centred(pet, pokemon):
    pet.display_pokemon_gif(pokemon, is_shiny=False)

    sprite = pet.pokemon_movie.scaledSize()
    grab = pet.window.mask().boundingRect()

    assert grab.size() == sprite + QSize(2 * BORDERLESS_GRAB_PADDING,
                                         2 * BORDERLESS_GRAB_PADDING)
    # Centred, so a larger or smaller species does not shift the pet on screen.
    assert grab.center() == pet.window.rect().center()
    # No sprite may be clipped by the canvas.
    assert pet.window.rect().contains(grab)


@pytest.mark.parametrize("pokemon", [WIDEST, TALLEST, SMALL])
def test_canvas_corners_stay_click_through(pet, pokemon):
    pet.display_pokemon_gif(pokemon, is_shiny=False)

    region = pet.window.mask()
    width, height = BORDERLESS_CANVAS_SIZE.width(), BORDERLESS_CANVAS_SIZE.height()
    corners = [
        QPoint(0, 0),
        QPoint(width - 1, 0),
        QPoint(0, height - 1),
        QPoint(width - 1, height - 1),
    ]

    for corner in corners:
        assert not region.contains(corner), f"{corner} should pass clicks to the desktop"


def test_context_menu_is_parented_to_the_sprite(pet):
    """An unparented popup lands in a screen corner on Wayland."""
    menu = pet.build_context_menu()

    assert menu.parent() is pet.pokemon_label


def test_context_menu_offers_continue_only_while_paused(pet):
    pet.window.shiny_paused = False
    assert "Continue Hunt" not in _menu_labels(pet)

    pet.window.shiny_paused = True
    assert "Continue Hunt" in _menu_labels(pet)


def _menu_labels(pet):
    return [action.text() for action in pet.build_context_menu().actions() if action.text()]


def test_canvas_fits_every_bundled_sprite(qapp):
    """Guards against a GIF_SCALE_FACTOR bump silently clipping the largest sprites."""
    from PySide6.QtGui import QMovie

    worst_width = worst_height = 0
    for generation in paths.GENERATIONS:
        for variant in ("normal", "shiny"):
            for gif_path in paths.asset_path("gifs", generation, variant).glob("*.gif"):
                movie = QMovie(str(gif_path))
                movie.jumpToFrame(0)
                size = movie.currentPixmap().size()
                worst_width = max(worst_width, size.width())
                worst_height = max(worst_height, size.height())
                del movie

    assert worst_width and worst_height, "no sprites were scanned"

    needed = QSize(
        round(worst_width * GIF_SCALE_FACTOR) + 2 * BORDERLESS_GRAB_PADDING,
        round(worst_height * GIF_SCALE_FACTOR) + 2 * BORDERLESS_GRAB_PADDING,
    )
    assert needed.width() <= BORDERLESS_CANVAS_SIZE.width()
    assert needed.height() <= BORDERLESS_CANVAS_SIZE.height()
