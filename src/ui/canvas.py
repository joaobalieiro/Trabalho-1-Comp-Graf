from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

from PySide6.QtCore import Qt, QPointF, QSize
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from src.core.polygon import Styles
# no futuro: from src.core.scanline import scanline_fill_even_odd


class GLCanvas(QOpenGLWidget):
    """
    Canvas 2D baseado em OpenGL com renderização via QPainter.
    """
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.vertices: List[QPointF] = []
        self.hover: Optional[QPointF] = None
        self.closed: bool = False
        self.styles = Styles()
        self._bg = QColor(255, 255, 255)

    # ---- OpenGL lifecycle ----
    def initializeGL(self) -> None:
        self.makeCurrent()
        self._apply_msaa(True)

    def resizeGL(self, w: int, h: int) -> None:
        pass

    def paintGL(self) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.fillRect(self.rect(), self._bg)

        # contorno
        pen = QPen(QColor(self.styles.stroke_r, self.styles.stroke_g, self.styles.stroke_b, self.styles.stroke_a),
                   self.styles.stroke_width)
        painter.setPen(pen)

        n = len(self.vertices)
        for i in range(1, n):
            painter.drawLine(self.vertices[i - 1], self.vertices[i])

        if self.closed and n >= 2:
            painter.drawLine(self.vertices[-1], self.vertices[0])

        # (placeholder) quando o ET/AET estiver pronto, preencher aqui.
        # Example:
        # if self.closed and n >= 3:
        #     spans_by_y = scanline_fill_even_odd(self.vertices)
        #     fill_color = QColor(self.styles.fill_r, self.styles.fill_g, self.styles.fill_b, self.styles.fill_a)
        #     painter.setPen(fill_color)
        #     for y, spans in spans_by_y.items():
        #         for x1, x2 in spans:
        #             painter.drawLine(x1, y, x2, y)

        if not self.closed and self.hover is not None and n >= 1:
            ghost_pen = QPen(QColor(120, 120, 120, 160),
                             max(1, self.styles.stroke_width - 1),
                             Qt.DashLine)
            painter.setPen(ghost_pen)
            painter.drawLine(self.vertices[-1], self.hover)

        painter.end()

    # ---- Interação ----
    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.LeftButton and not self.closed:
            self.vertices.append(QPointF(e.position()))
            self.update()
        elif e.button() == Qt.RightButton:
            self.close_polygon()

    def mouseMoveEvent(self, e: QMouseEvent) -> None:
        self.hover = QPointF(e.position())
        self.update()

    def keyPressEvent(self, e) -> None:
        if e.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.close_polygon()
        elif e.key() == Qt.Key_Escape:
            self.clear()

    # ---- Ações ----
    def clear(self) -> None:
        self.vertices.clear()
        self.hover = None
        self.closed = False
        self.update()

    def undo(self) -> None:
        if self.closed:
            self.closed = False
        elif self.vertices:
            self.vertices.pop()
        self.update()

    def close_polygon(self) -> None:
        if self.closed:
            return
        if len(self.vertices) < 3:
            QMessageBox.information(self, "Aviso", "Precisa de pelo menos 3 vértices para fechar o polígono.")
            return
        unique = {(p.x(), p.y()) for p in self.vertices}
        if len(unique) < 3:
            QMessageBox.warning(self, "Polígono degenerado", "Existem vértices repetidos demais.")
            return
        self.closed = True
        self.update()

    # ---- Estilo ----
    def set_stroke_color(self, color: QColor) -> None:
        self.styles.stroke_r = color.red()
        self.styles.stroke_g = color.green()
        self.styles.stroke_b = color.blue()
        self.styles.stroke_a = color.alpha()
        self.update()

    def set_stroke_width(self, w: int) -> None:
        self.styles.stroke_width = max(1, int(w))
        self.update()

    # ---- Util ----
    def sizeHint(self) -> QSize:
        return QSize(900, 600)

    def _apply_msaa(self, enabled: bool) -> None:
        fmt = self.format()
        fmt.setSamples(4 if enabled else 0)
        self.setFormat(fmt)
