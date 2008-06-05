"""Exceptions and generic classes"""
from math import pi

class FileLoadError(Exception): pass
class FileSyntaxError(FileLoadError): pass

class InadequateConfiguration(Exception): pass

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

class Position(tuple):
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
