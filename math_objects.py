from __future__ import annotations

import math


class Euler:
    """A class representing an Euler rotation.

    Instance Attributes:
      - order: Euler rotation order.
      - x: Rotation along the local x-axis (degrees)
      - y: Rotation along the local y-axis (degrees)
      - z: Rotation along the local z-axis (degrees)
    """

    def __init__(self, order: str, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        """Create a new Euler object.
            order: Euler rotation order.
            x: Rotation along the local x-axis (degrees)
            y: Rotation along the local y-axis (degrees)
            z: Rotation along the local z-axis (degrees)
        """
        self.order = order
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self) -> str:
        """Return a string representation of the Euler object for debugging purposes."""
        return 'Euler({}, {}, {}, {})'.format(self.order, self.x, self.y, self.z)

    def copy(self) -> Euler:
        """Return a copy of the Euler object"""
        return Euler(self.order, self.x, self.y, self.z)

    def set_from_quaternion(self, quaternion: Quaternion) -> Euler:
        """Set the rotation of the Euler object from a Quaternion object.
            quaternion: A Quaternion object.
        """
        # quaternion to euler angles XYZ
        qx = quaternion.x
        qy = quaternion.y
        qz = quaternion.z
        qw = quaternion.w

        x2 = qx + qx
        y2 = qy + qy
        z2 = qz + qz
        xx = qx * x2
        xy = qx * y2
        xz = qx * z2
        yy = qy * y2
        yz = qy * z2
        zz = qz * z2
        wx = qw * x2
        wy = qw * y2
        wz = qw * z2

        m11 = (1 - (yy + zz))
        m21 = (xy + wz)
        m31 = (xz - wy)

        m12 = (xy - wz)
        m22 = (1 - (xx + zz))
        m32 = (yz + wx)

        m13 = (xz + wy)
        m23 = (yz - wx)
        m33 = (1 - (xx + yy))

        if self.order == 'xyz':

            self.y = math.asin(min(max(m13, -1), 1))

            if abs(m13) < 0.9999999:

                self.x = math.atan2(- m23, m33)
                self.z = math.atan2(- m12, m11)

            else:

                self.x = math.atan2(m32, m22)
                self.z = 0

        elif self.order == 'yxz':

            self.x = math.asin(- min(max(m23, -1), 1))

            if abs(m23) < 0.9999999:

                self.y = math.atan2(m13, m33)
                self.z = math.atan2(m21, m22)

            else:

                self.y = math.atan2(- m31, m11)
                self.z = 0

        elif self.order == 'zxy':

            self.x = math.asin(min(max(m32, -1), 1))

            if abs(m32) < 0.9999999:

                self.y = math.atan2(- m31, m33)
                self.z = math.atan2(- m12, m22)

            else:

                self.y = 0
                self.z = math.atan2(m21, m11)

        elif self.order == 'zyx':

            self.y = math.asin(- min(max(m31, -1), 1))

            if abs(m31) < 0.9999999:

                self.x = math.atan2(m32, m33)
                self.z = math.atan2(m21, m11)

            else:

                self.x = 0
                self.z = math.atan2(- m12, m22)

        elif self.order == 'yzx':

            self.z = math.asin(min(max(m21, -1), 1))

            if abs(m21) < 0.9999999:

                self.x = math.atan2(- m23, m22)
                self.y = math.atan2(- m31, m11)

            else:

                self.x = 0
                self.y = math.atan2(m13, m33)

        elif self.order == 'xzy':

            self.z = math.asin(- min(max(m12, -1), 1))

            if abs(m12) < 0.9999999:

                self.x = math.atan2(m32, m22)
                self.y = math.atan2(m13, m11)

            else:

                self.x = math.atan2(- m23, m33)
                self.y = 0

        self.x = math.degrees(self.x)
        self.y = math.degrees(self.y)
        self.z = math.degrees(self.z)
        return self

    def change_order(self, new_order: str) -> None:
        """Change the Euler order from self.order to new_order while keeping the rotation
        representation the same.
            new_order: The new Euler order.
        """
        quaternion = Quaternion()
        quaternion.set_from_euler(self)
        self.order = new_order
        self.set_from_quaternion(quaternion)

    def to_tuple(self) -> tuple[float, float, float]:
        """Return a tuple representation of the Euler object.
        """
        return self.x, self.y, self.z


