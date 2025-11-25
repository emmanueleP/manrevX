"""
ManRev - Gestione mandati e reversali
"""

from .gui import ManRevGUI
from .generator import generate_documents

__all__ = ['ManRevGUI', 'generate_documents'] 