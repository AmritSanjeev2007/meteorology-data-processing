# pyright: standard

import glfw
import math
import sys

from pyglm import glm
from src.camera import ( Camera )
from src.constants import ( MOUSE_SENSITIVITY, WORLD_MAP_IMAGE_PATH )
from src.control import ( InputManager, MouseData )
from src.data import TemperatureData
from src.globe import ( Globe )
from src.renderer import ( Renderer )
from typing import ( NoReturn, cast )


EXIT_SUCCESS = 0


def main(argv: list[str]) -> NoReturn:
    """ The main entry point into the program. """

    renderer = Renderer("Meteorology")
    globe = Globe(renderer.ctx, WORLD_MAP_IMAGE_PATH)
    input_manager = InputManager(renderer)
    camera = Camera()

    temperature_data = TemperatureData(renderer)
    globe.set_temperature_data_texture(temperature_data.generate_data_texture())

    dragging = False

    def on_button(event: MouseData) -> None:
        nonlocal dragging
        if event.button == glfw.MOUSE_BUTTON_LEFT:
            dragging = event.action == glfw.PRESS

    max_pitch = math.radians(89)
    yaw_angle = 0.0
    pitch_angle = 0.0

    def on_move(event: MouseData) -> None:
        nonlocal yaw_angle, pitch_angle

        if not dragging or event.position_change is None:
            return

        dx, dy = event.position_change
        yaw_angle -= dx * MOUSE_SENSITIVITY
        pitch_angle = max(-max_pitch, min(max_pitch, pitch_angle - dy * MOUSE_SENSITIVITY)) # disable roll

        target = \
            glm.angleAxis(yaw_angle, glm.vec3(0, 1, 0)) * glm.angleAxis(pitch_angle, glm.vec3(1, 0, 0))

        camera.revolveBy(cast(glm.quat, glm.inverse(camera.orientation)) * target)

    def on_scroll(event: MouseData) -> None:
        assert event.scroll_offset is not None
        camera.zoom(math.exp(-event.scroll_offset * 0.1))

    input_manager.on_mouse_button(on_button)
    input_manager.on_mouse_move(on_move)
    input_manager.on_scroll(on_scroll)

    def renderer_callback(r: Renderer):
        globe.render(r, camera)

    renderer.render(renderer_callback)
    renderer.destory()

    exit(EXIT_SUCCESS)

if __name__ == "__main__":
    main(sys.argv)
