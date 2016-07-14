import sys

def log(string):
    sys.stdout.write("<log>   " + str(string) + "\n")
    sys.stdout.flush()
def error(string, e):
    sys.stderr.write("<ERROR> " + str(string) + "\n")
    sys.stderr.write("============================\n")
    sys.stderr.write(str(e))
    sys.stderr.flush()
    sys.exit(1)
