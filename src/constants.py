""" This module contains all the constants that are shared among all source modules. """

from pathlib import Path
from typing import Any

DEFAULT_CLEAR_COLOR = (0.02, 0.04, 0.08, 1.0)
"""The default color (rgba) used to clear the previous frame. If setup correctly, can also be used as the 
"background" color of the window."""

GLOBE_VERTEX_SHADER_PATH = Path("./shaders/globe.vert")
""" The path to the vertex shader used for rendering the globe sphere. """
GLOBE_FRAGMENT_SHADER_PATH = Path("./shaders/globe.frag")
""" The path to the fragment shader used for rendering the globe sphere. """

INITIAL_WINDOW_SIZE = (1000, 1000)
""" The initial size (width, height) of the window at its creation in pixels. """

MOUSE_SENSITIVITY = 0.003
""" The sensitivity of the mouse while controlling the globe's rotation. """

WORLD_MAP_IMAGE_PATH = Path("./assets/world-map.zip")
""" The path to the zipped world map image which is converted to a texture and wrapped around the Globe's surface. """

# ====== DATASET =======

TEMPERATURE_SAVE_FILE = Path("./data/global_mean_temperature.zip")
""" The file to which the zipped temperature dataset is saved to. """
TEMPERATURE_DATASET = "ecv-for-climate-change"
""" The specific name of the temperature dataset. """
TEMPERATURE_REQUEST: dict[str, Any] = {
    "variable": ["surface_air_temperature"],
    "origin": ["era5"],
    "product_type": ["monthly_mean"],
    "time_aggregation": ["1_month_mean"],
    "data_format": "grib"
}
""" The request for getting the temperature dataset without the day and month fields. """
