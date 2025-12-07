# Hyper Automata

Hyper Automata is a Tkinter desktop app for designing and simulating finite automata. It lets you draw states and transitions, feed multiple words through a breadth-first search runner, and store run history per user in a local SQLite database.

## Features
- **User accounts and persistence:** Register or log in before using the canvas; run histories are saved per user in SQLite via SQLAlchemy.
- **Visual automata builder:** Add states and transitions with toolbar buttons, toggle start/accept markers, and use undo/redo and zoom controls while editing the canvas.
- **Simulation controls:** Run, pause, step, or stop BFS evaluation over multiple input words, with visual highlighting and a live snapshot of the current configuration.
- **Save and reload runs:** Keep snapshots of automata and their histories, then reload them later for review or continued experimentation.
- **Logging:** Application and error logs are written to the `logs/` directory using rotating file handlers.

## Requirements
- Python 3.9+
- Tkinter (bundled with most Python distributions)
- Pillow
- SQLAlchemy

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Running the app
From the project root:

```bash
python main.py
```

1. Use **Register** to create a user or **Login** if you already have one.
2. Use the left toolbar to add states, transitions, and adjust the word count.
3. Enter words in the bottom panel, then use the run controls to simulate acceptance.
4. Save snapshots of interesting runs; reload them from the history icon.

The app creates a local `demo.db` SQLite file by default and writes logs under `logs/`.

## Project structure
- `main.py` – launches the Tkinter interface and wires together the canvas, tools, and run controls.
- `components/` – UI widgets such as the drawing board, login dialog, toolbars, and state/transition helpers.
- `managers/` – coordination logic for building automata and orchestrating BFS runs.
- `backend/` – core automata data structures and algorithms.
- `utils/` – shared constants and logging setup.
- `assets/` – toolbar icons.

## Notes
- The default database URL is `sqlite:///demo.db`; adjust it in `MainApplication` within `main.py` if needed.
- Log files rotate automatically; clear the `logs/` directory if you want to start fresh.
