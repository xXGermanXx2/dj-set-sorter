# DJ Set Sorter

**DJ Set Sorter** ist ein lokales Python-Programm für DJs, das vorhandene Playlists aus **VirtualDJ** oder **rekordbox 6/7** einliest, mehrere Playlists zusammenführt und daraus eine neue Playlist mit einer musikalisch sinnvollen Energie-Dramaturgie erstellt.

Die geplante Reihenfolge ist:

1. **Anfang – Aufbau:** niedrigere Energie, grooviger und weniger intensiv
2. **Mitte – Steigerung:** mehr Druck, härtere Kicks und höhere Energie
3. **Ende – Peak:** die intensivsten Tracks als Höhepunkt des Sets

Das Programm arbeitet lokal. Es lädt weder Audiodateien noch Datenbanken in die Cloud und verändert die Originaldatenbank nicht direkt.

---

## Inhaltsverzeichnis

- [Funktionen](#funktionen)
- [Systemanforderungen](#systemanforderungen)
- [Installation](#installation)
- [Programm starten](#programm-starten)
- [Bedienung](#bedienung)
- [VirtualDJ](#virtualdj)
- [rekordbox 6/7](#rekordbox-67)
- [Sortierlogik](#sortierlogik)
- [Backups](#backups)
- [Ausgabedateien](#ausgabedateien)
- [Tests und Validierung](#tests-und-validierung)
- [Automatische README-Pflege über GitHub](#automatische-readme-pflege-über-github)
- [Fehlerbehebung](#fehlerbehebung)
- [Sicherheit und Grenzen](#sicherheit-und-grenzen)
- [Projektstruktur](#projektstruktur)
- [Quellen](#quellen)
- [Lizenz](#lizenz)

---

## Funktionen

- Startmenü mit grafischer Benutzeroberfläche auf Basis von Tkinter
- Auswahl zwischen **VirtualDJ** und **rekordbox 6/7**
- Automatische Erkennung typischer Datenbank- oder XML-Pfade
- Manuelle Auswahl einer Datenbank- oder XML-Datei
- Einlesen vorhandener Playlists
- Auswahl einer oder mehrerer Playlists
- Zusammenführen der ausgewählten Tracks ohne Duplikate
- Eigener Name für die neue Set-Playlist
- Energie-Sortierung anhand von BPM, Genre und Rating
- optionale Audioanalyse anhand von Lautheit, Dynamik, Bass- und Transientenanteil
- Aufteilung in Aufbau-, Steigerungs- und Peak-Phase
- Optionales Backup vor der Verarbeitung
- Ausgabe als VirtualDJ-kompatible `.m3u`-Datei
- Ausgabe als rekordbox-XML-Datei
- Keine direkte Änderung der Originaldatenbank
- Keine externen Python-Pakete für den normalen Betrieb
- Lokale Verarbeitung ohne Upload von Musikdateien

---

## Systemanforderungen

### Allgemein

- Python **3.10 oder neuer** empfohlen
- Betriebssystem: Windows, macOS oder Linux
- Schreibrechte im Projektordner und im Dokumente-Ordner

### Zusätzlich für die grafische Oberfläche

Tkinter muss installiert sein. Unter vielen Windows- und macOS-Python-Installationen ist Tkinter bereits enthalten.

Unter Debian/Ubuntu kann es nachinstalliert werden:

```bash
sudo apt update
sudo apt install python3-tk
```

### Zusätzlich für Audioanalyse

Für die Audioanalyse wird `ffmpeg` benötigt. Das Programm verwendet ffmpeg nur zum lokalen Dekodieren kurzer Audioabschnitte; es werden keine Audiodateien gespeichert oder hochgeladen.

Unter Debian/Ubuntu:

```bash
sudo apt install ffmpeg
```

Unter macOS mit Homebrew:

```bash
brew install ffmpeg
```

Unter Windows kann ffmpeg von [ffmpeg.org](https://ffmpeg.org/download.html) installiert und zum PATH hinzugefügt werden. Wenn ffmpeg fehlt, funktioniert das Programm weiterhin mit der Metadaten-Sortierung.

### Unterstützte DJ-Programme

- VirtualDJ mit zugänglicher `database.xml` und Playlist-Dateien
- rekordbox 6 oder 7 über einen kompatiblen XML-Export

---

## Installation

Das Projekt verwendet ausschließlich Python-Standardbibliotheken. Eine Installation über `pip` ist für das Programm nicht erforderlich.

```bash
git clone https://github.com/xXGermanXx2/dj-set-sorter.git
cd dj-set-sorter
```

Alternativ kann der Projektordner auch direkt als ZIP-Datei heruntergeladen und entpackt werden.

---

## Programm starten

### Linux oder macOS

```bash
cd dj-set-sorter
python3 dj_set_sorter.py
```

### Windows Eingabeaufforderung

```bat
cd dj-set-sorter
python dj_set_sorter.py
```

### Windows per Doppelklick

Die Datei `start_dj_set_sorter.bat` starten. Dafür muss Python installiert und über den PATH erreichbar sein.

Wenn Windows Python nicht findet, kann das Programm auch über den vollständigen Pfad gestartet werden, zum Beispiel:

```bat
C:\Users\DEIN_NAME\AppData\Local\Programs\Python\Python312\python.exe dj_set_sorter.py
```

---

## Bedienung

### 1. DJ-Programm auswählen

Im Startfenster zunächst auswählen:

- **VirtualDJ**
- **rekordbox 6/7**

Das Programm versucht anschließend, einen typischen Datenbankpfad automatisch zu finden.

### 2. Datenbank oder XML auswählen

Wenn der Pfad nicht automatisch gefunden wird, auf **Datenbank/XML wählen…** klicken und die passende Datei auswählen.

Danach **Playlists laden** drücken.

### 3. Quell-Playlists auswählen

Im Listenfeld werden die gefundenen Playlists angezeigt. Mehrere Einträge können mit `Strg` beziehungsweise `Cmd` ausgewählt werden.

Alle Tracks aus den ausgewählten Playlists werden zusammengeführt. Derselbe Track wird dabei nur einmal übernommen.

### 4. Namen für das neue Set eingeben

Im Feld **Name der neuen Playlist** einen Namen eintragen, zum Beispiel:

```text
Freitag Club Set
```

### 5. Backup auswählen

Die Backup-Option ist standardmäßig aktiviert. Sie sollte vor dem ersten produktiven Einsatz aktiviert bleiben.

### 6. HTML-Vorschau prüfen

Vor dem Export auf **HTML-Vorschau öffnen** klicken. Die lokale Browseransicht zeigt Tracknummer, Interpret, Titel, Set-Phase, Energie-Wert, BPM, Genre, Audio-Wert und Dateipfad. Die Zeilen sind farblich markiert: grün für Aufbau, gelb für Steigerung und rot für Peak.

Die Vorschau wird in `DJ Set Sorter Previews/<Name>_preview.html` neben der ausgewählten Datenbank- oder XML-Datei gespeichert. Sie ist eine reine Prüfansicht und verändert keine DJ-Datenbank.

### 7. Playlist erstellen

Auf **Neue Set-Playlist erstellen** klicken.

Das Programm sortiert die Tracks, erzeugt die neue Datei und zeigt den Speicherort sowie – falls aktiviert – den Backup-Ordner an.

### Empfohlener Prüfablauf

1. Quell-Playlists laden und auswählen.
2. Audioanalyse aktivieren, sofern `ffmpeg` installiert ist.
3. HTML-Vorschau öffnen.
4. Reihenfolge und Set-Phasen kontrollieren.
5. Auf BPM-Sprünge, falsche Energieeinschätzungen, Breaks und Übergänge achten.
6. Erst danach die neue Playlist erzeugen.

---

## VirtualDJ

### Eingelesene Daten

Das Programm liest die VirtualDJ-`database.xml`. Zusätzlich werden folgende Playlist-Dateien im Umfeld der Datenbank berücksichtigt:

- `.m3u`-Dateien im Datenbankordner
- XML-Playlistdateien im Datenbankordner
- XML-Playlistdateien im Unterordner `My Lists`

Die konkreten Speicherorte können je nach Betriebssystem, VirtualDJ-Version, Benutzerkonto und Laufwerk abweichen.

### Typischer Pfad

Ein möglicher Standardpfad unter Windows ist:

```text
Dokumente\VirtualDJ\database.xml
```

Bei Musik auf externen Laufwerken können zusätzlich Datenbankdateien im Stammverzeichnis des jeweiligen Laufwerks existieren.

### Ausgabe

Die neue Playlist wird als `.m3u` abgelegt. Der Speicherort ist:

```text
<Ordner der Datenbank>\DJ Set Sorter Playlists\<Playlistname>.m3u
```

Die `.m3u`-Datei kann anschließend in VirtualDJ importiert oder im Browser geöffnet werden.

---

## rekordbox 6/7

### Wichtiger Hinweis zur Datenbank

rekordbox 6 und 7 verwenden eine proprietäre interne Datenbank. Dieses Programm schreibt diese interne Datenbank **nicht direkt**.

Stattdessen wird ein XML-Export eingelesen und eine neue XML-Datei mit der sortierten Playlist erzeugt. Das vermeidet direkte, potenziell riskante Änderungen an der rekordbox-Bibliothek.

### XML-Datei vorbereiten

In rekordbox muss zunächst eine Bibliothek beziehungsweise Playlist als XML exportiert werden. Die genauen Menübezeichnungen können je nach Version und Betriebssystem abweichen.

Anschließend diese XML-Datei im DJ Set Sorter über **Datenbank/XML wählen…** auswählen.

### Ausgabe importieren

Die erzeugte Datei liegt hier:

```text
<Ordner der XML-Datei>\DJ Set Sorter Playlists\<Playlistname>.xml
```

Diese XML-Datei anschließend in rekordbox über die XML-/Playlist-Funktionen laden oder importieren. Vor dem Import sollte rekordbox geschlossen beziehungsweise die XML-Ansicht neu geladen werden, sofern rekordbox dies verlangt.

### Empfehlung

Vor einem Import in rekordbox:

1. rekordbox schließen oder die Bibliothek vollständig speichern lassen
2. das Backup aktiviert lassen
3. die erzeugte XML-Datei zunächst kontrollieren
4. nur die gewünschte Playlist importieren
5. die Reihenfolge in rekordbox prüfen

---

## Sortierlogik

Die Energie wird als heuristischer Wert zwischen ungefähr 0 und 100 berechnet. Standardmäßig ist in der GUI die Audioanalyse aktiviert. Der Wert kombiniert Metadaten mit lokal berechneten Audio-Merkmalen:

| Faktor | Bedeutung |
|---|---|
| BPM | Höhere BPM werden grundsätzlich als energiereicher bewertet. |
| Genre | Typische Genre-Begriffe wie Ambient, Deep, House, Techno oder Hardstyle erhalten unterschiedliche Grundwerte. |
| Rating | Ein vorhandenes Rating wird als zusätzliches Qualitätssignal berücksichtigt. |

### Audio-Merkmale

Das Programm dekodiert pro Track maximal 120 Sekunden und berechnet daraus Lautheit, Dynamik, Bassanteil sowie schnelle Transienten als Hinweis auf Kick- und Schlagzeugdruck. Das ist keine vollständige Musikproduktionsanalyse; insbesondere die Kick-Erkennung ist eine robuste Näherung und keine Instrumententrennung.

Die aktuelle Gewichtung ist ungefähr:

- Metadaten gesamt: **55 %** (BPM 24,75 %, Genre 22 %, Rating 8,25 %)
- Audio gesamt: **45 %** (Lautheit 15,75 %, Dynamik 6,75 %, Bass 11,25 %, Transienten/Kick 11,25 %)

Die Tracks werden danach ungefähr in diese Set-Abschnitte eingeteilt:

| Set-Phase | Anteil | Sortierung |
|---|---:|---|
| Anfang / Aufbau | ca. 45 % | Energie aufsteigend, grooviger Start |
| Mitte / Steigerung | ca. 37 % | Energie aufsteigend, mehr Druck |
| Ende / Peak | ca. 18 % | stärkste Tracks zuerst innerhalb des Peak-Blocks |

### Nicht automatisch analysiert

Das Programm analysiert derzeit nicht automatisch:

- exakte Kick-Härte oder Instrumententrennung
- musikalische Phrasen und Taktpositionen
- Breaks und Drops
- Vocal-Dichte
- Tonart-Kompatibilität
- tatsächliche Club-Wirkung eines Tracks

Die Sortierung ist damit eine kombinierte Audio- und Metadaten-Heuristik, aber keine vollständige musikalische Analyse. Für bessere Ergebnisse sollten BPM, Genre und Rating in VirtualDJ beziehungsweise rekordbox gepflegt sein. Die Audioanalyse kann in der GUI abgewählt werden, wenn ffmpeg nicht installiert ist oder die Verarbeitung schneller erfolgen soll.

---

## Backups

Wenn die Backup-Option aktiviert ist, wird vor der Erstellung eine Kopie im Dokumente-Ordner abgelegt.

VirtualDJ:

```text
Dokumente/database backup/VirtualDJ/<Zeitstempel>/
```

rekordbox:

```text
Dokumente/database backup/rekordbox/<Zeitstempel>/
```

Der Zeitstempel hat ungefähr dieses Format:

```text
2026-09-09_05-30-00
```

Das Programm erstellt den Zielordner automatisch. Eine vorhandene Backup-Kopie wird nicht überschrieben, weil jeder Lauf einen eigenen Zeitstempel erhält.

Trotzdem sollte zusätzlich das reguläre Backup-System des jeweiligen DJ-Programms verwendet werden.

---

## Ausgabedateien

### VirtualDJ

```text
DJ Set Sorter Playlists/<Name>.m3u
```

Die Datei enthält eine Liste der vollständigen Track-Pfade im M3U-Format.

### rekordbox

```text
DJ Set Sorter Playlists/<Name>.xml
```

Die Datei enthält:

- Track-Informationen
- Dateipfade
- BPM-Informationen, sofern vorhanden
- eine neue Playlist mit dem eingegebenen Namen
- die sortierte Track-Reihenfolge

Sonderzeichen im Dateinamen werden aus Sicherheitsgründen teilweise durch `_` ersetzt.

---

## Tests und Validierung

Das Projekt enthält einen kleinen Selbsttest für Sortierung und XML-Roundtrip.

```bash
python3 validate.py
```

Erwartete Ausgabe:

```text
self-test: OK
```

Zusätzlich kann die Syntax geprüft werden:

```bash
python3 -m py_compile dj_set_sorter.py validate.py sync_readme.py
```

Die Datei `test_dj_set_sorter.py` enthält pytest-kompatible Tests. Falls `pytest` installiert ist, können sie so ausgeführt werden:

```bash
python3 -m pytest -q
```

---

## Automatische README-Pflege über GitHub

Im Ordner `.github/workflows/` liegt der Workflow:

```text
.github/workflows/sync-readme.yml
```

Bei jedem Push auf den Branch `main` wird automatisch:

1. das Repository ausgecheckt
2. `sync_readme.py` ausgeführt
3. der Projektstatus in der README aktualisiert
4. geprüft, ob sich die README geändert hat
5. bei Änderungen ein Dokumentations-Commit erstellt
6. der Commit automatisch nach GitHub gepusht

Der automatisch gepflegte Abschnitt enthält beispielsweise:

- den Namen des Hauptprogramms
- die Anzahl der Python-Funktionen
- die Anzahl der Klassen
- eine Liste der Projektdateien

Der Workflow kann außerdem im GitHub-Bereich **Actions** manuell über **Run workflow** gestartet werden.

### Berechtigungen

Der Workflow verwendet das von GitHub bereitgestellte `GITHUB_TOKEN` und benötigt in der Workflow-Datei:

```yaml
permissions:
  contents: write
```

In den Repository-Einstellungen muss außerdem unter **Settings → Actions → General → Workflow permissions** gegebenenfalls **Read and write permissions** aktiviert werden.

Wenn GitHub beim ersten Push meldet, dass der Token keine Workflow-Berechtigung besitzt, muss der verwendete GitHub-Token beziehungsweise die GitHub-CLI-Autorisierung einmal mit dem zusätzlichen Bereich `workflow` autorisiert werden.

### Warum `[skip ci]` verwendet wird

Der automatische Dokumentations-Commit enthält `[skip ci]`. Dadurch wird verhindert, dass die README-Änderung erneut denselben Workflow endlos auslöst.

---

## Fehlerbehebung

### `Tkinter fehlt`

Unter Ubuntu/Debian:

```bash
sudo apt install python3-tk
```

Unter Windows sollte Python von [python.org](https://www.python.org/downloads/) installiert werden. Bei der Installation die Option **Add Python to PATH** aktivieren.

### Keine Playlists gefunden

Folgende Punkte prüfen:

1. Wurde die richtige Datenbank- oder XML-Datei ausgewählt?
2. Wurde **Playlists laden** gedrückt?
3. Ist die Playlist-Datei im erwarteten Ordner vorhanden?
4. Sind in der Playlist tatsächlich Tracks enthalten?
5. Wurde die Bibliothek vorher exportiert oder gespeichert?

### Tracks fehlen in der Ausgabe

Mögliche Ursachen:

- derselbe Track kommt mehrfach vor und wird absichtlich nur einmal übernommen
- der Dateipfad ist in der Datenbank nicht mehr gültig
- die Playlist enthält Einträge ohne vollständigen Pfad
- die XML-Datei enthält nicht die vollständige Sammlung
- Track-Metadaten wie Genre oder BPM fehlen

### rekordbox importiert die Datei nicht

Sicherstellen, dass:

- die XML-Datei aus einer kompatiblen rekordbox-Version stammt
- rekordbox geschlossen oder neu geladen wurde
- die XML-Datei nicht manuell beschädigt wurde
- der Import über die XML-/Playlist-Funktion von rekordbox erfolgt
- die Originalbibliothek vorher gesichert wurde

### Die Reihenfolge ist musikalisch nicht perfekt

Die Sortierung verwendet Metadaten und ersetzt kein DJ-Gehör. BPM, Genre und Ratings pflegen, anschließend die erzeugte Playlist manuell kontrollieren. Übergänge, Tonart, Breaks, Intros und Drops sollten vor dem Auftritt immer geprüft werden.

---

## Sicherheit und Grenzen

- Originaldatenbanken werden nicht direkt überschrieben.
- Backups sollten vor jeder produktiven Änderung aktiviert werden.
- Das Programm verschiebt, kopiert oder löscht keine Musikdateien.
- Das Programm lädt keine Audiodateien hoch.
- Das Programm benötigt im normalen Betrieb keine Internetverbindung.
- Für rekordbox 6/7 erfolgt keine direkte Bearbeitung der proprietären Datenbank.
- Die erzeugten Playlists sollten vor einem Live-Einsatz vollständig geprüft werden.

Dieses Projekt wird ohne Garantie für jede Version, jedes Betriebssystem oder jede Bibliotheksstruktur bereitgestellt.

---

## Projektstruktur

```text
DJ Set Sorter/
├── dj_set_sorter.py                 # Hauptprogramm mit Tkinter-GUI
├── preview.py                       # Erzeugt die lokale HTML-Prüfvorschau
├── sync_readme.py                   # Aktualisiert den Projektstatus in README.md
├── validate.py                      # Schneller Selbsttest ohne pytest
├── test_dj_set_sorter.py            # pytest-kompatible Tests
├── start_dj_set_sorter.bat          # Windows-Startdatei
├── README.md                        # Projektdokumentation
├── .gitignore                       # Ausschluss lokaler Dateien
└── .github/
    └── workflows/
        └── sync-readme.yml          # Automatische README-Pflege
```

---

## Quellen

- [VirtualDJ User Manual – Playlists](https://virtualdj.com/manuals/virtualdj/interface/database/playlists.html)
- [Lexicon Manual – Syncing to rekordbox](https://www.lexicondj.com/manual/sync-rekordbox-xml)

Die Quellen dienen der Orientierung zu Playlist- und XML-Workflows. Die konkrete Verfügbarkeit und das Verhalten können sich je nach Version der DJ-Software ändern.

---

## Lizenz

Privates Hobbyprojekt ohne Gewähr. Die Nutzung erfolgt auf eigene Verantwortung. Vor produktiver Nutzung immer ein Backup erstellen und die erzeugte Playlist zunächst in der DJ-Software kontrollieren.

## Automatisch gepflegter Projektstatus

- Hauptprogramm: `dj_set_sorter.py`
- Python-Funktionen: **14**
- Python-Klassen: **2**
- Projektdateien: `dj_set_sorter.py`, `preview.py`, `start_dj_set_sorter.bat`, `sync_readme.py`, `test_dj_set_sorter.py`, `validate.py`
