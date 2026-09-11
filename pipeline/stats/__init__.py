"""Reusable analytical functions for the PTIT Academic Insights pipeline.

Each module here is a pure, independently testable statistical building
block. s4_metrics.py composes them into the concrete aggregates shipped to
the frontend; nothing in this package knows about JSON shapes or the site.
"""
