"""Verify invented pebble counts without files, network, or dependencies."""

counts = (2, 3, 5)
assert sum(counts) == 10
print("PASS: synthetic pebble total is 10")
