
from tomlpython import parse, toJSON

A = """
a = [1, 2, 3]
"""

B = """
a = [1, 2,
  3]
"""

print(parse(A))
print(parse(B))

print(toJSON(open("test2.toml"), indent=4))
