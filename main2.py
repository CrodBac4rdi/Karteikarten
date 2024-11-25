import pandas as pd
import random
from tkinter import *
from tkinter import filedialog, messagebox
from typing import List, Dict

BACKGROUND_COLOR = "#B1DDC6"

word_list: List[Dict[str, str]] = []


class NewCards:
    def __init__(self):
        self.window1 = Tk()
        self.window1.title("Karteikarten")
        self.window1.config(padx=20, pady=20, bg=BACKGROUND_COLOR)

        # Text-Felder für Vorder- und Rückseite
        self.front_text = Text(height=5, width=40, wrap="word", bd=1)
        self.front_text.insert("1.0", "Hier kommt die Vorderseite hin!")
        self.front_text.bind("<FocusIn>", self.clear_text)
        self.front_text.grid(row=0, column=0, padx=10, pady=10)

        self.back_text = Text(height=5, width=40, wrap="word", bd=1)
        self.back_text.insert("1.0", "Hier kommt die Rückseite hin!")
        self.back_text.bind("<FocusIn>", self.clear_text)
        self.back_text.grid(row=0, column=1, padx=10, pady=10)

        # Entry-Feld für Dateinamen
        self.filename_entry = Entry(bd=1, justify="center", width=40)
        self.filename_entry.insert(0, "Name Des Lernfelds")
        self.filename_entry.bind("<FocusIn>", self.clear_entry)
        self.filename_entry.grid(row=1, column=0, columnspan=2, pady=10)

        # Button zum Hinzufügen von Wörtern
        self.add_button = Button(text="Wort hinzufügen", command=self.add_word_button, width=20)
        self.add_button.grid(row=2, column=0, pady=10, columnspan=2)

        # Button zum Schließen des aktuellen Fensters und Öffnen eines neuen UI
        self.switch_button = Button(text="Auswählen der Lernkarten(CSV-Datei)", command=self.open_file_selection,
                                    width=40)
        self.switch_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Mainloop muss ganz zum Schluss kommen
        self.window1.mainloop()

    def clear_text(self, event):
        """Löscht den Inhalt eines Text-Feldes beim Fokuserhalt."""
        event.widget.delete("1.0", END)

    def clear_entry(self, event):
        """Löscht den Inhalt eines Entry-Feldes beim Fokuserhalt."""
        event.widget.delete(0, END)

    def add_word_button(self):
        """Fügt ein Wort hinzu und speichert/erweitert die CSV-Datei."""
        front = self.front_text.get("1.0", END).strip()
        back = self.back_text.get("1.0", END).strip()
        file_name = self.filename_entry.get()

        # Stelle sicher, dass die Dateiendung .csv hat
        if not file_name.lower().endswith('.csv'):
            file_name += '.csv'

        # Neues Wort zur Liste hinzufügen
        word_list.append({"Vorne": front, "Hinten": back})

        # Versuche, bestehende Datei zu laden und zu erweitern
        try:
            existing_df = pd.read_csv(file_name)
            new_word_df = pd.DataFrame({"Vorne": [front], "Hinten": [back]})
            updated_df = pd.concat([existing_df, new_word_df], ignore_index=True)
        except FileNotFoundError:
            # Wenn Datei nicht existiert, erstelle neue
            updated_df = pd.DataFrame(word_list)

        # Speichere aktualisierte Datei
        updated_df.to_csv(file_name, index=False)
        print(f"Wort hinzugefügt und in '{file_name}' gespeichert.")

        # Felder zurücksetzen
        self.front_text.delete("1.0", END)
        self.front_text.insert("1.0", "Hier kommt die Vorderseite hin!")
        self.back_text.delete("1.0", END)
        self.back_text.insert("1.0", "Hier kommt die Rückseite hin!")

    def open_file_selection(self):
        """Öffnet einen Dateiauswahl-Dialog für CSV-Dateien."""
        file_path = filedialog.askopenfilename(
            title="CSV-Datei für Karteikarten auswählen",
            filetypes=[("CSV Dateien", "*.csv"), ("Alle Dateien", "*.*")]
        )

        if file_path:
            # Überprüfe, ob die Datei gültige Spalten hat
            try:
                df = pd.read_csv(file_path)
                if "Vorne" in df.columns and "Hinten" in df.columns:
                    # Schließe das aktuelle Fenster
                    self.window1.destroy()
                    # Öffne Karteikarten mit der ausgewählten Datei
                    Karteikarten(file_path)
                else:
                    messagebox.showerror("Fehler", "Die CSV-Datei muss 'Vorne' und 'Hinten' Spalten haben.")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Laden der Datei: {str(e)}")


