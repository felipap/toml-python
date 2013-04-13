#! /usr/bin/env python3
# -*- encoding: utf8 -*-

# A TOML parser for Python3

from datetime import datetime as dt
import re
import sys

from tomlpython.reader import Reader
from tomlpython.reader import pop, top, skip
from tomlpython.reader import readLine, assertEOL, allownl


if sys.version_info[0] == 2:
	from tomlpython.reader import custom_next as next


class Parser(object):

	def __init__(self, reader, asJson=False, pedantic=True):
		self._asJson = asJson
		self._is_pedantic = pedantic
		self.reader = reader
		self.runtime = dict()
		self.kgObj = self.runtime
		self.mainLoop()

	def loadKeyGroup(self, keygroup):
		cg = self.runtime
		nlist = keygroup.split('.')
		for index, name in enumerate(nlist):
			if not name:
				raise Exception("Unexpected emtpy symbol in %s" % keygroup)
			elif not name in cg:
				cg[name] = dict()
			elif isinstance(cg[name], dict)\
				 and index == len(nlist)-1\
				 and self._is_pedantic:
				raise Exception("Duplicated keygroup definition: %s" % keygroup)
			cg = cg[name]
		self.kgObj = cg
	
	####

	def parseEXP(self):
		# Locals are faster
		ISO8601 = re.compile(r'^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}Z$')
		FLOAT = re.compile(r'^[+-]?\d(>?\.\d+)?$')
		STRING = re.compile(r'(?:".*?[^\\]?")|(?:\'.*?[^\\]?\')')

		token = next(self.reader)
		if token == '[':
		# Array
			array = []
			skip(self.reader, '[')
			while top(self.reader) != ']':
				array.append(self.parseEXP())
				if len(array) > 1 and self._is_pedantic\
				   and type(array[-1]) != type(array[0]):
					raise Exception("Array of mixed data types.")
				if next(self.reader) != ',':
					break
				skip(self.reader, ",")
			allownl(self.reader)
			skip(self.reader, "]")
			return array
		elif STRING.match(token):
		# String
			return pop(self.reader)[1:-1].decode('string-escape')
		elif token in ('true', 'false'):
		# Boolean
			return {'true': True, 'false': False}[pop(self.reader)]
		elif token.isdigit() or token[1:].isdigit() and token[0] in ('+', '-'):
		# Integer
			return int(pop(self.reader))
		elif FLOAT.match(token):
		# Float
			return float(pop(self.reader))
		elif ISO8601.match(token):
		# Date
			date = dt.strptime(pop(self.reader), "%Y-%m-%dT%H:%M:%SZ")
			return date if not self._asJson else date.isoformat()
		raise Exception("Invalid token: %s" % token)

	#######

	def parseCOMMENT(self):
		# Do nothing.
		# Wait loop to next line. 
		pass
	
	def parseKEYGROUP(self):
		symbol = pop(self.reader)[1:-1]
		if not symbol or symbol.isspace():
			raise Exception("Empty keygroup found.")
		self.loadKeyGroup(symbol)
	
	def parseASSIGN(self):
		# Parse an assignment
		# disallow variable rewriting
		var = pop(self.reader) # symbol
		pop(self.reader, expect='=')
		val = self.parseEXP()
		if self.kgObj.get(var):
			# Disallow variable rewriting.
			raise Exception("Cannot rewrite variable: %s" % var)
		self.kgObj[var] = val

	#######

	def mainLoop(self):
		# Due to the 0-lookahead and non-recursive nature of the markup,
		# all expressions can be identified by the first meaninful
		# (non-whitespace) character of the line.

		while readLine(self.reader):
			token = next(self.reader)
			if token == "#":
				self.parseCOMMENT()
			elif token[0] == "[":
				self.parseKEYGROUP()
			elif re.match(r'[^\W\d_]', token, re.U):
				self.parseASSIGN()
			else:
				raise Exception("Unrecognized token: %s" % token)
			assertEOL(self.reader)
		# return self.runtime

def parse(input):
	"""Parse a TOML string or file."""
	
	reader = Reader(input)
	parser = Parser(reader)
	return parser.runtime

def toJSON(input, **kwargs):
	"""Parse a TOML string or file to JSON string."""
	import json
	reader = Reader(input)
	parser = Parser(reader, asJson=True)
	return json.dumps(parser.runtime, **kwargs)