class Quaternion:
    """A class representing a Quaternion.

    Instance Attributes:
      - x: The i component of the quaternion.
      - y: The j component of the quaternion.
      - z: The k component of the quaternion.
      - w: The real component of the quaternion.
    """

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 1.0) -> None:
        """Create a new Quaternion object. Note that the real part goes at the end unlike
        some quaternion representations.

            x: The i component of the quaternion.
            y: The j component of the quaternion.
            z: The k component of the quaternion.
            w: The real component of the quaternion.
        """
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def __repr__(self) -> str:
        """Return a string representation of the Quaternion object for debugging purposes."""
        # return 'Quaternion({}, {}, {}, {})'.format(self.x, self.y, self.z, self.w)

        e = Euler('zyx').set_from_quaternion(self)
        return 'Quaternion({}, {}, {}, {}), Euler(\'-z-yx\',{},{},{})'.format(self.x, self.y, self.z, self.w, e.x, -e.y, -e.z)

    def copy(self) -> Quaternion:
        """Return a copy of the Quaternion object."""
        return Quaternion(self.x, self.y, self.z, self.w)

    def extract_vector(self) -> Vector3:
        sin = math.sin(math.acos(self.w))
        try:
            return Vector3(self.x, self.y, self.z) * (1 / sin)
        except ZeroDivisionError:
            return Vector3(0.0, 0.0, 0.0)

    def replace_vector(self, vector: Vector3):
        sin = math.sin(math.acos(self.w))
        self.x, self.y, self.z = (vector * sin).to_tuple()

    def set_from_euler(self, euler: Euler) -> Quaternion:
        """Set the quaternion from an Euler object.
            euler: A Euler object.
        """
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

    def parent(self, parent: Quaternion) -> None:
        """Rotate self by the parent quaternion.

            parent: A Quaternion object to parent.
        """
        child = self

        x = parent.w * child.x + parent.x * child.w + parent.y * child.z - parent.z * child.y
        y = parent.w * child.y - parent.x * child.z + parent.y * child.w + parent.z * child.x
        z = parent.w * child.z + parent.x * child.y - parent.y * child.x + parent.z * child.w
        w = parent.w * child.w - parent.x * child.x - parent.y * child.y - parent.z * child.z

        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def parented(self, parent: Quaternion) -> Quaternion:
        """Return a quaternion that is self rotated by the parent quaternion.

            parent: A Quaternion object to parent.
        """
        child = self.copy()

        x = parent.w * child.x + parent.x * child.w + parent.y * child.z - parent.z * child.y
        y = parent.w * child.y - parent.x * child.z + parent.y * child.w + parent.z * child.x
        z = parent.w * child.z + parent.x * child.y - parent.y * child.x + parent.z * child.w
        w = parent.w * child.w - parent.x * child.x - parent.y * child.y - parent.z * child.z

        child.x = x
        child.y = y
        child.z = z
        child.w = w

        return child

    def normalize(self) -> None:
        """Normalize self such that the magnitude is 1.
        """
        length = math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2 + self.w ** 2)
        self.x = self.x / length
        self.y = self.y / length
        self.z = self.z / length
        self.w = self.w / length

    def normalized(self) -> Quaternion:
        """Return a normalized quaternion from self.
        """
        length = math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2 + self.w ** 2)
        x = self.x / length
        y = self.y / length
        z = self.z / length
        w = self.w / length
        return Quaternion(x, y, z, w)

    def conjugate(self) -> Quaternion:
        """Return the conjugate quaternion"""
        return Quaternion(-1 * self.x, -1 * self.y, -1 * self.z, self.w)

    def between_vectors(self, v_1: Vector3, v_2: Vector3) -> Quaternion:
        """Set the quaternion as the shortest rotation from v_1 to v_2.
            v_1: A Vector3 object
            v_2: A Vector3 object

        Rotating v_1 by self.between_vectors(v_1,v_2) yields a vector
        pointing in the same direction as v_2.
        """
        try:
            v1 = v_1.normalized()
            v2 = v_2.normalized()
            dot = Vector3.dot_prod(v1, v2)
        except ZeroDivisionError:
            dot = 1.0
            v1 = Vector3()
            v2 = Vector3()

        if dot > 0.99999:
            self.x = 0.0
            self.y = 0.0
            self.z = 0.0
            self.w = 1.0
        elif dot < -0.99999:
            # produce a different vector
            i = v1.x + 1.0
            j = v1.y + 1.0
            k = v1.z + 1.0

            self.x, self.y, self.z = Vector3.cross_prod(v1, Vector3(i, j, k)).to_tuple()
            self.w = 0
            self.normalize()
        else:
            self.x, self.y, self.z = Vector3.cross_prod(v1, v2).to_tuple()
            self.w = dot + 1.0
            self.normalize()

        return self

    def to_tuple(self) -> tuple[float, float, float, float]:
        """Return a tuple representation of the quaternion
        """
        return self.x, self.y, self.z, self.w


