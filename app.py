from __future__ import annotations
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QToolBar, QColorDialog, QSpinBox
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QSurfaceFormat, QColor, QAction  
from src.ui.canvas import GLCanvas


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Preenchimento de Polígonos — Base (PySide6 + OpenGL)")
        self.canvas = GLCanvas(self)
        self.setCentralWidget(self.canvas)
        self._build_toolbar()
        self.statusBar().showMessage(
            "Clique esq.: add vértice • Direito/Enter: fechar • Ctrl+Z: desfazer • Ctrl+L: limpar"
        )

    def _build_toolbar(self) -> None:
        tb = QToolBar("Ferramentas", self)
        tb.setMovable(False)
        self.addToolBar(tb)

        act_undo = QAction("Desfazer", self, shortcut="Ctrl+Z", triggered=self.canvas.undo)
        act_clear = QAction("Limpar", self, shortcut="Ctrl+L", triggered=self.canvas.clear)
        act_close = QAction("Fechar polígono", self, shortcut="Enter", triggered=self.canvas.close_polygon)
        act_color = QAction("Cor do traço", self, triggered=self.canvas.change_color)

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
        tb.addWidget(width_spin)

        tb.addSeparator()
        act_fill = QAction("Preencher (ET/AET)", self, triggered=self.canvas.fill_polygon)
        tb.addAction(act_fill)

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
    win.setStyleSheet("background-color: " + "#000000" + ";")  
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
