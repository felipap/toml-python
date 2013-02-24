# -*- encoding: utf8 -*-

import re

class Reader(object):

	def __init__(self, input):
		"""Takes as argument an object to feed lines tot the Reader."""
		
		try:
			# Try to use as a file.
			input.read(4)
			input.seek(0)
			self.lineFeeder = input
		except AttributeError:
			# Assume it's a string.
			# Use string with file interface. :)
			from io import StringIO
			self.lineFeeder = StringIO(input)
		
	def __iter__(self):
		return self
	
	def __next__(self):
		if not self.line:
			raise StopIteration()
		return self.line.pop(0)
	
	###
	
	@staticmethod
	def _cleverSplit(line):
		# Splits tokens

		PATTERN = re.compile(r"""(\s|\]|\[|
								\, |
								".*?[^\\]" 	| 	# match single quoted exp
								'.*?[^\\]'	| 	# match double quoted exp
								)""", re.X)
		return [p for p in PATTERN.split(line) if p.strip()]
		
	def _getNextLine(self):
		try: # Turn next line into a list of tokens.
			tline = self._cleverSplit(next(self.lineFeeder))
			if not tline:
				return self._getNextLine()
			return tline
		except StopIteration:
			return None
		
	###
	
	def top(self):
		# get "top of the stack" #!doc
		return self.line[0]

	def readNextLine(self):
		self.line = self._getNextLine()
		return True if self.line else False

	def ungetToken(self, value):
		self.line = [value]+self.line

	def discartLine(self):
		# Discarts the contents of the rest of the line.
		# The usage of this method is preferred over having the reader iterate
		# through the rest of the line.
		self.line = []
	
	def skipToken(self, *expected):
		val = next(self)
		if expected is not None:
			assert val in expected, "FAIL! '%s' not in '%s'" % (val, expected)
	
	def assertEOF(self):
		if self.line and self.line[0] != '#':
			raise Exception("EOF expected but not found.", self.line)