import unittest
import pytest
import engine
import testhelper

"""
    author: Gian-Luca Frei & Fedor Gamper
    date: 30.05.2018
    project: Stocksearch

    Test for the engine.
"""

class DetailQueryTestCase(unittest.TestCase):
    def test_execute_stmt(self):
        stmt = engine.DetailStatement("logi")
        connection = testhelper.get_connection()
        result = stmt.execute(connection)
        assert result.type == "detail"
        assert result.key == "logi"

class AllStatementTest(unittest.TestCase):
    def test_execute_stmt(self):
        stmt = engine.AllStatement()
        connection = testhelper.get_connection()
        result = stmt.execute(connection)
        assert result.type == "table"

if __name__ == "__main__":
    pytest.main(["test_engine.py"])