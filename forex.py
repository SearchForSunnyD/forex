import requests
import json


class Forex:
    """
    A utility class for currency conversion with exchange rates relative to the United States Dollar (USD).

    This class provides methods for retrieving, processing, and managing currency exchange rates. It uses USD as the reference currency for conversions
    and can also store exchange rates locally to minimize the frequency of API calls.

    Attributes:
        api_key (str): The API key used to access the currency exchange rate data from an external source.
        conv_table (dict): A dictionary containing the latest currency exchange rates or the last successfully retrieved rates from a backup file.
        supported (list): A list of supported currency codes based on the available exchange rates.

    Methods:
        - parse_conv_table: Retrieve and process currency exchange rates, using 'USD' as a reference and local storage.
        - currently_supported: Return a list of supported currency codes.
        - api_dump: Retrieve up-to-date currency exchange rates from an external API.
        - con_to_usd: Convert a value from a specified currency to USD.
        - con_from_usd: Convert a value from USD to a specified currency.
        - converter: Convert a value between currencies using USD as the reference currency, with rounding to two decimal places.
    """

    def __init__(self, api_key="1"):
        self.api_key = api_key
        self.conv_table = self.parse_conv_table()
        self.supported = self.parse_supported()

    def parse_supported(self):
        """Retrieve and process the list of supported currency codes from an external API.

        This method sends a request to an external API to obtain a list of supported currency codes.
        The response includes a dictionary of currency codes and their corresponding names.
        It then filters the supported currency codes based on whether they exist in the exchange rate data.

        Returns:
            dict: A dictionary containing supported currency codes and their names.

        Raises:
            requests.exceptions.RequestException: If there is a problem during the API request.
            json.JSONDecodeError: If there is an issue with decoding the API response.
        """
        try:
            currencies = self.api_supp_dump()
            supported = {
                key: currencies[key] for key in currencies if key in self.conv_table
            }

            # Save successful API pull to json file
            with open("forex_supported_backup.json", "w") as json_file:
                json.dump(supported, json_file)

            return supported
        except:
            print("Error in parsing API data")

        try:
            with open("forex_supported_backup.json", "r") as json_file:
                backup = json.load(json_file)
                return backup
        except:
            print("File not found")

    def parse_conv_table(self):
        """Retrieve, process, and manage currency exchange rates with 'USD' as a reference.

        This method acquires the most recent currency exchange rates, either by making an API request or, in case of API issues,
        loading the most recent data from a local backup file. The retrieved rates are cleaned and organized, with 'USD' set as the
        reference currency and a conversion rate of 1.0. Incase of API downtime, the rates are also saved locally for future use.

        Returns:
            dict: A dictionary containing currency exchange rates, either the latest from the API or the last successfully retrieved
                data from the backup file.

        Raises:
            Exception: If any unforeseen errors occur during the API request, data processing, or file operations.
        """
        try:
            quote = self.api_conv_dump()
            clean = {key[-3:]: quote[key] for key in quote}

            # Add USD as 1.0 reference to all currencies
            clean["USD"] = 1

            # Save successful API pull to json file
            with open("forex_backup.json", "w") as json_file:
                json.dump(clean, json_file)

            return clean
        except:
            print("Error in parsing API data")

        try:
            with open("forex_backup.json", "r") as json_file:
                backup = json.load(json_file)
                return backup
        except:
            print("File not found")

    def api_conv_dump(self):
        """Retrieve up-to-date currency exchange rates from an external API.

        This method sends a request to an external API to obtain the latest currency exchange rates. The response includes a 'quotes' section
        with rates for various currencies relative to the United States Dollar (USD). To reduce the frequency of API calls, retrieved rates
        are stored in the current session.

        Returns:
            dict: A dictionary containing currency exchange rates with USD as the reference currency.

        Raises:
            requests.exceptions.RequestException: If there is a problem during the API request.
            json.JSONDecodeError: If there is an issue with decoding the API response.
        """
        request = requests.get(
            "http://api.exchangerate.host/live", params={"access_key": self.api_key}
        )
        return request.json()["quotes"]

    def api_supp_dump(self):
        """Retrieve a list of supported currency codes from an external API.

        This method sends a request to an external API to obtain a list of supported currency codes.
        The response includes a dictionary of currency codes and their corresponding names.

        Returns:
            dict: A dictionary containing currency codes and their names.

        Raises:
            requests.exceptions.RequestException: If there is a problem during the API request.
            json.JSONDecodeError: If there is an issue with decoding the API response.
        """

        request = requests.get(
            "http://api.exchangerate.host/list", params={"access_key": self.api_key}
        )
        return request.json()["currencies"]

    def con_to_usd(self, val, con_from):
        """Convert a value from a specified currency to USD.

        Args:
            val (float): The value to convert.
            con_from (str): The currency code to convert from.

        Returns:
            float: The converted value in USD.
        """
        return val / self.conv_table[con_from]

    def con_from_usd(self, val, con_to):
        """Convert a value from USD to a specified currency.

        Args:
            val (float): The value to convert from USD.
            con_to (str): The currency code to convert to.

        Returns:
            float: The converted value in the target currency.
        """
        return val * self.conv_table[con_to]

    def converter(self, con_from="USD", con_to="USD", val=0):
        """Convert a value between currencies using USD as the reference currency.

        Args:
            con_from (str): The source currency code.
            con_to (str): The target currency code.
            val (float): The value to convert.

        Returns:
            float: The converted value in the target currency, rounded to a maximum of two decimal places.
        """
        if con_from == con_to:
            result = val
        elif con_from == "USD":
            result = self.con_from_usd(val, con_to)
        elif con_to == "USD":
            result = self.con_to_usd(val, con_from)
        else:
            result = self.con_to_usd(val, con_from) * self.conv_table[con_to]
        return round(float(result), 2)

    def get_symbol(self, code):
        """Get the symbol associated with the code provided.

        Args:
            code (str): The target currency code.

        Returns:
            str: A string format of the associated currency symbol that is UTF-8 readable

        """
        with open("forex_symbols.json", "r", encoding="utf-8") as json_file:
            symbols = json.load(json_file)
        return symbols[code]

    def is_valid(self, val=0):
        """Check the validity of a currency value.

        Args:
            val (float): The value of the currency being converted.

        Returns:
            bool: True if the value is non-negative, otherwise raises a ValueError.

        Raises:
            ValueError: If the provided value is less than 0, indicating an invalid currency value.

        The function checks if the provided 'val' is a non-negative number. If 'val' is less than 0, it raises
        a ValueError with a descriptive error message.
        """
        if val < 0:
            raise ValueError("The value is less than 0. It should be a non-negative number.")
        else:
            return True

    def conv_string(self, con_from="USD", con_to="USD", val=0):
        """Convert a value between currencies and format the result as a string.

        This method converts a value between specified source and target currencies using USD as the reference currency.
        The result is rounded to a maximum of two decimal places and formatted as a string with the target currency symbol.

        Args:
            con_from (str): The source currency code (default is "USD").
            con_to (str): The target currency code (default is "USD").
            val (float): The value to convert (default is 0).

        Returns:
            str: A formatted string that represents the converted value in the target currency, including the currency symbol.

        Example:
            If converting 10 USD to EUR, the result may be formatted as "€8.50".

        """
        return f'{self.get_symbol(con_to)} {"{:.2f}".format(self.converter(con_from, con_to, val))}'
