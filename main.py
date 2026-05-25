import streamlit as st
from ga import count_conflicts, run_ga
import time
import base64
import os

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
            return f"data:image/png;base64,{encoded}"
    return ""

def render_chessboard(solution: list[int], n: int) -> str:
    queen_to_base64 = get_image_base64("./imgs/queen.png")
    red_queen_to_base64 = get_image_base64("./imgs/red_queen.png")
    conflicts = set()
    for i in range(n):
        for j in range(i + 1, n):
            # Diagonal Check
            if abs(solution[i] - solution[j]) == abs(i - j):
                conflicts.add(i)
                conflicts.add(j)
            # Horizontal Check
            if solution[i] == solution[j] and i != j:
                conflicts.add(i)
                conflicts.add(j)

    cell = min(60, 600 // n)
    board_px = n * cell

    rows_html = ""
    for row in range(n):
        cells_html = ""
        for col in range(n):
            bg = "#EAE9D2" if (row + col) % 2 == 0 else "#4B7399"
            queen_html = ""
            if solution[col] == row:
                img = red_queen_to_base64 if col in conflicts else queen_to_base64
                queen_html = (
                    f'<img src="{img}" style="width:{int(cell*0.75)}px;'
                    f'height:{int(cell*0.75)}px;object-fit:contain;" />'
                )
            cells_html += (
                f'<td style="width:{cell}px;height:{cell}px;background:{bg};'
                f'text-align:center;vertical-align:middle;padding:0;">'
                f'{queen_html}</td>'
            )
        rows_html += f"<tr>{cells_html}</tr>"
    return (
    f'<div style="display:flex;justify-content:center;">'
    f'<table class="chess-board" style="border-collapse:collapse;width:{board_px}px;'
    f'height:{board_px}px;table-layout:fixed;">'
    f"{rows_html}</table>"
    f"</div>"
)

st.set_page_config(
    page_title="N-Queens Problem - A Genetic Algorithm",
    page_icon="♛",
    layout="wide",
)
# Title and description
st.markdown(
    """
    <div style="text-align:center;">
        <h1>
            N-Queens Problem
        </h1>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## ♛ Parameters")
    st.markdown("---")

    # Sliders
    n = st.slider("Board size (N)", min_value=4, max_value=20, value=8, step=1)
    pop_size = st.slider("Population size", min_value=20, max_value=500, value=100, step=10)
    max_gen = st.number_input(
        "Max generations", min_value=1000, max_value=1_000_000, value=1000, step=1000
    )
    # Add Mutation Options
    mutation_type = st.selectbox(
        "Mutation type",
        ["random", "swap", "inversion", "scramble"],
        index=0,
    )
    mutation_prob = st.slider(
        "Mutation probability", min_value=0.01, max_value=0.99, value=0.05, step=0.01
    )
    crossover_type = st.selectbox(
        "Crossover type",
        ["single_point", "two_points", "uniform", "scattered"],
        index=0,
    )
    parent_sel = st.selectbox(
        "Parent selection",
        ["tournament", "rank", "rws", "random"],
        index=0,
    )

    st.markdown("---")
    run_btn = st.button("Run GA")

if run_btn:
    
    col1, col2, col3, col4 = st.columns(4)
    m_gen = col1.empty()
    m_fitness = col2.empty()
    m_conflicts = col3.empty()
    m_elapsed = col4.empty()

    # Metric Style
    st.markdown("""
    <style>
    [data-testid="stMetricValue"] {
        text-align: center;
    }
    [data-testid="stMetricLabel"] {
        text-align: center;
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)
    # Init Metrics
    m_gen.metric("Generation", 0)
    m_fitness.metric("Best Fitness", "—")
    m_conflicts.metric("Conflicts", "—")
    m_elapsed.metric("Elapsed", "0.0s")

    # Shared state
    shared = {
        "history": [],
        "start": time.time(),
        "last_ui_update": 0.0,
        "best_fitness": -float("inf"),
        "best_solution": None,
    }

    # Refresh rate in seconds
    UI_THROTTLE = 0.25
    board_placeholder = st.empty()

    def on_gen(gen: int, fitness: int, best_sol):
        now = time.time()
        shared["history"].append({"generation": gen, "fitness": fitness})

        if fitness > shared["best_fitness"]:
            shared["best_fitness"] = fitness
            shared["best_solution"] = [int(x) for x in best_sol]

        if now - shared["last_ui_update"] < UI_THROTTLE:
            return
        shared["last_ui_update"] = now

        elapsed = now - shared["start"]

        global_best_conflicts = count_conflicts(shared["best_solution"])
        m_gen.metric("Generation", f"{gen:,}")
        m_fitness.metric("Best Fitness", int(shared["best_fitness"]))
        m_conflicts.metric("Conflicts", int(global_best_conflicts))
        m_elapsed.metric("Elapsed", f"{elapsed:.1f}s")

        if shared["best_solution"] is not None:
            board_placeholder.markdown(
                render_chessboard(shared["best_solution"], n),
                unsafe_allow_html=True,
            )

    result = run_ga(
        n=n,
        pop_size=pop_size,
        num_generations=int(max_gen),
        mutation_probability=mutation_prob,
        mutation_type=mutation_type,
        crossover_type=crossover_type,
        parent_selection_type=parent_sel,
        on_generation_callback=on_gen,
    )
    # Final Metrics Update
    final_sol = [int(x) for x in result["solution"]]
    final_conflicts = count_conflicts(final_sol)
    elapsed = time.time() - shared["start"]
    m_gen.metric("Generation", f"{len(shared['history']):,}")
    m_fitness.metric("Best Fitness", int(shared["best_fitness"]))
    m_conflicts.metric("Conflicts", int(final_conflicts))
    m_elapsed.metric("Elapsed", f"{elapsed:.1f}s")
    
    st.markdown(
        '<p style="text-align:center;" class="section-title">Best Final Solution</p>',
        unsafe_allow_html=True,
    )
    
    # Make Board border green
    st.markdown("""
    <style>
    .chess-board {
        border: 5px solid #2e7d32 !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    if result["solved"]:
        sol = [int(x) for x in result["solution"]]
        board_placeholder.markdown(
            render_chessboard(sol, n),
            unsafe_allow_html=True,
        )
    else:
        st.warning(
            "No perfect solution found, showing best attempt from history."
        )
        st.markdown("""
        <style>
        .chess-board {
            border: 5px solid #ff0f0f !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        </style>
        """, unsafe_allow_html=True)
        if shared["best_solution"] is not None:
            board_placeholder.markdown(
                render_chessboard(shared["best_solution"], n),
                unsafe_allow_html=True,
            )