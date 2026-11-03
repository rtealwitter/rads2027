#!/usr/bin/env python3
"""Convert the archived Colab statements to editable LaTeX handouts.

No notebooks are executed. The manifest is the authority for topic paths and
2027 deadlines. Figures and starter data are extracted from the same snapshot.
Run this only when deliberately regenerating handouts; it overwrites TeX edits.
"""
import base64
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def convert(markdown):
    result = subprocess.run(
        ['pandoc', '--from=markdown+tex_math_dollars+raw_tex', '--to=latex',
         '--wrap=none', '--top-level-division=section'],
        input=markdown, text=True, capture_output=True, check=True)
    text = result.stdout
    text = re.sub(r'\\(?:sub)*section\{', r'\\subsection*{', text)
    text = text.replace(r'\begin{align}', r'\begin{align*}').replace(r'\end{align}', r'\end{align*}')
    text = text.replace(r'\[', r'\begin{align*}').replace(r'\]', r'\end{align*}')
    return text


def main():
    manifest_path = ROOT/'problems/manifest.json'
    manifest = json.loads(manifest_path.read_text())
    for row in manifest['problems']:
        number = row['number']
        source = ROOT/row['source_notebook']
        notebook = json.loads(source.read_text())
        folder = (ROOT/row['tex']).parent
        folder.mkdir(parents=True, exist_ok=True)
        row['source_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
        row['markdown_cells'] = sum(c['cell_type'] == 'markdown' for c in notebook['cells'])
        row['code_cells'] = sum(c['cell_type'] == 'code' for c in notebook['cells'])
        image_count = 0
        code_count = 0
        pieces = []

        def image(match):
            nonlocal image_count
            image_count += 1
            extension = {'jpeg':'jpg', 'png':'png', 'jpg':'jpg'}[match['type']]
            filename = f'problem{number:02}-figure{image_count}.{extension}'
            (folder/'images').mkdir(exist_ok=True)
            (folder/'images'/filename).write_bytes(base64.b64decode(match['data']))
            # A raw TeX block prevents Pandoc's implicit floating figures.
            return '\n\n' + r'\begin{center}' + '\n' + r'\includegraphics[width=0.65\linewidth,height=0.28\textheight,keepaspectratio]{images/' + filename + '}\n' + r'\end{center}' + '\n\n'

        # Every notebook begins with a title cell and a submission-policy cell.
        # Preserve the policy but replace the old date and minor notebook typo.
        policy = ''.join(notebook['cells'][1]['source'])
        due = datetime.fromisoformat(row['due_at'])
        due_text = f'{due:%A, %B} {due.day}, {due.year}'
        policy = re.sub(r'Please upload your work[^\n]*',
                        f'Please upload your work to Gradescope by **11:59pm on {due_text} (Pacific time).**', policy)
        policy = policy.replace('write your solutions python notebook', 'write your solutions in a Python notebook')
        pieces.append(convert(policy))
        pieces.append(r'\noindent Original notebook: \href{' + row['source_url'] + '}{Google Colab}.\n')
        for index, cell in enumerate(notebook['cells'][2:], start=2):
            content = ''.join(cell['source'])
            if cell['cell_type'] == 'markdown':
                content = re.sub(r'!\[[^\]]*\]\(data:image/(?P<type>png|jpeg|jpg);base64,(?P<data>[A-Za-z0-9+/=\s]+)\)', image, content)
                # This stray brace is present in the original notebook prose.
                content = content.replace('structure of $\\mathbf{T}$?}', 'structure of $\\mathbf{T}$?')
                content = content.replace('$N = $', '$N =$')
                pieces.append(f'% Source notebook cell {index}\n' + convert(content))
            elif cell['cell_type'] == 'code' and content.strip():
                code_count += 1
                filename = f'problem{number:02}_starter' + (f'_{code_count}' if code_count > 1 else '') + '.py'
                (folder/filename).write_text(content.rstrip()+'\n')
                pieces.append(f'% Source notebook cell {index}\n' + r'\subsection*{Starter Code and Data}' + '\n' + r'\lstinputlisting[language=Python]{' + filename + '}\n')
        row['extracted_images'] = image_count
        title = row['title'].replace('&', r'\&').replace('%', r'\%')
        header = (r'\documentclass{article}' + '\n'
                  r'\input{../../../problems/common/preamble.tex}' + '\n'
                  r'\title{Math 126 Problem ' + str(number) + ': ' + title + '}\n'
                  r'\author{} % Put your name here.' + '\n'
                  r'\date{Spring 2027}' + '\n'
                  r'\begin{document}' + '\n' + r'\maketitle' + '\n\n')
        (ROOT/row['tex']).write_text(header + '\n'.join(pieces) + '\n' + r'\end{document}' + '\n')
    manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')
    print(f"Converted {len(manifest['problems'])} notebooks to TeX.")


if __name__ == '__main__':
    main()
