from turtlewar import app, mongo
from turtlewar.model import Drawing, current_generation, battles_to_fight
import random
from flask import render_template, redirect
import pymongo
from bson.objectid import ObjectId


def fetch_2_random_drawings():
    """
    Fetch 2 random, different drawings from the current generation
    """
    current_gen = current_generation()
    drawings = list(mongo.db.drawings.find(
        {'generation': current_gen,
         'battles': {"$lt": battles_to_fight}}
    ))
    # FIXME: this method of selecting 2 drawings doesn't guarantee that we
    # end up selecting drawings in such a way that at the end, some drawing
    # is left alone still needing to fight 2 battles while all others have
    # fought enough, in this case we're stuck because we can't select the
    # drawing to fight against itself.
    # Long-term planned fix is to have the battles pre-generated when
    # creating a new generation
    if len(drawings) < 2:
        raise RuntimeError("Generation has fought enough, they're tired of this shit")
    # Choose 2 different drawings: shuffle the list and take the first two
    random.shuffle(drawings)
    d1, d2 = drawings[0:2]
    # Mark them as battling
    for d in (d1, d2):
        mongo.db.drawings.update_one(
            {'_id': d['_id']},
            {'$inc': {'battles': 1}}
        )
    return d1, d2


@app.route('/')
def index():
    d1, d2 = fetch_2_random_drawings()
    return render_template(
        'index.html',
        drawing1=d1,
        drawing2=d2
    )


@app.route('/drawing/<int:drawing_id>')
def drawing(drawing_id):
    drawings = mongo.db.drawings.find()
    return render_template(
        'drawing.html',
        drawing_instructions=drawings[drawing_id-1]['instructions']
    )


@app.route('/battle/<winner>/<loser>/')
def update_scores(winner, loser):
    mongo.db.drawings.update_one(
        {'_id': ObjectId(winner)},
        {'$inc': {'wins': 1}}
    )
    mongo.db.drawings.update_one(
        {'_id': ObjectId(loser)},
        {'$inc': {'losses': 1}}
    )
    return redirect('/')
