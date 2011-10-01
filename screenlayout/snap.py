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

from .auxiliary import Position

class Snap(object):
    """Snap-to-edges manager"""
    def __init__(self, size, tolerance, list):
        self.tolerance = tolerance

        self.horizontal = set()
        self.vertical = set()
        for i in list:
            self.vertical.add(i[0].left)
            self.vertical.add(i[0].left+i[1].width)
            self.horizontal.add(i[0].top)
            self.horizontal.add(i[0].top+i[1].height)

            self.vertical.add(i[0].left-size.width)
            self.vertical.add(i[0].left+i[1].width-size.width)
            self.horizontal.add(i[0].top-size.height)
            self.horizontal.add(i[0].top+i[1].height-size.height)

    def suggest(self, position):
        vertical = [x for x in self.vertical if abs(x-position[0])<self.tolerance]
        horizontal = [y for y in self.horizontal if abs(y-position[1])<self.tolerance]

        if vertical:
            position = Position((vertical[0], position[1]))
        if horizontal:
            position = Position((position[0], horizontal[0]))

        return position
