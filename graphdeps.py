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
    print(query)
    raw, err = call_taskwarrior('export %s' % query)
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
