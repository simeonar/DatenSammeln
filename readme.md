# Datenerfassungs-Anwendung
### Dokumentation und Installationsanleitung

## Beschreibung
Diese Anwendung ermöglicht die strukturierte Erfassung von Daten durch eine grafische Benutzeroberfläche. Die Anwendung ist konfigurierbar und ermöglicht:
- Flexible Definition verschiedener Datenerfassungsoptionen
- Mehrere Erfassungsschritte (Frames) pro Option
- Unterschiedliche Eingabetypen (Checkboxen und Textfelder)
- Automatische PDF-Generierung der erfassten Daten

## Systemvoraussetzungen
- Python 3.8 oder höher
- pip (Python Package Installer)
- Windows, Linux oder macOS

## Installation

1. **Repository klonen oder herunterladen**
```bash
git clone [repository-url]
cd datenerfassung
```

2. **Virtuelle Umgebung erstellen und aktivieren**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

3. **Abhängigkeiten installieren**
```bash
pip install -r requirements.txt
```

## Konfiguration

Die Anwendung wird über eine JSON-Datei (`frames_config.json`) konfiguriert. Diese muss im gleichen Verzeichnis wie die Hauptanwendung liegen.

### Beispiel-Konfiguration:
```json
{
    "options": {
        "Technische Prüfung": {
            "frames": [
                {
                    "name": "Grundinformation",
                    "description": "Bitte füllen Sie die grundlegenden Informationen aus:",
                    "controls": [
                        {
                            "type": "entry",
                            "text": "Projektnummer"
                        },
                        {
                            "type": "entry",
                            "text": "Prüfer Name"
                        }
                    ]
                }
            ]
        }
    }
}
```

### Konfigurationsstruktur:
- **options**: Hauptcontainer für alle Optionen
  - **[Optionsname]**: Name der Erfassungsoption
    - **frames**: Array von Erfassungsschritten
      - **name**: Name des Frames
      - **description**: Beschreibung/Anweisungen
      - **controls**: Array von Eingabeelementen
        - **type**: "checkbox" oder "entry"
        - **text**: Beschriftung des Elements

## Verwendung

1. **Anwendung starten**
```bash
python app.py
```

2. **Bedienung**
   - Option aus der Hauptansicht wählen
   - Daten in den verschiedenen Frames eingeben
   - Mit "Weiter" und "Zurück" navigieren
   - Am Ende "Fertig" klicken zur PDF-Generierung

3. **PDF-Ausgabe**
   - PDFs werden im Arbeitsverzeichnis gespeichert
   - Dateiname: `Datenerfassung_[Zeitstempel].pdf`

## Projektstruktur
```
datenerfassung/
│
├── app.py                 # Hauptanwendung
├── frames_config.json     # Konfigurationsdatei
├── requirements.txt       # Abhängigkeiten
├── README.md             # Diese Dokumentation
└── .venv/                # Virtuelle Umgebung
```

## Abhängigkeiten
- tkinter: GUI-Framework
- reportlab: PDF-Generierung
- json: Konfigurationsverarbeitung

## Entwicklung und Erweiterung

### Neue Eingabetypen hinzufügen
1. JSON-Schema erweitern
2. Neue Eingabetyp-Logik in `create_control()` implementieren
3. PDF-Generierung in `generate_pdf()` anpassen

### Styling anpassen
- Schriftarten und -größen in `__init__()` konfigurieren
- Widget-Abstände in den Layout-Methoden anpassen

## Fehlerbehebung

### Häufige Probleme:
1. **Konfigurationsdatei nicht gefunden**
   - Überprüfen Sie, ob `frames_config.json` im richtigen Verzeichnis liegt
   - Prüfen Sie die JSON-Syntax

2. **PDF-Generierung schlägt fehl**
   - Stellen Sie sicher, dass das Arbeitsverzeichnis beschreibbar ist
   - Prüfen Sie, ob alle erforderlichen Daten erfasst wurden

3. **GUI-Elemente werden nicht korrekt angezeigt**
   - Überprüfen Sie die Bildschirmauflösung
   - Prüfen Sie die Fenstergröße-Einstellungen

## Support und Kontakt
[Ihre Kontaktinformationen]

## Lizenz
[Ihre Lizenzinformationen]

## Changelog
- Version 1.0.0 (YYYY-MM-DD)
  - Erste Veröffentlichung
  - Grundfunktionalität implementiert

## Beitragen
1. Fork des Repositories erstellen
2. Feature-Branch erstellen (`git checkout -b feature/AmazingFeature`)
3. Änderungen committen (`git commit -m 'Add some AmazingFeature'`)
4. Branch pushen (`git push origin feature/AmazingFeature`)
5. Pull Request erstellen

## Bekannte Probleme
- [Liste bekannter Probleme und geplanter Verbesserungen]