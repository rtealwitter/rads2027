#!/usr/bin/env python3
"""Check the calendar, notebook coverage, and complete homework packages."""
from datetime import date, datetime, timedelta
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT/'problems/manifest.json').read_text())
rows = manifest['problems']
assert [r['number'] for r in rows] == list(range(1, 23))
home = (ROOT/'index.qmd').read_text()
for week, monday, wednesday in re.findall(r'Week (\d+) \((\d+/\d+) and (\d+/\d+)\)', home):
    expected = date(2027, 1, 18) + timedelta(weeks=int(week)-1)
    for value, day in [(monday, expected), (wednesday, expected+timedelta(days=2))]:
        assert value == f'{day.month}/{day.day}', (week, value, day)
assert len(re.findall(r'Week \d+ \(', home)) == 17
assert 'Week 9 (3/15 and 3/17)' in home
assert 'Week 16 (5/3 and 5/5)' in home
assert 'Spring 2027 course preparation' not in home
assert (ROOT/'CNAME').read_text().strip() == 'rads.rtealwitter.com'
for row in rows:
    number = row['number']
    source = ROOT/row['source_notebook']
    notebook = json.loads(source.read_text())
    assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256']
    assert (ROOT/row['pdf']).read_bytes().startswith(b'%PDF-'), number
    text = (ROOT/row['tex']).read_text()
    due = datetime.fromisoformat(row['due_at'])
    assert due.year == 2027 and due.weekday() == 0, (number, due)
    assert not date(2027, 3, 13) <= due.date() <= date(2027, 3, 21)
    assert f'{due:%B} {due.day}, 2027' in text, number
    for index, cell in enumerate(notebook['cells'][2:], start=2):
        if ''.join(cell['source']).strip():
            assert f'% Source notebook cell {index}\n' in text, (number, index)
    for relative in re.findall(r'\\(?:input|lstinputlisting)(?:\[[^]]*\])?\{([^}]+)\}', text):
        assert ((ROOT/row['tex']).parent/relative).is_file(), (number, relative)
    assert row['pdf'] in home, row['pdf']
    assert row['tex'] not in home
    assert row['source_url'] not in home
    assert r'\$' not in text, f'Unconverted math delimiter in Problem {number}'
assert sum(r['extracted_images'] for r in rows) == 3
assert sum(r['code_cells'] for r in rows) == 2
assert len(list((ROOT/'topics').glob('*/reading.qmd'))) == 21
print('Verified 17 calendar weeks, 21 readings, all 22 homework packages, 3 figures, and 2 starter-code cells.')
