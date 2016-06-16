from pymongo import MongoClient


def clear_db():
    client = MongoClient()
    db = client.turtlewar
    db.drawings.delete_many({})

if __name__ == '__main__':
    clear_db()
