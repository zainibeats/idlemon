import json
from pathlib import Path

import config_loader


def _write_required_data_files(project_root):
    data_dir = project_root / "assets" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    for gen in range(1, 6):
        (data_dir / f"gen{gen}_pokemon_names.txt").write_text(
            "Bulbasaur,Very Common\n",
            encoding="utf-8",
        )


def test_load_config_merges_defaults_and_resolves_paths(tmp_path, monkeypatch):
    monkeypatch.setattr(config_loader, "PROJECT_ROOT", tmp_path)
    _write_required_data_files(tmp_path)

    (tmp_path / "config.json").write_text(
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
    assert config["save_data_file"] == str(tmp_path / "data" / "save.json")
    assert all(Path(path).is_absolute() for path in config["pokemon_data_files"].values())
