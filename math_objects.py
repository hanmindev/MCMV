from __future__ import annotations

import math


class Euler:
    def __init__(self, order: str, x: float = None, y: float = None, z: float = None, ) -> None:
        self.order = order
        self.x = x
        self.y = y
        self.z = z

    def set_from_quaternion(self, quaternion: Quaternion) -> Euler:
        # quaternion to euler angles XYZ
        qx = quaternion.x
        qy = quaternion.y
        qz = quaternion.z
        qw = quaternion.w

        if self.order == 'xyz':
            # pitch (y-axis rotation)
            sinp = 2 * (qx * qz + qw * qy)
            self.y = math.asin(max(-1.0, min(sinp, 1.0)))

            # roll (x-axis rotation)
            sinr_cosp = 2 * (qy * qz - qw * qx)
            cosr_cosp = 1 - 2 * (qx * qx + qy * qy)
            self.x = math.atan2(-sinr_cosp, cosr_cosp)

            # yaw (z-axis rotation)
            siny_cosp = 2 * (qx * qy - qw * qz)
            cosy_cosp = 1 - 2 * (qy * qy + qz * qz)
            self.z = math.atan2(-siny_cosp, cosy_cosp)
        elif self.order == 'yxz':
            sinp = 2 * (qy * qz - qw * qx)
            self.x = math.asin(-1 * max(-1.0, min(sinp, 1.0)))

            sinr_cosp = 2 * (qx * qz + qw * qy)
            cosr_cosp = 1 - 2 * (qx * qx + qy * qy)
            self.y = math.atan2(sinr_cosp, cosr_cosp)

            siny_cosp = 2 * (qx * qy + qw * qz)
            cosy_cosp = 1 - 2 * (qx * qx + qz * qz)
            self.z = math.atan2(siny_cosp, cosy_cosp)
        elif self.order == 'zxy':
            sinp = 2 * (qy * qz + qw * qx)
            self.x = math.asin(max(-1.0, min(sinp, 1.0)))

            sinr_cosp = 2 * (qx * qz - qw * qy)
            cosr_cosp = 1 - 2 * (qx * qx + qy * qy)
            self.y = math.atan2(-sinr_cosp, cosr_cosp)

            siny_cosp = 2 * (qx * qy - qw * qz)
            cosy_cosp = 1 - 2 * (qx * qx + qz * qz)
            self.z = math.atan2(-siny_cosp, cosy_cosp)
        elif self.order == 'zyx':
            sinp = 2 * (qw * qy - qz * qx)
            self.y = math.asin(max(-1.0, min(sinp, 1.0)))

            sinr_cosp = 2 * (qw * qx + qy * qz)
            cosr_cosp = 1 - 2 * (qx * qx + qy * qy)
            self.x = math.atan2(sinr_cosp, cosr_cosp)

            siny_cosp = 2 * (qw * qz + qx * qy)
            cosy_cosp = 1 - 2 * (qy * qy + qz * qz)
            self.z = math.atan2(siny_cosp, cosy_cosp)
        elif self.order == 'yzx':
            sinp = 2 * (qx * qy + qw * qz)
            self.z = math.asin(max(-1.0, min(sinp, 1.0)))

            sinr_cosp = 2 * (qy * qz - qw * qx)
            cosr_cosp = 1 - 2 * (qx * qx + qz * qz)
            self.x = math.atan2(-sinr_cosp, cosr_cosp)

            siny_cosp = 2 * (qx * qz - qw * qy)
            cosy_cosp = 1 - 2 * (qy * qy + qz * qz)
            self.y = math.atan2(-siny_cosp, cosy_cosp)
        elif self.order == 'xzy':
            sinp = 2 * (qx * qy - qw * qz)
            self.z = math.asin(-1 * max(-1.0, min(sinp, 1.0)))

            sinr_cosp = 2 * (qy * qz + qw * qx)
            cosr_cosp = 1 - 2 * (qx * qx + qz * qz)
            self.x = math.atan2(sinr_cosp, cosr_cosp)

            siny_cosp = 2 * (qx * qz + qw * qy)
            cosy_cosp = 1 - 2 * (qy * qy + qz * qz)
            self.y = math.atan2(siny_cosp, cosy_cosp)

        self.x = math.degrees(self.x)
        self.y = math.degrees(self.y)
        self.z = math.degrees(self.z)
        return self

    def change_order(self, new_order: str):
        quaternion = Quaternion()
        quaternion.set_from_euler(self)
        self.order = new_order
        self.set_from_quaternion(quaternion)

    def to_tuple(self):
        return (self.x, self.y, self.z)


