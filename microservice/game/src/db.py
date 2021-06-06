from motor.motor_asyncio import AsyncIOMotorClient
import os
from bson.objectid import ObjectId
from models import Game

DB_URL = os.getenv("MONGODB_URL", "mongodb://game:game@localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "game_db")

client : AsyncIOMotorClient = None

database = None

game_collection = None


# helpers

async def connect_db():
    try:
        print("Connecting to DB...")
        client = AsyncIOMotorClient(DB_URL)
        database = client[DB_NAME]
        global game_collection
        game_collection = database.get_collection("game")
        await client.admin.command('ping')
        print("DB is connected")
        return client
    except Exception as err:
        raise Exception('Can not connect to Database', err)


def game_helper(game: Game) -> dict:
    return {
        "id": str(game["_id"]),
        "player": str(game["player"]),
        "picked": game["picked"],
        "picked_count": int(game["picked_count"]),
        "last_pick": int(game["last_pick"])
    }

async def retrieve_games():
    games = []
    async for game in game_collection.find():
        games.append(game_helper(game))
    return games


# Add a new game into to the database
async def add_game(game_data: dict) -> dict:
    game = await game_collection.insert_one(game_data)
    new_game = await game_collection.find_one({"_id": game.inserted_id})
    return game_helper(new_game)


# Retrieve a game with a matching ID
async def retrieve_game(id: str) -> dict:
    try:
        game = await game_collection.find_one({"_id": ObjectId(id)})
        if game:
            return game
        return
    except:
        return


# Update a game with a matching ID
async def update_game(id: str, data: dict):
    # Return false if an empty request body is sent.
    if len(data) < 1:
        return False
    game = await game_collection.find_one({"_id": ObjectId(id)})
    if game:
        updated_game = await game_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": data}
        )
        if updated_game:
            return await retrieve_game(id)
        return False


# Delete a game from the database
async def delete_game(id: str):
    game = await game_collection.find_one({"_id": ObjectId(id)})
    if game:
        await game_collection.delete_one({"_id": ObjectId(id)})
        return True

async def find_top_score():
    filter = {"$expr": {"$eq": ["$picked", "$map"]}}
    try:
        result = game_collection.find(filter).sort("picked_count", 1).limit(1)
        if result:
            game = await result.to_list(100)
            return game_helper(game[0])
    except Exception as err:
        print('find error! ' ,err)
        return