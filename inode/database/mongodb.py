from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from utils.layout import base
import logging

logger = logging.getLogger("pymongo")
logger.setLevel(logging.WARNING)


def test_db_connection():
    try:
        client = MongoClient(
            base["MONGOD_DB"]["MONGO_URL"], serverSelectionTimeoutMS=5000
        )

        client.admin.command("ping")
        print("MongoDB connection established successfully.")
        return True
    except ConnectionFailure:
        print("Failed to connect to MongoDB.")
        return False


def get_db_connection():
    client = MongoClient(base["MONGOD_DB"]["MONGO_URL"])
    return client.iNode


# Initialize the connection
db = get_db_connection()


# transaction
tempWithdrawals = db.tempWithdrawals
submittedTransactions = db.submittedTransactions
verifiedTransactions = db.verifiedTransactions
rewardLog = db.rewardLog
entityOwners = db.entityOwners
blockHeight = db.blockHeight
blockTransactions = db.blockTransactions
errorTransactions = db.errorTransactions
catchTransactions = db.catchTransactions

# iNode
validatorsList = db.validatorsList
poolList = db.poolList
minerPool = db.minerPool
