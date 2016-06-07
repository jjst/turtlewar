import random

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


class Drawing(object):
    def __init__(self, instructions):
        self.instructions = instructions


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
