import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QPushButton
from PyQt6 import QtGui
from PyQt6.QtCore import Qt
import time


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
        self.PUNKTE_SPALTEN = np.arange(0,self.MAPPEN_PRO_KLAUSUR) + self.PREFIX_ZEILEN
        self.positions = [(x, y) for x in range(self.SUMME_ZEILEN) for y in range(self.SUMME_SPALTEN)]  # Alle Positionen im GRID
        self.romans = range(self.PREFIX_ZEILEN, self.PREFIX_ZEILEN + MAPPEN_PRO_KLAUSUR) # Vektor mit Positionen für römische Zahlen
        self.aufgabenpos = self._calcHeaderPositions()
        self.PUNKTE_ZEILEN, self.BUCHSTABEN_ZEILEN = self._calcPointColumns()
        self.PUNKTE_MATRIX = np.tile(self.PUNKTE_ZEILEN,(self.MAPPEN_PRO_KLAUSUR,1))
        self.AUFGABEN_SUMMEN_POSITION = self._calcAufgabenSumPositions()
        self.initUI()
        self.PUNKTE_MATRIX = self._initPUNKTEMATRIX()       #   -> HIER WEITERMACHEN
        # Übersicht Koordinaten:
        # -> x entspricht SUMME_ZEILEN entspricht positions[1]
        # |
        # v
        # y entspricht SUMME_SPALTEN entspricht positions[0]
        self.CUR_ZEILE = 0
        self.CUR_SPALTE = 0
        self._highlightCurCell()

    def initUI(self):   
        self.grid = QGridLayout()  
        self.setLayout(self.grid)
        self._widgets_points = list()
        # Loop über GRID und beschrifte Felder
        for idx, position in enumerate(self.positions):
            # 1. Zeile Clear Button
            row_span = None
            col_span = None
            if position == (0, 0):
                # element = QPushButton("Clear")
                # element.clicked.connect(self._clearUI)
                element = None                              # -> TEMPORÄRER FIX
            else:   # Alle anderen Instrumente sind QLabel's
                # Labels unterscheiden sich nur im Text:
                # X0,Y1: Mappe, damit roman Zahlen ersichtlich sind
                if position == (1,0):
                    text = "Mappe:"
                elif position == (self.SUMME_ZEILEN-1,self.SUMME_SPALTEN-1):
                    text = "SUMMISUM"
                # X0,Yend: Text für Spaltensumme
                elif position == (self.SUMME_ZEILEN-1,0): # -1 weil bei 0 gestartet wird
                    text = "Spalten-" + "\u03A3" + ":"
                # Xend,Y0: Text für Zeilensumme
                elif position == (0,self.SUMME_SPALTEN-1):
                    text = "Zeilen-" + "\u03A3" + ":"
                    row_span = 2
                    col_span = 1
                elif position == (1,self.SUMME_SPALTEN-1):
                    text = None
                # Aufgaben-Überschriften
                elif position[0] == 0 and position[1] in self.aufgabenpos[:,1]:
                    idx = np.where(self.aufgabenpos[:,1] == position[1])
                    idx = idx[0][0]
                    text = self.AUFGABEN_PRO_KLASUR[idx]
                    row_span = 1
                    col_span = self.aufgabenpos[idx,3]
                # Einzel Summen-Aufgaben
                elif position[0] == (self.SUMME_ZEILEN-1) and position[1] in self.aufgabenpos[:,1]:
                    idx = np.where(self.aufgabenpos[:,1] == position[1])
                    idx = idx[0][0]
                    text = "AUFGABEN-" + "\u03A3"
                    row_span = 1
                    col_span = self.aufgabenpos[idx,3]
                # Summenzeichen für Aufgaben hinzufügen
                elif position[0] == 1 and position[1] in self.AUFGABEN_SUMMEN_POSITION:
                    text = "\u03A3"
                # Übrig gebliebene Zeilen entfernen
                elif position[0] == 0:
                    text = None
                elif position[0] == self.SUMME_ZEILEN-1:
                    text = None
                # X0,Y-Range: Roman Zahlen für Mappen
                elif position[1] == 0 and position[0] in self.romans:
                    text = self._to_roman_numeral(position[0]-1)
                # Buchstaben Übersicht
                elif position[0] == 1 and position[1] in self.PUNKTE_ZEILEN:
                    text = self.BUCHSTABEN_ZEILEN[np.where(self.PUNKTE_ZEILEN == position[1])]
                    text = text[0]
                # Punkte-Felder
                elif position[1] in self.PUNKTE_ZEILEN and position[0] in self.romans:
                    text = "-"
                    self._widgets_points.append(position)
                else:
                    text = f"F{idx},X{position[0]},Y{position[1]}"
                if text is not None:
                    element = QLabel(text)
                else:
                    element = None
            if element is not None:
                if (col_span is None) and (row_span is None):
                    self.grid.addWidget(element, *position)
                else:
                    #align = Qt.AlignmentFlag.AlignCenter
                    #align = Qt.AlignmentFlag.AlignRight
                    #align = Qt.AlignmentFlag.AlignLeft
                    align = Qt.AlignmentFlag.AlignVCenter
                    self.grid.addWidget(element, *position,row_span,col_span,align)
        self.move(300, 150)
        self.setWindowTitle('Kratzomat 3000')  
        self.show()

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        for widget in self.children():
            if isinstance(widget,QLabel):
                pass
                #print(f"Widget-Text: {widget.text()} at position x{widget.x()} - y{widget.y()}")
            elif isinstance(widget,QGridLayout):
                pass
        if a0.key() == self.key_up:
            print("Key up pressed")
            self.setPoint(1)
            self.step(1)
        elif a0.key() == self.key_down:
            self.setPoint()
            self.step(1)
            print("Key down pressed")
        elif a0.key() == self.key_left:
            print("Key left pressed")
            self.step(-1)
        elif a0.key() == self.key_right:
            print("Key right pressed")
            self.step(1)
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
        aufgabenpos = np.zeros((4,len(self.PUNKTE_PRO_AUFGABE)),int)
        for idx, val in enumerate(self.PUNKTE_PRO_AUFGABE):
            aufgabenpos[idx][1] = self.PREFIX_SPALTEN+sum(PUNKTE_PRO_AUFGABE_INKL_SIGMA[:idx])
            aufgabenpos[idx][3] = val+1
        return aufgabenpos
    
    def _calcAufgabenSumPositions(self) -> np.array:
        size = len(self.PUNKTE_PRO_AUFGABE)
        aufgabensum = np.zeros([1,size],int)
        for idx in range(size):
            aufgabensum[0][idx] = self.aufgabenpos[:,1][idx] + self.aufgabenpos[:,3][idx] - 1
        #print(f"AufgabenSummenPosition: {aufgabensum}")
        return aufgabensum

    def _calcPointColumns(self) -> np.array:
        size = sum(self.PUNKTE_PRO_AUFGABE)
        point_col = np.zeros((1,size),int)
        point_letters = np.zeros((1,size),str)
        for r_idx,row in enumerate(zip(self.aufgabenpos,self.PUNKTE_PRO_AUFGABE)):
            for c_idx in range(row[1]):
                index = row[0][1] - r_idx + c_idx - 1
                point_col[0][index] = row[0][1] + c_idx
                point_letters[0][index] = chr(65+c_idx)
        return point_col, point_letters

    def step(self,step: int) -> None:
        # Get current position:
        c_r = self.CUR_ZEILE
        c_c = self.CUR_SPALTE
        # Überhang berechnen
        next_c =  c_c + step
        # Positiver Schritt
        if next_c >= self.PUNKTE_ZEILEN.size and c_r < self.MAPPEN_PRO_KLAUSUR-1 and step > 0:
            self.CUR_SPALTE = next_c - self.PUNKTE_ZEILEN.size
            self.CUR_ZEILE += 1
        elif next_c >= 0 and next_c < self.PUNKTE_ZEILEN.size and step > 0:
            self.CUR_SPALTE += step
        elif next_c > 0 and c_r > self.PREFIX_SPALTEN and step < 0:
            self.CUR_SPALTE = next_c
        elif next_c == 0 and step < 0:
            self.CUR_SPALTE = 0
            print("HIER WEITERMACHEN !!!!!!!!!!!!!!")
        else:
            print("Nichts verschoben")
        self._highlightCurCell()
        print(f"CUR_SPALTE: {self.CUR_SPALTE}, CUR_ZEILE: {self.CUR_ZEILE}")
        
    
    def _initPUNKTEMATRIX(self) -> np.empty:
        x = self.PUNKTE_ZEILEN.size
        y = self.MAPPEN_PRO_KLAUSUR
        punktematrix = np.empty([y,x],dtype=QLabel)
        for i_x in range(x):
            for i_y in range(y):
                # Get corresponding rows and colums of point fields
                i_col = self.PUNKTE_ZEILEN[0][i_x]
                i_row = self.PUNKTE_SPALTEN[i_y]
                #print(f"({self.PUNKTE_ZEILEN[0][i_y]},{i_x})")
                punktematrix[i_y][i_x] = self._getLabelfromCoord(i_row,i_col)
        return punktematrix

    def setPoint(self,point: int = 0) -> None:
        widget = self.PUNKTE_MATRIX[self.CUR_ZEILE][self.CUR_SPALTE]
        widget.setText(str(point))

    def _getLabelfromCoord(self,row,col) -> QLabel:
        lay = self.layout()
        widgets = (lay.itemAt(i).widget() for i in range(lay.count()))
        for widget in widgets:
            if isinstance(widget, QLabel):
                row_w, col_w, cols_w, rows_w = lay.getItemPosition(lay.indexOf(widget))
                if row_w == row and col_w == col:
                    return widget
        return None

        
    
    def _highlightCurCell(self):
        for index, widget in np.ndenumerate(self.PUNKTE_MATRIX):
            if index[0] == self.CUR_ZEILE and index[1] == self.CUR_SPALTE:
                widget.setStyleSheet("background-color: lightgreen")
            elif index[0] == self.CUR_ZEILE or index[1] == self.CUR_SPALTE:
                widget.setStyleSheet("background-color: yellow")
            else:
                widget.setStyleSheet("background-color: none")


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