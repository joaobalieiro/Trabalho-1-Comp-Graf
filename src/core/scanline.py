from __future__ import annotations
from typing import Dict, List, Tuple
from PySide6.QtCore import QPointF

Span = Tuple[int, int]
SpansByY = Dict[int, List[Span]]

def scanline_fill_even_odd(vertices: List[QPointF]) -> SpansByY:
    """
    Retorna dicionário { y_int : [(x1,x2), (x3,x4), ...] } com spans por linha.
    TODO: implementar ET/AET de verdade. Esta função é só um placeholder.
    """
    return {}
