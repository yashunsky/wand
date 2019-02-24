#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from gui.ring import KEYS

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
  </style>
 </head>
 <body style="font-family: sans-serif;">
  {rows}
 </body>
</html>
'''

KEY_TEMPLATE = '<div class="key" style="background-image: url({url}); border-color:{border_color}">{char}</div>'
ROW_TEMPLATE = '<div style="display: table; border-spacing: 5px"><div style="display: table-cell; width: {offset}px">&nbsp;</div>{cells}</div>'


def get_key_by_char(char):
    side, position = KEYS.get(char, (None, None))
    if side is None:
        border_color = '#64330c'
    else:
        border_color = 'red' if side else 'blue'
        side = 'right' if side else 'left'

    if position is None:
        url = ''
    elif char == ' ' and position == 'random':
        return '<div class="key" style="width: 440px; text-align: center; vertical-align: middle">Мне повезёт</div>'
    else:
        url = 'gui/sprites/%s/%s.gif' % (side, position)

    return KEY_TEMPLATE.format(url=url, border_color=border_color, char=char)


def make_html_row(offset, chars):
    html_cells = ''.join([get_key_by_char(char) for char in chars])
    return ROW_TEMPLATE.format(offset=offset, cells=html_cells)


if __name__ == '__main__':
    rows = [
        (0, 'qwertyuiop'),
        (15, 'asdfghjkl;'),
        (40, 'zxcvbnm,.'),
        (210, ' ')]
    html_rows = [make_html_row(offset, chars) for offset, chars in rows]
    html = TEMPLATE.format(rows='\n'.join(html_rows))
    with open('manual.html', 'w') as f:
        f.write(html)
