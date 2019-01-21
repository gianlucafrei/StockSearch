import unittest
import pytest
import simplejson as json
import testhelper

"""
    author: Gian-Luca Frei & Fedor Gamper
    date: 30.05.2018
    project: Stocksearch

    Test for the api
"""

class AcceptanceTest(unittest.TestCase):
    """
        Base class for acceptance test to test the web interface of the application.
    """
    def setUp(self):
        """
        Setups the testapplication
        """
        self.app = testhelper.get_test_app()

    def assert_returns_code_200(self, url):
        """
        Tests if a GET-Request on the given url returns a 200 status code
        """
        response = self.app.get(url)
        assert response.status_code == 200

    def get_raw(self, url):
        """
        Makes a GET-Request and returns the reponse as a string
        """
        response = self.app.get(url)
        return response.data.decode('utf8')

    def get_json(self, url):
        """
        Makes a GET-Request and deserialzes the json reponse
        """
        json_str = self.get_raw(url)
        result = json.loads(json_str)
        return result
    
    def query(self, ssql):
        """
        Returns the result of a ssql query by calling the api
        """
        url = f'/?q={ssql}'
        return self.get_json(url)

class StaticResourcesAcceptanceTest(AcceptanceTest):
    def test_static_resources(self):
        """
        Tests if the used static resources are found
        """
        self.assert_returns_code_200('/static/easyMode.js')
        self.assert_returns_code_200('/static/results.js')
        self.assert_returns_code_200('/static/main.js')
        self.assert_returns_code_200('/static/custom.css')

    def test_documentation_reports(self):
        """
        Test if the documentation pages are found
        """
        self.assert_returns_code_200('/static/site/')
        self.assert_returns_code_200('static/site/tests/')
        self.assert_returns_code_200('/static/site/Setup/')

class AutocompleteAcceptanceTestCase(AcceptanceTest):
    """
    Test the autocomplete api
    """
    def test_autocomplete_1(self):
        """
        Test if the app returns the right autocomplete proposal
        """
        res = self.get_json('/autocomplete/all ')
        assert "all shares" in res
        assert "all shares where " in res

    def test_autocomplete_2(self):
        """
        Test if the app returns the right autocomplete proposal for a change term
        """
        res = self.get_json('/autocomplete/all shares where change')
        assert "since" in res
        assert "from" in res

    def test_valid_stmt(self):
        """
        Tests if the api returns true for a correct ssql stmt
        """
        res = self.get_json('/autocomplete/all shares')
        assert res == True

class ReponseErrorCodesTestCase(AcceptanceTest):
    """
    This tests tests if the right http-status codes are returned
    """
    def test_valid_query(self):
        """
        Tests if the response code is OK for a valid ssql statement
        """
        resp = self.app.get('/?q=all shares')
        assert resp.status_code == 200

    def test_invalid_query(self):
        """
        Tests if the response code is BAD_REQUEST for a invalid ssql statement
        """
        resp = self.app.get('/?q=all sharasdasdes')
        assert resp.status_code == 400

class QueryAcceptanceTestCase(AcceptanceTest):
    """
        Test if the query api return the correct results.
    """
    def _test(self, ssql, *args, **kwarg):
        """
            Test if all the args and no more are in the response of the query call
        """
        result = self.query(ssql)
        assert result["type"]=="table"

        result_keys = set()

        for entry in result["data"]:
            result_keys.add(entry["key"])

        expected_results = set(args)
        assert result_keys == expected_results

    def test_all_shares(self):
        self._test('ALL shares',
            "apple", "logi", "micro", "usb")

    def test_condition(self):
        self._test("ALL shares Where value on 2018-01-06 > 100",
            "usb")

    def test_combined_condition(self):
        self._test('ALL shares Where value on 2018-01-06 > 100 or value on 2018-01-06 < 20',
            "usb", "apple", "logi")

    def test_parenthesed_condition(self):
        self._test("ALL shares Where (value on 2018-01-06 > 100 or value on 2018-01-06 = 20) and value < 50",
            "micro")

    def test_parenthesed_condition_false(self):
        self._test("ALL shares Where (value on 2018-01-06 > 100 or value on 2018-01-06 = 20) and 2<1")

    def test_change(self):
        self._test("ALL shares where change from 2018-01-01 to 2018-01-05 > 0",
            "usb", "apple")

    def test_absolute_change(self):
        self._test("ALL shares where absolute change from 2018-01-01 to 2018-01-05 > 10",
            "usb")

    def test_constants(self):
        self._test("ALL shares where 220% = 2.2",
            "apple", "logi", "micro", "usb")

    @pytest.mark.skip(reason="Not yet implemented")
    def test_function_combination(self):
        self._test("All shares where value * change from 2018-01-01 to 2018-01-05 > 0",
            "apple", "ubs")
    
    def test_average(self):
        self._test("All shares where average from 2018-01-01 to 2018-01-05 = 11",
            "apple")
    
    def test_variance1(self):
        self._test("All shares where variance <= 0.013 and variance > 0",
            "apple", "usb")

    def test_variance2(self):
        self._test("All shares where variance <= 0.001",
            "micro")

    def test_longest_grow1(self):
        self._test("All shares where longest grow >= 3",
            "apple", "usb")

    def test_longest_grow2(self):
        self._test("All shares where longest grow = 0",
            "logi", "micro")


class GetDetailsAcceptanceTestCase(AcceptanceTest):
    """
        This test case test if the detail data requests return the correct reponse
    """
    def _test(self, ssql, data , **values):
        result = self.query(ssql)
        assert result["type"] == "detail"

        # Test if all additional attributes are in the result 
        for key, val in values.items():
            assert result[key] == val

        # Test if for every date in the data dictionary the value matches
        res_data = result["data"]
        for date, val in data.items():
            # Search the entry with the same date
            entry_with_same_date = None
            for entry in res_data:
                if entry["date"]== date:
                    entry_with_same_date = entry
                    break
            else:
                raise Exception(f"Entry with date {date} not found in result of query: {ssql}")
            assert entry_with_same_date["value"] == val

    def test_get_detail(self):
        self._test("GET `logi`",
            {
                "2018-01-01": 5.0,
                "2018-01-02": 4.0
            },
            key="logi",
            start="2018-01-01",
            end ="2018-01-02",
            isin="200",
            name="Logitech",
            currency="TST",
            description="Ist konkurs seit 3",
            dataSource="test")

if __name__ == "__main__":
    pytest.main(["test_acceptance.py"])