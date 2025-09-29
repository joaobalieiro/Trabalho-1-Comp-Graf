from __future__ import annotations
from typing import List

from PySide6.QtCore import Qt, QPointF, QSize
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QMessageBox, QColorDialog
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from src.core.polygon import Styles
from src.core.scanline import scanline_fill_even_odd

# classe que implementa um canvas 2d baseado em qopenglwidget onde o usuario pode adicionar vertices,
# fechar poligonos, alterar cor e espessura do traço e aplicar preenchimento via algoritmo scanline
class GLCanvas(QOpenGLWidget):

    # inicializa o canvas guardando vertices estado de fechamento e preenchimento
    # e configurando estilos e cores iniciais do traço e do preenchimento
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vertices: List[QPointF] = []
        self.closed: bool = False
        self.filled: bool = False
        self.styles = Styles()

        # cor atual de traço/preenchimento espelhando Styles
        self._stroke_qcolor = QColor(self.styles.stroke_r, self.styles.stroke_g,
                                     self.styles.stroke_b, self.styles.stroke_a)
        self._fill_qcolor = QColor(self.styles.fill_r, self.styles.fill_g,
                                   self.styles.fill_b, self.styles.fill_a)

        # melhora nitidez de pontos/linhas
        self.setMouseTracking(True)

    # ciclo do QOpenGLWidget
    def initializeGL(self) -> None:
        # nada especifico: usamos QPainter
        pass

    def resizeGL(self, w: int, h: int) -> None:
        # nada especifico: QPainter ja usa o rect do widget
        pass

    # metodo responsavel por desenhar o canvas: fundo branco, vertices, arestas e preenchimento por scanline
    def paintGL(self) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        # 1) fundo branco
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

        # 2b) desenha arestas (linha aberta ou poligono)
        if n >= 2:
            for i in range(1, n):
                p.drawLine(self.vertices[i - 1], self.vertices[i])
            if self.closed:
                p.drawLine(self.vertices[-1], self.vertices[0])

        # 3) preenchimento (se fechado e marcado para preencher)
        if self.closed and self.filled and n >= 3 and self._fill_qcolor.alpha() > 0:
            p.setPen(self._fill_qcolor)
            spans_by_y = scanline_fill_even_odd(self.vertices)
            # pinta em spans horizontais (x1..x2) para cada y
            for y, spans in spans_by_y.items():
                for x1, x2 in spans:
                    p.drawLine(x1, y, x2, y)

        p.end()

    # interacao do mouse
    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.LeftButton and not self.closed:
            self.vertices.append(QPointF(e.position()))
            self.update()
        elif e.button() == Qt.RightButton:
            self.close_polygon()

    # trata eventos de teclado: enter fecha o poligono e esc limpa o canvas
    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.close_polygon()
        elif e.key() == Qt.Key_Escape:
            self.clear()

    # desfaz a ultima acao removendo o ultimo vertice ou reabrindo o poligono fechado
    def undo(self) -> None:
        if self.closed:
            self.closed = False
            self.filled = False
        elif self.vertices:
            self.vertices.pop()
        self.update()

    # limpa o canvas removendo todos os vertices e resetando estado de fechamento e preenchimento
    def clear(self) -> None:
        self.vertices.clear()
        self.closed = False
        self.filled = False
        self.update()

    # fecha o poligono se houver pelo menos tres vertices caso contrario mostra aviso
    def close_polygon(self) -> None:
        if len(self.vertices) < 3:
            QMessageBox.information(self, "Polígono inválido",
                                    "São necessários pelo menos 3 vértices.")
            return
        self.closed = True
        self.update()

    # preenche o poligono fechado caso contrario exibe aviso para fechar antes
    def fill_polygon(self) -> None:
        if not self.closed:
            QMessageBox.information(self, "Feche o polígono",
                                    "Feche o polígono antes de preencher (botão direito ou Enter).")
            return
        self.filled = True
        self.update()

    # abre dialogo para escolher nova cor do traco e atualiza o estilo e a tela
    def change_color(self) -> None:
        c = QColorDialog.getColor(self._stroke_qcolor, self, "Cor do traço")
        if c.isValid():
            self._stroke_qcolor = c
            self.styles.stroke_r = c.red()
            self.styles.stroke_g = c.green()
            self.styles.stroke_b = c.blue()
            self.styles.stroke_a = c.alpha()
            self.update()

    # abre dialogo para escolher nova cor de preenchimento e atualiza o estilo e a tela
    def change_fill_color(self) -> None:
        c = QColorDialog.getColor(self._fill_qcolor, self, "Cor de preenchimento")
        if c.isValid():
            self._fill_qcolor = c
            self.styles.fill_r = c.red()
            self.styles.fill_g = c.green()
            self.styles.fill_b = c.blue()
            self.styles.fill_a = c.alpha()
            self.update()

    # ajusta a espessura do traco garantindo valor minimo 1 e atualiza a tela
    def set_stroke_width(self, w: int) -> None:
        self.styles.stroke_width = max(1, int(w))
        self.update()

    # sugere o tamanho padrao da janela do canvas
    def sizeHint(self) -> QSize:
        return QSize(900, 600)
