from werkzeug.debug import DebuggedApplication
from werkzeug.serving import run_simple
import os
import sys
from api import app

"""
    author: Gian-Luca Frei & Fedor Gamper
    date: 30.05.2018
    project: Stocksearch

    This programs runs stocksearch from the command line with
    a self containing server.
"""

def init():
    """
    Builds the documentation and runs the tests
    """
    print("[Build docs]")
    os.system("mkdocs build")

    print("[Run pytest]")
    os.system("pytest --doctest-modules --html=static/tests/index.html --cov --cov-report html:static/coverage --cov-config .coveragerc")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Stocksearch command line runner')
    parser.add_argument('-ho', '--host', default='127.0.0.1', help="<host> The host to listen to default 127.0.0.1")
    parser.add_argument('-p', '--port', default=5000, help="<port> The port to listen default 5000")
    parser.add_argument('-d', '--debug', action='store_true', help="Runs Stocksearch in Debug mode default flase")
    parser.add_argument('-c', '--connection', default="secured/postgres.json", help="The path to the database connection file default secured/postgres.json")
    parser.add_argument('-i','--init', action='store_true', help="Builds the documentation and runs all tests before start")

    args = parser.parse_args()

    if args.init:
        init()

    app.config['db-connection-file'] = args.connection

    if args.debug:
        app.debug = True
        debug_app = DebuggedApplication(app, evalex=True)
        run_simple(args.host, args.port, debug_app)
    else:
        run_simple(args.host, args.port, app)
