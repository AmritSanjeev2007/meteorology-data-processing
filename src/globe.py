# pyright: standard

""" The globe upon which the meteorological data will be displayed. """


import moderngl
import zipfile

from PIL import Image
Image.MAX_IMAGE_PIXELS = 250_000_000  # To avoid decompression limits
from array import array
from typing import TypeAlias
from pathlib import Path
from ._shared import Context, Texture
from .camera import Camera
from .constants import GLOBE_VERTEX_SHADER_PATH, GLOBE_FRAGMENT_SHADER_PATH
from .data import get_lighting_vec
from .renderer import Renderer
from .shaders import create_shader_program

_VectorTuple: TypeAlias = tuple[float, float, float]
_RotationMatrixTuple: TypeAlias = tuple[_VectorTuple, _VectorTuple, _VectorTuple]
def _flatten_rotation_matrix_tuple(x: _RotationMatrixTuple) -> tuple[float, ...]:
    result = ()
    for tup in x:
        result = (*result, *tup)

    return result

def load_zipped_map_texture(context: Context, path: Path) -> Texture:
    """ Loads a 2D texture from the zipped map image file at the specified ``path``. """

    with zipfile.ZipFile(path, 'r') as zip_file:
        zip_file.extractall(path.parent)  # Extract to parent folder

    map_image: Path | None = None

    for file in path.parent.iterdir():
        if ".tif" in file.name:
            map_image = file
            break

    assert map_image is not None, "The map image has not been extracted correctly."

    max_size = context.info["GL_MAX_TEXTURE_SIZE"]

    with Image.open(map_image) as source:
        source.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        image = source.convert("RGB").transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        texture = context.texture(image.size, 3, image.tobytes(), alignment=1)

    texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
    texture.repeat_x = True
    texture.repeat_y = False
    return texture

class Globe:
    """ The object on whose surface, the meteorological data will be displayed. """

    def __init__(self, context: Context, texture_path: Path | None = None) -> None:

        self._program = create_shader_program(
            context=context,
            vert_shader_path=GLOBE_VERTEX_SHADER_PATH,
            frag_shader_path=GLOBE_FRAGMENT_SHADER_PATH,
        )
        self.lighting_vec = get_lighting_vec()
        self.temperature_data_texture: Texture | None = None
        self.map_texture: Texture | None = None

        if texture_path is not None:
            self.map_texture = load_zipped_map_texture(context, texture_path)

        QUAD_VERTICES_ARR = array("f", [
            -1.0, -1.0, 0.0,
             1.0, -1.0, 0.0,
            -1.0,  1.0, 0.0,
             1.0,  1.0, 0.0,
        ])

        self._vertices = context.buffer(QUAD_VERTICES_ARR.tobytes())
        self._vao = context.vertex_array(
            self._program,
            [(self._vertices, "3f", "in_position")],
        )
    
    def set_temperature_data_texture(self, texture: Texture) -> None:
        """ Sets the temperature data texture for this Globe. """
        self.temperature_data_texture = texture

    def render(self, renderer: Renderer, camera: Camera) -> None:
        """ Renders this globe to the screen. """

        from typing import cast

        resolution_uniform = cast(moderngl.Uniform, self._program["uResolution"])
        resolution_uniform.value = renderer.framebuffer_size

        lighting_vec_uniform = cast(moderngl.Uniform, self._program["fLightingVec"])
        lighting_vec_uniform.value = self.lighting_vec.to_tuple()

        rotation_mat_uniform = cast(moderngl.Uniform, self._program["fRotationMat"])
        rotation_mat_uniform.value = _flatten_rotation_matrix_tuple(camera.rotation_matrix.to_tuple())

        assert self.map_texture is not None
        self.map_texture.use(location=0)
        map_texture_uniform = cast(moderngl.Uniform, self._program["uMapTexture"])
        map_texture_uniform.value = 0

        assert self.temperature_data_texture is not None
        self.temperature_data_texture.use(location=1)
        temperature_data_texture_uniform = cast(moderngl.Uniform, self._program["uTemperature"])
        temperature_data_texture_uniform.value = 1

        self._vao.render(mode=moderngl.TRIANGLE_STRIP, vertices=4)


    def update_data(self) -> None:
        """ Updates all the data to be displayed on the globe. This should be called rarely. """

        self.lighting_vec = get_lighting_vec()
