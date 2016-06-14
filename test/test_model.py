from turtlewar.model import Drawing, generate_drawing
import pytest
import new
import copy


class TestDrawing:

    def test_drawing_generation_init_default_gen(self):
        d = Drawing([1, 2])
        assert d.generation == 1

    def test_drawing_generation_starts_at_birth_generation(self):
        d = Drawing([1, 2], birth_generation=5)
        assert d.generation == d.birth_generation

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

    def test_survive(self):
        d = Drawing([1, 2, 3, 4], birth_generation=3)
        d.survive()
        assert d.generation == 4

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
            for potential_parent in potential_parents:
                parent_first_half, parent_second_half = (
                    potential_parent.instructions[:half_length],
                    potential_parent.instructions[half_length:]
                )
                if ((first_half == parent_first_half and second_half != parent_second_half) or
                        (first_half != parent_first_half and second_half == parent_second_half)):
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
        iteration_count = 4000
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