class Vector3:
    """A class representing a 3-dimensional Vector.

    Instance Attributes:
      - i: The i component of the vector.
      - j: The i component of the vector.
      - k: The i component of the vector.
    """
    x: float
    y: float
    z: float

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        """Create a new Vector3 object.

            x: The x component of the vector.
            y: The y component of the vector.
            z: The z component of the vector.
        """
        self.x = x
        self.y = y
        self.z = z

    def __neg__(self) -> Vector3:
        """Return a Vector3 object with opposite direction.
        """
        return Vector3(*(-1 * self[i] for i in range(3)))

    def __sub__(self, other: Vector3) -> Vector3:
        """Return the difference between self and other.
            other: Vector3 to subtract from self.
        """
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __add__(self, other: Vector3) -> Vector3:
        """Return the sum of self and other.
            other: Vector3 to add to self.
        """
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    # constants only
    def __mul__(self, other: float):
        """Return the product of self and a constant.
            other: A constant to multiply to self.
        """
        return Vector3(self.x * other, self.y * other, self.z * other)

    def __rmul__(self, other: float):
        """See __mul__.
        """
        return self.__mul__(other)

    def __iter__(self) -> float:
        """Iterate between each component of the vector in ijk order.
        """
        yield self.x
        yield self.y
        yield self.z

    def __getitem__(self, item: int) -> float:
        """Return the component of the vector after indexing.
            item: Index of the vector. i = 0, j = 1, k = 2.
        """
        if item == 0:
            return self.x
        if item == 1:
            return self.y
        if item == 2:
            return self.z

    def __repr__(self) -> str:
        """Return a string representation of the object for debugging"""
        return '({}, {}, {})'.format(self.x, self.y, self.z)

    def magnitude(self) -> float:
        """Return the magnitude of the vector"""
        return math.sqrt(sum(self[i] ** 2 for i in range(3)))

    def copy(self) -> Vector3:
        """Return a copy of the vector"""
        return Vector3(self.x, self.y, self.z)

    def to_tuple(self) -> tuple[float, float, float]:
        """Return a tuple representation of the vector"""
        return self.x, self.y, self.z

    def normalize(self) -> None:
        """Normalize the vector"""
        length = self.magnitude()
        self.x /= length
        self.y /= length
        self.z /= length

    def normalized(self) -> Vector3:
        """Return a normalized version of this vector"""
        length = self.magnitude()
        i = self.x / length
        j = self.y / length
        k = self.z / length
        return Vector3(i, j, k)

    def scale_to(self, scale: float) -> None:
        """Scale vector to desired magnitude."""
        m = self.magnitude()
        if m == 0:
            if scale == 0:
                return
            else:
                raise Exception('Vector scale error: Cannot scale zero vector to non-zero size.')
        else:
            scalar = scale / m
            self.x *= scalar
            self.y *= scalar
            self.z *= scalar

    def scaled_to(self, scale: float) -> Vector3:
        """Scale vector to desired magnitude."""
        m = self.magnitude()
        if m == 0:
            if scale == 0:
                return Vector3(0.0, 0.0, 0.0)
            else:
                raise Exception('Vector scale error: Cannot scale zero vector to non-zero size.')
        else:
            return self * (scale / m)

    def dot_prod(self, other: Vector3) -> float:
        """Return the dot product of self and other.
            other: The other Vector
        """
        return sum(self[i] * other[i] for i in range(3))

    def cross_prod(self, other: Vector3) -> Vector3:
        """Return the cross product of self and other.
            other: The second Vector
        """
        i = self.y * other.z - self.z * other.y
        j = self.z * other.x - self.x * other.z
        k = self.x * other.y - self.y * other.x
        return Vector3(i, j, k)

    def rotate_by_quaternion(self, quaternion: Quaternion):
        """Rotate self by quaternion.
            quaternion: A Quaternion object.
        """
        length = self.magnitude()
        if length == 0.0:
            self.x = 0.0
            self.y = 0.0
            self.z = 0.0
        else:
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

            i = self.x
            j = self.y
            k = self.z

            self.x = i * r11 + j * r12 + k * r13
            self.y = i * r21 + j * r22 + k * r23
            self.z = i * r31 + j * r32 + k * r33

            self.x *= length
            self.y *= length
            self.z *= length

    def rotated_by_quaternion(self, quaternion: Quaternion):
        """Return a rotated version of self by quaternion.
            quaternion: A Quaternion object.
        """
        length = self.magnitude()
        if length == 0.0:
            return Vector3(0.0, 0.0, 0.0)
        self_copy = self.normalized()

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

        i = self_copy.x
        j = self_copy.y
        k = self_copy.z

        self_copy.x = i * r11 + j * r12 + k * r13
        self_copy.y = i * r21 + j * r22 + k * r23
        self_copy.z = i * r31 + j * r32 + k * r33

        self_copy.x *= length
        self_copy.y *= length
        self_copy.z *= length

        return self_copy

    def scale_pixels_to_meter(self) -> None:
        """Scale self from pixels to meters.
        """
        self.x /= 16.0
        self.y /= 16.0
        self.z /= 16.0

    def scaled_pixels_to_meter(self) -> Vector3:
        """Return a scaled version of self from pixels to meters.
        """
        return Vector3(self.x / 16.0, self.y / 16.0, self.z / 16.0)
