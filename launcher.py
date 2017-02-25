import sys
import web_dashboard.server

# This launcher exists to make it easier when using python 2.X
if __name__ == '__main__':
    web_dashboard.server.main(sys.argv[1:])
