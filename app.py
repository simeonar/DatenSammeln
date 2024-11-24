import sys
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

        # Fenstergröße und Position
        window_width = 1024
        window_height = 768
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)

        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.root.minsize(800, 600)

        # Konfiguriere Root für Größenanpassung
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Stil konfigurieren
        self.style = ttk.Style()
        self.style.configure('Main.TFrame', background='#f0f0f0')
        self.style.configure('Header.TLabel',
                             font=('Arial', 14, 'bold'),
                             background='#f0f0f0',
                             padding=10)
        self.style.configure('Navigation.TLabel',
                             font=('Arial', 12),
                             background='#f0f0f0',
                             padding=5)
        self.style.configure('Content.TFrame',
                             background='white',
                             relief='solid')
        self.style.configure('SubFrame.TLabelframe',
                             background='white',
                             padding=10)

        # Hauptcontainer
        self.main_container = ttk.Frame(self.root, style='Main.TFrame')
        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.main_container.grid_rowconfigure(1, weight=1)  # Content-Bereich dehnt sich
        self.main_container.grid_columnconfigure(0, weight=1)

        # Header Frame
        self.header_frame = ttk.Frame(self.main_container, style='Main.TFrame')
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        self.header_frame.grid_columnconfigure(0, weight=1)

        # Navigation Label
        self.navigation_label = ttk.Label(
            self.header_frame,
            text="",
            style='Navigation.TLabel'
        )
        self.navigation_label.grid(row=0, column=0, sticky="w")

        # Content Container mit Scrollbar
        self.content_container = ttk.Frame(self.main_container, style='Main.TFrame')
        self.content_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # Canvas und Scrollbar
        self.canvas = tk.Canvas(self.content_container, background='white')
        self.scrollbar = ttk.Scrollbar(
            self.content_container,
            orient="vertical",
            command=self.canvas.yview
        )
        self.scrollable_frame = ttk.Frame(self.canvas, style='Content.TFrame')

        # Konfiguriere scrollable_frame für Größenanpassung
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Bind für Größenanpassung
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Canvas Fenster erstellen
        self.canvas_frame = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw",
            width=self.content_container.winfo_reqwidth()
        )

        # Canvas Konfiguration
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Canvas Layout
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Bind für Canvas-Größenanpassung
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        self.root.bind('<Configure>', self.on_window_configure)

        # Datenspeicherung
        self.current_option = None
        self.current_frame_index = 0
        self.collected_data = {}
        self.sub_frames = {}

        self.load_config()

    def on_canvas_configure(self, event):
        """Passt die Breite des scrollbaren Frames an"""
        # Minimale Breite setzen
        min_width = 800
        new_width = max(event.width, min_width)
        self.canvas.itemconfig(self.canvas_frame, width=new_width)

    def on_window_configure(self, event):
        """Reagiert auf Fenstergrößenänderungen"""
        if event.widget == self.root:
            # Minimale Verzögerung für bessere Performance
            self.root.after(100, self.update_frame_sizes)

    def update_frame_sizes(self):
        """Aktualisiert die Größen aller Frames"""
        # Berechne verfügbare Breite
        available_width = self.content_container.winfo_width() - self.scrollbar.winfo_width() - 40

        # Aktualisiere Canvas und scrollable_frame
        self.canvas.itemconfig(self.canvas_frame, width=available_width)

        # Aktualisiere alle Unterframes
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                widget.configure(width=available_width)

    def create_sub_frame(self, parent_frame, sub_frame_config, parent_data, row_position):
        """Erstellt einen Sub-Frame für eine Checkbox"""
        sub_frame = ttk.LabelFrame(
            parent_frame,
            text=sub_frame_config["name"],
            style='SubFrame.TLabelframe'
        )
        sub_frame.grid(row=row_position, column=0, columnspan=2,
                       pady=10, padx=20, sticky="ew")

        # Konfiguriere Sub-Frame für Größenanpassung
        sub_frame.grid_columnconfigure(1, weight=1)
        parent_frame.grid_columnconfigure(0, weight=1)

        sub_frame.grid_remove()  # Initial versteckt

        sub_frame_data = {}
        current_row = 0

        # Beschreibung
        if "description" in sub_frame_config:
            desc_label = ttk.Label(
                sub_frame,
                text=sub_frame_config["description"],
                wraplength=600,
                style='Description.TLabel'
            )
            desc_label.grid(row=current_row, column=0, columnspan=2, pady=10, sticky="ew")
            current_row += 1

        # Controls erstellen
        for control in sub_frame_config["controls"]:
            if control["type"] == "checkbox":
                var = tk.BooleanVar()
                chk = ttk.Checkbutton(
                    sub_frame,
                    text=control["text"],
                    variable=var,
                    padding=5
                )
                chk.grid(row=current_row, column=0, columnspan=2, sticky="w", pady=5)
                sub_frame_data[control["text"]] = var

                if "sub_frame" in control:
                    inner_sub_frame, inner_sub_data = self.create_sub_frame(
                        sub_frame,
                        control["sub_frame"],
                        sub_frame_data,
                        current_row + 1
                    )

                    def toggle_inner_frame(frame=inner_sub_frame, var=var):
                        if var.get():
                            frame.grid()
                        else:
                            frame.grid_remove()

                    var.trace_add("write", lambda *args, v=var: toggle_inner_frame())
                    sub_frame_data[f"sub_frame_{control['text']}"] = inner_sub_data
                    current_row += 1

            elif control["type"] == "entry":
                label = ttk.Label(
                    sub_frame,
                    text=control["text"],
                    padding=5
                )
                label.grid(row=current_row, column=0, sticky="w", pady=5)

                entry = ttk.Entry(sub_frame)
                entry.grid(row=current_row, column=1, sticky="ew", padx=(5, 0), pady=5)
                sub_frame_data[control["text"]] = entry

            current_row += 1

        return sub_frame, sub_frame_data

    def show_option_selection(self):
        """Zeigt die Optionsauswahl an"""
        self.clear_frames()

        # Container für den gesamten Inhalt
        content = ttk.Frame(self.scrollable_frame)
        content.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        content.grid_columnconfigure(0, weight=1)

        # Titel
        title_label = ttk.Label(
            content,
            text="Bitte wählen Sie eine Option:",
            style='Header.TLabel'
        )
        title_label.grid(row=0, column=0, pady=20, sticky="w")

        # Button-Container
        button_frame = ttk.Frame(content)
        button_frame.grid(row=1, column=0, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)

        # Optionsbuttons
        for i, option in enumerate(self.config["options"].keys()):
            btn = ttk.Button(
                button_frame,
                text=option,
                command=lambda opt=option: self.start_option(opt),
                padding=10
            )
            btn.grid(row=i, column=0, pady=5, sticky="ew")

    def create_control(self, frame, control, row, frame_data):
        """Erstellt ein einzelnes Kontrollelement"""
        frame.grid_columnconfigure(1, weight=1)  # Spalte mit Eingabefeldern dehnt sich

        if control["type"] == "checkbox":
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(
                frame,
                text=control["text"],
                variable=var,
                padding=5
            )
            chk.grid(row=row, column=0, columnspan=2, sticky="w", pady=5, padx=20)
            frame_data[control["text"]] = var

            if "sub_frame" in control:
                sub_frame, sub_data = self.create_sub_frame(
                    frame,
                    control["sub_frame"],
                    frame_data,
                    row + 1
                )

                def toggle_sub_frame():
                    if var.get():
                        sub_frame.grid()
                    else:
                        sub_frame.grid_remove()

                var.trace_add("write", lambda *args: toggle_sub_frame())
                frame_data[f"sub_frame_{control['text']}"] = sub_data
                return 2

        elif control["type"] == "entry":
            ttk.Label(
                frame,
                text=control["text"],
                padding=5
            ).grid(row=row, column=0, sticky="w", pady=5, padx=20)

            entry = ttk.Entry(frame, width=50)
            entry.grid(row=row, column=1, sticky="ew", pady=5, padx=(0, 20))
            frame_data[control["text"]] = entry

        return 1

    def clear_frames(self):
        """Löscht alle Widgets aus dem scrollbaren Frame"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def load_config(self):
        """Lädt die Konfiguration aus der JSON-Datei"""
        try:
            with open('frames_config.json', 'r', encoding='utf-8') as file:
                self.config = json.load(file)
            self.show_option_selection()
        except Exception as e:
            messagebox.showerror("Fehler", f"Konfigurationsfehler: {str(e)}")

    def start_option(self, option_name):
        """Startet die Datenerfassung für die gewählte Option"""
        self.current_option = option_name
        self.current_frame_index = 0
        self.collected_data[option_name] = {}
        self.show_current_frame()

    def show_current_frame(self):
        """Zeigt den aktuellen Frame an"""
        self.clear_frames()

        frames = self.config["options"][self.current_option]["frames"]
        current_frame = frames[self.current_frame_index]

        # Container für den gesamten Inhalt
        content = ttk.Frame(self.scrollable_frame)
        content.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        content.grid_columnconfigure(0, weight=1)

        # Frame-Titel
        title_label = ttk.Label(
            content,
            text=current_frame["name"],
            style='Header.TLabel'
        )
        title_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # Frame-Beschreibung
        if "description" in current_frame:
            desc_label = ttk.Label(
                content,
                text=current_frame["description"],
                wraplength=800,
                style='Navigation.TLabel'
            )
            desc_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 20))

        # Controls Container
        controls_frame = ttk.Frame(content)
        controls_frame.grid(row=2, column=0, sticky="nsew")
        controls_frame.grid_columnconfigure(1, weight=1)

        # Frame-Daten initialisieren
        frame_data = {}
        current_row = 0

        # Controls erstellen
        for control in current_frame["controls"]:
            rows_added = self.create_control(controls_frame, control, current_row, frame_data)
            current_row += rows_added

        # Navigation Buttons
        nav_frame = ttk.Frame(content)
        nav_frame.grid(row=3, column=0, sticky="ew", pady=20)
        nav_frame.grid_columnconfigure(1, weight=1)

        if self.current_frame_index > 0:
            ttk.Button(
                nav_frame,
                text="← Zurück",
                command=self.previous_frame,
                padding=10
            ).grid(row=0, column=0, padx=5)

        is_last_frame = self.current_frame_index == len(frames) - 1
        next_btn = ttk.Button(
            nav_frame,
            text="Fertig" if is_last_frame else "Weiter →",
            command=lambda: self.save_and_continue(frame_data,
                                                   self.generate_pdf if is_last_frame else self.next_frame),
            padding=10
        )
        next_btn.grid(row=0, column=2, padx=5)

        # Navigation aktualisieren
        self.update_navigation()

    def previous_frame(self):
        """Geht zum vorherigen Frame zurück"""
        if self.current_frame_index > 0:
            self.current_frame_index -= 1
            self.show_current_frame()

    def next_frame(self):
        """Geht zum nächsten Frame"""
        frames = self.config["options"][self.current_option]["frames"]
        if self.current_frame_index < len(frames) - 1:
            self.current_frame_index += 1
            self.show_current_frame()

    def update_navigation(self):
        """Aktualisiert die Navigationsanzeige"""
        frames = self.config["options"][self.current_option]["frames"]
        self.navigation_label.config(
            text=f"{self.current_option} - Schritt {self.current_frame_index + 1} von {len(frames)}"
        )

    def save_and_continue(self, frame_data, next_action):
        """Speichert die Daten des aktuellen Frames und führt die nächste Aktion aus"""
        current_frame = self.config["options"][self.current_option]["frames"][self.current_frame_index]
        saved_data = self.collect_frame_data(frame_data)
        self.collected_data[self.current_option][current_frame["name"]] = saved_data
        next_action()

    def collect_frame_data(self, frame_data):
        """Sammelt rekursiv alle Daten aus dem Frame und Sub-Frames"""
        saved_data = {}
        for key, value in frame_data.items():
            if key.startswith("sub_frame_"):
                # Rekursiv Sub-Frame-Daten sammeln
                saved_data[key] = self.collect_frame_data(value)
            elif isinstance(value, tk.BooleanVar):
                saved_data[key] = value.get()
            elif isinstance(value, ttk.Entry):
                saved_data[key] = value.get()
        return saved_data

    def on_closing(self):
        """Handler für Fenster-Schließen"""
        if messagebox.askokcancel("Beenden", "Möchten Sie das Programm wirklich beenden?"):
            self.root.quit()
            self.root.destroy()
            sys.exit(0)

    def generate_pdf(self):
        """Erstellt die PDF mit allen gesammelten Daten und schließt das Programm"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Datenerfassung_{timestamp}.pdf"

        c = canvas.Canvas(filename, pagesize=letter)
        y = 750

        def write_data(data, indent=0):
            nonlocal y
            for key, value in data.items():
                if key.startswith("sub_frame_"):
                    # Sub-Frame-Titel
                    c.setFont("Helvetica-Bold", 10)
                    c.drawString(50 + indent, y, f"Details für {key[10:]}")
                    y -= 20
                    # Rekursiv Sub-Frame-Daten schreiben
                    write_data(value, indent + 20)
                else:
                    c.setFont("Helvetica", 10)
                    text = f"{key}: {'Ja' if value == True else 'Nein' if value == False else value}"
                    c.drawString(50 + indent, y, text)
                    y -= 20

                if y < 50:
                    c.showPage()
                    y = 750

        for option, frames in self.collected_data.items():
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y, f"Option: {option}")
            y -= 30

            for frame_name, data in frames.items():
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y, f"Frame: {frame_name}")
                y -= 20

                write_data(data)
                y -= 10

        c.save()
        self.root.quit()
        self.root.destroy()
        sys.exit(0)


if __name__ == "__main__":
    root = tk.Tk()
    app = DataCollectionApp(root)
    root.mainloop()