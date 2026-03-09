import os

from PIL import Image, ImageDraw, ImageFont

out_dir = '/Users/hejinyang/社会学读书笔记/wechat_posts/assets/images/wechat'
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, 'ate_att_atu_static.png')

width, height = 1200, 720
img = Image.new('RGB', (width, height), '#ffffff')
draw = ImageDraw.Draw(img)

axis_color = '#334155'
bar_colors = ['#e63946', '#2d5a8a', '#2a9d8f']
labels = ['ATE', 'ATT', 'ATU']
values = [0.557, 0.612, 0.487]

try:
    font_title = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf', 42)
    font_label = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf', 32)
    font_tick = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf', 24)
    font_note = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf', 22)
except Exception:
    font_title = ImageFont.load_default()
    font_label = ImageFont.load_default()
    font_tick = ImageFont.load_default()
    font_note = ImageFont.load_default()

title = 'Preset Demonstration: ATE vs ATT vs ATU'
title_width = draw.textlength(title, font=font_title)
draw.text(((width - title_width) / 2, 30), title, fill='#0f172a', font=font_title)

left, top, right, bottom = 120, 130, 1100, 610
plot_width, plot_height = right - left, bottom - top

for i in range(0, 8):
    y_value = i * 0.1
    y = bottom - int((y_value / 0.7) * plot_height)
    draw.line([(left, y), (right, y)], fill='#e2e8f0', width=2)
    draw.text((30, y - 12), f'{y_value:.1f}', fill='#475569', font=font_tick)

draw.line([(left, top), (left, bottom)], fill=axis_color, width=4)
draw.line([(left, bottom), (right, bottom)], fill=axis_color, width=4)

bar_width = 170
gap = (plot_width - 3 * bar_width) // 4
x = left + gap
for label, value, color in zip(labels, values, bar_colors):
    bar_height = int((value / 0.7) * plot_height)
    y_top = bottom - bar_height
    draw.rounded_rectangle([x, y_top, x + bar_width, bottom], radius=16, fill=color)

    value_text = f'{value:.3f}'
    value_width = draw.textlength(value_text, font=font_label)
    draw.text((x + (bar_width - value_width) / 2, y_top - 42), value_text, fill='#111827', font=font_label)

    label_width = draw.textlength(label, font=font_label)
    draw.text((x + (bar_width - label_width) / 2, bottom + 20), label, fill='#1f2937', font=font_label)
    x += bar_width + gap

note = 'Static figure for WeChat long-image rendering (no drag interaction required).'
note_width = draw.textlength(note, font=font_note)
draw.text(((width - note_width) / 2, 665), note, fill='#64748b', font=font_note)

img.save(out)
print(out)
