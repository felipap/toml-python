#! /usr/bin/env python3

# a simplistic TOML parser for python

import functools
import re
import datetime

class Reader(object):

	def __init__(self, generator):
		"""Takes as argument an object to feed lines tot the Reader."""		
		assert iter(generator), "Argument not iterable." # Some duck-typing.
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
		try:
			# Turn next line into a list of tokens.
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
	

from colorama import Fore, Back, Style
from colorama import init

init(autoreset=True)

def logCall(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		print("%sfunction %s() called" % (Fore.RED, func.__name__))
		return func(*args, **kwargs)
	return wrapper
	

class Evaluator(object):
	# THE parser

	def __init__(self, file):
		self.file = file
		self.runtime = dict()
		self._current_keygroup = self.runtime
		self.mainLoop()
	
	def assignKeyGroup(self, keygroup):
		cg = self.runtime
		nlist = keygroup.split('.')
		for name in nlist:
			try:
				cg[name]
			except KeyError:
				cg[name] = dict()
			print("going to %s", name)
			cg = cg[name]
		
		self._current_keygroup = cg

	####
	
	@logCall
	def parseComment(self, reader):
		reader.discartLine()
	
	@logCall
	def parseSymbol(self, reader):
		return next(reader)

	@logCall
	def parseKEYGROUP(self, reader):
		reader.skipToken('[')
		keygroup = self.parseSymbol(reader)
		reader.skipToken(']')
		reader.assertEOF()
		self.assignKeyGroup(keygroup)
	
	@logCall
	def parseASSIGN(self, reader):
		# Parse an assignment
		var = self.parseSymbol(reader)
		reader.skipToken('=')
		val = self.parseEXP(reader)
		reader.assertEOF()
		self._current_keygroup[var] = val
	
	@logCall
	def parseEXP(self, reader):

		isLIST 		= lambda i, token: token == '['
		isINTEGER 	= lambda i, token: token.isdigit()
		isSTRING 	= lambda i, token: token[0] in ('"', "'")
		isBOOL 		= lambda i, token: token in ('true', 'false')
		def isDATE(i, token):
			try:
				datetime.datetime.strptime(token, "%Y-%m-%dT%H:%M:%SZ")
				return True
			except ValueError:
				return False


		print("\tPARSING EXPRESSION", reader.line)

		for index, token in enumerate(reader):
			
			print("\t\tTOKEN: ", token)
			reader.ungetToken(token)
			
			if isLIST(index, token):
				return self.parseLIST(reader)
			elif isSTRING(index, token):
				return self.parseSTRING(reader)
			elif isINTEGER(index, token):
				return self.parseINTEGER(reader)
			elif isDATE(index, token):
				return self.parseDATE(reader)
			elif isBOOL(index, token):
				return self.parseBOOL(reader)
			else:
				WUT()

	# EXP evaluators

	@logCall
	def parseINTEGER(self, reader):
		return int(next(reader))
	
	@logCall
	def parseFLOAT(self, reader):
		return float(next(reader))

	@logCall
	def parseSTRING(self, reader):
		return next(reader)[1:-1] # Remove quotes.
	
	@logCall
	def parseLIST(self, reader):
		reader.skipToken("[")
		l = [self.parseEXP(reader), ]
		while reader.top() != ']':
			reader.skipToken(",")
			l.append(self.parseEXP(reader))
		reader.skipToken("]")
		return l
	
	@logCall
	def parseDATE(self, reader):
		return datetime.datetime.strptime(next(reader), "%Y-%m-%dT%H:%M:%SZ").isoformat()
	
	@logCall
	def parseBOOL(self, reader):
		return {'true': True, 'false': False}[next(reader)]

	#
	def mainLoop(self):
		# parse lines
		
		isCOMMENT 	= lambda i, token: token in ("#",)
		isKEYGROUP 	= lambda i, token: token == ("[") and i==0
		isSYMBOL 	= lambda token: bool(re.match(r'[^\W\d_]', token, re.U))
		isASSIGN 	= lambda i, token: isSYMBOL(token) and i==0

		reader = Reader(self.file)
		while reader.readNextLine():
			
			print("\nnewline: ", reader.line)

			for index, token in enumerate(reader):
				# Due to the simplistic and non-recursive nature of the markup,
				# the index might be used to identify certain types of tokens.

				print("\tTOKEN: ", token)
				
				reader.ungetToken(token)
				
				if isCOMMENT(index, token):
					self.parseComment(reader)
				elif isKEYGROUP(index, token):
					self.parseKEYGROUP(reader)
				elif isASSIGN(index, token):
					self.parseASSIGN(reader)	
				else:
					print("Uncaught token", token, "at", index)
			
			print("RUNTIME:", self.runtime)
	
		import json
		s = json.dumps(self.runtime, indent=4, separators=(',', ': '))
		json.dump(self.runtime, open("do.json", "w"))
		print(s)
#

def main():
	# some setting up

	import sys
	file = open(sys.argv[1], "r")
	obj = Evaluator(file)
	return obj


if __name__ == "__main__":
	main()
