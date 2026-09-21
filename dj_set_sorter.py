#!/usr/bin/env python3
"""DJ Set Sorter – lokale GUI für VirtualDJ und rekordbox 6/7.

Keine Cloud, keine Änderungen an Originaldatenbanken. Rekordbox wird sicher
über das offizielle XML-Exportformat verarbeitet; die proprietäre DB wird nie
ungefragt direkt beschrieben.
"""
from __future__ import annotations
import copy, datetime as dt, html, json, math, os, re, shutil, struct, subprocess, sys, urllib.parse, wave, webbrowser, xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from preview import write_preview_html
try:
    from tkinter import Tk, StringVar, BooleanVar, Listbox, END, SINGLE, filedialog, messagebox
    from tkinter import ttk
except ModuleNotFoundError:  # Parser/Export können auf Minimalservern trotzdem genutzt werden.
    Tk = StringVar = BooleanVar = Listbox = END = SINGLE = filedialog = messagebox = ttk = None

APP = "DJ Set Sorter"
REKORDBOX_VERSIONS = ("6", "7")
STATE_FILE = Path.home() / ".dj_set_sorter_state.json"

@dataclass
class Track:
    path: str
    title: str = ""
    artist: str = ""
    album: str = ""
    genre: str = ""
    bpm: float = 0.0
    rating: int = 0
    energy: float = 0.0
    source_id: str = ""
    audio_energy: float = 0.0
    audio_analyzed: bool = False
    position_marks: list[dict] | None = None
    tempos: list[dict] | None = None

    @property
    def label(self):
        return f"{self.artist} – {self.title}".strip(" –") or Path(self.path).name


def attr(node, *names, default=""):
    for name in names:
        if name in node.attrib and node.attrib[name] != "":
            return node.attrib[name]
    return default


def number(value):
    try: return float(str(value).replace(",", "."))
    except (TypeError, ValueError): return 0.0


def path_from_uri(value: str) -> str:
    """Wandelt lokale rekordbox-/VirtualDJ-URIs zuverlässig in Dateipfade um."""
    value = html.unescape(str(value or "")).strip()
    if value.lower().startswith("file://"):
        parsed = urllib.parse.urlparse(value)
        path = urllib.parse.unquote(parsed.path or "")
        if parsed.netloc and parsed.netloc.lower() != "localhost":
            path = "//" + parsed.netloc + path
        if parsed.netloc.lower() == "localhost" and parsed.path == "":
            path = ""
    else:
        path = urllib.parse.unquote(value)
    # XML-Dateien aus Windows enthalten gelegentlich /C:/ oder C:/.
    if re.match(r"^/[A-Za-z]:", path): path = path[1:]
    if re.match(r"^[A-Za-z]:/", path): path = path.replace("/", "\\") if os.name == "nt" else path
    return path


def path_to_uri(path: str) -> str:
    """Erzeugt eine rekordbox-kompatible lokale file://localhost-URI."""
    raw = str(path or "")
    if re.match(r"^[A-Za-z]:[\\/]", raw):
        raw = "/" + raw.replace("\\", "/")
    elif not raw.startswith("/"):
        raw = "/" + raw
    return "file://localhost" + urllib.parse.quote(raw, safe="/:\\")


def track_from_node(node, path_override=""):
    p = path_override or attr(node, "FilePath", "Location", "path", "file", "Name")
    p = path_from_uri(p)
    marks = [dict(x.attrib) for x in node.findall("POSITION_MARK")]
    tempos = [dict(x.attrib) for x in node.findall("TEMPO")]
    return Track(path=p, title=attr(node, "Title", "title", "Name"), artist=attr(node, "Artist", "artist"),
                 album=attr(node, "Album", "album"), genre=attr(node, "Genre", "genre"),
                 bpm=number(attr(node, "BPM", "AverageBpm", "Tempo", "bpm")),
                 rating=int(round(number(attr(node, "Rating", "rating")) / 51)) if number(attr(node, "Rating", "rating")) > 5 else int(number(attr(node, "Rating", "rating"))), source_id=attr(node, "ID", "TrackID", "id"), position_marks=marks, tempos=tempos)


