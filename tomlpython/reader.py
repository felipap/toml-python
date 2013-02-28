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
	# Returns next token on STACK. Ignores comments.
	# If EOL, next line is loaded.
	rem = next(reader)
	if not rem:
		reader._readNextLine()
		return top(reader)
	return rem


def skip(reader, *expect):
	# Skips next token from reader.
	val = pop(reader)
	if expect and val not in expect:
		raise Exception("Failed to skip token '%s': expected one in '%s,'."\
				% (val, ', '.join(expect)))


def readLine(reader):
	# Updates line on reader and returns False if EOF is found.
	return reader._readNextLine()


def allownl(reader):
	# If nothing left on stack, read new line.
	# Used for multiline arrays and such.
	if not next(reader):
		readLine(reader)


class Reader(object):

	def __init__(self, input):
		"""Takes as argument an object to feed lines to the Reader."""
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
	
	@staticmethod
	def _cleverSplit(line):
		# Split tokens (keeping quoted strings intact).
		PATTERN = re.compile(r"""(
				\s | \] | \[ | \, | = |	\# | # Whitespace, braces, comma, =
				".*?[^\\]" | '.*?[^\\]' # Match single/double-quotes.
			)""", re.X)
		return [p for p in PATTERN.split(line) if p.strip()]
		
	def _readNextLine(self):
		# Get next line from input.
		try: # Turn next line into a list of tokens.
			tline = self._cleverSplit(next(self.lineFeeder))
			if not tline or tline[0] == "#":
				self.line = self._readNextLine()
			else:
				self.line = tline
		except StopIteration:
			self.line = None
		return self.line
	
	def __next__(self):
		# Returns next token in the current LINE.
		# Ignores comments.
		if not self.line or self.line[0] == "#":
			return None
		return self.line[0]

