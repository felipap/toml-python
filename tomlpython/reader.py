# -*- encoding: utf8 -*-

import re

def assertEOL(reader):
	# Asserts not valid token is found until EOL.
	# Accepts comments.
	if reader.line and reader.line[0] != '#':
		raise Exception("EOF expected but not found.", reader.line)

def pop(reader, expect=None):
	# Pops top token from "stack" and returns.
	if not reader.line:
		return False
	val = reader.line.pop(0)
	if expect and val != expect:
		raise Exception("Popped token '%s' was not expected '%s'." %\
				(val, expect))
	return val

def top(reader):
	# Returns next token on STACK. Ignores comments.
	# If EOL, next line is loaded.
	rem = reader.__next__()
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
	if not reader.__next__():
		readLine(reader)

def custom_next(obj):
	# For backward compatibility.
	# Imported only if python is 2.x
	return obj.__next__()

VERBOSE = True
	
class Reader(object):

	def __init__(self, input, verbose=False):
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
			self.lineFeeder = StringIO(unicode(input))
		global VERBOSE
		VERBOSE = verbose # be dragons
	
	@staticmethod
	def _cleverSplit(line):
		# Split tokens (keeping quoted strings intact).
		PATTERN = re.compile(r"""(
				^\[.*?\] |						# Match Braces
				".*?[^\\]?" | '.*?[^\\]?' |		# Match Single/double-quotes
				\# | 						# hash
				\s | \] | \[ | \, | \s= |		# Whitespace, braces, comma, =
			)""", re.X)
		# Line stripping is essential for keygroup matching to work.
		if VERBOSE:
			print("token:", [p for p in PATTERN.split(line.strip()) if p.strip()])
		return [p for p in PATTERN.split(line.strip()) if p.strip()]
		
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

