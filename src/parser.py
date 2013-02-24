#! /usr/bin/env python3
# -*- encoding: utf8 -*-

# A TOML parser for Python3

from datetime import datetime as dt
import re

from src.reader import Reader	

class Parser(object):

	def __init__(self, input):
		self.reader = Reader(input)

		self.runtime = dict()
		self.current_keygroup = self.runtime
		print(self.mainLoop())
		import json
		print(json.dumps(self.runtime, indent=4, separators=(',', ': ')))

	def __call__(self):
		raise Exception("hey, I'm here")
	
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
	obj = Parser(file)
	return obj


if __name__ == "__main__":
	main()
