# DJ Set Sorter

Lokales Python-Tool mit Tkinter-Oberfläche zum Zusammenführen und Sortieren von VirtualDJ- oder rekordbox-Playlists nach einer Set-Dramaturgie: **langsamer Aufbau**, **deutliche Steigerung** und **Peak/Ende**.

## Start

```bash
cd /home/ubuntu/dj_set_sorter
python3 dj_set_sorter.py
```

Unter Windows reicht ein Doppelklick auf `start_dj_set_sorter.bat` (Python 3 muss installiert sein). Es werden ausschließlich Python-Standardbibliotheken verwendet.

## Bedienung

1. **VirtualDJ** oder **rekordbox 6/7** auswählen.
2. Die Datenbank bzw. den XML-Export auswählen. Das Programm versucht einen Standardpfad automatisch zu finden.
3. **Playlists laden** drücken und eine oder mehrere Quell-Playlists markieren.
4. Einen Namen eingeben.
5. Optional das Backup aktivieren und **Neue Set-Playlist erstellen** drücken.

Die Ausgabe wird in `DJ Set Sorter Playlists` neben der gewählten Datenbank abgelegt. Für VirtualDJ ist die Ausgabe eine `.m3u`-Playlist. Für rekordbox ist sie eine importierbare `.xml`-Playlistdatei. Das Original wird nicht verändert.

Backups werden in `Dokumente/database backup/VirtualDJ/<Zeitstempel>` bzw. `Dokumente/database backup/rekordbox/<Zeitstempel>` gespeichert.

## Datenquellen und wichtige Grenzen

VirtualDJ wird aus `database.xml` gelesen; vorhandene `.m3u`-Dateien und XML-Dateien im Datenbankordner bzw. `My Lists` werden als Quell-Playlists angeboten. Je nach VirtualDJ-Version und Laufwerk können Datenbank- und Playlistpfade abweichen; in diesem Fall die Datei über **Datenbank/XML wählen…** angeben.

Rekordbox 6/7 verwendet eine proprietäre interne Datenbank. Dieses Tool schreibt sie aus Sicherheitsgründen **nicht direkt**. Stattdessen wird ein von rekordbox unterstützter XML-Export eingelesen und eine neue XML-Playlist erzeugt. Die XML-Datei kann anschließend in rekordbox über die XML-/Playlist-Importfunktionen eingelesen werden. Für eine automatische direkte Datenbankintegration müsste die konkrete rekordbox-Version und das Betriebssystem getestet werden, da ein falscher Schreibzugriff die Bibliothek beschädigen kann.

## Sortierlogik

Die Energie wird heuristisch aus BPM, Genre und – falls vorhanden – Rating berechnet. Audio-Merkmale wie Kick-Härte, Lautheit oder musikalische Phrase werden nicht selbst analysiert. Die Tracks werden in ungefähr 45 % Aufbau, 37 % Steigerung und 18 % Peak aufgeteilt und innerhalb dieser Zonen aufsteigend bzw. am Peak absteigend nach Energie angeordnet. Für besonders gute Ergebnisse sollten BPM, Genre und Ratings in der DJ-Software gepflegt sein.

## Datenschutz

Das Programm arbeitet lokal, benötigt keine Internetverbindung und lädt keine Audiodaten hoch.

## Quellen

- [VirtualDJ User Manual – Playlists](https://virtualdj.com/manuals/virtualdj/interface/database/playlists.html)
- [Lexicon Manual – Syncing to rekordbox](https://www.lexicondj.com/manual/sync-rekordbox-xml)

## Lizenz

Privates Projekt; ohne Gewähr. Vor produktiver Nutzung immer ein Backup aktivieren und die erzeugte Playlist zunächst prüfen.


## Automatische GitHub-Aktualisierung

Das Repository enthält den Workflow `.github/workflows/sync-readme.yml`. Bei jedem Push auf `main` wird `sync_readme.py` ausgeführt. Falls sich der automatisch gepflegte Projektstatus ändert, erstellt GitHub Actions einen Dokumentations-Commit und pusht ihn automatisch zurück in das Repository. Zusätzlich kann der Workflow im GitHub-Tab **Actions** manuell gestartet werden.

Der Workflow benötigt keine zusätzlichen Secrets: Das standardmäßig bereitgestellte `GITHUB_TOKEN` erhält nur die Berechtigung `contents: write` für dieses Repository.

## Automatisch gepflegter Projektstatus

- Hauptprogramm: `dj_set_sorter.py`
- Python-Funktionen: **12**
- Python-Klassen: **2**
- Projektdateien: `dj_set_sorter.py`, `start_dj_set_sorter.bat`, `sync_readme.py`, `test_dj_set_sorter.py`, `validate.py`
