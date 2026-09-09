import tempfile
from pathlib import Path
from dj_set_sorter import Track, sort_for_set, write_rekordbox_xml, parse_rekordbox_xml, parse_virtualdj, path_from_uri, path_to_uri
from preview import write_preview_html
assert path_from_uri('file://localhost/C:/Music/My%20Track.mp3') == ('C:/Music/My Track.mp3' if __import__('os').name != 'nt' else 'C:\\Music\\My Track.mp3')
assert '%20' in path_to_uri('/Music/My Track.mp3')
tracks=[Track(path='/music/My Track.mp3', title='A', genre='ambient', bpm=90, position_marks=[{'Name':'Hot Cue A','Type':'0','Start':'12.5','Num':'0'}, {'Name':'Loop 1','Type':'4','Start':'30.0','End':'34.0','Num':'1'}], tempos=[{'Inizio':'0.0','Bpm':'90.0','Metro':'4/4','Battito':'1'}]),Track(path='/music/b.mp3', title='B', genre='hard techno', bpm=145)]
ordered=sort_for_set(tracks, use_audio=True)
assert ordered[0].title=='A' and ordered[-1].title=='B' and all(t.energy > 0 for t in ordered)
with tempfile.TemporaryDirectory() as d:
    root=Path(d); db=root/'database.xml'
    db.write_text('<VirtualDJ><Song FilePath="/music/a.mp3" Title="A"/><Song FilePath="/music/b.mp3" Title="B"/></VirtualDJ>', encoding='utf-8')
    m3u=root/'set.m3u'; m3u.write_text('#EXTM3U\n/music/a.mp3\n/music/b.mp3\n', encoding='utf-8')
    _, vdj_playlists=parse_virtualdj(db,[m3u]); assert len(vdj_playlists['set']) == 2
    p=root/'out.xml'; write_rekordbox_xml(tracks,'Test Set',p)
    all_tracks, playlists=parse_rekordbox_xml(p)
    assert len(all_tracks)==2 and playlists['Test Set'][0].title=='A' and all_tracks[0].bpm==90
    xml=p.read_text(encoding='utf-8'); assert 'POSITION_MARK' in xml and 'TEMPO' in xml and 'End="34.0"' in xml and '%20' in xml
    preview=root/'preview.html'; write_preview_html(ordered,'Test Set',preview)
    assert preview.exists() and 'Test Set' in preview.read_text(encoding='utf-8') and 'Aufbau' in preview.read_text(encoding='utf-8')
print('self-test: OK')
