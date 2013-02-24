#! /usr/bin/env python3

# TOML parser for python
# re is freaking fast

from datetime import datetime as dt
import re



class Reader(object):

	def __init__(self, generator):
		"""Takes as argument an object to feed lines tot the Reader."""		
		assert iter(generator), "Argument not iterable." # Some duck-typing.:P
		self._lineGen = generator
		
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
			tline = self._cleverSplit(next(self._lineGen))
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
	

class Evaluator(object):

	def __init__(self, file):
		self.runtime = dict()
		self.reader = Reader(file)
		self.current_keygroup = self.runtime

		import json
		print(json.dumps(self.runtime, indent=4, separators=(',', ': ')))
	
	def assignKeyGroup(self, keygroup):
		cg = self.runtime
		nlist = keygroup.split('.')
		for name in nlist:
			try: cg[name]
			except KeyError:
				cg[name] = dict()
			# print("going to %s", name)
			cg = cg[name]
		self.current_keygroup = cg

	####
	
	def parseEXP(self):

		ISO8601 = re.compile(r'^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}Z$')
		FLOAT = re.compile(r'^[+-]?\d(>?\.\d+)?$')
		INTEGER = re.compile(r'^[+-]?\d*$')
		STRING = re.compile(r'(?:".*?[^\\]")|(?:\'.*?[^\\]\')')

		token = self.reader.top()
		if token == '[':
			self.reader.skipToken("[")
			l = [self.parseEXP(), ]
			while self.reader.top() != ']':
				self.reader.skipToken(",")
				l.append(self.parseEXP())
			self.reader.skipToken("]")
			return l
		elif token in ('true', 'false'):
			return {'true': True, 'false': False}[next(self.reader)]
		elif token.isdigit() or token[1:].isdigit() and token[1] in ('+', '-'):
			return int(next(self.reader))
		elif FLOAT.match(token):
			return float(next(self.reader))
		elif ISO8601.match(token):
			return dt.strptime(next(self.reader), "%Y-%m-%dT%H:%M:%SZ").isoformat()
		elif STRING.match(token):
			return next(self.reader)[1:-1]
		raise Exception("WTF!")

	#######

	def parseCOMMENT(self):
		self.reader.discartLine()
	
	def parseKEYGROUP(self):
		self.reader.skipToken('[')
		keygroup = next(self.reader) # symbol
		self.reader.skipToken(']')
		self.assignKeyGroup(keygroup)
	
	def parseASSIGN(self):
		# Parse an assignment
		var = next(self.reader) # symbol
		self.reader.skipToken('=')
		val = self.parseEXP()
		self.current_keygroup[var] = val

	#######

	def mainLoop(self):
		TESTS = (
			(self.parseCOMMENT, 	lambda token: token in ("#",)),
			(self.parseKEYGROUP, 	lambda token: token == ("[")),
			(self.parseASSIGN,lambda token: re.match(r'[^\W\d_]', token, re.U)),
		)

		while self.reader.readNextLine():
			# Due to the simplistic and non-recursive nature of the markup,
			# all expressions can be identified by the first meaninful
			# (non-whitespace) character of the line.

			for callback, test in TESTS:
				if test(self.reader.top()):
					callback()
					break
			else:
				raise Exception("Unrecognized token %s" % self.reader.top())
			self.reader.assertEOF()

		return self.runtime

def main():

	import sys
	file = open('test.toml', "r")
	obj = Evaluator(file)
	return obj


if __name__ == "__main__":
	main()
