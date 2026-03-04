#!/usr/bin/env python3
"""
Spaced Repetition App - Entry point.
"""

import logging

from spaced_repetition import db
from spaced_repetition.app import SpacedRepetitionApp

logging.basicConfig(level=logging.INFO)


def main():
    db.init_db()
    app = SpacedRepetitionApp()
    app.mainloop()


if __name__ == "__main__":
    main()
