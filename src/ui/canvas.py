from __future__ import annotations
from typing import List

from PySide6.QtCore import Qt, QPointF, QSize
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QMessageBox, QColorDialog
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from src.core.polygon import Styles
from src.core.scanline import scanline_fill_even_odd


class GLCanvas(QOpenGLWidget):
    """
    Canvas 2D (QOpenGLWidget) com desenho via QPainter.
    - Fundo branco
    - Traço com espessura ajustável (QSpinBox)
    - Preenchimento por scanline (Even-Odd)
    - Mudança de cor do traço e do preenchimento por diálogo
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vertices: List[QPointF] = []
        self.closed: bool = False
        self.filled: bool = False
        self.styles = Styles()  # usa defaults (traço escuro fino, fill azul translúcido)

        # cor atual de traço/preenchimento espelhando Styles
        self._stroke_qcolor = QColor(self.styles.stroke_r, self.styles.stroke_g,
                                     self.styles.stroke_b, self.styles.stroke_a)
        self._fill_qcolor = QColor(self.styles.fill_r, self.styles.fill_g,
                                   self.styles.fill_b, self.styles.fill_a)

        # melhora nitidez de pontos/linhas
        self.setMouseTracking(True)

    # ----------------------------
    # Ciclo do QOpenGLWidget
    # ----------------------------
    def initializeGL(self) -> None:
        # nada específico: usamos QPainter
        pass

    def resizeGL(self, w: int, h: int) -> None:
        # nada específico: QPainter já usa o rect do widget
        pass

    def paintGL(self) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        # 1) FUNDO BRANCO
        p.fillRect(self.rect(), Qt.white)

        n = len(self.vertices)
        if n == 0:
            p.end()
            return

        # 2) Traço (sempre deriva do estado atual / Styles)
        pen = QPen(self._stroke_qcolor, max(1, int(self.styles.stroke_width)),
                   Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(pen)

        # 2a) desenha pontos para feedback
        for v in self.vertices:
            p.drawPoint(v)

        # 2b) desenha arestas (polilinha aberta ou polígono)
        if n >= 2:
            for i in range(1, n):
                p.drawLine(self.vertices[i - 1], self.vertices[i])
            if self.closed:
                p.drawLine(self.vertices[-1], self.vertices[0])

        # 3) Preenchimento (se fechado e marcado para preencher)
        if self.closed and self.filled and n >= 3 and self._fill_qcolor.alpha() > 0:
            p.setPen(self._fill_qcolor)
            spans_by_y = scanline_fill_even_odd(self.vertices)
            # pinta em spans horizontais (x1..x2) para cada y
            for y, spans in spans_by_y.items():
                for x1, x2 in spans:
                    p.drawLine(x1, y, x2, y)

        p.end()

    # ----------------------------
    # Interação
    # ----------------------------
    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.LeftButton and not self.closed:
            self.vertices.append(QPointF(e.position()))
            self.update()
        elif e.button() == Qt.RightButton:
            self.close_polygon()

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.close_polygon()
        elif e.key() == Qt.Key_Escape:
            self.clear()

    # ----------------------------
    # Comandos acionados pela toolbar
    # ----------------------------
    def undo(self) -> None:
        if self.closed:
            # “desfecha” primeiro
            self.closed = False
            self.filled = False
        elif self.vertices:
            self.vertices.pop()
        self.update()

    def clear(self) -> None:
        self.vertices.clear()
        self.closed = False
        self.filled = False
        self.update()

    def close_polygon(self) -> None:
        if len(self.vertices) < 3:
            QMessageBox.information(self, "Polígono inválido",
                                    "São necessários pelo menos 3 vértices.")
            return
        self.closed = True
        self.update()

    def fill_polygon(self) -> None:
        if not self.closed:
            QMessageBox.information(self, "Feche o polígono",
                                    "Feche o polígono antes de preencher (botão direito ou Enter).")
            return
        self.filled = True
        self.update()

    # ---------- cores ----------
    def change_color(self) -> None:
        """Muda a cor do traço."""
        c = QColorDialog.getColor(self._stroke_qcolor, self, "Cor do traço")
        if c.isValid():
            self._stroke_qcolor = c
            self.styles.stroke_r = c.red()
            self.styles.stroke_g = c.green()
            self.styles.stroke_b = c.blue()
            self.styles.stroke_a = c.alpha()
            self.update()

    def change_fill_color(self) -> None:
        """Muda a cor do preenchimento."""
        c = QColorDialog.getColor(self._fill_qcolor, self, "Cor de preenchimento")
        if c.isValid():
            self._fill_qcolor = c
            self.styles.fill_r = c.red()
            self.styles.fill_g = c.green()
            self.styles.fill_b = c.blue()
            self.styles.fill_a = c.alpha()
            self.update()

    # ---------- espessura ----------
    def set_stroke_width(self, w: int) -> None:
        self.styles.stroke_width = max(1, int(w))
        self.update()

    # ---------- util ----------
    def sizeHint(self) -> QSize:
        return QSize(900, 600)
