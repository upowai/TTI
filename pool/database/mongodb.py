from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from utils.layout import base
import logging
import gridfs

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
    return client.pooldb


# Initialize the connection
db = get_db_connection()
fs = gridfs.GridFS(db)

# miners system
miners = db.miners
challenges = db.challenges

# transaction
userStats = db.userStats
tempWithdrawals = db.tempWithdrawals
submittedTransactions = db.submittedTransactions
userTxReference = db.userTxReference
verifiedTransactions = db.verifiedTransactions
rewardLog = db.rewardLog
entityOwners = db.entityOwners
blockHeight = db.blockHeight
blockTransactions = db.blockTransactions
errorTransactions = db.errorTransactions
catchTransactions = db.catchTransactions


# task
AiTask = db.AiTask
ResponseTask = db.ResponseTask
ValidationTask = db.ValidationTask
ValidationTaskHistory = db.ValidationTaskHistory


try:
    ResponseTask.create_index([("expireAt", 1)], expireAfterSeconds=0)
    print("TTL index created successfully on ResponseTask collection.")
except Exception as e:
    print(f"An error occurred while creating TTL index: {e}")
