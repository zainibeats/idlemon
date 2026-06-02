from pathlib import Path

import config_loader


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_all_configured_pokemon_entries_have_normal_and_shiny_gifs():
    entries = []

    for gen, relative_data_path in config_loader.DEFAULT_CONFIG["pokemon_data_files"].items():
        data_path = PROJECT_ROOT / relative_data_path
        assert data_path.exists(), f"Missing data file: {relative_data_path}"

        for line in data_path.read_text(encoding="utf-8").splitlines():
            name, rarity = line.split(",", maxsplit=1)
            assert name
            assert rarity
            entries.append((gen, name))

            for variant in ("normal", "shiny"):
                gif_path = PROJECT_ROOT / "assets" / "gifs" / gen / variant / f"{name}.gif"
                assert gif_path.exists(), f"Missing {variant} GIF for {name}: {gif_path}"

    assert len(entries) == 649
