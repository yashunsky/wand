#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

from os.path import basename

from demo import StrokeSplitter

OUTPUT = 'migration_to_c/strokes.h'

PREFIX = 'stroke'

ACTION_TEMPLATE = 'ACTION_%i'

NORMAL_ACTION_LENGTH = 3


def stroke_const_name(key):
    return '{prefix}_{key}'.format(prefix=PREFIX.upper(), key=key.upper())


def format_define_to_c(name, value, comment):
    return u'''#define {name} {value} // {comment}
'''.format(name=name, value=value,
           comment=comment)


def format_action_to_c(value, names, empty_name):
    strokes = [[stroke_const_name(key) for key, s_name in names.items()
               if s_name == stroke_name][0] for stroke_name in value]

    strokes += [empty_name] * (NORMAL_ACTION_LENGTH - len(strokes))

    return '    {%s}' % ', '.join(strokes)


def format_formated_strokes_to_c(value):
    data = ',\n'.join(['        {%s}' % ', '.join(['% 2.5f' % x for x in line])
                      for line in value])

    text = u'''    {{\n{data}\n    }}'''
    return text.format(data=data)

if __name__ == '__main__':
    splitter = StrokeSplitter(None)
    names = splitter.strokes_names
    strokes = splitter.selector.letters_dict
    actions = splitter.sequences

    empty_stroke_name = stroke_const_name('________')

    with open(OUTPUT, 'w') as f:

        f.write('/*\n * {filename}\n * autogenerated\n*/\n\n'.
                format(filename=basename(OUTPUT)))

        f.write('#ifndef STROKES_H_\n#define STROKES_H_\n\n')

        f.write('#define SEGMENTATION %d\n\n' % splitter.selector.segmentation)

        formated_strokes = []

        header = u''

        formated_actions = []

        for index, (key, value) in enumerate(strokes.items()):
            name = names[key] if key in names else key
            formated_strokes += [format_formated_strokes_to_c(value)]
            header += format_define_to_c(stroke_const_name(key), index, name)

        header += format_define_to_c(empty_stroke_name,
                                     index + 1,
                                     u'заглушка, если надо 2 жеста, а не 3')

        header += '\n'

        for index, (name, value) in enumerate(actions.items()):
            header += format_define_to_c(ACTION_TEMPLATE % index, index, name)
            formated_actions += [format_action_to_c(value, names,
                                                    empty_stroke_name)]

        formated_actions = '''
const int_16t actions[{actions_count}][3] = {{
{formated_actions}
}}'''.format(actions_count=len(actions),
             formated_actions=',\n'.join(formated_actions))

        formated_strokes = '''
const float_t strokes[{strokes_count}][{segmentation}][4] = {{
{formated_strokes}
}}'''.format(strokes_count=len(strokes),
             segmentation=splitter.selector.segmentation,
             formated_strokes=',\n'.join(formated_strokes))

        f.write((u'{header}\n{formated_actions}\n{formated_strokes}'.
                format(header=header,
                       formated_actions=formated_actions,
                       formated_strokes=formated_strokes)).encode('UTF-8'))
