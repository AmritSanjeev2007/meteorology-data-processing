# pyright: standard

""" The module responsible with loading and processing the meteorological data. """

import ephem
import math
import moderngl
import numpy
import xarray
import zipfile

from datetime import datetime, time, timezone
from pathlib import Path
from pyglm import glm

from ._shared import Texture
from .constants import TEMPERATURE_SAVE_FILE
from .renderer import Renderer


def get_lighting_vec() -> glm.vec3:
    """Returns the vector describing the direction of travel of the sunrays hitting Earth in a coordinate 
    system where the arc of the prime-meridian extends out in the ``-z`` direction (i.e., towards the camera) 
    and India is in the ``+x`` (left) direction while the US is on the ``-x`` (right) direction.
    
    More precisely, the north-south axis is represented by the y-axis and the daily rotation occurs around 
    the y-axis. The "sun-vector" exists only on the Y-Z plane.
    
    Note: this function is only a rough approximation, a heuristic, not a precise model of the sunlight 
    hitting the Earth."""

    TROPICAL_YEAR_DAYS = 365.2422
    AXIAL_TILT = math.radians(23.44)

    now = datetime.now(timezone.utc)
    solstice = ephem.next_summer_solstice(f'{now.year}/01/01').datetime().replace(tzinfo=timezone.utc)

    elapsed_days = (now - solstice).total_seconds() / 86_400.0
    orbital_fraction = (elapsed_days / TROPICAL_YEAR_DAYS) % 1.0
    cos_orbit = math.cos(orbital_fraction * math.tau) # between [-1.0, +1.0]

    y_part = math.sin(AXIAL_TILT * cos_orbit)
    z_part = math.cos(AXIAL_TILT * cos_orbit)

    sunlight_orbit = glm.vec3(0, -y_part, z_part)

    midnight = datetime.combine(now.date(), time().min, timezone.utc)
    day_fraction = -((now - midnight).total_seconds() / 86_400.0)

    lighting_vec = glm.rotateY(sunlight_orbit, day_fraction * math.tau)  # math.tau == 2 * math.pi

    return glm.normalize(lighting_vec)


class TemperatureData:
    """Parses the fetched temperature dataset and tries to render a texture that can be mapped onto a Globe. This 
    is done by drawing to a framebuffer object and then eventually written to a texture object.
    
    Since the data is discrete and the data needs to be rendered in a specific way, a separate pipeline as compared 
    to the regular render loop is used to convert data into color fragments (via a fragment shader) and then 
    written eventually into a texture object.
    
    The overall process is:
    ``get data -> pass data into pipeline -> render data in a fragment shader -> write to framebuffer object -> 
    convert to texture``.
    
    Ihe object takes in a reference to a renderer and a target render size for the resultant texture to be 
    generated."""

    def __init__(self, renderer: Renderer) -> None:

        with zipfile.ZipFile(TEMPERATURE_SAVE_FILE, 'r') as zip_file:
            zip_file.extractall(TEMPERATURE_SAVE_FILE.parent)

        dataset_file: Path | None = None

        for file in  TEMPERATURE_SAVE_FILE.parent.iterdir():
            if ".grib" in file.name:
                dataset_file = file
                break

        assert dataset_file is not None, \
            "Dataset has either not been extracted properly or has been incorrectly downloaded."

        self.renderer = renderer
        self.dataset = xarray.open_dataset(dataset_file, engine="cfgrib")

        with open("info.log", 'w') as cout:
            print(self.dataset, file=cout)

        print("Wrote temperature dataset info to info.log.")

        temperature_celsius = self.dataset["t2m"] - 273.15
        temperature_quantile_data = temperature_celsius.quantile([0.02, 0.5, 0.98]).values
        print(
            f"The temperature range is roughly (celsius): [{temperature_quantile_data[0]}, "
            f"{temperature_quantile_data[2]}]"
        )


    def generate_data_texture(self) -> Texture:
        """ Generates a 2D texture that is made of the temperature data. Emphasis on the word "data". Since the 
        generated texture isn't a texture in the conventional sense. But rather, an object of convinience for
        transferring and reading the data at the shader."""

        values = numpy.asarray(self.dataset["t2m"].values, dtype=numpy.float32)

        # Latitude runs north-to-south in the dataset. Reverse rows so texture
        # y=0 corresponds to the southern edge.
        values = numpy.ascontiguousarray(numpy.flipud(values))

        height, width = values.shape
        temperature_texture = self.renderer.ctx.texture(
            (width, height),
            components=1,
            data=values.tobytes(),
            dtype="f4",
            alignment=1,
        )
        temperature_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
        temperature_texture.repeat_x = True
        temperature_texture.repeat_y = False

        return temperature_texture
