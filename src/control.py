""" The module for handling and reacting to inputs responsible for rotating the globe. """

import glfw

from dataclasses import dataclass
from typing import Any, Callable
from .renderer import Renderer

@dataclass(frozen=True)
class MouseData:
    """ Represents the data for a mouse event. """

    position: tuple[float, float] | None = None
    """ The position of the event on the screen. ``(x, y)`` """
    button: int | None = None
    """ The mouse button whose state changed. """
    action: int | None = None
    """ The specific action that caused the state change (e.g., press, release, etc). """
    position_change: tuple[float, float] | None = None
    """ The change in the position compared to the last mouse event. ``(dx, dy)`` """
    scroll_offset: float | None = None
    """ The scroll offset after the scroll wheel was moved.  """


class InputManager:
    """ An input manager class for attaching callbacks for inputs. """

    def __init__(self, renderer: Renderer) -> None:
        self.renderer = renderer
        self.last_mouse_pos: tuple[float, float] = (0, 0)

    def on_mouse_button(self, callback: Callable[[MouseData], None]) -> None:
        """ Registers a callback for whenever a mouse button's state changes. """

        def _exec(win: Any, button: int, action: int, _: Any) -> None:
            current_pos = glfw.get_cursor_pos(win)
            pos_change = (
                current_pos[0] - self.last_mouse_pos[0],
                current_pos[1] - self.last_mouse_pos[1]
            )

            callback(MouseData(
                button=button,
                action=action,
                position=current_pos,
                position_change=pos_change
            ))

            self.last_mouse_pos = current_pos

        glfw.set_mouse_button_callback(self.renderer.window, _exec)

    def on_mouse_move(self, callback: Callable[[MouseData], None]) -> None:
        """ Registers a callback for whenever a mouse moved. """

        def _exec(_: Any, x: float, y: float) -> None:
            current_pos = (x, y)
            pos_change = (
                x - self.last_mouse_pos[0],
                y - self.last_mouse_pos[1]
            )

            callback(MouseData(position=current_pos, position_change=pos_change))

            self.last_mouse_pos = current_pos

        glfw.set_cursor_pos_callback(self.renderer.window, _exec)

    def on_scroll(self, callback: Callable[[MouseData], None]) -> None:
        """ Registers a callback for whenever the scroll wheel was moved. """

        def _exec(_: Any, _xoffset: float, yoffset: float) -> None:
            callback(MouseData(scroll_offset=yoffset))

        glfw.set_scroll_callback(self.renderer.window, _exec)
