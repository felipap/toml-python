# -*- encoding: utf8 -*-

import re


def assertEOL(reader):
	# Asserts not valid token is found until EOL.
	# Accepts comments.
	if reader.line and reader.line[0] != '#':
		raise Exception("EOF expected but not found.", self.line)

def pop(reader):
	# Pops top token from "stack" and returns.
	if not reader.line:
		return False
	return reader.line.pop(0)

def top(reader):
	# Returns top element on stack.
	if not reader.line:
		return False
	return reader.line[0]

def skip(reader, *expect):
	# Skips next token from reader.
	val = pop(reader)
	if expect and val not in expect:
		raise Exception("Failed to skip '%s': expected '%s'." % (val, expect))

def readLine(reader):
	# Updates line on reader and returns False if EOF is found.
	reader._readNextLine()
	return bool(reader.line)


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
	
	###
	
	@staticmethod
	def _cleverSplit(line):
		# Split tokens (keeping quoted strings intact).

		PATTERN = re.compile(r"""(
				\s | \] | \[ | \, | = |	# Match whitespace, braces, comma, =
				".*?[^\\]" | '.*?[^\\]' # Match single/double-quotes.
			)""", re.X)
		return [p for p in PATTERN.split(line) if p.strip()]
		
	def _readNextLine(self):
		# Get next line from input.
		try: # Turn next line into a list of tokens.
			tline = self._cleverSplit(next(self.lineFeeder))
			if not tline:
				self.line = self._readNextLine()
			self.line = tline
		except StopIteration:
			self.line = None
