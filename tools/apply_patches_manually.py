#!/usr/bin/env python3
"""Manually apply the bootstrap patch changes to build/upstream."""

import sys
from pathlib import Path

UPSTREAM = Path(__file__).parents[1] / "build" / "upstream"

def apply_audio_rules():
    """Apply changes to audio_rules.mk"""
    file = UPSTREAM / "audio_rules.mk"
    content = file.read_text()
    old = """$(SONG_BUILDDIR)/%.o: $(SONG_SUBDIR)/%.s
	$(AS) $(ASFLAGS) -I sound -o $@ $<
$(MID_BUILDDIR)/%.o: $(MID_ASM_DIR)/%.s
	$(AS) $(ASFLAGS) -I sound -o $@ $<"""
    new = """$(SONG_BUILDDIR)/%.o: $(SONG_SUBDIR)/%.s
	$(ASM_PSEUDO_OP_CONV) $< | $(AS) $(ASFLAGS) -I sound -o $@
	$(FIX_UNDERSCORE) $@
$(MID_BUILDDIR)/%.o: $(MID_ASM_DIR)/%.s
	$(ASM_PSEUDO_OP_CONV) $< | $(AS) $(ASFLAGS) -I sound -o $@
	$(FIX_UNDERSCORE) $@"""
    if old in content:
        content = content.replace(old, new)
        file.write_text(content)
        print(f"Applied audio_rules.mk")
    else:
        print(f"Warning: audio_rules.mk pattern not found")

def apply_graphics_rules():
    """Apply changes to graphics_file_rules.mk"""
    file = UPSTREAM / "graphics_file_rules.mk"
    content = file.read_text()
    old = "\tdd if=/dev/zero bs=1 count=12 >> $@"
    new = "\thead -c 12 /dev/zero >> $@"
    if old in content:
        content = content.replace(old, new)
        file.write_text(content)
        print(f"Applied graphics_file_rules.mk")
    else:
        print(f"Warning: graphics_file_rules.mk pattern not found")

def apply_map_data_rules():
    """Apply changes to map_data_rules.mk"""
    file = UPSTREAM / "map_data_rules.mk"
    content = file.read_text()
    old1 = """$(DATA_ASM_BUILDDIR)/maps.o: $(DATA_ASM_SUBDIR)/maps.s $(LAYOUTS_DIR)/layouts.inc $(LAYOUTS_DIR)/layouts_table.inc $(MAPS_DIR)/headers.inc $(MAPS_DIR)/groups.inc $(MAPS_DIR)/connections.inc $(MAP_CONNECTIONS) $(MAP_HEADERS)
	$(PREPROC) $< charmap.txt | $(CPP) -I include - | $(PREPROC) -ie $< charmap.txt | $(AS) $(ASFLAGS) -o $@"""
    new1 = """$(DATA_ASM_BUILDDIR)/maps.o: $(DATA_ASM_SUBDIR)/maps.s $(LAYOUTS_DIR)/layouts.inc $(LAYOUTS_DIR)/layouts_table.inc $(MAPS_DIR)/headers.inc $(MAPS_DIR)/groups.inc $(MAPS_DIR)/connections.inc $(MAP_CONNECTIONS) $(MAP_HEADERS)
	$(PREPROC) $< charmap.txt | $(CPP) -I include - | $(PREPROC) -ie $< charmap.txt | $(ASM_PSEUDO_OP_CONV) - | $(AS) $(ASFLAGS) -o $@
	$(FIX_UNDERSCORE) $@"""

    old2 = """$(DATA_ASM_BUILDDIR)/map_events.o: $(DATA_ASM_SUBDIR)/map_events.s $(MAPS_DIR)/events.inc $(MAP_EVENTS)
	$(PREPROC) $< charmap.txt | $(CPP) -I include - | $(PREPROC) -ie $< charmap.txt | $(AS) $(ASFLAGS) -o $@"""
    new2 = """$(DATA_ASM_BUILDDIR)/map_events.o: $(DATA_ASM_SUBDIR)/map_events.s $(MAPS_DIR)/events.inc $(MAP_EVENTS)
	$(PREPROC) $< charmap.txt | $(CPP) -I include - | $(PREPROC) -ie $< charmap.txt | $(ASM_PSEUDO_OP_CONV) - | $(AS) $(ASFLAGS) -o $@
	$(FIX_UNDERSCORE) $@"""

    changed = False
    if old1 in content:
        content = content.replace(old1, new1)
        changed = True
    if old2 in content:
        content = content.replace(old2, new2)
        changed = True
    if changed:
        file.write_text(content)
        print(f"Applied map_data_rules.mk")
    else:
        print(f"Warning: map_data_rules.mk patterns not found")

def apply_mapjson():
    """Apply changes to tools/mapjson/mapjson.cpp"""
    file = UPSTREAM / "tools" / "mapjson" / "mapjson.cpp"
    content = file.read_text()
    old1 = """    text << "enum\\n{\\n";

    int group_num = 0;

    for (auto &group : groups_data["group_order"].array_items()) {
        string groupName = json_to_string(group);
        text << "    // " << groupName << "\\n";"""
    new1 = """    int group_num = 0;

    for (auto &group : groups_data["group_order"].array_items()) {
        string groupName = json_to_string(group);
        text << "// " << groupName << "\\n";"""

    old2 = """            text << "    " << map_id << string(max_length - map_id.length(), ' ')
                 << " = (" << map_id_num++ << " | (" << group_num << " << 8)),\\n";"""
    new2 = """            text << "#define " << map_id << string((max_length - map_id.length() + 1), ' ')
                 << "(" << map_id_num++ << " | (" << group_num << " << 8))\\n";"""

    old3 = """    }

    text << "};\\n\\n";"""
    new3 = """    }"""

    changed = False
    if old1 in content:
        content = content.replace(old1, new1)
        changed = True
    if old2 in content:
        content = content.replace(old2, new2)
        changed = True
    if old3 in content:
        content = content.replace(old3, new3)
        changed = True
    if changed:
        file.write_text(content)
        print(f"Applied tools/mapjson/mapjson.cpp")
    else:
        print(f"Warning: tools/mapjson/mapjson.cpp patterns not found")