class Karteikarten:
    def __init__(self, csv_path):
        # Initialisierung des Fensters
        self.window = Tk()
        self.window.title("Karteikarten")
        self.window.config(padx=50, pady=50, bg=BACKGROUND_COLOR)

        # Speichere den Pfad der aktuellen Datei
        self.current_file_path = csv_path

        # Setzen einer Instanz für die Karte und ob es die Vorderseite oder Rückseite ist
        self.is_front = True
        self.current_card = None

        # Laden der Wörter
        self.data = pd.read_csv(csv_path)
        self.to_learn = self.data.to_dict(orient="records")

        # Neue Eigenschaft: Tracking für aufeinanderfolgende korrekte Antworten
        self.consecutive_correct = {}

        # Initialize consecutive correct attempts to 0 for all cards
        for card in self.to_learn:
            card_key = (card['Vorne'], card['Hinten'])
            self.consecutive_correct[card_key] = 0

        # Erstellen des Canvas
        self.canvas = Canvas(width=800, height=526)
        self.canvas.grid(row=0, column=0, columnspan=3)

        # Definieren der Bilder
        self.card_front_image = PhotoImage(file="card_front.png")
        self.card_back_image = PhotoImage(file="card_back.png")
        self.right_image = PhotoImage(file="right.png")
        self.wrong_image = PhotoImage(file="wrong.png")

        # Erstellen, Konfigurieren der Buttons
        self.right_button = Button(image=self.right_image, highlightthickness=0, command=self.right_next_card)
        self.right_button.grid(row=1, column=2)
        self.wrong_button = Button(image=self.wrong_image, highlightthickness=0, command=self.wrong_next_card)
        self.wrong_button.grid(row=1, column=0)
        self.flip_button = Button(text="Flip Card", highlightthickness=0, command=self.flip_card)
        self.flip_button.grid(row=1, column=1)

        # Button zum Zurückkehren zum Hauptmenü
        self.back_button = Button(text="Zurück zum Hauptmenü", command=self.back_to_main_menu)
        self.back_button.grid(row=2, column=0, columnspan=3, pady=10)

        # Erste Karte laden
        self.right_next_card()

        # Mainloop des Fensters starten
        self.window.mainloop()

    def back_to_main_menu(self):
        """Schließt das Karteikarten-Fenster und öffnet das Hauptmenü."""
        self.window.destroy()
        NewCards()

    def wrong_next_card(self):
        """Verwaltet Karteikarten-Fortschritt und speichert Karten in verschiedenen CSV-Dateien."""
        if self.current_card:
            base_filename = self.current_file_path.rsplit('.', 1)[0]
            not_learned_filename = f"{base_filename}_noch_nicht_gelernt.csv"

            # Reset consecutive correct attempts when card is marked wrong
            card_key = (self.current_card['Vorne'], self.current_card['Hinten'])
            self.consecutive_correct[card_key] = 0

            # Speichere in nicht gelernt CSV
            try:
                df = pd.read_csv(not_learned_filename)
            except FileNotFoundError:
                df = pd.DataFrame(columns=["Vorne", "Hinten"])

            new_card = pd.DataFrame([self.current_card])
            df = pd.concat([df, new_card], ignore_index=True)
            df.to_csv(not_learned_filename, index=False)

        # Wähle nächste Karte
        if self.to_learn:
            self.current_card = random.choice(self.to_learn)
            self.is_front = True
            self.update_card()
        else:
            # Wenn keine Karten mehr übrig sind
            messagebox.showinfo("Gratulation", "Alle Karten gelernt!")
            self.back_to_main_menu()

    def right_next_card(self):
        """Verwaltet Karteikarten-Fortschritt bei richtiger Antwort."""
        if self.current_card:
            base_filename = self.current_file_path.rsplit('.', 1)[0]
            not_learned_filename = f"{base_filename}_noch_nicht_gelernt.csv"
            learned_filename = f"{base_filename}_gelernt.csv"

            # Create a unique key for the current card
            card_key = (self.current_card['Vorne'], self.current_card['Hinten'])

            # Increment consecutive correct attempts
            self.consecutive_correct[card_key] += 1

            # Check if card has been correctly answered 3 times consecutively
            if self.consecutive_correct[card_key] >= 3:
                # Move to learned list
                try:
                    learned_df = pd.read_csv(learned_filename)
                except FileNotFoundError:
                    learned_df = pd.DataFrame(columns=["Vorne", "Hinten"])

                learned_df = pd.concat([learned_df, pd.DataFrame([self.current_card])], ignore_index=True)
                learned_df.to_csv(learned_filename, index=False)

                # Remove from to_learn list
                self.to_learn = [card for card in self.to_learn if card != self.current_card]

                # Reset consecutive correct count for this card
                self.consecutive_correct[card_key] = 0

            # Lösche aus nicht gelernt, falls vorhanden
            try:
                not_learned_df = pd.read_csv(not_learned_filename)
                not_learned_df = not_learned_df[
                    (not_learned_df['Vorne'] != self.current_card['Vorne']) |
                    (not_learned_df['Hinten'] != self.current_card['Hinten'])
                    ]
                not_learned_df.to_csv(not_learned_filename, index=False)
            except FileNotFoundError:
                pass

        # Wähle nächste Karte
        if self.to_learn:
            self.current_card = random.choice(self.to_learn)
            self.is_front = True
            self.update_card()
        else:
            # Wenn keine Karten mehr übrig sind
            messagebox.showinfo("Gratulation", "Alle Karten gelernt!")
            self.back_to_main_menu()

    def flip_card(self):
        """Dreht die Karte um."""
        self.is_front = not self.is_front  # Wechselt den Status
        self.update_card()

    def update_card(self):
        """Aktualisiert die Karte basierend auf dem Status (Vorder-/Rückseite)."""
        self.canvas.delete('all')  # Löscht alle Elemente auf der Karte

        if self.is_front:
            self.canvas.create_image(400, 263, image=self.card_front_image)
            self.canvas.create_text(400, 150, text="Vorne", font=("Ariel", 40, "italic"))
            self.canvas.create_text(400, 263, text=self.current_card["Vorne"], font=("Ariel", 18, "bold"))
        else:
            self.canvas.create_image(400, 263, image=self.card_back_image)
            self.canvas.create_text(400, 150, text="Hinten", font=("Ariel", 40, "italic"))
            self.canvas.create_text(400, 263, text=self.current_card["Hinten"], font=("Ariel", 18, "bold"))


# Starte die Anwendung
NewCards()