from turtlewar import app, mongo
import random
from turtlewar.model import Drawing, current_generation
from flask import render_template, redirect


def get_random_drawing():
    current_gen = current_generation()
    count = mongo.db.drawings.count(
        {'generation': current_gen}
    )
    r = random.randint(0, count-1)
    drawing = mongo.db.drawings.find(
        {'generation': current_gen}
    ).limit(-1).skip(r).next()
    mongo.db.drawings.update_one(
        {'_id': drawing['_id']},
        {'$inc': {'battles': 1}}
    )
    return drawing


@app.route('/')
def index():
    d1 = get_random_drawing()
    d2 = get_random_drawing()
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
        {'_id': winner},
        {'$inc': {'wins': 1}}
    )
    mongo.db.drawings.update_one(
        {'_id': loser},
        {'$inc': {'losses': 1}}
    )
    return redirect('/')
