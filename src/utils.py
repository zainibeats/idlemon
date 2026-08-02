"""Utility functions shared across modules"""
import paths


def find_pokemon_gif(pokemon_name, is_shiny=False):
    """
    Find the GIF file path for a Pokemon across all generations

    Args:
        pokemon_name: Name of the Pokemon
        is_shiny: Whether to find the shiny version

    Returns:
        Path object if found, None otherwise
    """
    gif_subdir = "shiny" if is_shiny else "normal"

    for generation in paths.GENERATIONS:
        gif_path = paths.asset_path("gifs", generation, gif_subdir, f"{pokemon_name}.gif")
        if gif_path.exists():
            return gif_path

    return None
