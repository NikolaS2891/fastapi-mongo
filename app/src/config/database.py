import motor.motor_asyncio
import os


client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["DB_URL"])
db = client.myTestDB
Users = db.users
