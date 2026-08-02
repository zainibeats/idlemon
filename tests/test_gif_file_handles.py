"""Regression tests for the GIF file handles that once exhausted the fd limit.

QLabel.setMovie() keeps a reference to every QMovie it is given, and a QMovie holds
its GIF open for its whole lifetime. Creating a movie per encounter or per collection
tile therefore leaked one file descriptor at a time until the app hit "Too many open
files". Both display paths now reuse a single QMovie.
"""
import os
from pathlib import Path

import pytest

pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtWidgets import QMainWindow  # noqa: E402

import paths  # noqa: E402
from collection_window import CollectionWindow  # noqa: E402
from ui_manager import UIManager  # noqa: E402

pytestmark = pytest.mark.skipif(
    not Path("/proc/self/fd").exists(),
    reason="counting open file descriptors requires /proc",
)

POKEMON = ["Bulbasaur", "Charmander", "Squirtle", "Pikachu", "Eevee"]


def open_gif_count():
    """Return how many GIF files this process currently holds open."""
    total = 0
    for entry in Path("/proc/self/fd").iterdir():
        try:
            if os.readlink(entry).endswith(".gif"):
                total += 1
        except OSError:
            # The descriptor was closed while the directory was being scanned.
            continue
    return total


class StubDataManager:
    def __init__(self, shinies):
        self.shinies = shinies

    def get_all_shinies(self):
        return dict(self.shinies)


@pytest.fixture
def ui_manager(qapp):
    window = QMainWindow()
    manager = UIManager(window, paths.asset_path("images", "default_background.jpg"),
                        borderless_mode=True)
    manager.setup_ui()
    yield manager
    window.close()


def test_repeated_encounters_hold_at_most_one_gif_open(ui_manager):
    baseline = open_gif_count()

    for index in range(120):
        ui_manager.display_pokemon_gif(POKEMON[index % len(POKEMON)], is_shiny=False)

    assert open_gif_count() - baseline <= 1


def test_encounter_gif_is_scaled_up(ui_manager):
    """GIF_SCALE_FACTOR must be applied to the real frame size, not an unset one."""
    ui_manager.display_pokemon_gif("Bulbasaur", is_shiny=False)

    scaled_size = ui_manager.pokemon_movie.scaledSize()
    assert scaled_size.isValid()
    assert scaled_size.width() > 0 and scaled_size.height() > 0
    assert ui_manager.pokemon_movie.currentPixmap().size() == scaled_size


def test_collection_rebuilds_do_not_accumulate_gif_handles(qapp):
    data_manager = StubDataManager({
        name: {"rarity": "Common", "count": 1} for name in POKEMON
    })
    window = CollectionWindow(data_manager)
    try:
        baseline = open_gif_count()

        for _ in range(10):
            window.update_collection_display()
            qapp.processEvents()

        assert open_gif_count() - baseline <= 1
    finally:
        window.close()


def test_hovering_every_tile_holds_at_most_one_gif_open(qapp):
    data_manager = StubDataManager({
        name: {"rarity": "Common", "count": 1} for name in POKEMON
    })
    window = CollectionWindow(data_manager)
    try:
        baseline = open_gif_count()
        items = [
            window.collection_layout.itemAt(index).widget()
            for index in range(window.collection_layout.count())
        ]
        assert items

        for _ in range(5):
            for item in items:
                window.start_hover(item)
                window.stop_hover(item)

        assert open_gif_count() - baseline <= 1
    finally:
        window.close()


def test_reopening_after_a_dangling_hover_does_not_touch_deleted_tiles(qapp):
    """Closing while a tile is hovered leaves hover state pointing at doomed widgets."""
    data_manager = StubDataManager({
        name: {"rarity": "Common", "count": 1} for name in POKEMON
    })
    window = CollectionWindow(data_manager)
    try:
        window.start_hover(window.collection_layout.itemAt(0).widget())
        window.close()  # no leave event is delivered
        qapp.processEvents()

        window.load_collection_data()  # rebuilds the grid over the stale hover
        qapp.processEvents()

        assert window.hovered_item is None
    finally:
        window.close()


def test_stale_leave_event_does_not_stop_the_current_tile(qapp):
    """A leave event from the previous tile must not cancel the new tile's animation."""
    data_manager = StubDataManager({
        name: {"rarity": "Common", "count": 1} for name in POKEMON[:2]
    })
    window = CollectionWindow(data_manager)
    try:
        first = window.collection_layout.itemAt(0).widget()
        second = window.collection_layout.itemAt(1).widget()

        window.start_hover(first)
        window.start_hover(second)
        window.stop_hover(first)  # arrives after the move to `second`

        assert window.hovered_item is second
    finally:
        window.close()