def parse_virtualdj(database: Path, playlist_files: list[Path]) -> tuple[list[Track], dict[str, list[Track]]]:
    root = ET.parse(database).getroot()
    by_path = {}
    for n in root.iter():
        if n.tag.lower().endswith("song") or any(k in n.attrib for k in ("FilePath", "Location")):
            t = track_from_node(n)
            if t.path: by_path[os.path.normcase(os.path.normpath(t.path))] = t
    playlists = {}
    for pf in playlist_files:
        tracks = []
        if pf.suffix.lower() == ".m3u":
            for line in pf.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    if not os.path.isabs(line): line = str((pf.parent / line).resolve())
                    tracks.append(by_path.get(os.path.normcase(os.path.normpath(line)), Track(path=line)))
        else:
            try:
                pr = ET.parse(pf).getroot()
                for n in pr.iter():
                    p = attr(n, "FilePath", "Location", "path", "file")
                    if p: tracks.append(by_path.get(os.path.normcase(os.path.normpath(p)), track_from_node(n)))
            except ET.ParseError: pass
        if tracks:
            playlists[pf.stem] = unique_tracks(tracks)
    if not playlists and by_path:
        playlists["Alle Tracks aus Datenbank"] = list(by_path.values())
    return list(by_path.values()), playlists


def virtualdj_playlist_candidates(database: Path) -> list[Path]:
    """Findet nur echte Playlistkandidaten, nicht VDJ-System-/Backup-XMLs."""
    ignored_names = {
        "database.xml", "foldercache.xml", "foldercontent.xml", "history.xml",
        "searchdb.xml", "settings.xml", "playlists.xml"
    }
    candidates = []
    for item in database.parent.rglob("*"):
        if not item.is_file() or item.resolve() == database.resolve():
            continue
        if any(part.lower() in {"backup", "backups", "database backup", "database_backup"} for part in item.parts):
            continue
        suffix = item.suffix.lower()
        stem = item.stem.lower()
        if any(token in stem for token in ("foldercache", "foldercontent", "database", "broken database", "searchdb", "settings")):
            continue
        if suffix == ".m3u":
            candidates.append(item)
        elif suffix == ".xml" and item.name.lower() not in ignored_names:
            # XML-Playlisten liegen typischerweise in "My Lists"; benannte XMLs
            # im VDJ-Ordner bleiben ebenfalls möglich, Systemdateien sind oben ausgeschlossen.
            candidates.append(item)
    return candidates


def parse_rekordbox_xml(xml_file: Path) -> tuple[list[Track], dict[str, list[Track]]]:
    root = ET.parse(xml_file).getroot()
    by_id = {}
    for n in root.iter("TRACK"):
        t = track_from_node(n, attr(n, "Location"))
        if t.path: by_id[attr(n, "TrackID", "ID", default=str(len(by_id)))] = t
    playlists = {}
    for p in root.iter("NODE"):
        # rekordbox nutzt Type=1 für Playlists; Type=0 bezeichnet meist Ordner.
        name = attr(p, "Name", default="Playlist")
        tracks = [by_id.get(attr(x, "Key")) for x in p.iter("TRACK")]
        if tracks and attr(p, "Type") in ("0", "1"):
            playlists[name] = unique_tracks([x for x in tracks if x])
    if not playlists and by_id:
        playlists["Alle Tracks aus XML"] = list(by_id.values())
    return list(by_id.values()), playlists


def unique_tracks(tracks):
    out, seen = [], set()
    for t in tracks:
        key = os.path.normcase(os.path.normpath(t.path))
        if key and key not in seen: seen.add(key); out.append(t)
    return out

GENRE_SCORE = {"ambient": 10, "chill": 15, "deep": 25, "house": 42, "disco": 45, "funk": 48,
               "tech house": 58, "progressive": 60, "trance": 68, "electro": 72, "techno": 78,
               "hard techno": 92, "hardstyle": 96, "drum & bass": 88, "dnb": 88, "gabber": 100}

