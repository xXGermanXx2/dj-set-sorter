from __future__ import annotations
import datetime as dt
import html
from pathlib import Path


def write_preview_html(tracks, name: str, output: Path) -> None:
    n = len(tracks)
    a = max(1, round(n * .45))
    b = max(a + 1, round(n * .82)) if n > 2 else n
    rows = []
    for i, track in enumerate(tracks, 1):
        phase = "Aufbau" if i <= a else "Steigerung" if i <= b else "Peak"
        css = {"Aufbau": "build", "Steigerung": "rise", "Peak": "peak"}[phase]
        audio = f"{track.audio_energy:.1f}" if getattr(track, "audio_analyzed", False) else "–"
        rows.append(
            f"<tr class='{css}'><td>{i}</td><td><strong>{html.escape(track.artist or 'Unbekannt')}</strong>"
            f"<br>{html.escape(track.title or Path(track.path).stem)}</td><td>{phase}</td>"
            f"<td>{track.energy:.1f}</td><td>{track.bpm or '–'}</td><td>{html.escape(track.genre or '–')}</td>"
            f"<td>{audio}</td><td class='path'>{html.escape(track.path)}</td></tr>"
        )
    document = f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>DJ Set Vorschau – {html.escape(name)}</title>
<style>
body{{font-family:system-ui,-apple-system,Segoe UI,sans-serif;background:#f5f7fb;color:#182230;margin:0;padding:24px}}
main{{max-width:1400px;margin:auto;background:#fff;border-radius:14px;padding:28px;box-shadow:0 4px 20px #18223018}}
h1{{margin:0 0 5px}} .muted{{color:#607080}} .cards{{display:flex;gap:12px;flex-wrap:wrap;margin:22px 0}}
.card{{padding:14px 18px;border-radius:10px;background:#eef3f8;min-width:130px}} .card b{{display:block;font-size:24px}}
table{{border-collapse:collapse;width:100%;font-size:14px}} th{{background:#182230;color:#fff;text-align:left;position:sticky;top:0}}
th,td{{padding:10px 9px;border-bottom:1px solid #e3e8ee;vertical-align:top}} tr.build{{background:#eef8f1}} tr.rise{{background:#fff9e8}} tr.peak{{background:#fff0f0}}
.path{{font-size:11px;color:#6b7785;max-width:320px;word-break:break-all}}
.legend span{{margin-right:14px;padding:5px 9px;border-radius:7px}} .legend .b{{background:#eef8f1}} .legend .r{{background:#fff9e8}} .legend .p{{background:#fff0f0}}
</style></head><body><main><h1>DJ Set Vorschau</h1>
<div class="muted">{html.escape(name)} · erstellt am {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
<div class="cards"><div class="card"><b>{n}</b>Tracks</div><div class="card"><b>{a}</b>Aufbau</div><div class="card"><b>{max(0,b-a)}</b>Steigerung</div><div class="card"><b>{max(0,n-b)}</b>Peak</div></div>
<p class="legend"><span class="b">Aufbau: Energie langsam steigern</span><span class="r">Steigerung: mehr Druck</span><span class="p">Peak: Höhepunkt</span></p>
<p class="muted">Vor dem Export bitte BPM-Sprünge, Übergänge, Breaks, Tonart und die tatsächliche Wirkung prüfen. Diese Datei ist nur eine Vorschau und verändert keine DJ-Datenbank.</p>
<table><thead><tr><th>#</th><th>Track</th><th>Phase</th><th>Energie</th><th>BPM</th><th>Genre</th><th>Audio</th><th>Dateipfad</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
</main></body></html>"""
    output.write_text(document, encoding="utf-8")
