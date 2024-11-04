from typing import TypeAlias, Tuple, NamedTuple

Matrix: TypeAlias = Tuple[float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float]

class Vector3(NamedTuple):
    x: float
    y: float
    z: float

class Quaternion(NamedTuple):
    w: float
    v: Vector3

class UV(NamedTuple):
    u: float
    v: float
