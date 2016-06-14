import random
import pymongo
from turtlewar import app, mongo

commands = (
    "up",
    "down",
    "color",
    "forward",
    "rotate"
)

colors = (
    (0, 0, 0),
    (255, 255, 255),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (0, 255, 255),
    (255, 0, 255),
    (255, 255, 0)
)

generation_size = 20
battles_to_fight = 3
mutation_rate = 0.4


class Drawing(object):

    def __init__(self, instructions, wins=0, losses=0,
                 battles=0, birth_generation=1, generation=None, _id=None):
        self.instructions = instructions
        self.wins = 0
        self.losses = 0
        self.battles = 0
        if generation and generation < birth_generation:
            raise ValueError(
                "Current generation cannot be smaller than birth generation")
        self.birth_generation = birth_generation
        self.generation = generation or self.birth_generation
        if _id is not None:
            self._id = _id

    def cross(self, other_drawing):
        if self.generation != other_drawing.generation:
            raise ValueError(
                "Drawings must be of the same generation to cross")
        if len(self.instructions) != len(other_drawing.instructions):
            raise ValueError("Can't cross drawings of different lengths")
        half_length = len(self.instructions) / 2
        return Drawing(
            self.instructions[:half_length] +
            other_drawing.instructions[half_length:],
            birth_generation=self.generation + 1
        )

    def survive(self):
        return Drawing(
            instructions=self.instructions,
            birth_generation=self.birth_generation,
            generation=self.generation+1
        )

    def mutate(self):
        position = random.randint(0, len(self.instructions) - 1)
        self.instructions[position] = generate_instruction()

    def fitness(self):
        if self.battles == 0:
            return 0
        return float(self.wins - self.losses) / float(self.battles)

    @staticmethod
    def new_generation(generation):
        half_length = len(generation) / 2
        generation = sorted(generation, key=lambda drawing: (
            drawing.fitness() + 1) + random.random(), reverse=True)
        survivors = generation[:half_length]
        child_count = len(generation) - half_length
        children = []
        for i in xrange(child_count):
            parent1 = random.choice(survivors)
            parent2 = random.choice(survivors)
            child = parent1.cross(parent2)
            if random.random() < mutation_rate:
                child.mutate()
            children.append(child)

        survivors = [s.survive() for s in survivors]

        return survivors + children

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


def fetch_2_random_drawings():
    """
    Fetch 2 random, different drawings from the current generation
    """
    current_gen = current_generation_number()
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
        generate_and_save_new_generation()
        return fetch_2_random_drawings()
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


def current_generation_number():
    with app.app_context():
        return mongo.db.drawings.find().sort(
            [['generation', pymongo.DESCENDING]]).limit(1).next()['generation']


def fetch_drawings(generation_id=None):
    """
    Fetch drawings for a given generation
    If generation_id is unspecified defaults to the current generation
    """
    gen_id = generation_id or current_generation_number()
    with app.app_context():
        return [
            Drawing(**d) for d in
            mongo.db.drawings.find({'generation': gen_id})
        ]


def generate_and_save_new_generation():
    drawings = fetch_drawings()
    new_drawings = Drawing.new_generation(drawings)
    with app.app_context():
        mongo.db.drawings.insert_many(
            [drawing.__dict__ for drawing in new_drawings])


def generate_drawing(num_instructions=50):
    return Drawing([generate_instruction() for _ in xrange(num_instructions)])


def generate_instruction():
    command = random.choice(commands)
    if command in ('up', 'down'):
        return (command,)
    elif command == "color":
        colorid = random.randint(0, len(colors) - 1)
        return (command, colorid)
    elif command == "rotate":
        return (command, random.randint(0, 360))
    elif command == "forward":
        return (command, random.randint(0, 200))
