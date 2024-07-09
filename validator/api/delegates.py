import requests
import logging


def fetch_all_delegate_info(api_url, validator, limit=1000):
    all_delegates = []
    offset = 0
    try:
        while True:
            full_url = f"{api_url}/get_delegates_info?validator={validator}&offset={offset}&limit={limit}"
            # print("full_url", full_url)
            response = requests.get(full_url)
            response.raise_for_status()
            data = response.json()
            if not data or len(data) < limit:
                all_delegates.extend(data)
                break
            all_delegates.extend(data)
            offset += limit
        return all_delegates
    except requests.exceptions.HTTPError as errh:
        logging.error(f"Http Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        logging.error(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        logging.error(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        logging.error(f"fetch_all_delegate_info: Something Else: {err}")
    return None


def sort_delegates(delegates_info):
    try:
        if not isinstance(delegates_info, list) or not delegates_info:
            raise ValueError("Invalid or empty delegate information provided.")
        total_token_power = 0
        for delegate in delegates_info:
            if (
                "vote" not in delegate
                or "totalStake" not in delegate
                or not delegate["vote"]
            ):
                raise KeyError(
                    "Missing 'vote' or 'totalStake' in delegate information."
                )
            vote_count = delegate["vote"][0]["vote_count"]
            if not isinstance(vote_count, (int, float)) or not isinstance(
                delegate["totalStake"], (int, float)
            ):
                raise TypeError("Vote count and total stake must be numeric.")
            delegate["token_power"] = (vote_count * delegate["totalStake"]) / 10
            total_token_power += delegate["token_power"]
            for vote in delegate["vote"]:
                if "wallet" in vote:
                    del vote["wallet"]

        if total_token_power == 0:
            raise ValueError("Total token power is zero, cannot calculate percentages.")

        for delegate in delegates_info:
            delegate["percentage"] = round(
                (delegate["token_power"] / total_token_power) * 100, 8
            )

        sorted_delegates = sorted(
            delegates_info, key=lambda x: x["token_power"], reverse=True
        )
        return True, sorted_delegates
    except ValueError as ve:
        return False, str(ve)
    except KeyError as ke:
        return False, str(ke)
    except TypeError as te:
        return False, str(te)
    except Exception as e:
        return False, f"sort_delegates An unexpected error occurred: {str(e)}"
