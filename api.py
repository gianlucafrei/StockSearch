from flask import Flask
from flask import send_from_directory
from flask import render_template
from flask import request
from flask import jsonify
from flask import Response
import simplejson as json
import database
import parser
import decimal
import engine as eg
import sys
import traceback
import logging.config
import modgrammar
import datetime

"""
    author: Gian-Luca Frei & Fedor Gamper
    date: 30.05.2018
    project: Stocksearch

    This is the api that response to http request whith the found results of the database.
"""

app = Flask(__name__, static_folder=None)

def json(obj, status_code=200):
    json_text = obj.jsonify()
    r = Response(response=json_text, status=status_code, mimetype="application/json")
    return r

def rewrite_path(path):
    """
    >>> rewrite_path('/static/main.js')
    'static/main.js'

    >>> rewrite_path('site/meetings')
    'site/meetings/index.html'

    >>> rewrite_path('/site/meetings/')
    'site/meetings/index.html'
    """
    if path[0]!='/': path = '/' + path
    index_last_slash = path.rfind('/')
    last_part = path[index_last_slash:]
    if '.' in last_part:
        return path[1:]
    
    if path[-1] != '/': path += '/'
    return path[1:] + 'index.html'

@app.route('/static/', defaults={'path': ''})
@app.route('/static/<path:path>')
def static(path):
    path = rewrite_path(path)
    return send_from_directory('static', path)

# Here we serve the main index page
@app.route("/")
def index():
    ssql = request.args.get('q')

    if ssql is not None:
        return query(ssql)

    return render_template("index.html")

@app.route("/autocomplete/<ssql>")
def autocomplete(ssql):
    try:
        stmt = parser.parseStmt(ssql)
        return jsonify(True)

    except modgrammar.ParseError as ex: 

        def trim(s):
            try:
                s = str(s)
                start = s.index("'")
                s = s[start+1:]
                end = s.index("'")
                return s[:end]
            except Exception:
                return None

        trimmed = [trim(s) for s in ex.expected]
        res = filter(lambda x: x is not None, trimmed)

        return jsonify(list(res))

#localhost:5000/tryit?q=sbjasbd
@app.route("/tryit")
@app.route("/tryit/")
def tryit():
    ssql = request.args.get('q')
    return render_template('index.html', tryit=ssql)

def query(ssql):
    sql = None
    warnings = None
    exec_result = None

    try:
        stmt = parser.parseStmt(ssql)

    except modgrammar.ParseError as ex:
        result = eg.ErrorResult()
        result.ssql = ssql
        result.error = str(ex)
        return json(result, 400) # Bad Request

    try:
        db_file_path = app.config['db-connection-file']
        connection = database.get_connecction(db_file_path)
        result = stmt.execute(connection)
        result.ssql = ssql

        if result.success:
            return json(result, 200) # Success
        else:
            # Here the execute method returned a error result
            return json(result, 500) # Internal Error

    except Exception as ex:
        # This should not happen and means the statment execute method
        # has raised an exception
        # (normaly the statement should return a error result instead)
        # DEBUG
        result = eg.ErrorResult()
        result.type = "uncatched"
        result.ssql = ssql
        result.error = str(ex)
        return json(result, 500) # Internal Error
        


# For debugging we just add no-cache to all requests.
@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

if __name__ == "__main__":
    import doctest
    doctest.testmod()