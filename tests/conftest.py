"""
conftest.py according to pytest docs:
https://docs.pytest.org/en/2.7.3/plugins.html?highlight=re#conftest-py-plugins
"""
import sys

from os.path import dirname
from os.path import abspath, join

# Adds the src folder to the local path
root_dir = join(dirname(abspath(__file__)), '..', 'src')
sys.path.append(root_dir)
