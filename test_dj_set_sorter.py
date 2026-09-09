import tempfile
from pathlib import Path
from dj_set_sorter import Track, sort_for_set, write_rekordbox_xml, parse_rekordbox_xml

def test_sort_increases_energy():
    tracks = [Track(path=f"/x/{i}.mp3", title=str(i), genre=g, bpm=b) for i, (g,b) in enumerate([
        ("ambient", 90), ("house", 120), ("hard techno", 145), ("deep house", 110), ("techno", 135)])]
    result = sort_for_set(tracks)
    assert result[0].energy <= result[1].energy
    assert result[-1].energy >= result[0].energy

def test_rekordbox_roundtrip():
    tracks = [Track(path="/music/a.mp3", title="A", artist="DJ", bpm=128)]
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "out.xml"
        write_rekordbox_xml(tracks, "Test Set", p)
        all_tracks, playlists = parse_rekordbox_xml(p)
        assert len(all_tracks) == 1
        assert "Test Set" in playlists
        assert playlists["Test Set"][0].title == "A"
