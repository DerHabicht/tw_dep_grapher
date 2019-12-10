#!/usr/bin/env python
'graph dependencies in projects'
import json
import sys
from subprocess import Popen, PIPE
from textwrap import fill

HEADER = 'digraph dependencies {\nrankdir="LR"'
FOOTER = '}'

JSON_START = '['
JSON_END = ']'


def call_taskwarrior(cmd):
    'call taskwarrior, returning output and error'
    tw = Popen(['task'] + cmd.split(), stdout=PIPE, stderr=PIPE)
    return tw.communicate()


def get_json(query):
    'call taskwarrior, returning objects from json'
    print(query)
    raw, err = call_taskwarrior('export %s' % query)
    result = raw.decode('UTF-8')
    return json.loads(JSON_START + str(result) + JSON_END)


def call_dot(instr):
    'call dot, returning stdout and stdout'
    dot = Popen('dot -Tpdf'.split(), stdout=PIPE, stderr=PIPE, stdin=PIPE)
    return dot.communicate(instr)


if __name__ == '__main__':
    query = sys.argv[1:]
    print(query)
    print('Calling TaskWarrior')
    data = get_json(' '.join(query))

    # first pass: labels
    lines = [HEADER]
    print('Printing Labels')
    for datum in data[0]:
        uuid = datum['uuid'].replace(r'"', r'\"')
        description = fill(datum['description'].replace(r'"', r'\"'), width=25)
        lines.append('"%s"[label="%s"];'
                     % (uuid, description))

    # second pass: dependencies
    print('Resolving Dependencies')
    for datum in data[0]:
        for dep in datum.get('depends', '').split(','):
            if dep != '':
                lines.append('"%s" -> "%s";' % (dep, datum['uuid']))

    lines.append(FOOTER)

    with open('deps.dot', 'w') as f:
        f.write('\n'.join(lines))

    print('Calling dot')
    pdf, err = call_dot('\n'.join(lines).encode('utf-8'))
    if err != b'':
        print('Error calling dot:')
        print(err.strip())

    print('Writing to deps.pdf')
    with open('deps.pdf', 'wb') as f:
        f.write(pdf)
