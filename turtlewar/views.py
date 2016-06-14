from turtlewar import app, mongo
from turtlewar.model import *
import random
from flask import render_template, redirect
import pymongo
from bson.objectid import ObjectId


def render_drawing(drawing):
    return render_template(
        'drawing.html',
        drawing_instructions=drawing.instructions
    )


@app.route('/')
def index():
    generation = current_generation_number()
    d1, d2 = fetch_2_random_drawings()
    return render_template(
        'index.html',
        drawing1=d1,
        drawing2=d2,
        generation=generation
    )


@app.route('/gen/<int:gen_id>/<int:drawing_id>')
def generation_drawing(gen_id, drawing_id):
    drawings = fetch_drawings(gen_id)
    return render_drawing(drawings[drawing_id-1])


@app.route('/drawing/<int:drawing_id>')
def drawing(drawing_id):
    drawings = fetch_drawings()
    return render_drawing(drawings[drawing_id-1])


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
