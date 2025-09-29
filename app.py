from __future__ import annotations
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QToolBar, QSpinBox
from PySide6.QtGui import QSurfaceFormat, QAction
from src.ui.canvas import GLCanvas


class MainWindow(QMainWindow):
    # inicializa a janela principal com titulo, canvas opengl, barra de ferramentas e mensagens de status
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Preenchimento de Polígonos — Base (PySide6 + OpenGL)")
        self.canvas = GLCanvas(self)
        self.setCentralWidget(self.canvas)
        self._build_toolbar()
        self.statusBar().showMessage(
            "Clique esq.: add vértice • Direito/Enter: fechar • Ctrl+Z: desfazer • Ctrl+L: limpar"
        )

    # constroi a barra de ferramentas com botoes de edicao cor espessura e preenchimento do poligono
    def _build_toolbar(self) -> None:
        tb = QToolBar("Ferramentas", self)
        tb.setMovable(False)
        self.addToolBar(tb)

        # dentro de _build_toolbar(self)
        act_undo = QAction("Desfazer", self, shortcut="Ctrl+Z", triggered=self.canvas.undo)
        act_clear = QAction("Limpar", self, shortcut="Ctrl+L", triggered=self.canvas.clear)
        act_close = QAction("Fechar polígono", self, shortcut="Enter", triggered=self.canvas.close_polygon)

        act_color = QAction("Cor do traço", self, triggered=self.canvas.change_color)
        act_fill_color = QAction("Cor de preenchimento", self, triggered=self.canvas.change_fill_color)  # NOVO

        width_spin = QSpinBox(self)
        width_spin.setRange(1, 12)
        width_spin.setValue(self.canvas.styles.stroke_width)
        width_spin.setToolTip("Espessura do traço")
        width_spin.valueChanged.connect(self.canvas.set_stroke_width)

        tb.addAction(act_undo)
        tb.addAction(act_clear)
        tb.addAction(act_close)
        tb.addSeparator()
        tb.addAction(act_color)
        tb.addAction(act_fill_color)
        tb.addWidget(width_spin)

        tb.addSeparator()
        act_fill = QAction("Preencher (ET/AET)", self, triggered=self.canvas.fill_polygon)
        tb.addAction(act_fill)

# configura o formato padrao da superficie opengl definindo multisample buffer profundidade estencil e double buffer
def configure_default_surface_format(samples: int = 4) -> None:
    fmt = QSurfaceFormat()
    fmt.setSamples(samples)
    fmt.setDepthBufferSize(24)
    fmt.setStencilBufferSize(8)
    fmt.setSwapBehavior(QSurfaceFormat.DoubleBuffer)
    QSurfaceFormat.setDefaultFormat(fmt)


def main():
    configure_default_surface_format(4)
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(1000, 700)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
