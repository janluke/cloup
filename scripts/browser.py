import os
import webbrowser
import sys

path = os.path.abspath(sys.argv[1])
print('Opening with browser:', path)
webbrowser.open(path)
