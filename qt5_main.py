import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QPushButton
from PyQt6 import QtGui
from PyQt6.QtCore import Qt

class Kratzomat(QWidget):
    key_up = Qt.Key.Key_Up.value
    key_down = Qt.Key.Key_Down.value
    key_left = Qt.Key.Key_Left.value
    key_right = Qt.Key.Key_Right.value
    key_esc = Qt.Key.Key_Escape.value
    key_return = Qt.Key.Key_Return.value

    def __init__(self, MAPPEN_PRO_KLAUSUR: int = 10, AUFGABEN_PRO_KLASUR: list = ["KURZFRAGEN","A7","A8","A9"], PUNKTE_PRO_AUFGABE: list = [15,10,10,10]):
        super().__init__()
        self.MAPPEN_PRO_KLAUSUR = MAPPEN_PRO_KLAUSUR
        self.AUFGABEN_PRO_KLASUR = AUFGABEN_PRO_KLASUR
        self.PUNKTE_PRO_AUFGABE = PUNKTE_PRO_AUFGABE
        # Sanity check:
        if len(AUFGABEN_PRO_KLASUR) != len(PUNKTE_PRO_AUFGABE):
            print("Eingabe-Fehler")
            return
        self.PREFIX_SPALTEN = 1
        self.SUFFIX_SPALTEN = 1
        self.SUMME_SPALTEN = sum(PUNKTE_PRO_AUFGABE) + self.PREFIX_SPALTEN + len(AUFGABEN_PRO_KLASUR) + self.SUFFIX_SPALTEN
        # 2 Zeilen für Header: Aufgabentitel + Buchstaben bzw. SIGMA + Zeilensumme
        self.PREFIX_ZEILEN = 2
        self.SUFFIX_ZEILEN = 1
        self.SUMME_ZEILEN = self.PREFIX_ZEILEN + MAPPEN_PRO_KLAUSUR + self.SUFFIX_ZEILEN
        # Benötigte Matrizen und Vektoren definieren
        self.positions = [(x, y) for x in range(self.SUMME_ZEILEN) for y in range(self.SUMME_SPALTEN)]  # Alle Positionen im GRID
        self.romans = range(self.PREFIX_ZEILEN, self.PREFIX_ZEILEN + MAPPEN_PRO_KLAUSUR) # Vektor mit Positionen für römische Zahlen
        self.aufgabenpos = self._calcHeaderPositions()
        test = self._calcPointColumns()
        print(f"Aufgabenpos: {self.aufgabenpos}")
        print(f"ZeilenSumme: {self.SUMME_ZEILEN}, Spaltensumme: {self.SUMME_SPALTEN}")
        self.initUI()
        # Übersicht Koordinaten:
        # -> x entspricht SUMME_ZEILEN entspricht positions[1]
        # |
        # v
        # y entspricht SUMME_SPALTEN entspricht positions[0]


    def initUI(self):   
        grid = QGridLayout()  
        self.setLayout(grid)
        
        # Loop über GRID und beschrifte Felder
        for idx, position in enumerate(self.positions):
            # 1. Zeile Clear Button
            if position == (0, 0):
                element = QPushButton("Clear")
                element.clicked.connect(self._clearUI)
            else:   # Alle anderen Instrumente sind QLabel's
                # Labels unterscheiden sich nur im Text:
                # X0,Y1: Mappe, damit roman Zahlen ersichtlich sind
                if position == (1,0):
                    text = "Mappe:"
                # X0,Yend: Text für Spaltensumme
                elif position == (self.SUMME_ZEILEN-1,0): # -1 weil bei 0 gestartet wird
                    text = "Spaltensumme:"
                # Xend,Y0: Text für Zeilensumme
                elif position == (0,self.SUMME_SPALTEN-1):
                    text = "Zeilensumme:"
                # X0,Y-Range: Roman Zahlen für Mappen
                elif position[1] == 0 and position[0] in self.romans:
                    text = self._to_roman_numeral(position[0]-1)
                else:
                    text = f"F{idx},X{position[0]},Y{position[1]}"
                element = QLabel(text)

            grid.addWidget(element, *position)
        self.move(300, 150)
        self.setWindowTitle('Kratzomat 3000')  
        self.show()

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        for widget in self.children():
            if isinstance(widget,QLabel):
                print(f"Widget-Text: {widget.text()} at position x{widget.x()} - y{widget.y()}")
            elif isinstance(widget,QGridLayout):
                pass
        if a0.key() == self.key_up:
            print("Key up pressed")
        elif a0.key() == self.key_down:
            print("Key down pressed")
        elif a0.key() == self.key_left:
            print("Key left pressed")
        elif a0.key() == self.key_right:
            print("Key right pressed")
        elif a0.key() == self.key_esc:
            print("Key escape pressed")
            self.close()    # Funktion beenden, wenn Esc gedrückt wird
        elif a0.key() == self.key_return:
            print("Key return pressed")
        else:           
            print(f"Unknown key pressed, ID: {a0.key()}")
    
    def _clearUI(self) -> None:
        print("_clearUI - Noch nicht programmiert")

    def _to_roman_numeral(self,value):
        roman_map = {                                   # 1
            1: "I", 5: "V",
            10: "X", 50: "L", 
            100: "C", 500: "D",
            1000: "M",
        }
        result = ""
        remainder = value
        for i in sorted(roman_map.keys(), reverse=True):# 2
            if remainder > 0:
                multiplier = i
                roman_digit = roman_map[i]

                times = remainder // multiplier         # 3
                remainder = remainder % multiplier      # 4
                result += roman_digit * times           # 4
        return result
    
    def _calcHeaderPositions(self) -> np.array:
        PUNKTE_PRO_AUFGABE_INKL_SIGMA = [x+1 for x in self.PUNKTE_PRO_AUFGABE] # Spaltenbreite muss um jeweils 1 erhöht werden damit Platz für SIGMA Zeichen ist
        aufgabenpos = np.empty((4,len(self.PUNKTE_PRO_AUFGABE)),int)
        for idx, val in enumerate(self.PUNKTE_PRO_AUFGABE):
            aufgabenpos[idx][1] = self.PREFIX_SPALTEN+sum(PUNKTE_PRO_AUFGABE_INKL_SIGMA[:idx])
            aufgabenpos[idx][3] = val+1
        return aufgabenpos
    

    def _calcPointColumns(self) -> np.array:
        result = np.empty((1,sum(self.PUNKTE_PRO_AUFGABE)),int)
        for r_idx,row in enumerate(zip(self.aufgabenpos,self.PUNKTE_PRO_AUFGABE)):
            for c_idx in range(row[1]):
                index = row[0][1] - r_idx + c_idx - 1
                print(f"index: {index}")
                result[0][index] = row[0][1] + c_idx
        print(f"result: {result}")
        return result

if __name__ == '__main__':
     debug = 0
     if not debug:
        app = QApplication(sys.argv)
        ex = Kratzomat()
        sys.exit(app.exec()) 
     else:
        pass
"""
        layout = self.layout()
        index = layout.indexOf(widget)
        row, column, cols, rows = layout.getItemPosition(index)
        self.itemSelected.emit(widget, pos(row, column))


"""