
from os.path import dirname, abspath, join

from tomlpython import parse, toJSON

DIR = dirname(abspath(__file__))

A = """
a = [1, 2, 3]
"""

B = """
a = [1, 2,
  3]
"""

print(parse(A))
print(parse(B))

print(toJSON(open(join(DIR, "test2.toml")), indent=4))
print(toJSON(open(join(DIR, "hard_example.toml")), indent=4))
