from decimal import Decimal
from reward_logic.reward_log import store_in_db, retrieve_from_db
from reward_logic.percentage import round_up_decimal_new
from database.mongodb import userStats


def update_delegate_balances(amount, sorted_delegates, block_range_str):
    amount = Decimal(amount)
    delegate_updates = {}
    try:
        for delegate_info in sorted_delegates[1]:
            # Debug: Print each delegate_info
            # print("Processing delegate_info:", delegate_info)

            delegate = delegate_info.get("delegate")
            percentage = delegate_info.get("percentage")

            if delegate is None:
                print(f"Delegate information missing in: {delegate_info}")
                continue

            if percentage is None or percentage < 0.00000001:
                print(f"Percentage for delegate {delegate} is too small or missing.")
                continue

            percentage = Decimal(percentage)
            amount_to_add = round_up_decimal_new((amount * percentage) / 100)

            if amount_to_add == 0:
                print(
                    f"Calculated amount for delegate {delegate} is too small to process."
                )
                continue

            # Fetch the current balance from MongoDB
            delegate_record = userStats.find_one({"delegate": delegate})
            if delegate_record:
                current_balance = Decimal(delegate_record["balance"])
                previous_balance = current_balance
                new_balance = current_balance + amount_to_add
            else:
                previous_balance = Decimal("0.0")
                new_balance = amount_to_add

            # Update or insert the delegate balance in MongoDB
            userStats.update_one(
                {"delegate": delegate},
                {"$set": {"balance": float(new_balance)}},
                upsert=True,
            )

            # Update delegate_updates with the necessary information
            delegate_updates[delegate] = {
                "previous_balance": float(previous_balance),
                "added_amount": float(amount_to_add),
                "current_balance": float(new_balance),
            }

        # Store the updates in DB
        store_in_db(f"delegate_{block_range_str}", delegate_updates)
        retrieve_from_db(f"delegate_{block_range_str}")

        print("Delegate balances updated successfully.")
    except Exception as e:
        print(f"update_delegate_balances An error occurred: {e}")
