#!/usr/bin/env python

'''
Visualize taskwarrior task dependencies using graphviz.
'''

import json
import sys
from subprocess import Popen, PIPE
from textwrap import fill

HEADER = 'digraph dependencies {\nrankdir="LR"'
FOOTER = '}'


def call_taskwarrior(cmd):
    'call taskwarrior, returning output and error'
    task_warrior = Popen(['task'] + cmd.split(), stdout=PIPE, stderr=PIPE)
    return task_warrior.communicate()


def get_json(query):
    'call taskwarrior, returning objects from json'
    raw, _ = call_taskwarrior(f'{query} export')
    result = raw.decode('UTF-8')
    return json.loads(f'[ {str(result)} ]')


def call_dot(instr):
    'call dot, returning stdout and stdout'
    dot = Popen('dot -Tpdf'.split(), stdout=PIPE, stderr=PIPE, stdin=PIPE)
    return dot.communicate(instr)


if __name__ == '__main__':
    QUERY = ' '.join(sys.argv[1:])
    print(f'Calling TaskWarrior with query\t{QUERY}')
    data = get_json(QUERY)

    lines = [HEADER]
    lines.append('node [shape=none];')
    if not data:
        print('No tasks with dependencies found')
        sys.exit(1)
    for datum in data[0]:
        description = fill(datum['description'].replace(r'"', r'\"'), width=25)
        lines.append('"%s"[label="%s"];'
                     % (datum['uuid'], description))
        for dep in datum.get('depends', []):
            if dep:
                lines.append(f"\"{dep}\" -> \"{datum['uuid']}\";")
    lines.append(FOOTER)

    dot_input = '\n'.join(lines)

    with open('deps.dot', 'w', encoding='utf-8') as f:
        f.write(dot_input)

    print('Calling dot')
    pdf, err = call_dot('\n'.join(lines).encode('utf-8'))
    if err != b'':
        print('Error calling dot:')
        print(err.strip())

    print('Writing pdf')
    with open('deps.pdf', 'wb') as f:
        f.write(pdf)
