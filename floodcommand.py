"""
Root module shim for FloodCommand.
Allows backward compatibility for imports from `floodcommand.X`.
"""

import agents
import data
import utils

__all__ = ["agents", "data", "utils"]
