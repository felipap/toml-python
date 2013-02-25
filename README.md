
Python3 parser for TOML
=======================

Info here: [https://github.com/mojombo/toml](https://github.com/mojombo/toml)

## Usage
	
	# As a string (must be unicode)
	from src import parser
	obj = parser.Parser("""
		[database]
		server = "192.168.1.1"
		ports = [ 8001, 8001, 8002 ]
	""")

	# or using a file
	from src import parser
	obj = parser.Parser(open('test.toml', 'r'))

## To Do
- Support multiline array.
- Write de-serializer
