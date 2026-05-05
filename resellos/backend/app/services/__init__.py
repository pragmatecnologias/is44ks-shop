"""Service package for ResellOS.

The individual service modules are imported directly by routes and tests.
Keeping this package lightweight avoids pulling in the database engine when
callers only need a utility module.
"""
