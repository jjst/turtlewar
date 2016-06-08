from turtlewar import app
from turtlewar.model import generate_drawing
from flask import jsonify, render_template


@app.route('/')
def index():
    return render_template(
        'index.html',
        drawing1=generate_drawing(),
        drawing2=generate_drawing()
        )


@app.route('/drawing/')
def drawing():
    return jsonify(generate_drawing().__dict__)
