Python parser for [TOML](https://github.com/mojombo/toml)
=======================

Check out the spec here: [https://github.com/mojombo/toml](https://github.com/mojombo/toml)
### Feel free to send a pull request.

## ToDos and Features
- [x] Allow multiline arrays.
- [x] Disallow variable rewriting.
- [x] Format to JSON.
- [x] Pypi support (see [toml-python](https://pypi.python.org/pypi/toml-python))
- [x] Build unittests.
- [ ] Write de-serializer
- [ ] Improve debugging system.
- [ ] Improve tests.

## Installation
```bash
pip install toml-python
```

## Usage
### TOML from string
```python
>>> import tomlpython
>>> tomlpython.parse("""
	[database]
	server = "192.168.1.1"
	ports = [ 8001, 8001, 8002 ]
""")
{'database': {'ports': [8001, 8001, 8002], 'server': '192.168.1.1'}}
```

### TOML from file
```python
>>> import tomlpython
>>> with open('data.toml') as datafile:
>>>		data = tomlpython.parse(datafile)
```

### TOML to JSON (support to prettify as in json.dumps)
```python
>>> import tomlpython
>>> tomlpython.toJSON("""
		[database]
		server = "192.168.1.1"
		ports = [ 8001, 8001, 8002 ]
    """, indent=4)
{
    "database": {
        "ports": [ 8001, 8001, 8002 ], 
        "server": "192.168.1.1"
    }
}
```

### Testing
Use `tests/test.py`

## License
MIT
