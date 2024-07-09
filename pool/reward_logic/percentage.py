from decimal import Decimal
from utils.layout import base
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)


def round_up_decimal_new(decimal: Decimal, round_up_length: str = "0.00000001"):
    round_up_length = Decimal(round_up_length)
    decimal = decimal.quantize(round_up_length)
    return decimal


def percentage_match():
    try:
        fee_key = base["AWARD_SYSTEM"]["FEE"]
        reward_key = base["AWARD_SYSTEM"]["MINER_REWARD"]

        # Convert the percentage strings to Decimal after removing the '%' sign
        fee_percentage = Decimal(fee_key.strip("%"))
        reward_percentage = Decimal(reward_key.strip("%"))

        # Validate that the total percentage is 100%
        total_percentage = fee_percentage + reward_percentage
        if total_percentage != Decimal("100"):
            return False
        return True

    except KeyError as e:
        logging.error(f"Key not found: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return False


def calculate_percentages(total_amount):
    total_amount = Decimal(total_amount)

    fee_key = base["AWARD_SYSTEM"]["FEE"]
    reward_key = base["AWARD_SYSTEM"]["MINER_REWARD"]

    fee_percentage = Decimal(fee_key.strip("%"))
    reward_percentage = Decimal(reward_key.strip("%"))

    # Validate that the total percentage is 100%
    total_percentage = fee_percentage + reward_percentage
    if total_percentage != Decimal("100"):
        return False

    fee_percentage /= Decimal("100")
    reward_percentage /= Decimal("100")

    percentages = {"18%": 0, "82%": 0}
    percentages["18%"] = round_up_decimal_new(total_amount * fee_percentage)
    percentages["82%"] = round_up_decimal_new(total_amount * reward_percentage)

    return percentages
