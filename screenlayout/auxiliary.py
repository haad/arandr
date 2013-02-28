# ARandR -- Another XRandR GUI
# Copyright (C) 2008 -- 2011 chrysn <chrysn@fsfe.org>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Exceptions and generic classes"""

from math import pi

class FileLoadError(Exception): pass
class FileSyntaxError(FileLoadError):
    """A file's syntax could not be parsed."""

class InadequateConfiguration(Exception):
    """A configuration is incompatible with the current state of X."""


class BetterList(list):
    """List that can be split like a string"""
    def indices(self, item):
        i = -1
        while True:
            try:
                i = self.index(item, i+1)
            except ValueError:
                break
            yield i

    def split(self, item):
        indices = list(self.indices(item))
        yield self[:indices[0]]
        for x in (self[a+1:b] for (a,b) in zip(indices[:-1], indices[1:])):
            yield x
        yield self[indices[-1]+1:]


class Size(tuple):
    """2-tuple of width and height that can be created from a '<width>x<height>' string"""
    def __new__(cls, arg):
        if isinstance(arg, basestring):
            arg = [int(x) for x in arg.split("x")]
        arg = tuple(arg)
        assert len(arg)==2
        return super(Size, cls).__new__(cls, arg)

    width = property(lambda self:self[0])
    height = property(lambda self:self[1])
    def __str__(self):
        return "%dx%d"%self

class NamedSize(object):
    """Object that behaves like a size, but has an additional name attribute"""
    def __init__(self, size, name):
        self._size = size
        self.name = name

    width = property(lambda self:self[0])
    height = property(lambda self:self[1])
    def __str__(self):
        if "%dx%d"%(self.width, self.height) in self.name:
            return self.name
        else:
            return "%s (%dx%d)"%(self.name, self.width, self.height)

    def __iter__(self):
        return self._size.__iter__()

    def __getitem__(self, i):
        return self._size[i]

    def __len__(self):
        return 2

class Position(tuple):
    """2-tuple of left and top that can be created from a '<left>x<top>' string"""
    def __new__(cls, arg):
        if isinstance(arg, basestring):
            arg = [int(x) for x in arg.split("x")]
        arg = tuple(arg)
        assert len(arg)==2
        return super(Position, cls).__new__(cls, arg)

    left = property(lambda self:self[0])
    top = property(lambda self:self[1])
    def __str__(self):
        return "%dx%d"%self

class Geometry(tuple):
    """4-tuple of width, height, left and top that can be created from an XParseGeometry style string"""
    # FIXME: use XParseGeometry instead of an own incomplete implementation
    def __new__(cls, width, height=None, left=None, top=None):
        if isinstance(width, basestring):
            width,rest = width.split("x")
            height,left,top = rest.split("+")
        return super(Geometry, cls).__new__(cls, (int(width), int(height), int(left), int(top)))

    def __str__(self):
        return "%dx%d+%d+%d"%self

    width = property(lambda self:self[0])
    height = property(lambda self:self[1])
    left = property(lambda self:self[2])
    top = property(lambda self:self[3])

    position = property(lambda self:Position(self[2:4]))
    size = property(lambda self:Size(self[0:2]))


class Rotation(str):
    """String that represents a rotation by a multiple of 90 degree"""
    def __init__(self, original_me):
        if self not in ('left','right','normal','inverted'):
            raise Exception("No know rotation.")
    is_odd = property(lambda self: self in ('left','right'))
    _angles = {'left':pi/2,'inverted':pi,'right':3*pi/2,'normal':0}
    angle = property(lambda self: Rotation._angles[self])
    def __repr__(self):
        return '<Rotation %s>'%self

LEFT = Rotation('left')
RIGHT = Rotation('right')
INVERTED = Rotation('inverted')
NORMAL = Rotation('normal')
ROTATIONS = (NORMAL, RIGHT, INVERTED, LEFT)
