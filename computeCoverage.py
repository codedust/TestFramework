#!/bin/python
'''
This tool requires coverage.py to be installed. See
https://coverage.readthedocs.org/en/coverage-4.0.3/install.html
for more information.
'''

import coverage
import unittest
import os

if __name__ == '__main__':
    c = coverage.Coverage(
        branch=True,
        source=['.'],
        omit=[
            '*Interface*',
            '*__init__.py',
            'setup.py',
            'start_server.py',
            'computeCoverage.py',
            'tests/*'])

    c.start()

    for root, _, _ in os.walk('tests/'):
        if not ("__pycache__" in root or "htmlcov" in root):
            suite = unittest.TestLoader().discover(root, 'test*')
            unittest.TextTestRunner().run(suite)
    c.stop()
    c.report()
    c.html_report()
