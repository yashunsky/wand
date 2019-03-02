#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gui.ring import KEYS
from knowledge.spells import ALL_SPELLS

TEMPLATE = '''<html>
 <head>
  <meta charset="utf-8">
  <title>Руководство</title>
  <style>
   .key {{
     background-color: #ebcd89;
     background-position: center center;
     background-repeat: no-repeat;
     background-size: auto 60px;
     border-radius: 5px;
     border: solid 2px #64330c;
     color: #64330c;
     display: table-cell;
     font-size: 20px;
     height: 70px;
     margin: 2px;
     padding: 5px;
     text-align: left;
     vertical-align: top;
     width: 70px;
    }}
    .left {{
     border-color: blue;
    }}
    .right {{
     border-color: red;
    }}
    .spellbook {{
     background-color: #ebcd89;
     border-radius: 5px;
     border: solid 2px #64330c;
     color: #64330c;
     display: table;
     font-size: 30px;
     margin-top: 30px;
    }}
    .spellbook_cell {{
     border-bottom: solid 2px #64330c;
     display: table-cell;
     padding: 10px;
     text-align: center;
     vertical-align: middle;
    }}
  </style>
 </head>
 <body style="font-family: sans-serif;">
{rows}
  <div class="spellbook">
{spells}
  </div>
 </body>
</html>
'''

POSITION_TEMPLATE = 'gui/sprites/%s/%s.gif'

KEY_TEMPLATE = '    <div class="{classes}" style="background-image: url({url});">{char}</div>'
ROW_TEMPLATE = '   <div style="display: table; border-spacing: 5px"><div style="display: table-cell; width: {offset}px">&nbsp;</div>\n{cells}\n   </div>'

SPELL_TEMPLATE = '   <div style="display: table-row;">{cells}</div>'
CELL_TEMPLATE = '<div class="spellbook_cell">{content}</div>'
IMAGE_TEMPLATE = '<img src="{src}" height="60px">'


def get_key_by_char(char):
    side, position = KEYS.get(char, (None, None))
    classes = 'key'
    if side is not None:
        side = 'right' if side else 'left'
        classes += ' ' + side

    if position is None:
        url = ''
    elif char == ' ' and position == 'random':
        return '    <div class="key" style="width: 440px; text-align: center; vertical-align: middle">Мне повезёт</div>'
    else:
        url = POSITION_TEMPLATE % (side, position)

    return KEY_TEMPLATE.format(classes=classes, url=url, char=char)


def make_html_row(offset, chars):
    html_cells = '\n'.join([get_key_by_char(char) for char in chars])
    return ROW_TEMPLATE.format(offset=offset, cells=html_cells)


def image_sequence(sequence, side):
    srcs = [POSITION_TEMPLATE % (side, position) for position in sequence]
    imgs = [IMAGE_TEMPLATE.format(src=src) for src in srcs]
    return ''.join(imgs)


def make_html_spell(spell):
    left_images = image_sequence(spell.sequence, 'left')
    right_images = image_sequence(spell.sequence, 'right')
    cells = [CELL_TEMPLATE.format(content=content) for content in
             [left_images, spell.name, right_images]]
    return SPELL_TEMPLATE.format(cells=''.join(cells))


if __name__ == '__main__':
    rows = [
        (0, 'qwertyuiop'),
        (15, 'asdfghjkl;'),
        (40, 'zxcvbnm,.'),
        (210, ' ')]
    html_rows = [make_html_row(offset, chars) for offset, chars in rows]
    html_spells = [make_html_spell(spell) for spell in ALL_SPELLS.values()]
    html = TEMPLATE.format(rows='\n'.join(html_rows),
                           spells='\n'.join(html_spells))
    with open('manual.html', 'w') as f:
        f.write(html)