class Quaternion:
    def __init__(self, x: float = None, y: float = None, z: float = None, w: float = None) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def __repr__(self):
        return '({}, {}, {}, {})'.format(self.x, self.y, self.z, self.w)

    def set_from_euler(self, euler: Euler) -> Quaternion:
        x = math.radians(euler.x)
        y = math.radians(euler.y)
        z = math.radians(euler.z)
        order = euler.order

        c1 = math.cos(x / 2)
        c2 = math.cos(y / 2)
        c3 = math.cos(z / 2)

        s1 = math.sin(x / 2)
        s2 = math.sin(y / 2)
        s3 = math.sin(z / 2)

        if order == 'xyz':
            self.x = s1 * c2 * c3 + c1 * s2 * s3
            self.y = c1 * s2 * c3 - s1 * c2 * s3
            self.z = c1 * c2 * s3 + s1 * s2 * c3
            self.w = c1 * c2 * c3 - s1 * s2 * s3
        elif order == 'yxz':
            self.x = s1 * c2 * c3 + c1 * s2 * s3
            self.y = c1 * s2 * c3 - s1 * c2 * s3
            self.z = c1 * c2 * s3 - s1 * s2 * c3
            self.w = c1 * c2 * c3 + s1 * s2 * s3
        elif order == 'zxy':
            self.x = s1 * c2 * c3 - c1 * s2 * s3
            self.y = c1 * s2 * c3 + s1 * c2 * s3
            self.z = c1 * c2 * s3 + s1 * s2 * c3
            self.w = c1 * c2 * c3 - s1 * s2 * s3
        elif order == 'zyx':
            self.x = s1 * c2 * c3 - c1 * s2 * s3
            self.y = c1 * s2 * c3 + s1 * c2 * s3
            self.z = c1 * c2 * s3 - s1 * s2 * c3
            self.w = c1 * c2 * c3 + s1 * s2 * s3
        elif order == 'yzx':
            self.x = s1 * c2 * c3 + c1 * s2 * s3
            self.y = c1 * s2 * c3 + s1 * c2 * s3
            self.z = c1 * c2 * s3 - s1 * s2 * c3
            self.w = c1 * c2 * c3 - s1 * s2 * s3
        elif order == 'xzy':
            self.x = s1 * c2 * c3 - c1 * s2 * s3
            self.y = c1 * s2 * c3 - s1 * c2 * s3
            self.z = c1 * c2 * s3 + s1 * s2 * c3
            self.w = c1 * c2 * c3 + s1 * s2 * s3
        return self

    def parent(self, parent):
        """Rotates self by the parent quaternion"""
        child = self

        x = parent.w * child.x + parent.x * child.w + parent.y * child.z - parent.z * child.y
        y = parent.w * child.y - parent.x * child.z + parent.y * child.w + parent.z * child.x
        z = parent.w * child.z + parent.x * child.y - parent.y * child.x + parent.z * child.w
        w = parent.w * child.w - parent.x * child.x - parent.y * child.y - parent.z * child.z

        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def normalize(self) -> None:
        length = math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2 + self.w ** 2)
        self.x = self.x / length
        self.y = self.y / length
        self.z = self.z / length
        self.w = self.w / length

    def normalized(self) -> Quaternion:
        length = math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2 + self.w ** 2)
        x = self.x / length
        y = self.y / length
        z = self.z / length
        w = self.w / length
        return Quaternion(x, y, z, w)

    def between_vectors(self, v_1: Vector3, v_2: Vector3) -> Quaternion:
        v1 = v_1.normalized()
        v2 = v_2.normalized()
        dot = Vector3.dot_prod(v1, v2)

        if dot > 0.99999:
            self.x = 0.0
            self.y = 0.0
            self.z = 0.0
            self.w = 1.0
        elif dot < -0.99999:
            # produce a different vector
            i = v1.i + 1.0
            j = v1.j + 1.0
            k = v1.k + 1.0

            self.x, self.y, self.z = Vector3.cross_prod(v1, Vector3(i, j, k)).to_tuple()
            self.w = 0
            self.normalize()
        else:
            self.x, self.y, self.z = Vector3.cross_prod(v1, v2).to_tuple()
            self.w = dot + 1.0
            self.normalize()

        return self

    def to_tuple(self) -> tuple[float, float, float, float]:
        return (self.x, self.y, self.z, self.w)


