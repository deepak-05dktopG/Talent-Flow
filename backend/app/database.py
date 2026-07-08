from motor.motor_asyncio import AsyncIOMotorClient
from app import config

# Clean, Native Motor Client
client = AsyncIOMotorClient(config.MONGO_URI, tlsAllowInvalidCertificates=True)
db = client[config.DB_NAME]

print("--- SERVICE STATUS LOG ---")
print("MongoDB: AsyncIOMotorClient initialized (tlsAllowInvalidCertificates=True)")

# Collections
users_collection = db["users"]
companies_collection = db["companies"]
jobs_collection = db["jobs"]
candidates_collection = db["candidates"]
applications_collection = db["applications"]
interviews_collection = db["interviews"]
notifications_collection = db["notifications"]
