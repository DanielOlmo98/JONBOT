import subprocess
import os
import sys

# https://stackoverflow.com/questions/44112399/automatically-restart-a-python-program-if-its-killed
filename = 'main.py'
os.chdir(os.path.dirname(os.path.abspath(__file__)))
try:
    while True:
        """However, you should be careful with the '.wait()'"""
        p = subprocess.Popen('python3 ' + filename, shell=True).wait()

        """#if your there is an error from running 'main.py', 
        the while loop will be repeated, 
        otherwise the program will break from the loop"""
        if p != 0:
            continue
        else:
            break
except FileNotFoundError:
    sys.exit("File not found")
