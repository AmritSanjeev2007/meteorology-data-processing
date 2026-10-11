""" The renderer used to display stuff to the window. """

import glfw
import moderngl

from typing import ( Any, Callable )
from ._shared import ( Context )
from .constants import ( DEFAULT_CLEAR_COLOR, INITIAL_WINDOW_SIZE )

class Renderer:
    """The object used to create and control a rendering pipeline. This object is responsible for creating
    and managing GLFW and its resources."""

    def __init__(self, window_title: str) -> None:
        glfw.init()

        self._should_run: bool = False

        _tmp_screen_size = glfw.get_video_mode(glfw.get_primary_monitor()).size

        self.screen_size: tuple[int, int] = (_tmp_screen_size.width, _tmp_screen_size.height)
        """ The resolution of the screen. This is a fixed value and is tied to the primary monitor. """
        self.framebuffer_size: tuple[int, int] = INITIAL_WINDOW_SIZE
        """The size of the framebuffer in pixels (width, height). Note that the size of the framebuffer 
        changes as the window is resized."""
        self.window = glfw.create_window(*self.framebuffer_size, window_title, None, None)
        """ A handle to the object that manages the window. """

        def viewport_resizer(_: Any, w: int, h: int) -> None:
            self.framebuffer_size = (w, h)
            self.ctx.viewport = (0, 0, *self.framebuffer_size)

        glfw.set_window_size_callback(self.window, viewport_resizer)
        glfw.make_context_current(self.window)
    
        self.ctx: Context = moderngl.create_context()
        """ A handle to the context used by OpenGL to render objects while minimizing boilerplate. """

    def stop_rendering(self) -> None:
        """ Stops the renderer from rendering all subsequent frames. """
        self._should_run = False

    def render(self, exec: Callable[[Renderer], None] = lambda _: None) -> None:
        """Begins the render loop which blocks the main thread until either the window recieves a closed 
        event or the renderer is explicitly set to stop rendering via the ``.stop_rendering()`` method. 
        
        This method also takes in an optional `exec` callback which takes in a reference to this renderer 
        which is called every frame right after the current (drawing) framebuffer has been cleared but 
        right before it is swapped with the window's framebuffer."""

        self._should_run = True
        self.ctx.clear(*DEFAULT_CLEAR_COLOR)  # Initial clear

        while not glfw.window_should_close(self.window) and self._should_run:
            glfw.poll_events()
            self.ctx.clear(*DEFAULT_CLEAR_COLOR)
    
            exec(self)
    
            glfw.swap_buffers(self.window)

    def destory(self) -> None:
        """ Destroys this renderer and frees all its resources. """
        glfw.terminate()
