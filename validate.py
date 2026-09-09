import tempfile
from pathlib import Path
from dj_set_sorter import Track, sort_for_set, write_rekordbox_xml, parse_rekordbox_xml
from preview import write_preview_html
tracks=[Track(path='/music/a.mp3', title='A', genre='ambient', bpm=90),Track(path='/music/b.mp3', title='B', genre='hard techno', bpm=145)]
ordered=sort_for_set(tracks, use_audio=True)
assert ordered[0].title=='A' and ordered[-1].title=='B'
assert all(t.energy > 0 for t in ordered)
with tempfile.TemporaryDirectory() as d:
    p=Path(d)/'out.xml'
    write_rekordbox_xml(tracks,'Test Set',p)
    all_tracks, playlists=parse_rekordbox_xml(p)
    assert len(all_tracks)==2 and playlists['Test Set'][0].title=='A'
    preview=Path(d)/'preview.html'
    write_preview_html(ordered,'Test Set',preview)
    assert preview.exists() and 'Test Set' in preview.read_text(encoding='utf-8') and 'Aufbau' in preview.read_text(encoding='utf-8')
print('self-test: OK')
