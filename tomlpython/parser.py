#! /usr/bin/env python3
# -*- encoding: utf8 -*-

# A TOML _parser for Python3

from datetime import datetime as dt
import json
import re

from tomlpython.reader import Reader
from tomlpython.reader import top, pop, skip
from tomlpython.reader import readLine, assertEOL

class _TOMLParser(object):

	def __init__(self, reader):

		self.reader = reader
		self.runtime = dict()
		self.curkeygroup = self.runtime
		self.mainLoop()

	def assignKeyGroup(self, keygroup):
		cg = self.runtime
		nlist = keygroup.split('.')
		for name in nlist:
			try: cg[name]
			except KeyError:
				cg[name] = dict()
			cg = cg[name]
		self.curkeygroup = cg

	####
	
	def parseEXP(self):
		
		# Locals are faster

		ISO8601 = re.compile(r'^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}Z$')
		FLOAT = re.compile(r'^[+-]?\d(>?\.\d+)?$')
		STRING = re.compile(r'(?:".*?[^\\]")|(?:\'.*?[^\\]\')')

		token = top(self.reader)
		if token == '[':
			skip(self.reader, "[")
			l = [self.parseEXP(), ]
			while top(self.reader) != ']':
				skip(self.reader, ",")
				l.append(self.parseEXP())
			skip(self.reader, "]")
			return l
		elif token in ('true', 'false'):
			return {'true': True, 'false': False}[pop(self.reader)]
		elif token.isdigit() or token[1:].isdigit() and token[1] in ('+', '-'):
			return int(pop(self.reader))
		elif FLOAT.match(token):
			return float(pop(self.reader))
		elif ISO8601.match(token):
			return dt.strptime(pop(self.reader), "%Y-%m-%dT%H:%M:%SZ").isoformat()
		elif STRING.match(token):
			return pop(self.reader)[1:-1]
		raise Exception("WTF!")

	#######

	def parseCOMMENT(self):
		# Do nothing.
		# Loop to next line. 
		pass
	
	def parseKEYGROUP(self):
		skip(self.reader, '[')
		keygroup = pop(self.reader) # symbol
		skip(self.reader, ']')
		self.assignKeyGroup(keygroup)
	
	def parseASSIGN(self):
		# Parse an assignment
		var = pop(self.reader) # symbol
		skip(self.reader, '=')
		val = self.parseEXP()
		self.curkeygroup[var] = val

	#######

	def mainLoop(self):
		TESTS = (
			(self.parseCOMMENT, 	lambda token: token in ("#",)),
			(self.parseKEYGROUP, 	lambda token: token == ("[")),
			(self.parseASSIGN,lambda token: re.match(r'[^\W\d_]', token, re.U)),
		)

		while readLine(self.reader):
			# Due to the simplistic and non-recursive nature of the markup,
			# all expressions can be identified by the first meaninful
			# (non-whitespace) character of the line.

			for callback, test in TESTS:
				if test(top(self.reader)):
					callback()
					break
			else:
				raise Exception("Unrecognized token %s" % top(self.reader))
			assertEOL(self.reader)

		return self.runtime


class Parser(object):
	"""Python3 parser for TOML."""
	
	def __init__(self, input):
		self.reader = Reader(input)
		self.parser = _TOMLParser(self.reader)

	def __getitem__(self, item):
		return self.parser.runtime[item]
	
	def __setitem__(self, item, val):
		self.parser.runtime[item] = val
		
	def __repr__(self):
		return self.toJson()

	def toDict(self):
		return self.parser.runtime
	
	def toJson(self):
		return json.dumps(self.parser.runtime)