class Vector3:
    def __init__(self, i: float, j: float, k: float):
        self.i = i
        self.j = j
        self.k = k

    def __eq__(self, other: Vector3) -> bool:
        return all(self[i] == other[i] for i in range(3))

    def __neg__(self) -> Vector3:
        return Vector3(*(-1 * self[i] for i in range(3)))

    def __sub__(self, other: Vector3) -> Vector3:
        return Vector3(self.i - other.i, self.j - other.j, self.k - other.k)

    def __add__(self, other: Vector3) -> Vector3:
        return Vector3(self.i + other.i, self.j + other.j, self.k + other.k)

    # constants only
    def __mul__(self, other: float):
        return Vector3(self.i * other, self.j * other, self.k * other)

    def __rmul__(self, other: float):
        self.__mul__(other)

    def __iter__(self) -> float:
        yield self.i
        yield self.j
        yield self.k

    def __getitem__(self, item: int):
        if item == 0:
            return self.i
        if item == 1:
            return self.j
        if item == 2:
            return self.k

    def __repr__(self):
        return '({}, {}, {})'.format(self.i, self.j, self.k)

    def magnitude(self) -> float:
        return math.sqrt(sum(self[i] ** 2 for i in range(3)))

    def copy(self) -> Vector3:
        return Vector3(self.i, self.j, self.k)

    def to_tuple(self) -> tuple[float, float, float]:
        return (self.i, self.j, self.k)

    def normalize(self) -> None:
        length = self.magnitude()
        self.i /= length
        self.j /= length
        self.k /= length

    def normalized(self) -> Vector3:
        length = self.magnitude()
        i = self.i / length
        j = self.j / length
        k = self.k / length
        return Vector3(i, j, k)

    def dot_prod(self, other: Vector3) -> float:
        return sum(self[i] * other[i] for i in range(3))

    def cross_prod(self, other: Vector3) -> Vector3:
        i = self.j * other.k - self.k * other.j
        j = self.k * other.i - self.i * other.k
        k = self.i * other.j - self.j * other.i
        return Vector3(i, j, k)

    def rotate_by_quaternion(self, quaternion: Quaternion):
        length = self.magnitude()
        self.normalize()

        a = quaternion.w
        b = quaternion.x
        c = quaternion.y
        d = quaternion.z

        r11 = a * a + b * b - c * c - d * d
        r21 = 2 * b * c + 2 * a * d
        r31 = 2 * b * d - 2 * a * c
        r12 = 2 * b * c - 2 * a * d
        r22 = a * a - b * b + c * c - d * d
        r32 = 2 * c * d + 2 * a * b
        r13 = 2 * b * d + 2 * a * c
        r23 = 2 * c * d - 2 * a * b
        r33 = a * a - b * b - c * c + d * d

        i = self.i
        j = self.j
        k = self.k

        self.i = i * r11 + j * r12 + k * r13
        self.j = i * r21 + j * r22 + k * r23
        self.k = i * r31 + j * r32 + k * r33

        self.i *= length
        self.j *= length
        self.k *= length
