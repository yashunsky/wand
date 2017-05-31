#!/usr/bin/env python

PREFIX = 'stroke'

FILENAME = 'knowledge'

STROKE_MAX_LENGTH = 4096


def stroke_const_name(key):
    return '{prefix}_{key}'.format(prefix=PREFIX.upper(), key=key.upper())


def format_define_to_c(name, value, comment=None):
    comment = ' // ' + comment if comment is not None else ''
    return '''#define {name} {value}{comment}
'''.format(name=name, value=value,
           comment=comment)


def format_formated_strokes_to_c(value):
    data = ',\n'.join(['        {%s}' % ', '.join(['% 2.5f' % x for x in line])
                      for line in value])

    text = '''    {{\n{data}\n    }}'''
    return text.format(data=data)


def convert_knowledge(knowledge):

    strokes = knowledge['strokes']

    h_text = ('/*\n * {filename}.h\n * autogenerated\n*/\n\n'
              .format(filename=FILENAME))

    c_text = ('/*\n * {filename}.cpp\n * autogenerated\n*/\n\n'
              .format(filename=FILENAME))

    c_text += '#include "{filename}.h"\n\n'.format(filename=FILENAME)

    h_text += '#ifndef STROKES_H_\n#define STROKES_H_\n\n'

    h_text += format_define_to_c('DIMENTION', 3)

    h_text += format_define_to_c('STROKE_MAX_LENGTH', 256)

    h_text += format_define_to_c('KP_INIT', knowledge['kp_init'])
    h_text += format_define_to_c('KI_INIT', knowledge['ki_init'])
    h_text += format_define_to_c('KP_WORK', knowledge['kp_work'])
    h_text += format_define_to_c('KI_WORK', knowledge['ki_work'])
    h_text += format_define_to_c('INIT_EDGE', knowledge['init_edge'])

    h_text += format_define_to_c('SEGMENTATION', knowledge['segmentation'])
    h_text += format_define_to_c('GYRO_SCALE', knowledge['gyro_scale'])
    h_text += format_define_to_c('ACC_SCALE', knowledge['acc_scale'])
    h_text += format_define_to_c('G_CONST', knowledge['g_const'])
    h_text += format_define_to_c('STROKES_COUNT', len(strokes))

    h_text += format_define_to_c('MIN_DIMENTION', knowledge['splitting']['min_dimention'])
    h_text += format_define_to_c('ACCELERATION_TIME_CONST', knowledge['splitting']['acceleration_time_const'])

    h_text += format_define_to_c('GYRO_MIN', knowledge['splitting']['gyro_min'])
    h_text += format_define_to_c('GYRO_TIMEOUT', knowledge['splitting']['gyro_timeout'])
    h_text += format_define_to_c('MIN_STROKE_LENGTH', knowledge['splitting']['min_length'])
    h_text += format_define_to_c('COMPARE_LIMIT', knowledge['splitting']['compare_limit'])

    h_text += format_define_to_c('CALIBRATION', knowledge['states']['calibration'])
    h_text += format_define_to_c('IDLE', knowledge['states']['idle'])
    h_text += format_define_to_c('STATES_OFFSET', knowledge['states']['idle'] + 1)

    for key, value in knowledge['splitting']['states'].items():
        h_text += format_define_to_c(key.upper(), value)

    header = ''

    formated_strokes = []

    for name in knowledge['strokes_order']:
        value = strokes[name]
        formated_strokes += [format_formated_strokes_to_c(value)]

    formated_strokes = '''
const float STROKES[STROKES_COUNT][SEGMENTATION][DIMENTION] = {{
{formated_strokes}
}};'''.format(formated_strokes=',\n'.join(formated_strokes))

    h_text += header + '\n'

    h_text += 'extern const float STROKES[STROKES_COUNT][SEGMENTATION][DIMENTION];\n'

    c_text += formated_strokes

    c_text += '\n'

    h_text += '\n\n#endif\n'

    return h_text, c_text
