import random
import pymongo
from turtlewar import app, mongo

commands = [
    "up",
    "down",
    "color",
    "forward",
    "rotate"
]

colors = [
    (0, 0, 0),
    (255, 255, 255),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (0, 255, 255),
    (255, 0, 255),
    (255, 255, 0)
]

generation_size = 10
battles_to_fight = 5
mutation_rate = 0.4

def current_generation():
    with app.app_context():
        return mongo.db.drawings.find().sort([['generation', pymongo.DESCENDING]]).limit(1).next()['generation']


class Drawing(object):
    def __init__(self, instructions, birth_generation=1):
        self.instructions = instructions
        self.wins = 0
        self.losses = 0
        self.battles = 0
        self.birth_generation = birth_generation
        self.generation = self.birth_generation

    def cross(self, other_drawing):
        if self.generation != other_drawing.generation:
            raise ValueError("Drawings must be of the same generation to cross")
        if len(self.instructions) != len(other_drawing.instructions):
            raise ValueError("Can't cross drawings of different lengths")
        half_length = len(self.instructions) / 2
        return Drawing(
            self.instructions[:half_length] + other_drawing.instructions[half_length:],
            birth_generation=self.generation+1
        )

    def survive(self):
        self.generation += 1

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
        generation = sorted(generation, key=lambda drawing: (drawing.fitness() + 1) + random.random(), reverse=True)
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

        for survivor in survivors:
            survivor.survive()

        return survivors + children

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


def generate_drawing(num_instructions=50):
    return Drawing([generate_instruction() for _ in xrange(num_instructions)])


def generate_instruction():
    command = random.choice(commands)
    if command in ('up', 'down'):
        return [command]
    elif command == "color":
        colorid = random.randint(0, len(colors) - 1)
        return [command, colorid]
    elif command == "rotate":
        return [command, random.randint(0, 360)]
    elif command == "forward":
        return [command, random.randint(0, 200)]
