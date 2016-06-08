from turtlewar.model import generation_size, generate_drawing
from pymongo import MongoClient


def populate_db():
    client = MongoClient()
    db = client.turtlewar
    if db.drawings.find_one():
        raise RuntimeError("Database isn't empty, I won't add stuff!")
    drawings = (generate_drawing() for _ in xrange(generation_size))
    db.drawings.insert_many([drawing.__dict__ for drawing in drawings])

if __name__ == '__main__':
    populate_db()
