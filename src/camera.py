# pyright: standard

""" The camera module. """

import math

from pyglm import glm
from typing import cast

def _complement(q: glm.quat) -> glm.quat:
    """ Returns the complement ``q*`` of the specified quaternion ``q`` such that ``q q* = |q|^2``. """
    return glm.quat(q.w, -q.x, -q.y, -q.z)

class Camera:
    """ The object which controls the perspective to be displayed on the screen. It can be set to an initial
    orientation relative to null island. The data inside a camera just stores a rotation matrix by which the
    globe is rotated by. It's important to note that the matrix doesn't represent the rotation of the Camera
    but instead the rotation of the Globe. One can think of it as rotating the globe while keeping the Camera
    as it is.

    Note that the camera always points toward the center of the globe i.e., toward the core of the Earth.

    It can optionally be initialized with an orientation quaternion which represents a rotation around a 
    specific axis and a zoom factor (default is 1)."""

    def __init__(self, orientation: glm.quat | None = None, zoom: float = 1.0) -> None:

        assert zoom > 0.0

        self.rotation_matrix: glm.mat3x3 = glm.identity(glm.mat3x3)
        self.rotation_matrix = cast(glm.mat3x3, self.rotation_matrix * (1.0 / zoom))

        if orientation is None:
            return

        normalized_orientation = glm.normalize(orientation)
        self.rotation_matrix = glm.mat3_cast(_complement(normalized_orientation))
        self.rotation_matrix = cast(glm.mat3x3, self.rotation_matrix * (1.0 / zoom))

    def revolveBy(self, orientation: glm.quat) -> None:
        """ Revolves this camera around a certain axis by an angle represented by the ``orientation`` quaternion. """

        normalized_orientation = glm.normalize(orientation)
        self.rotation_matrix = cast(glm.mat3x3, glm.mat3_cast(_complement(normalized_orientation)) * self.rotation_matrix)

    def zoom(self, factor: float) -> None:
        """This function makes the camera zoom in if the ``factor`` is greater than 1 or zoom out if the ``factor`` 
        is less than 1. Mathematically all this does is just move the camera further back or bring it forward."""

        assert factor > 0.0
        self.rotation_matrix = cast(glm.mat3x3, self.rotation_matrix * (1.0 / factor))
        

    @property
    def orientation(self) -> glm.quat:
        """ Returns the (readonly) orientation of this camera as a quaternion. """

        normalization_factor = 1.0 / math.cbrt(glm.determinant(self.rotation_matrix))
        return _complement(glm.quat_cast(self.rotation_matrix * normalization_factor))

    @property
    def zoom_factor(self) -> float:
        """ Returns the (readonly) zoom factor of this camera as a float. """
        return 1.0 / glm.length(self.rotation_matrix * glm.vec3(1, 0, 0))
