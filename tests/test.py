# -*- encoding: utf8 -*-

from os.path import abspath, dirname, join
from functools import wraps
from glob import glob
import unittest
import sys

DIR = dirname(abspath(__file__))
TOMLFiles = glob(join(DIR, '*.toml'))

def addSysPath(path):
	# Add path to sys.path during executing of routine.
	def decorator(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			sys.path.insert(0, abspath(path))
			val = func(*args, **kwargs)
			sys.path = sys.path[1:]
			return val
		return wrapper	
	return decorator


def parseTOMLfiles():
	# Parse TOML files in current dir.
	for filename in TOMLFiles:
		with open(filename) as file:
			print("Testing file ", filename)
			tomlpython.toJSON(file)
			tomlpython.parse(file)
	

class Test(unittest.TestCase):
	
	def setUp(self):
		pass
	
	def test_toml_examples(self):
		# Check if Exception is not thrown
		parseTOMLfiles()


@addSysPath(dirname(DIR))
def main():
	global tomlpython # little hack?
	import tomlpython as tomlpython
	unittest.main()

if __name__ == "__main__":
	main()


