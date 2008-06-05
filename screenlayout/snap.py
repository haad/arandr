from .xrandr import Position

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
