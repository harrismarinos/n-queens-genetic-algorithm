import pygad
import random

def run_ga(
    n: int,
    fitness_func,
    pop_size: int = 100,
    num_generations: int = 1000,
    mutation_probability: float = 0.05,
    mutation_type: str = "random",
    crossover_type: str = "single_point",
    parent_selection_type: str = "rws",
    on_generation_callback=None,
) -> dict:

    history: list[dict] = []

    def on_generation(ga: pygad.GA):
        best_sol, best_fit, _ = ga.best_solution()
        gen = ga.generations_completed
        history.append({"generation": gen, "fitness": int(best_fit)})

        if on_generation_callback is not None:
            on_generation_callback(gen, int(best_fit), best_sol)

        if best_fit >= 0:
            return "stop"

    initial_population = [random.sample(range(n), n) for _ in range(pop_size)]

    ga_instance = pygad.GA(
        num_generations=num_generations,
        num_parents_mating=pop_size // 2,
        fitness_func=fitness_func,
        sol_per_pop=pop_size,
        num_genes=n,
        gene_space=list(range(n)),
        parent_selection_type=parent_selection_type,
        keep_parents=pop_size // 2,
        crossover_type=crossover_type,
        mutation_type=mutation_type,
        mutation_probability=mutation_probability,
        gene_type=int,
        initial_population=initial_population,
        on_generation=on_generation,
        allow_duplicate_genes=False,
        init_range_low=0,
        init_range_high=n - 1,
    )

    ga_instance.run()

    solution, fitness, _ = ga_instance.best_solution()
    solution = [int(x) for x in solution]

    return {
        "solution": solution,
        "fitness": int(fitness),
        "generations": ga_instance.generations_completed,
        "history": history,
        "solved": int(fitness) >= 0,
    }