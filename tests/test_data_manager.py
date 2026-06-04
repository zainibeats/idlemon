import json

from data_manager import DataManager


class StubLogger:
    def __init__(self):
        self.errors = []

    def log_error(self, message):
        self.errors.append(message)


def _config(tmp_path, pokemon_files):
    return {
        "save_data_file": str(tmp_path / "save_data.json"),
        "pokemon_data_files": {name: str(path) for name, path in pokemon_files.items()},
    }


def test_shiny_count_round_trip(tmp_path):
    data_file = tmp_path / "gen1.txt"
    data_file.write_text("Bulbasaur,Very Common\n", encoding="utf-8")
    manager = DataManager(_config(tmp_path, {"gen1": data_file}), StubLogger())

    manager.save_shiny_count(12)

    assert manager.load_shiny_count() == 12
    assert json.loads((tmp_path / "save_data.json").read_text(encoding="utf-8")) == {
        "version": 1,
        "total_shiny_found": 12,
        "shinies": {},
    }


def test_shiny_collection_aggregates_and_round_trips(tmp_path):
    data_file = tmp_path / "gen1.txt"
    data_file.write_text("Bulbasaur,Very Common\n", encoding="utf-8")
    manager = DataManager(_config(tmp_path, {"gen1": data_file}), StubLogger())

    manager.log_shiny("Bulbasaur", "Very Common")
    manager.log_shiny("Bulbasaur", "Very Common")
    manager.log_shiny("Charmander", "Common")

    reloaded = DataManager(_config(tmp_path, {"gen1": data_file}), StubLogger())

    assert reloaded.get_all_shinies() == {
        "Bulbasaur": {"rarity": "Very Common", "count": 2},
        "Charmander": {"rarity": "Common", "count": 1},
    }


def test_load_pokemon_data_skips_invalid_lines_and_caches(tmp_path):
    data_file = tmp_path / "gen1.txt"
    data_file.write_text(
        "Bulbasaur,Very Common\nInvalid line\nCharmander,Common\n",
        encoding="utf-8",
    )
    logger = StubLogger()
    manager = DataManager(_config(tmp_path, {"gen1": data_file}), logger)

    first_load = manager.load_pokemon_data()
    data_file.write_text("Squirtle,Common\n", encoding="utf-8")

    assert first_load == {"Bulbasaur": "Very Common", "Charmander": "Common"}
    assert manager.load_pokemon_data() is first_load
    assert any("Invalid entry" in message for message in logger.errors)


def test_load_pokemon_catalog_resolves_gif_paths_and_caches(tmp_path):
    data_dir = tmp_path / "assets" / "data"
    data_dir.mkdir(parents=True)
    data_file = data_dir / "gen1_pokemon_names.txt"
    data_file.write_text("Bulbasaur,Very Common\n", encoding="utf-8")

    manager = DataManager(_config(tmp_path, {"gen1": data_file}), StubLogger())

    catalog = manager.load_pokemon_catalog()

    assert catalog == [
        {
            "name": "Bulbasaur",
            "rarity": "Very Common",
            "generation": "gen1",
            "normal_gif": tmp_path / "assets" / "gifs" / "gen1" / "normal" / "Bulbasaur.gif",
            "shiny_gif": tmp_path / "assets" / "gifs" / "gen1" / "shiny" / "Bulbasaur.gif",
        }
    ]
    assert manager.load_pokemon_catalog() is catalog
    assert manager.load_pokemon_data() == {"Bulbasaur": "Very Common"}
