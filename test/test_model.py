from turtlewar.model import Drawing, generate_drawing, generate_color
import pytest
import new
import copy


def test_generate_color():
    for _ in xrange(100):
        color = generate_color()
        assert len(color) == 3
        assert all(0 <= i <= 255 for i in color)


class TestDrawing:

    def test_drawing_generation_init_default_gen(self):
        d = Drawing([1, 2])
        assert d.generation == 1

    def test_drawing_generation_cant_be_smaller_than_birth_generation(self):
        with pytest.raises(ValueError):
            Drawing([1, 2], generation=1, birth_generation=2)

    def test_drawing_generation_starts_at_birth_generation(self):
        d = Drawing([1, 2], birth_generation=5)
        assert d.generation == d.birth_generation

    def test_drawing_generation_can_be_specified_in_constructor(self):
        d = Drawing([1, 2], generation=3, birth_generation=2)
        assert d.generation == 3

    def test_cross(self):
        d1 = Drawing([1, 2, 3, 4])
        d2 = Drawing(['a', 'b', 'c', 'd'])
        expected = Drawing([1, 2, 'c', 'd'], birth_generation=2)
        assert d1.cross(d2) == expected

    def test_cross_different_instruction_lengths(self):
        with pytest.raises(ValueError):
            Drawing([1, 2]).cross(Drawing(['a', 'b', 'c']))

    def test_cross_bigger_size(self):
        d1 = Drawing([1, 2, 3, 4, 5, 6])
        d2 = Drawing(['a', 'b', 'c', 'd', 'e', 'f'])
        expected = Drawing([1, 2, 3, 'd', 'e', 'f'], birth_generation=2)
        assert d1.cross(d2) == expected

    def test_cross_different_generations(self):
        d1 = Drawing([], birth_generation=3)
        d2 = Drawing([], birth_generation=4)
        with pytest.raises(ValueError):
            d1.cross(d2)

    def test_cross_increments_generation(self):
        d1 = Drawing([1, 2, 3, 4], birth_generation=3)
        d2 = Drawing(['a', 'b', 'c', 'd'], birth_generation=3)
        assert d1.cross(d2).generation == 4

    def test_cross_increments_birth_generation(self):
        d1 = Drawing([1, 2, 3, 4], birth_generation=3)
        d2 = Drawing(['a', 'b', 'c', 'd'], birth_generation=3)
        assert d1.cross(d2).birth_generation == 4

    def test_survive_should_increment_generation(self):
        d = Drawing([1, 2, 3, 4], birth_generation=3)
        new_drawing = d.survive()
        assert new_drawing.generation == 4

    def test_survive_should_keep_birth_generation(self):
        d = Drawing([1, 2, 3, 4], birth_generation=3)
        new_drawing = d.survive()
        assert new_drawing.birth_generation == 3

    def test_survive_should_keep_instructions(self):
        d = Drawing([1, 2, 3, 4], birth_generation=3)
        new_drawing = d.survive()
        assert new_drawing.instructions == d.instructions

    def test_survive_should_reset_id_and_battle_counts(self):
        d = Drawing(
            [1, 2, 3, 4], birth_generation=3, _id=5,
            battles=5, wins=3, losses=2)
        new_drawing = d.survive()
        with pytest.raises(AttributeError):
            new_drawing._id
        assert (
            new_drawing.battles == new_drawing.wins == new_drawing.losses == 0)

    def test_mutate(self):
        d = generate_drawing(num_instructions=6)
        original_instructions = d.instructions
        d.mutate()
        mutated_instructions = d.instructions
        changed = 0
        for (i1, i2) in zip(original_instructions, mutated_instructions):
            if i1 != i2:
                changed += 1
        assert changed in (0, 1)

    def test_fitness(self):
        d = generate_drawing()
        d.wins = 14
        d.losses = 4
        d.battles = 20
        assert d.fitness() == 0.5

    def test_fitness_no_battles(self):
        d = generate_drawing()
        assert d.fitness() == 0

    def test_new_generation_same_length(self):
        generation = [generate_drawing() for i in range(11)]
        new_generation = Drawing.new_generation(generation)
        assert len(generation) == len(new_generation)

    def test_new_generation_half_survives(self):
        generation = [generate_drawing() for i in range(11)]
        new_generation = Drawing.new_generation(generation)

        survivor_count = len([
            drawing for drawing in new_generation
            if drawing.birth_generation == 1]
        )
        assert survivor_count == len(generation) / 2

    def test_new_generation_half_new(self):
        generation = [generate_drawing() for i in range(11)]
        new_generation = Drawing.new_generation(generation)

        new_count = len([
            drawing for drawing in new_generation
            if drawing.birth_generation == 2
        ])
        assert new_count == len(generation) - len(generation) / 2

    def test_new_generation_is_previous_gen_plus_one(self):
        generation = [generate_drawing() for i in range(11)]
        new_generation = Drawing.new_generation(generation)

        assert all(d.generation == 2 for d in new_generation)

    def test_new_generation_comes_from_parents(self):
        def is_child(child, potential_parents):
            half_length = len(child.instructions) / 2
            first_half, second_half = (
                child.instructions[:half_length],
                child.instructions[half_length:]
            )
            parent_first_halves = [
                p.instructions[:half_length] for p in potential_parents]
            parent_second_halves = [
                p.instructions[half_length:] for p in potential_parents]
            # Look for an identical half, and another half which is either
            # identical, or has just 1 element different.
            if first_half in parent_first_halves:
                for parent_second_half in parent_second_halves:
                    if len(set(second_half) - set(parent_second_half)) <= 1:
                        return True
            elif second_half in parent_second_halves:
                for parent_first_half in parent_first_halves:
                    if len(set(first_half) - set(parent_first_half)) <= 1:
                        return True
            return False

        generation = [generate_drawing() for i in range(11)]
        new_generation = Drawing.new_generation(generation)

        children = [
            drawing for drawing in new_generation
            if drawing.birth_generation == 2
        ]
        parents = [
            drawing for drawing in new_generation
            if drawing.birth_generation == 1
        ]
        assert all(is_child(child, parents) for child in children)

    def test_new_generation_bad_drawings_get_eliminated(self):
        the_worst = Drawing(["down"] * 50)
        the_best = Drawing(["up"] * 50)

        def new_fitness(self):
            up_count = len([i for i in self.instructions if i == 'up'])
            down_count = len([i for i in self.instructions if i == 'down'])
            return float(up_count - down_count) / len(self.instructions)
        generation = []
        for _ in xrange(20):
            generation += [copy.deepcopy(the_best), copy.deepcopy(the_worst)]
        for drawing in generation:
            drawing.fitness = new.instancemethod(new_fitness, drawing, None)
        new_generation = Drawing.new_generation(generation)
        for drawing in new_generation:
            assert new_fitness(drawing) >= .95

    def test_new_generations_converge_towards_better_fitness(self):
        generation = [generate_drawing() for i in range(11)]
        iteration_count = 1500
        new_fitness = lambda self: len(
            [i for i in self.instructions if i == ['up']])
        for drawing in generation:
            drawing.fitness = new.instancemethod(new_fitness, drawing, None)
        initial_best_fitness = max([drawing.fitness()
                                    for drawing in generation])
        for i in xrange(iteration_count):
            for drawing in generation:
                drawing.fitness = new.instancemethod(
                    new_fitness, drawing, None)
            generation = Drawing.new_generation(generation)
        final_best_fitness = max([drawing.fitness() for drawing in generation])
        assert final_best_fitness >= initial_best_fitness
