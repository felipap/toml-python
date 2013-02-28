Python 3 parser for [TOML](https://github.com/mojombo/toml)
=======================

Check out the spec here: [https://github.com/mojombo/toml](https://github.com/mojombo/toml)
### Feel free to send a pull request.

## ToDos and Features
- [x] Allow multiline arrays.
- [x] Disallow variable rewriting.
- [x] Format to JSON.
- [ ] Write de-serializer
- [ ] Improve debugging system.

## Usage
### TOML from string
```python
from tomlpython import parse
obj = parser("""
	[database]
	server = "192.168.1.1"
	ports = [ 8001, 8001, 8002 ]
""")
```
### TOML from file
```python
# From file
>>> import parser
>>> obj = parse(open('test.toml', 'r'))
```
### TOML to JSON (allowing prettify)
```python
from tomlpython import toJSON
obj = toJSON(open('test.toml', 'r'), indent=4)
```


