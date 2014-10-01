import os
import sys
root = os.path.abspath(__file__)
while not os.path.exists(os.path.join(root, 'IMU.py')):
    root = os.path.dirname(root)
sys.path.insert(0, root)
