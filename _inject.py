"""Re-inject ASCII art with corrected sizing and centering."""
from lxml import etree

SVG_NS = 'http://www.w3.org/2000/svg'

def inject(svg_file, txt_file, padding=20, left_panel_width=390, fill_ratio=0.75):
    tree = etree.parse(svg_file)
    root = tree.getroot()
    el = root.find(f".//{{{SVG_NS}}}*[@id='ascii_art']")

    svg_height = int(root.get('height', '530px').replace('px', ''))

    with open(txt_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    num_lines = len(lines)
    max_chars = max(len(line.rstrip()) for line in lines)

    char_width_ratio = 0.59
    available_width = left_panel_width - 2 * padding
    font_from_width = (available_width * fill_ratio) / (max_chars * char_width_ratio)

    available_height = svg_height - 2 * padding
    y_step = available_height / (num_lines - 1) if num_lines > 1 else available_height
    font_from_height = y_step

    font_size = round(min(font_from_width, font_from_height))

    text_block_width = max_chars * char_width_ratio * font_size
    total_text_height = (num_lines - 1) * y_step
    x_start = (left_panel_width - text_block_width) / 2
    y_start = (svg_height - total_text_height) / 2

    el.set('font-size', f'{font_size}px')
    if 'text-anchor' in el.attrib:
        del el.attrib['text-anchor']

    for child in list(el):
        el.remove(child)
    el.text = '\n'

    for i, line in enumerate(lines):
        tspan = etree.SubElement(el, 'tspan')
        tspan.set('x', str(round(x_start)))
        tspan.set('y', str(round(y_start + i * y_step)))
        tspan.text = line.rstrip('\n').rstrip('\r')
        tspan.tail = '\n'

    tree.write(svg_file, encoding='utf-8', xml_declaration=True)
    print(f"{svg_file}: {num_lines} lines, font={font_size}px (width_limit={font_from_width:.0f}, height_limit={font_from_height:.0f})")
    print(f"  x_start={round(x_start)}, y={round(y_start)}-{round(y_start+total_text_height)}, y_step={y_step:.1f}px, text_width={text_block_width:.0f}px")

inject('dark_mode.svg', 'assets/ascii-text-art.txt')
inject('light_mode.svg', 'assets/ascii-text-art.txt')
