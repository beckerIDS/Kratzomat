import tkinter as tk

class Kratzomat(tk.Tk):

    def __init__(self, MAPPEN_PRO_KLAUSUR: int = 10, AUFGABEN_PRO_KLASUR: list = ["KURZFRAGEN","A7","A8","A9"], PUNKTE_PRO_AUFGABE: list = [15,10,10,10]) -> None:
        super(Kratzomat,self).__init__()
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
        self.SUFFIX_ZEILEN = 1
        self.SUMME_ZEILEN = 2 + MAPPEN_PRO_KLAUSUR + self.SUFFIX_ZEILEN

        self.FensterAufspannen()
    
    def FensterAufspannen(self) -> None:
        self.fenster = tk.Tk()
        # Fenster mit Objekten füllen
        # 1. Schritt: Header
        topleft_frame = tk.Frame(self.fenster)
        topleft_frame.grid(row=0,column=0)
        cur_spalte = 1
        for idx, aufgabe in enumerate(self.AUFGABEN_PRO_KLASUR):
            breite = self.PUNKTE_PRO_AUFGABE[idx] + 1
            label = tk.Label(self.fenster,text=aufgabe)
            label.grid(row=0,column=cur_spalte,columnspan=breite)
            cur_spalte += breite
        cur_spalte = 1
        for aufgabe in self.PUNKTE_PRO_AUFGABE:
            for punkt in range(aufgabe+1):
                if punkt == aufgabe:
                    text = "\u03A3"
                else:
                    text = chr(65+punkt)
                label = tk.Label(self.fenster,text=text)
                label.grid(row=1,column=cur_spalte)
                cur_spalte += 1
        # 2. Schritt: 1. Spalte mit Klausuren in römischen Zahlen
        cur_reihe = 2
        for reihe in range(self.MAPPEN_PRO_KLAUSUR):
            label = tk.Label(self.fenster,text=self._to_roman_numeral(reihe+1))
            label.grid(row=cur_reihe+reihe,column=0)
        # 3. Zeilensummen (speichern für Zugriff)

        # 4. Spaltensummen (speichern für Zugriff)

        # 5. Summen Summen (speichern für Zugriff)

        # 6. Punktefelder (speichern für Zugriff)

        # 7. Punkte Summen pro Aufgabe (speichern für Zugriff)


        self.fenster.bind("<Button-1>",self._ClickEvent)
        self.fenster.mainloop()

    def _ClickEvent(self, event) -> None:
        print(event)

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

def main() -> None:
    app = Kratzomat()


if __name__ == "__main__":
    main()