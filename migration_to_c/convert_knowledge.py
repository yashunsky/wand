#!/usr/bin/env python

from os.path import basename

import json

KNOWLEDGE = 'test_knowledge.json'

OUTPUT = '../src_c/strokes'

PREFIX = 'stroke'

SEQUENCE_TEMPLATE = 'SEQUENCE_%i'

NORMAL_SEQUENCE_LENGTH = 2


def stroke_const_name(key):
    return '{prefix}_{key}'.format(prefix=PREFIX.upper(), key=key.upper())


def format_define_to_c(name, value, comment=None):
    comment = ' // ' + comment if comment is not None else ''
    return '''#define {name} {value}{comment}
'''.format(name=name, value=value,
           comment=comment)


def format_action_to_c(value, empty_name):
    strokes = [stroke_const_name(stroke_name) for stroke_name in value]

    strokes += [empty_name] * (NORMAL_SEQUENCE_LENGTH - len(strokes))

    return '    {%s}' % ', '.join(strokes)


def format_formated_strokes_to_c(value):
    data = ',\n'.join(['        {%s}' % ', '.join(['% 2.5f' % x for x in line])
                      for line in value])

    text = '''    {{\n{data}\n    }}'''
    return text.format(data=data)


def convert_knowledge(knowledge):
    empty_stroke_name = stroke_const_name('________')

    strokes = knowledge['strokes']

    names = knowledge['strokes_en_names']

    sequences = knowledge['sequences']['dictionary']

    sequences_names = knowledge['sequences_names']

    sequences_en_names = knowledge['sequences_en_names']

    init_stroke = knowledge['sequences']['init_stroke']

    h_text = ('/*\n * {filename}.h\n * autogenerated\n*/\n\n'
              .format(filename=basename(OUTPUT)))

    c_text = ('/*\n * {filename}.c\n * autogenerated\n*/\n\n'
              .format(filename=basename(OUTPUT)))

    c_text += '#include "{filename}.h"\n\n'.format(filename=basename(OUTPUT))

    h_text += '#ifndef STROKES_H_\n#define STROKES_H_\n\n'

    h_text += format_define_to_c('DIMENTION', 3)

    h_text += format_define_to_c('SEGMENTATION', knowledge['segmentation'])

    h_text += format_define_to_c('STROKES_COUNT', len(strokes))

    h_text += format_define_to_c('SEQUENCES_COUNT',
                                 len(knowledge['sequences']['dictionary']))

    h_text += format_define_to_c('NORMAL_SEQUENCE_LENGTH',
                                 NORMAL_SEQUENCE_LENGTH)

    header = ''

    formated_strokes = []

    formated_sequences = []

    for index, (key, value) in enumerate(strokes.items()):
        name = names[key] if key in names else key
        formated_strokes += [format_formated_strokes_to_c(value)]
        header += format_define_to_c(stroke_const_name(key), index, name)

    header += format_define_to_c(empty_stroke_name,
                                 index + 1,
                                 'used, if the seq is shorter then ' +
                                 'NORMAL_SEQUENCE_LENGTH')

    header += '\n'

    header += format_define_to_c('INIT_STROKE', stroke_const_name(init_stroke))

    for index, (name, value) in enumerate(zip(sequences_names, sequences)):
        en_name = sequences_en_names[name]
        header += format_define_to_c(SEQUENCE_TEMPLATE % index, index, en_name)
        formated_sequences += [format_action_to_c(value, empty_stroke_name)]

    formated_sequences = '''
const int SEQUENCES[SEQUENCES_COUNT][NORMAL_SEQUENCE_LENGTH] = {{
{formated_sequences}
}};'''.format(formated_sequences=',\n'.join(formated_sequences))

    formated_strokes = '''
const float STROKES[STROKES_COUNT][SEGMENTATION][DIMENTION + 1] = {{
{formated_strokes}
}};'''.format(formated_strokes=',\n'.join(formated_strokes))

    h_text += header + '\n'

    h_text += 'extern int const SEQUENCES[SEQUENCES_COUNT][NORMAL_SEQUENCE_LENGTH];\n'
    h_text += 'extern float const STROKES[STROKES_COUNT][SEGMENTATION][DIMENTION + 1];\n'

    c_text += ('{formated_sequences}\n{formated_strokes}'.
               format(formated_sequences=formated_sequences,
                      formated_strokes=formated_strokes))

    h_text += '\n\n#endif\n'

    return h_text, c_text

if __name__ == '__main__':
    with open(KNOWLEDGE, 'r') as f:
        knowledge = json.load(f)

    h_text, c_text = convert_knowledge(knowledge)

    with open(OUTPUT + '.h', 'w') as f:
        f.write(h_text)

    with open(OUTPUT + '.c', 'w') as f:
        f.write(c_text)