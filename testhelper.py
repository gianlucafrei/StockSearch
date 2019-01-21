import engine
import database
import api

"""
    author: Gian-Luca Frei & Fedor Gamper
    date: 30.05.2018
    project: Stocksearch

    Help methodes for the tests.
"""

mock_connection_file = "secured/postgresmock.json"
connection = database.get_connecction(mock_connection_file)

def get_connection():
    return connection

def get_test_app():
    flask_app = api.app
    flask_app.config['db-connection-file'] = mock_connection_file
    return flask_app.test_client()