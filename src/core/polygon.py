from __future__ import annotations
from dataclasses import dataclass
from typing import List
from PySide6.QtCore import QPointF


@dataclass
class Styles:
    stroke_r: int = 20
    stroke_g: int = 20
    stroke_b: int = 20
    stroke_a: int = 255
    stroke_width: int = 2
    fill_r: int = 60
    fill_g: int = 140
    fill_b: int = 255
    fill_a: int = 160


@dataclass
class Polygon:
    vertices: List[QPointF]
    styles: Styles

    def is_degenerate(self) -> bool:
        # degenerado se < 3 vértices ou muitos repetidos
        if len(self.vertices) < 3:
            return True
        unique = {(p.x(), p.y()) for p in self.vertices}
        return len(unique) < 3
