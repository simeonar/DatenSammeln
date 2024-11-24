import tkinter as tk
from tkinter import ttk, messagebox
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import os


class DataCollectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Datenerfassung")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Hauptcontainer
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # Navigation und Fortschritt
        self.navigation_label = ttk.Label(
            self.main_frame,
            text="",
            font=("Arial", 12, "bold")
        )
        self.navigation_label.grid(row=0, column=0, pady=10, sticky="w")

        # Datenspeicherung
        self.current_option = None
        self.current_frame_index = 0
        self.collected_data = {}

        # Lade Konfiguration
        try:
            with open('frames_config.json', 'r', encoding='utf-8') as file:
                self.config = json.load(file)
            self.show_option_selection()
        except Exception as e:
            messagebox.showerror("Fehler", f"Konfigurationsfehler: {str(e)}")

    def show_option_selection(self):
        """Zeigt die Optionsauswahl an"""
        self.clear_main_frame()

        # Überschrift
        title_label = ttk.Label(
            self.main_frame,
            text="Bitte wählen Sie eine Option:",
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=1, column=0, pady=20)

        # Optionsbuttons erstellen
        for i, option in enumerate(self.config["options"].keys()):
            btn = ttk.Button(
                self.main_frame,
                text=option,
                command=lambda opt=option: self.start_option(opt)
            )
            btn.grid(row=i + 2, column=0, pady=5)

    def start_option(self, option_name):
        """Startet die Datenerfassung für die gewählte Option"""
        self.current_option = option_name
        self.current_frame_index = 0
        self.collected_data[option_name] = {}
        self.show_current_frame()

    def show_current_frame(self):
        """Zeigt den aktuellen Frame an"""
        self.clear_main_frame()

        frames = self.config["options"][self.current_option]["frames"]
        current_frame = frames[self.current_frame_index]

        # Frame-Titel
        title = ttk.Label(
            self.main_frame,
            text=current_frame["name"],
            font=("Arial", 14, "bold")
        )
        title.grid(row=1, column=0, columnspan=2, pady=(0, 10))

        # Frame-Beschreibung
        description = ttk.Label(
            self.main_frame,
            text=current_frame["description"],
            wraplength=600
        )
        description.grid(row=2, column=0, columnspan=2, pady=(0, 20))

        # Speicherung für aktuelle Frame-Daten
        frame_data = {}

        # Steuerelemente erstellen
        for i, control in enumerate(current_frame["controls"]):
            if control["type"] == "checkbox":
                var = tk.BooleanVar()
                chk = ttk.Checkbutton(
                    self.main_frame,
                    text=control["text"],
                    variable=var
                )
                chk.grid(row=i + 3, column=0, sticky="w", pady=5)
                frame_data[control["text"]] = var

            elif control["type"] == "entry":
                ttk.Label(
                    self.main_frame,
                    text=control["text"]
                ).grid(row=i + 3, column=0, sticky="w", pady=5)

                entry = ttk.Entry(self.main_frame, width=40)
                entry.grid(row=i + 3, column=1, sticky="w", pady=5)
                frame_data[control["text"]] = entry

        # Navigation
        nav_frame = ttk.Frame(self.main_frame)
        nav_frame.grid(row=len(current_frame["controls"]) + 4, column=0, columnspan=2, pady=20)

        # Zurück-Button
        if self.current_frame_index > 0:
            ttk.Button(
                nav_frame,
                text="Zurück",
                command=self.previous_frame
            ).grid(row=0, column=0, padx=5)

        # Weiter/Fertig-Button
        is_last_frame = self.current_frame_index == len(frames) - 1
        btn_text = "Fertig" if is_last_frame else "Weiter"
        cmd = self.generate_pdf if is_last_frame else self.next_frame

        ttk.Button(
            nav_frame,
            text=btn_text,
            command=lambda: self.save_and_continue(frame_data, cmd)
        ).grid(row=0, column=1, padx=5)

        # Navigation aktualisieren
        self.update_navigation()

    def save_and_continue(self, frame_data, next_action):
        """Speichert die Daten des aktuellen Frames und führt die nächste Aktion aus"""
        current_frame = self.config["options"][self.current_option]["frames"][self.current_frame_index]

        # Speichere die aktuellen Werte
        saved_data = {}
        for key, widget in frame_data.items():
            if isinstance(widget, tk.BooleanVar):
                saved_data[key] = widget.get()
            elif isinstance(widget, ttk.Entry):
                saved_data[key] = widget.get()

        self.collected_data[self.current_option][current_frame["name"]] = saved_data
        next_action()

    def next_frame(self):
        """Wechselt zum nächsten Frame"""
        self.current_frame_index += 1
        self.show_current_frame()

    def previous_frame(self):
        """Wechselt zum vorherigen Frame"""
        self.current_frame_index -= 1
        self.show_current_frame()

    def clear_main_frame(self):
        """Löscht alle Widgets im Hauptframe"""
        for widget in self.main_frame.winfo_children():
            if widget != self.navigation_label:
                widget.destroy()

    def update_navigation(self):
        """Aktualisiert die Navigationsanzeige"""
        frames = self.config["options"][self.current_option]["frames"]
        self.navigation_label.config(
            text=f"{self.current_option} - Frame {self.current_frame_index + 1} von {len(frames)}"
        )

    def generate_pdf(self):
        """Erstellt die PDF mit allen gesammelten Daten"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Datenerfassung_{timestamp}.pdf"

        c = canvas.Canvas(filename, pagesize=letter)
        y = 750  # Startposition

        for option, frames in self.collected_data.items():
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y, f"Option: {option}")
            y -= 30

            for frame_name, data in frames.items():
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y, f"Frame: {frame_name}")
                y -= 20

                c.setFont("Helvetica", 10)
                for key, value in data.items():
                    if isinstance(value, bool):
                        text = f"{key}: {'Ja' if value else 'Nein'}"
                    else:  # String
                        text = f"{key}: {value}"

                    c.drawString(70, y, text)
                    y -= 20

                y -= 10

                # Neue Seite wenn nötig
                if y < 50:
                    c.showPage()
                    y = 750

        c.save()
        messagebox.showinfo("Erfolg", f"Die Daten wurden in '{filename}' gespeichert.")
        self.show_option_selection()  # Zurück zur Optionsauswahl


if __name__ == "__main__":
    root = tk.Tk()
    app = DataCollectionApp(root)
    root.mainloop()