def apply_mid2agb():
    """Apply changes to tools/mid2agb/agb.cpp"""
    file = UPSTREAM / "tools" / "mid2agb" / "agb.cpp"
    content = file.read_text()
    changes = [
        ("\tstd::fprintf(g_outputFile, \"\\t .word\\t\"", "\tstd::fprintf(g_outputFile, \"\\t .4byte\\t\""),
        ("\tstd::fprintf(g_outputFile, \"\\n@**************** Track %u (Midi-Chn.%u) ****************@\\n\\n\", g_agbTrack, g_midiChan + 1)", "//std::fprintf(g_outputFile, \"\\n@**************** Track %u (Midi-Chn.%u) ****************@\\n\\n\", g_agbTrack, g_midiChan + 1)"),
        ("int wholeNoteCount = 0", "int wholeNoteCount __attribute__((unused)) = 0"),
        ("\t\tstd::fprintf(g_outputFile, \"@ %03d   ----------------------------------------\\n\", wholeNoteCount++)", "\t\twholeNoteCount++; //std::fprintf(g_outputFile, \"@ %03d   ----------------------------------------\\n\", wholeNoteCount++)"),
        ("\tstd::fprintf(g_outputFile, \"\\n@******************************************************@\\n\"", "//std::fprintf(g_outputFile, \"\\n@******************************************************@\\n\""),
        ("\tstd::fprintf(g_outputFile, \"\\t.byte\\t%u\\t@ NumTrks\\n\", trackCount)", "\tstd::fprintf(g_outputFile, \"\\t.byte\\t%u\\n\", trackCount)"),
        ("\tstd::fprintf(g_outputFile, \"\\t.byte\\t%u\\t@ NumBlks\\n\", 0)", "\tstd::fprintf(g_outputFile, \"\\t.byte\\t%u\\n\", 0)"),
        ("\tstd::fprintf(g_outputFile, \"\\t.byte\\t%s_pri\\t@ Priority\\n\", g_asmLabel.c_str())", "\tstd::fprintf(g_outputFile, \"\\t.byte\\t%s_pri\\n\", g_asmLabel.c_str())"),
        ("\tstd::fprintf(g_outputFile, \"\\t.byte\\t%s_rev\\t@ Reverb.\\n\", g_asmLabel.c_str())", "\tstd::fprintf(g_outputFile, \"\\t.byte\\t%s_rev\\n\", g_asmLabel.c_str())"),
        ("\tstd::fprintf(g_outputFile, \"\\t.word\\t%s_grp\\n\", g_asmLabel.c_str())", "\tstd::fprintf(g_outputFile, \"\\t.4byte\\t%s_grp\\n\", g_asmLabel.c_str())"),
        ("\t\tstd::fprintf(g_outputFile, \"\\t.word\\t%s_%u\\n\", g_asmLabel.c_str(), i)", "\t\tstd::fprintf(g_outputFile, \"\\t.4byte\\t%s_%u\\n\", g_asmLabel.c_str(), i)"),
    ]
    changed = False
    for old, new in changes:
        if old in content:
            content = content.replace(old, new)
            changed = True
    if changed:
        file.write_text(content)
        print(f"Applied tools/mid2agb/agb.cpp")
    else:
        print(f"Warning: tools/mid2agb/agb.cpp patterns not found")

def apply_preproc_cpp():
    """Apply changes to tools/preproc/asm_file.cpp"""
    file = UPSTREAM / "tools" / "preproc" / "asm_file.cpp"
    content = file.read_text()
    old = """        if (m_buffer[m_pos] == '#')
        {
            currentHeaderLine = ParseLineSkipInEnum();
        }
        else if (m_buffer[m_pos] != ',')"""
    new = """        if (m_buffer[m_pos] != ',')"""
    if old in content:
        content = content.replace(old, new)
        file.write_text(content)
        print(f"Applied tools/preproc/asm_file.cpp")
    else:
        print(f"Warning: tools/preproc/asm_file.cpp pattern not found")

def apply_preproc_h():
    """Apply changes to tools/preproc/asm_file.h"""
    file = UPSTREAM / "tools" / "preproc" / "asm_file.h"
    content = file.read_text()
    old = "    int ParseLineSkipInEnum(void);"
    new = ""
    if old in content:
        content = content.replace(old, new)
        file.write_text(content)
        print(f"Applied tools/preproc/asm_file.h")
    else:
        print(f"Warning: tools/preproc/asm_file.h pattern not found")

if __name__ == "__main__":
    print("Applying manual patch changes to build/upstream...")
    apply_audio_rules()
    apply_graphics_rules()
    apply_map_data_rules()
    apply_mapjson()
    apply_mid2agb()
    apply_preproc_cpp()
    apply_preproc_h()
    print("Done!")
