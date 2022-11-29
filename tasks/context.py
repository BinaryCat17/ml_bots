import os
import sys

DATA_PATH = 'data'

if os.path.basename(os.getcwd()) != 'x_bots':
    os.chdir('../')

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
