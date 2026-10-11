""" Contains useful functions or objects for dealing with shaders. """

from pathlib import Path
from ._shared import ( Context, Program )

def create_shader_program(context: Context, vert_shader_path: Path, frag_shader_path: Path) -> Program:
    """ Creates a shader program using the specified vertex and fragment shaders. """

    return context.program(
        vertex_shader=vert_shader_path.read_bytes(),
        fragment_shader=frag_shader_path.read_bytes()
    )
