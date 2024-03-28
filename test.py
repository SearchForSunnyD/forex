from unittest import TestCase
from app import app
from flask import session
from forex import Forex


class ForexTests(TestCase):
    """A class for testing the Forex class"""

    def setUp(self):
        """Setup initial class to test functionality"""
        self.module = Forex()
        self.key_api = "96c6f66da45b139370b9a8d7305135fe"

    def test_init(self):
        self.assertTrue(self.module.api_key)
        self.assertTrue(self.module.conv_table)
        self.assertTrue(self.module.supported)

    def test_var(self):
        """Verify init creates variables"""
        self.assertIn("USD", self.module.conv_table)
        self.assertIn("USD", self.module.supported)
        self.assertEqual(self.module.api_key, "1")

    def test_symbol(self):
        """Verify symbols are being pulled from the static directory"""
        self.assertEqual(self.module.get_symbol("USD"), "$")
        self.assertEqual(self.module.get_symbol("EUR"), "&euro;")
        self.assertEqual(self.module.get_symbol("BAM"), "KM")
        self.assertEqual(self.module.get_symbol("VUV"), "Vt")

    def test_validity(self):
        """Verify the number validation"""
        self.assertTrue(self.module.is_valid(1))
        self.assertTrue(self.module.is_valid(1.1))
        with self.assertRaises(ValueError):
            self.module.is_valid(-1)
            self.module.is_valid(-1.1)

    def test_conversions(self):
        """Test both converters to verify functionality"""

        # set 'EUR' to a known value for test
        self.module.conv_table["EUR"] = 0.25

        self.assertTrue(isinstance(self.module.converter(), float))
        self.assertEqual(self.module.converter("USD", "USD", 10), 10)
        self.assertEqual(self.module.converter("USD", "EUR", 10), 2.5)
        self.assertEqual(self.module.converter("EUR", "USD", 10), 40)
        self.assertEqual(self.module.converter("EUR", "EUR", 10), 10)

        self.assertEqual(self.module.conv_string("USD", "USD", 10), "$ 10.00")
        self.assertEqual(self.module.conv_string("USD", "EUR", 10), "&euro; 2.50")
        self.assertEqual(self.module.conv_string("EUR", "USD", 10), "$ 40.00")
        self.assertEqual(self.module.conv_string("EUR", "EUR", 10), "&euro; 10.00")


class FlaskTests(TestCase):
    """A class for testing the Flask app"""

    def setUp(self):
        """
        Set up the test environment for Flask.
        Initializes the test client and configures testing mode.
        """
        self.client = app.test_client()
        app.config["TESTING"] = True

    def test_home(self):
        """
        Test the home route of the Flask application.
        Sends a GET request to the home route and checks for specific HTML elements.
        """
        with self.client as client:
            with client.get("/") as response:
                html = response.get_data(as_text=True)
                self.assertEqual(response.status_code, 200)
                self.assertIn("<title>Home</title>", html)
                self.assertIn('<form action="/exhange" id="con-form">', html)

    def test_conv(self):
        """Testing the converter"""
        with self.client as client:
            with client.get(f"/conv?from=USD&to=USD&amount=10") as response:
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data, b"$ 10.00")

    def test_bad_parameters(self):
        """Verify bad response"""
        with self.client as client:
            with client.get("/conv") as response:
                self.assertEqual(response.status_code, 400)
            with client.get("/conv?from=USD&to=USD&amount=-10") as response:
                self.assertRaises(ValueError)
                self.assertEqual(response.status_code, 400)
            with client.get("/conv?from=USD&to=FFF&amount=10") as response:
                self.assertRaises(KeyError)
                self.assertEqual(response.status_code, 400)
            with client.get("/conv?from=FFF&to=USD&amount=10") as response:
                self.assertRaises(KeyError)
                self.assertEqual(response.status_code, 400)
            with client.get("/conv?from=USD&to=USD&amount=frog") as response:
                self.assertRaises(TypeError)
                self.assertEqual(response.status_code, 400)