def energy_score(t: Track, position: float) -> float:
    bpm_score = max(0, min(100, (t.bpm - 80) * 1.25)) if t.bpm else 50
    genre = t.genre.lower()
    genre_score = max((v for k, v in GENRE_SCORE.items() if k in genre), default=50)
    # Rating wird leicht als Qualitäts-/Set-Sicherheitssignal genutzt.
    rating_score = min(100, t.rating * 20) if t.rating else 50
    return round(bpm_score * .45 + genre_score * .40 + rating_score * .15, 2)


def analyze_audio(t: Track, max_seconds: int = 120) -> float:
    """Analysiert bis zu 120 s Audio über ffmpeg, ohne Audiodaten zu speichern.

    Die Merkmale sind robuste Näherungen: Lautheit, Dynamik, Bassanteil und
    Transienten/Kick-Anteil. Fehlt ffmpeg oder ist der Pfad ungültig, bleibt
    die Metadaten-Sortierung aktiv.
    """
    if t.audio_analyzed: return t.audio_energy
    t.audio_analyzed = True
    try:
        cmd = ["ffmpeg", "-v", "error", "-i", t.path, "-t", str(max_seconds),
               "-ac", "1", "-ar", "11025", "-f", "s16le", "pipe:1"]
        raw = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                             timeout=max_seconds + 20, check=True).stdout
        samples = [x / 32768.0 for x in struct.unpack("<" + "h" * (len(raw) // 2), raw)]
        if len(samples) < 11025: return 0.0
        step = 11025 // 20
        windows = [samples[i:i + step] for i in range(0, len(samples) - step, step)]
        rms = [math.sqrt(sum(x * x for x in w) / len(w)) for w in windows]
        overall = math.sqrt(sum(x * x for x in samples) / len(samples))
        loudness = max(0.0, min(100.0, (20 * math.log10(max(overall, 1e-5)) + 60) * 1.67))
        dynamics = max(0.0, min(100.0, (max(rms) - min(rms)) * 220))
        # Tiefe Energie als geglättete Signalenergie; Transienten als schnelle Hüllkurvenänderung.
        low = []; transients = []
        prev = 0.0
        for w in windows:
            smooth = 0.0
            for x in w:
                smooth = smooth * .985 + abs(x) * .015
            low.append(smooth)
            transients.append(max(0.0, smooth - prev)); prev = smooth
        bass = max(0.0, min(100.0, (sum(low) / len(low)) * 230))
        kick = max(0.0, min(100.0, (sum(transients) / len(transients)) * 900))
        t.audio_energy = round(loudness * .35 + dynamics * .15 + bass * .25 + kick * .25, 2)
    except (OSError, subprocess.SubprocessError, ValueError, struct.error, ZeroDivisionError):
        t.audio_energy = 0.0
    return t.audio_energy


def combined_energy_score(t: Track, use_audio: bool = True) -> float:
    metadata = energy_score(t, 0)
    audio = analyze_audio(t) if use_audio else 0.0
    return round(metadata * .55 + audio * .45, 2) if use_audio and t.audio_analyzed and audio else metadata


def sort_for_set(tracks: list[Track], ramp: float = 1.0, use_audio: bool = True) -> list[Track]:
    if not tracks: return []
    for t in tracks: t.energy = combined_energy_score(t, use_audio)
    ordered = sorted(tracks, key=lambda x: (x.energy, x.bpm or 0, x.artist.lower(), x.title.lower()))
    # Drei dramaturgische Zonen; stabile Energie-Steigerung ohne brutale Sprünge.
    n = len(ordered); a = max(1, round(n * .45)); b = max(a + 1, round(n * .82)) if n > 2 else n
    start, middle, peak = ordered[:a], ordered[a:b], ordered[b:]
    start.sort(key=lambda x: (x.energy, x.bpm or 0))
    middle.sort(key=lambda x: (x.energy, x.bpm or 0))
    peak.sort(key=lambda x: (-x.energy, -(x.bpm or 0)))
    return start + middle + peak


def backup_database(path: Path, program: str) -> Path:
    target = Path.home() / "Documents" / "database backup" / program / dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    target.mkdir(parents=True, exist_ok=True)
    if path.is_dir(): shutil.copytree(path, target / path.name, dirs_exist_ok=True)
    else: shutil.copy2(path, target / path.name)
    return target


def write_virtualdj_m3u(tracks, output: Path):
    output.write_text("#EXTM3U\n" + "\n".join(t.path for t in tracks) + "\n", encoding="utf-8")


def write_rekordbox_xml(tracks, name: str, output: Path):
    root = ET.Element("DJ_PLAYLISTS", Version="1.0.0")
    ET.SubElement(root, "PRODUCT", Name="rekordbox", Version="7")
    collection = ET.SubElement(root, "COLLECTION", Entries=str(len(tracks)))
    for i, t in enumerate(tracks, 1):
        track_node = ET.SubElement(collection, "TRACK", TrackID=str(i), Name=t.title or Path(t.path).stem,
                       Artist=t.artist, Album=t.album, Genre=t.genre, AverageBpm=str(t.bpm or ""),
                       Rating=str(min(255, max(0, t.rating * 51))), Comments=f"DJ Set Sorter Reihenfolge: {i:02d}",
                       Location=path_to_uri(t.path))
        for mark in (t.position_marks or []):
            ET.SubElement(track_node, "POSITION_MARK", **{str(k): str(v) for k, v in mark.items()})
        for tempo in (t.tempos or []):
            ET.SubElement(track_node, "TEMPO", **{str(k): str(v) for k, v in tempo.items()})
    playlists = ET.SubElement(root, "PLAYLISTS"); root_node = ET.SubElement(playlists, "NODE", Type="0", Name="ROOT", Count="1")
    pl = ET.SubElement(root_node, "NODE", Type="1", Name=name, KeyType="0", Entries=str(len(tracks)))
    for i in range(1, len(tracks) + 1): ET.SubElement(pl, "TRACK", Key=str(i))
    ET.indent(root, space="  ")
    ET.ElementTree(root).write(output, encoding="utf-8", xml_declaration=True)


def autodetect(program):
    home = Path.home()
    if program == "VirtualDJ":
        candidates = [home / "Documents/VirtualDJ/database.xml", home / "Documents/VirtualDJ/database.xml"]
        return next((p for p in candidates if p.exists()), None)
    candidates = [home / "Library/Pioneer/rekordbox/rekordbox.xml", home / "Documents/Pioneer/rekordbox/rekordbox.xml"]
    return next((p for p in candidates if p.exists()), None)

class App:
    def __init__(self, root):
        if ttk is None:
            raise RuntimeError("Tkinter fehlt. Unter Debian/Ubuntu installieren: sudo apt install python3-tk")
        self.root = root; root.title(APP); root.geometry("1000x760"); root.minsize(900, 650)
        self.program = StringVar(value="VirtualDJ"); self.db = StringVar(); self.name = StringVar(value="Mein Set"); self.backup = BooleanVar(value=True); self.audio = BooleanVar(value=True)
        self.backup_status = StringVar(value="Noch kein Backup gespeichert.")
        self.backup_state = self._read_backup_state()
        self.playlists = {}; self._build(); self.db.set(str(autodetect(self.program.get()) or "")); self._refresh_backup_status()

    def _read_backup_state(self):
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    def _save_backup_state(self):
        try:
            STATE_FILE.write_text(json.dumps(self.backup_state, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            pass

    def _refresh_backup_status(self):
        program = "VirtualDJ" if self.program.get() == "VirtualDJ" else "rekordbox"
        info = self.backup_state.get(program)
        if info:
            self.backup_status.set(f"Letztes {program}-Backup: {info.get('time', 'unbekannt')} · {info.get('path', '')}")
        else:
            self.backup_status.set(f"Für {program} wurde bisher kein Backup gespeichert.")

    def _build(self):
        main = ttk.Frame(self.root, padding=18); main.pack(fill="both", expand=True)
        ttk.Label(main, text="DJ Set Sorter", font=("TkDefaultFont", 22, "bold")).pack(anchor="w")
        ttk.Label(main, text="Playlists auswählen → Backup optional → Energie-Dramaturgie erzeugen", foreground="#555").pack(anchor="w", pady=(0, 14))
        top = ttk.LabelFrame(main, text="1. DJ-Programm und Datenquelle", padding=10); top.pack(fill="x")
        ttk.Label(top, text="Programm:").grid(row=0, column=0, sticky="w")
        combo = ttk.Combobox(top, textvariable=self.program, values=["VirtualDJ", f"rekordbox {REKORDBOX_VERSIONS[0]}/{REKORDBOX_VERSIONS[1]}"], state="readonly", width=18); combo.grid(row=0, column=1, padx=8)
        combo.bind("<<ComboboxSelected>>", lambda e: self._program_changed())
        ttk.Entry(top, textvariable=self.db).grid(row=1, column=0, columnspan=2, sticky="ew", pady=8); top.columnconfigure(1, weight=1)
        ttk.Button(top, text="Datenbank/XML wählen…", command=self.choose_db).grid(row=1, column=2, padx=5)
        ttk.Button(top, text="Playlists laden", command=self.load).grid(row=1, column=3)
        mid = ttk.LabelFrame(main, text="2. Quell-Playlists", padding=10); mid.pack(fill="both", expand=True, pady=12)
        self.listbox = Listbox(mid, selectmode="extended", height=12); self.listbox.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(mid, orient="vertical", command=self.listbox.yview); scroll.pack(side="right", fill="y"); self.listbox.config(yscrollcommand=scroll.set)
        bottom = ttk.LabelFrame(main, text="3. Ausgabe", padding=10); bottom.pack(fill="x")
        ttk.Label(bottom, text="Name der neuen Playlist:").grid(row=0, column=0, sticky="w"); ttk.Entry(bottom, textvariable=self.name, width=34).grid(row=0, column=1, padx=8, sticky="ew"); bottom.columnconfigure(1, weight=1)
        ttk.Checkbutton(bottom, text="Audio analysieren (Lautheit, Dynamik, Bass/Kick; benötigt ffmpeg)", variable=self.audio).grid(row=1, column=0, columnspan=2, sticky="w")
        ttk.Checkbutton(bottom, text="Vorher Datenbank sichern (Dokumente/database backup/<Programm>/…)", variable=self.backup).grid(row=2, column=0, columnspan=2, sticky="w", pady=8)
        ttk.Button(bottom, text="Datenbank jetzt sichern", command=self.manual_backup).grid(row=3, column=0, sticky="w")
        ttk.Label(bottom, textvariable=self.backup_status, foreground="#245", wraplength=680).grid(row=3, column=1, sticky="w", padx=8)
        actions = ttk.Frame(main); actions.pack(anchor="e", pady=(12, 0))
        ttk.Button(actions, text="HTML-Vorschau öffnen", command=self.preview, padding=8).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Neue Set-Playlist erstellen", command=self.create, padding=8).pack(side="left")
        self.status = StringVar(value="Bereit. Originaldaten werden nicht verändert."); ttk.Label(main, textvariable=self.status, foreground="#245").pack(anchor="w", pady=(8, 0))

    def _program_changed(self): self.db.set(str(autodetect(self.program.get()) or "")); self.playlists = {}; self.listbox.delete(0, END); self._refresh_backup_status()
    def choose_db(self):
        f = filedialog.askopenfilename(title="Datenbank/XML wählen", filetypes=[("XML", "*.xml"), ("Alle Dateien", "*.*")]); self.db.set(f) if f else None
    def load(self):
        p = Path(self.db.get()).expanduser()
        if not p.exists(): return messagebox.showerror(APP, "Die Datenbank/XML-Datei wurde nicht gefunden.")
        try:
            if self.program.get() == "VirtualDJ":
                files = virtualdj_playlist_candidates(p)
                _, self.playlists = parse_virtualdj(p, files)
            else: _, self.playlists = parse_rekordbox_xml(p)
            self.listbox.delete(0, END)
            for n, ts in self.playlists.items(): self.listbox.insert(END, f"{n} ({len(ts)} Tracks)")
            if self.playlists:
                self.status.set(f"{len(self.playlists)} Playlists geladen.")
            else:
                self.status.set("Keine Playlists gefunden. Bitte Datenbank/XML und Export prüfen.")
        except Exception as e: messagebox.showerror(APP, f"Laden fehlgeschlagen:\n{e}")
    def selected_sorted(self):
        picks = self.listbox.curselection(); name = self.name.get().strip()
        if not picks or not name:
            messagebox.showwarning(APP, "Bitte Playlist(s) und einen Namen angeben."); return None, None
        tracks = unique_tracks(sum((list(self.playlists.values())[i] for i in picks), []))
        return name, sort_for_set(tracks, use_audio=self.audio.get())
    def manual_backup(self):
        p = Path(self.db.get()).expanduser()
        if not p.exists():
            return messagebox.showerror(APP, "Bitte zuerst die Datenbank/XML-Datei auswählen.")
        try:
            program = "VirtualDJ" if self.program.get() == "VirtualDJ" else "rekordbox"
            target = backup_database(p, program)
            now = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
            self.backup_state[program] = {"time": now, "path": str(target)}
            self._save_backup_state(); self._refresh_backup_status()
            messagebox.showinfo(APP, f"Backup erfolgreich erstellt:\n{target}")
        except Exception as e:
            messagebox.showerror(APP, f"Backup fehlgeschlagen:\n{e}")
    def preview(self):
        name, ordered = self.selected_sorted()
        if not ordered: return
        p = Path(self.db.get()).expanduser(); outdir = p.parent / "DJ Set Sorter Previews"; outdir.mkdir(exist_ok=True)
        safe = re.sub(r"[^A-Za-z0-9äöüÄÖÜß _-]", "_", name).strip() or "Set"
        out = outdir / (safe + "_preview.html"); write_preview_html(ordered, name, out); webbrowser.open(out.as_uri())
        self.status.set(f"HTML-Vorschau erstellt: {out.name}")
    def create(self):
        name, ordered = self.selected_sorted()
        if not ordered: return
        p = Path(self.db.get()).expanduser()
        try:
            backup = backup_database(p, "VirtualDJ" if self.program.get() == "VirtualDJ" else "rekordbox") if self.backup.get() else None
            if backup:
                program = "VirtualDJ" if self.program.get() == "VirtualDJ" else "rekordbox"
                self.backup_state[program] = {"time": dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z"), "path": str(backup)}
                self._save_backup_state(); self._refresh_backup_status()
            outdir = p.parent / "DJ Set Sorter Playlists"; outdir.mkdir(exist_ok=True)
            safe = re.sub(r"[^A-Za-z0-9äöüÄÖÜß _-]", "_", name).strip() or "Set"
            out = outdir / (safe + (".m3u" if self.program.get() == "VirtualDJ" else ".xml"))
            (write_virtualdj_m3u(ordered, out) if self.program.get() == "VirtualDJ" else write_rekordbox_xml(ordered, name, out))
            msg = f"Playlist erstellt: {out}\n{len(ordered)} Tracks sortiert."
            if backup: msg += f"\nBackup: {backup}"
            messagebox.showinfo(APP, msg); self.status.set(f"Fertig: {out.name}")
        except Exception as e: messagebox.showerror(APP, f"Erstellen fehlgeschlagen:\n{e}")

if __name__ == "__main__":
    if Tk is None:
        raise SystemExit("Tkinter fehlt. Unter Debian/Ubuntu installieren: sudo apt install python3-tk")
    root = Tk(); App(root); root.mainloop()
