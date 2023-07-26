import numpy as np
from qtpy import QtWidgets, QtGui


class QScientificFloatSpinner(QtWidgets.QDoubleSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(-np.inf, np.inf)
        self.setDecimals(100)
        return

    def valueFromText(self, text: str) -> float:
        return float(text)

    def textFromValue(self, val: float) -> str:
        return f"{val:.2e}"

    def validate(self, input_text: str, pos: int):
        try:
            float(input_text)
            return QtGui.QValidator.State.Acceptable, input_text, pos
        except ValueError:
            return QtGui.QValidator.State.Intermediate, input_text, pos


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = QScientificFloatSpinner()
    widget.show()
    sys.exit(app.exec_())
