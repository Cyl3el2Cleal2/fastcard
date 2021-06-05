import motor.motor_asyncio
import os
from bson.objectid import ObjectId

DB_URL = os.getenv("MONGODB_URL") or 'mongodb://game:game@localhost:27017/game'

client = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)

database = client.game_db

game_collection = database.get_collection("game")


# helpers


def game_helper(game) -> dict:
    return {
        "id": str(game["_id"]),
        "fullname": game["fullname"],
        "email": game["email"],
        "course_of_study": game["course_of_study"],
        "year": game["year"],
        "GPA": game["gpa"],
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
    game = await game_collection.find_one({"_id": ObjectId(id)})
    if game:
        return game_helper(game)


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
            return True
        return False


# Delete a game from the database
async def delete_game(id: str):
    game = await game_collection.find_one({"_id": ObjectId(id)})
    if game:
        await game_collection.delete_one({"_id": ObjectId(id)})
        return True