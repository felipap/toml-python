
Python3 parser for TOML
=======================

Info here: [https://github.com/mojombo/toml](https://github.com/mojombo/toml)
### Feel free to send a pull request.

## Usage
	
	# As a string (must be unicode)
	from tomlpython import parse
	obj = parser("""
		[database]
		server = "192.168.1.1"
		ports = [ 8001, 8001, 8002 ]
	""")

	# or using a file
	from tomlpyhon import parser
	obj = parse(open('test.toml', 'r'))

## To Do
- Support multiline array.
- Write de-serializer
