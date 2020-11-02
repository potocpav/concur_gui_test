from pathlib import Path

import concur as c
import imgui

font_name = "DejaVuSansCode_0.ttf"
font_name_2 = "Hack Regular Nerd Font Complete Mono Windows Compatible.ttf"
font_file = str(Path(__file__).parent / "src" / "resources" / font_name)
font_file_2 = str(Path(__file__).parent / "src" / "resources" / font_name_2)
imgui.create_context()
io = imgui.get_io()
font = io.fonts.add_font_from_file_ttf(font_file, 30, io.fonts.custom_glyph_ranges([
        0x0020, 0x00FF,
        0x2000, 0x206F,
        0x3000, 0x30FF,
        0x31F0, 0x31FF,
        0xFF00, 0xFFEF,
        0x4e00, 0x9FAF,
        ]))
io.fonts.add_font_from_file_ttf(font_file_2, 30, io.fonts.custom_glyph_ranges(
    [0x1f600, 0x1f800]),
    merge=True)

c.main(c.text("hello \U0001f600 汉字"))