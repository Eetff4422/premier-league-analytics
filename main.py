"""
Entry point — launches the Dash development server.

Run with:
    python main.py
"""

from src.presentation.app import create_app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="127.0.0.1", port=8050)
