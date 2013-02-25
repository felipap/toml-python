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
			# Otherwise, assume it's a string.
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
		# Split tokens (keeping quoted strings intact).

		PATTERN = re.compile(r"""(
				\s | \] | \[ | \, | = |	# Match whitespace, braces, comma, =
				".*?[^\\]" | '.*?[^\\]' # Match single/double-quotes.
			)""", re.X)
		return [p for p in PATTERN.split(line) if p.strip()]
		
	def _getNextLine(self):
		# Get next line from input.
		try: # Turn next line into a list of tokens.
			tline = self._cleverSplit(next(self.lineFeeder))
			if not tline:
				return self._getNextLine()
			return tline
		except StopIteration:
			return None
		
	###
	
	def top(self):
		"""Read next token in current line."""

		return self.line[0]

	def readNextLine(self):
		"""Update interval env to reference next line found in the input.
		If no next line is found: False is returned; otherwise, True."""

		self.line = self._getNextLine()
		return True if self.line else False

	def ungetToken(self, value):
		"""Put a token back on the stack."""

		self.line = [value]+self.line

<<<<<<< HEAD
	def discardLine(self):
=======
	def discartLine(self):
>>>>>>> d1442b78e77d36d368da55f2ff3aae97bf3959fc
		"""Discart the contents of the rest of the line.
		The usage of this method is preferred over having the reader iterate
		through the rest of the line (which is cleary way more expansive).
		"""
		
		self.line = []
	
	def skipToken(self, *expected):
		"""Skip the next token.
		If arguments are supplied, the skipped token is matched against them,
		raising an exception if match is negative."""

		val = next(self)
		if expected is not None and val not in expected:
			raise Exception("FAIL! '%s' not in '%s'" % (val, expected))
	
	def assertEOL(self):
		"""Assert no valid token is found until EOL.
		Ignores comemnts."""

		if self.line and self.line[0] != '#':
			raise Exception("EOF expected but not found.", self.line)
