import requests
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)


def fetch_block(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.HTTPError as errh:
        logging.error(f"Http Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        logging.error(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        logging.error(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        logging.error(f"Oops: Something Else: {err}")
    return None


def test_api_connection(url):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        logging.info(f"Successfully connected to API at {url}")
        return True
    except requests.ConnectionError:
        logging.error(f"Failed to connect to API at {url}. Connection error.")
    except requests.Timeout:
        logging.error(f"Timeout occurred while connecting to API at {url}.")
    except requests.HTTPError as http_err:
        logging.error(
            f"HTTP error occurred while connecting to API at {url}: {http_err}"
        )
    except Exception as e:
        logging.error(
            f"An unexpected error occurred while connecting to API at {url}: {e}"
        )
    return False


def fetch_pools(pools):
    try:
        response = requests.get(pools)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Oops: Something Else", err)
    return None
