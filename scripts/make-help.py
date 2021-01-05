import re
import sys

regex = re.compile(r'^([a-zA-Z_-]+):.*?## (.*)$')

for line in sys.stdin:
    match = regex.match(line)
    if match:
        target, help = match.groups()
        print("%-20s %s" % (target, help))
