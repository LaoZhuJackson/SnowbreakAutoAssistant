# coding: utf-8
from PyQt5.QtCore import QObject, pyqtSignal


class SignalBus(QObject):
    """ Signal bus """

    checkUpdateSig = pyqtSignal(int)
    micaEnableChanged = pyqtSignal(bool)
    switchToSampleCard = pyqtSignal(str, int)
    updatePiecesNum = pyqtSignal(dict)
    jigsawDisplaySignal = pyqtSignal(list)

    # check_ocr_progress = pyqtSignal(int, str)


signalBus = SignalBus()
