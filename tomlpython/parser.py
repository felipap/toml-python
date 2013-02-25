#! /usr/bin/env python3
# -*- encoding: utf8 -*-

# A TOML _parser for Python3

from datetime import datetime as dt
import json
import re

from src.reader import Reader	

class _Parser(object):

	def __init__(self, input):
		self.reader = Reader(input)

		self.runtime = dict()
		self._curkeygroup = self.runtime
		self._mainLoop()

	def _assignKeyGroup(self, keygroup):
		cg = self.runtime
		nlist = keygroup.split('.')
		for name in nlist:
			try: cg[name]
			except KeyError:
				cg[name] = dict()
			cg = cg[name]
		self._curkeygroup = cg

	####
	
	def __parseEXP(self):

		ISO8601 = re.compile(r'^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}Z$')
		FLOAT = re.compile(r'^[+-]?\d(>?\.\d+)?$')
		STRING = re.compile(r'(?:".*?[^\\]")|(?:\'.*?[^\\]\')')

		token = self.reader.top()
		if token == '[':
			self.reader.skipToken("[")
			l = [self.__parseEXP(), ]
			while self.reader.top() != ']':
				self.reader.skipToken(",")
				l.append(self.__parseEXP())
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

	def __parseCOMMENT(self):
		self.reader.discardLine()
	
	def _parseKEYGROUP(self):
		self.reader.skipToken('[')
		keygroup = next(self.reader) # symbol
		self.reader.skipToken(']')
		self._assignKeyGroup(keygroup)
	
	def _parseASSIGN(self):
		# Parse an assignment
		var = next(self.reader) # symbol
		self.reader.skipToken('=')
		val = self.__parseEXP()
		self._curkeygroup[var] = val

	#######

	def _mainLoop(self):
		TESTS = (
			(self.__parseCOMMENT, 	lambda token: token in ("#",)),
			(self._parseKEYGROUP, 	lambda token: token == ("[")),
			(self._parseASSIGN,lambda token: re.match(r'[^\W\d_]', token, re.U)),
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
			self.reader.assertEOL()

		return self.runtime


class Parser (_Parser):
	"""Python3 parser for TOML."""
	
	def __getitem__(self, item):
		return self.runtime[item]
	
	def __setitem__(self, item, val):
		self.runtime[item] = val
	
	def toDict(self):
		return self.runtime
	
	def toJson(self):
		return json.dumps(self.runtime)


