"""
conftest.py according to pytest docs:
https://docs.pytest.org/en/2.7.3/plugins.html?highlight=re#conftest-py-plugins
"""
import os
import sys

# Adds the src folder to the local path
test_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(test_dir, '..', 'src')
sys.path.append(root_dir)
