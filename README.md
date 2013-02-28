
Python3 parser for TOML
=======================

Info here: [https://github.com/mojombo/toml](https://github.com/mojombo/toml)
### Feel free to send a pull request.

## Usage
	
	# From string
	from tomlpython import parse
	obj = parser("""
		[database]
		server = "192.168.1.1"
		ports = [ 8001, 8001, 8002 ]
	""")

	# From file
	from tomlpyhon import parser
	obj = parse(open('test.toml', 'r'))

	# To JSON (prettified)
	from tomlpython import toJSON
	obj = toJSON(open('test.toml', 'r'), indent=4)

## To Do
- Write de-serializer
- Improve debugging system.
