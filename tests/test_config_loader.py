import json
from pathlib import Path

import pytest

import config_loader
import paths


def _write_required_data_files(project_root):
    data_dir = project_root / "assets" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    for gen in range(1, 6):
        (data_dir / f"gen{gen}_pokemon_names.txt").write_text(
            "Bulbasaur,Very Common\n",
            encoding="utf-8",
        )


def test_load_config_merges_defaults_and_resolves_paths(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "PROJECT_ROOT", tmp_path)
    _write_required_data_files(tmp_path)

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "config.json").write_text(
        json.dumps(
            {
                "mute_audio": True,
                "background_image": r"assets\images\custom.jpg",
                "save_data_file": r"data\save.json",
            }
        ),
        encoding="utf-8",
    )

    config = config_loader.load_config()

    assert config["mute_audio"] is True
    assert config["encounter_delay"] == config_loader.DEFAULT_CONFIG["encounter_delay"]
    assert config["background_image"] == "assets/images/custom.jpg"
    assert config["save_data_file"] == str(config_dir / "save_data.json")
    assert all(Path(path).is_absolute() for path in config["pokemon_data_files"].values())


def test_load_config_ignores_persisted_internal_defaults(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "PROJECT_ROOT", tmp_path)
    _write_required_data_files(tmp_path)

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "config.json").write_text(
        json.dumps(
            {
                "encounter_delay": 0.1,
                "rarity_weights": {"Common": 1},
                "shiny_rate": 1,
                "save_data_file": "/tmp/custom-save.json",
                "pokemon_data_files": {"gen1": "/tmp/gen1.txt"},
                "mute_audio": True,
            }
        ),
        encoding="utf-8",
    )

    config = config_loader.load_config()

    assert config["encounter_delay"] == config_loader.DEFAULT_RUNTIME_CONFIG["encounter_delay"]
    assert config["rarity_weights"] == config_loader.DEFAULT_RUNTIME_CONFIG["rarity_weights"]
    assert config["shiny_rate"] == config_loader.DEFAULT_RUNTIME_CONFIG["shiny_rate"]
    assert config["save_data_file"] == str(config_dir / "save_data.json")
    assert set(config["pokemon_data_files"]) == set(
        config_loader.DEFAULT_RUNTIME_CONFIG["pokemon_data_files"]
    )
    assert config["mute_audio"] is True


def test_load_config_reads_legacy_root_config_user_settings_only(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "PROJECT_ROOT", tmp_path)
    _write_required_data_files(tmp_path)

    (tmp_path / "config.json").write_text(
        json.dumps(
            {
                "borderless_mode": True,
                "save_data_file": "/tmp/old-save.json",
            }
        ),
        encoding="utf-8",
    )

    config = config_loader.load_config()

    assert config["borderless_mode"] is True
    assert config["save_data_file"] == str(tmp_path / "config" / "save_data.json")


@pytest.mark.parametrize(
    ("config_overrides", "message"),
    [
        ({"encounter_delay": -1}, "encounter_delay"),
        ({"shiny_rate": 0}, "shiny_rate"),
        ({"rarity_weights": {"Common": 0}}, "rarity_weights"),
        ({"rarity_weights": {"Common": -1}}, "rarity_weights"),
        ({"pokemon_data_files": {"gen1": "", "gen2": "/tmp/gen2.txt"}}, "pokemon_data_files"),
        ({"background_image": ""}, "background_image"),
        ({"mute_audio": "yes"}, "mute_audio"),
    ],
)
def test_load_config_rejects_invalid_runtime_defaults(
    tmp_path,
    monkeypatch,
    config_overrides,
    message,
):
    monkeypatch.setattr(paths, "PROJECT_ROOT", tmp_path)
    _write_required_data_files(tmp_path)
    runtime_overrides = {
        key: value
        for key, value in config_overrides.items()
        if key in config_loader.DEFAULT_RUNTIME_CONFIG
    }
    user_overrides = {
        key: value
        for key, value in config_overrides.items()
        if key in config_loader.DEFAULT_USER_SETTINGS
    }
    monkeypatch.setattr(
        config_loader,
        "DEFAULT_RUNTIME_CONFIG",
        {**config_loader.DEFAULT_RUNTIME_CONFIG, **runtime_overrides},
    )
    monkeypatch.setattr(
        config_loader,
        "DEFAULT_USER_SETTINGS",
        {**config_loader.DEFAULT_USER_SETTINGS, **user_overrides},
    )

    with pytest.raises(ValueError, match=message):
        config_loader.load_config()
