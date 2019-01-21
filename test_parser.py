import unittest
import pytest
import parser
import engine
import testhelper

"""
    author: Gian-Luca Frei & Fedor Gamper
    date: 30.05.2018
    project: Stocksearch

    Test for the parser
"""

class ConditionTest(unittest.TestCase):
    def test_value_large_than_constant(self):
        ssql = "ALL shares Where value on 2018-01-06 > 100"
        stmt = parser.parseStmt(ssql)
        connection = testhelper.get_connection()
        result = stmt.execute(connection)

class InfRecursionTest(unittest.TestCase):
    """
        Tests if the parser fails in a invinitive recursion while parsing
    """
    def test_recursion1(self):
        ssql = "ALL shares Where (value on 2018-01-06 > 100 or value on 2018-01-06 = 20) and 2<1"
        parser.valid(parser.Statement, ssql)

    def test_recursion2(self):
        ssql = "(value on 2018-01-06 > 100 or value on 2018-01-06 = 20) and 2<1"
        parser.valid(parser.Condition, ssql)

    def test_recursion3(self):
        ssql = "(value on 2018-01-06 > 100 or value on 2018-01-06 = 20)"
        parser.valid(parser.Condition, ssql)

    def test_left_combined1(self):
        ssql = "1>1 and 1>1 and 1>1"
        parser.valid(parser.Condition, ssql)

    def test_left_combined2(self):
        ssql = "1>1 and (1>1 and 1>1)"
    
    def test_left_combined3(self):
        ssql = "(1>1 and 1>1) and 1>1"

        parser.valid(parser.Condition, ssql)

if __name__ == "__main__":
    pytest.main(["test_parser.py"])