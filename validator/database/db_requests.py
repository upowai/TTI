from datetime import datetime, timedelta
from database.mongodb import userStats, entityOwners
from reward_logic.percentage import round_up_decimal_new
from transaction.payment import add_transaction_to_batch

from decimal import Decimal, InvalidOperation


def get_balance_from_wallet(delegate):
    try:
        user = userStats.find_one({"delegate": delegate}, {"balance": 1})
        if user is None:
            return "Error: Wallet address not found."

        balance = user.get("balance")
        if balance is not None:
            return balance
        else:
            return "Error: Balance not found for the given wallet address."
    except Exception as e:
        return f"Error: get_balance_from_wallet An unexpected error occurred - {str(e)}"


def get_balance_entityOwners():
    try:
        # Find the document with the _id "entityOwners"
        entrydata = entityOwners.find_one({"_id": "entityOwners"}, {"amount": 1})

        if entrydata:
            balance = entrydata.get("amount")
            if balance is not None:
                return balance
            else:
                return "Error: Balance not found for the validator."
        else:
            return "Error: Validator data not found."
    except Exception as e:
        return f"Error: get_balance_poolowner An unexpected error occurred - {str(e)}"


def deduct_balance_from_wallet(delegate, amount_to_deduct):
    try:
        # Validate the deduction amount
        try:
            amount_to_deduct = Decimal(str(amount_to_deduct))
            if (
                amount_to_deduct < Decimal("0.001")
                or len(str(amount_to_deduct).split(".")[-1]) > 8
            ):
                return (
                    None,
                    "Error: Invalid deduction amount. Must be at least 0.001 and have no more than 8 decimal places.",
                )
        except InvalidOperation:
            return None, "Error: Invalid deduction amount format."

        # Find the document with the given wallet address
        user = userStats.find_one({"delegate": delegate}, {"balance": 1})

        if user is None:
            return None, "Error: Delegate Wallet address not found."

        balance = Decimal(user.get("balance", 0))
        if balance is None or balance < Decimal("0.001"):
            return None, "Error: Insufficient balance for deduction."

        # Calculate the new balance
        new_balance = balance - amount_to_deduct
        if new_balance < 0:
            return None, "Error: Deduction amount exceeds current balance."

        new_balance = round_up_decimal_new(new_balance)

        # Update the balance in the database
        result = userStats.update_one(
            {"delegate": delegate},
            {"$set": {"balance": float(new_balance)}},
        )

        amount_to_deduct = round_up_decimal_new(amount_to_deduct)

        if result.modified_count == 1:
            add_transaction_to_batch(
                delegate, float(amount_to_deduct), "deduct_user_balance"
            )
            return True, {
                "message": f"Amount deducted successfully: {amount_to_deduct}"
            }
        else:
            return None, "Error: Failed to update the balance."

    except Exception as e:
        return (
            None,
            f"deduct_balance_from_wallet An unexpected error occurred - {str(e)}",
        )


def deduct_balance_from_entityOwners(amount_to_deduct):
    try:
        # Validate the deduction amount
        try:
            amount_to_deduct = Decimal(str(amount_to_deduct))
            if (
                amount_to_deduct < Decimal("0.001")
                or len(str(amount_to_deduct).split(".")[-1]) > 8
            ):
                return (
                    None,
                    "Error: Invalid deduction amount. Must be at least 0.001 and have no more than 8 decimal places.",
                )
        except InvalidOperation:
            return None, "Error: Invalid deduction amount format."

        # Find the pool document
        entry = entityOwners.find_one(
            {"_id": "entityOwners"}, {"amount": 1, "wallet_address": 1}
        )

        if entry is None:
            return None, "Error: validator reward not found."

        balance = Decimal(entry.get("amount", 0))
        if balance is None or balance < Decimal("0.001"):
            return None, "Error: Insufficient balance for deduction."

        # Calculate the new balance
        new_balance = balance - amount_to_deduct
        if new_balance < 0:
            return None, "Error: Deduction amount exceeds current balance."

        new_balance = round_up_decimal_new(new_balance)

        # Update the balance in the database
        result = entityOwners.update_one(
            {"_id": "entityOwners"},
            {
                "$set": {
                    "amount": float(new_balance),
                    "last_processed": datetime.utcnow(),
                }
            },
        )

        amount_to_deduct = round_up_decimal_new(amount_to_deduct)

        if result.modified_count == 1:
            add_transaction_to_batch(
                entry.get("wallet_address"),
                float(amount_to_deduct),
                "deduct_pool_balance",
            )
            return True, {
                "message": f"Amount deducted successfully: {amount_to_deduct}"
            }
        else:
            return None, "Error: Failed to update the pool balance."

    except Exception as e:
        return (
            None,
            f"deduct_balance_from_pool An unexpected error occurred - {str(e)}",
        )
