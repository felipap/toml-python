#! /usr/bin/env python3

# TOML parser for python

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

		PATTERN = re.compile(r"""(\ 		|	# match space
								\] | \[		| 	# match braces
								\s 		 	| 	# match whitespace
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
		self.file = file
		self.runtime = dict()

		self.current_keygroup = self.runtime
		self.mainLoop()

	def __call__(self):
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

		T = ((self.parseLIST, lambda t: t == '['),
			(self.parseINTEGER, lambda t: int(t)),
			(self.parseFLOAT, lambda t: float(t)),
			(self.parseSTRING, lambda t: t[0] in ('"', "'")),
			(self.parseDATE, lambda t: dt.strptime(t, "%Y-%m-%dT%H:%M:%SZ")),
			(self.parseBOOL, lambda t: t in ('true', 'false')))

		# print("\tPARSING EXPRESSION", self.reader.line)

		for callback, test in T:
			try:
				if test(self.reader.top()):
					return callback()
			except:
				continue

	#######

	def parseINTEGER(self):
		return int(next(self.reader))
	
	def parseFLOAT(self):
		return float(next(self.reader))

	def parseSTRING(self):
		return next(self.reader)[1:-1] # Remove quotes.
	
	def parseLIST(self):
		self.reader.skipToken("[")
		l = [self.parseEXP(), ]
		while self.reader.top() != ']':
			self.reader.skipToken(",")
			l.append(self.parseEXP())
		self.reader.skipToken("]")
		return l
	
	def parseDATE(self):
		return dt.strptime(next(self.reader), "%Y-%m-%dT%H:%M:%SZ").isoformat()
	
	def parseBOOL(self):
		return {'true': True, 'false': False}[next(self.reader)]

	#######

	def parseCOMMENT(self):
		self.reader.discartLine()
	
	def parseSymbol(self):
		return next(self.reader)

	def parseKEYGROUP(self):
		self.reader.skipToken('[')
		keygroup = self.parseSymbol()
		self.reader.skipToken(']')
		self.assignKeyGroup(keygroup)
	
	def parseASSIGN(self):
		# Parse an assignment
		var = self.parseSymbol()
		self.reader.skipToken('=')
		self.current_keygroup[var] = val

	#######

	def mainLoop(self):
		TESTS = (
			(self.parseCOMMENT, 	lambda token: token in ("#",)),
			(self.parseKEYGROUP, 	lambda token: token == ("[")),
			(self.parseASSIGN,lambda token: re.match(r'[^\W\d_]', token, re.U)),
		)

		self.reader = Reader(self.file)
		while self.reader.readNextLine():
			# Due to the simplistic and non-recursive nature of the markup,
			# all expressions can be identified by the first meaninful
			# (non-whitespace) character of the line.
	
			for callback, test in TESTS:
				if test(self.reader.top()):
					callback()
					break
			else:
				raise Exception("Unrecognized token %s" % token)
			self.reader.assertEOF()

		return self.runtime

def main():
	# some setting up

	obj = Evaluator(open('test.toml', 'r'))
	return

	import sys
	file = open(sys.argv[1], "r")
	obj = Evaluator(file)
	return obj


if __name__ == "__main__":
	main()
