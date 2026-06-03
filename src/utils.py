"""Utility functions shared across modules"""
import paths


def find_pokemon_gif(project_root, pokemon_name, is_shiny=False):
    """
    Find the GIF file path for a Pokemon across all generations

    Args:
        project_root: Base path for assets
        pokemon_name: Name of the Pokemon
        is_shiny: Whether to find the shiny version

    Returns:
        Path object if found, None otherwise
    """
    gif_subdir = "shiny" if is_shiny else "normal"

    for gen in range(1, 6):
        gif_path = paths.asset_path(
            "gifs",
            f"gen{gen}",
            gif_subdir,
            f"{pokemon_name}.gif",
            root=project_root,
        )
        if gif_path.exists():
            return gif_path

    return None
