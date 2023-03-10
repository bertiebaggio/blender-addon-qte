"""quicker-text-editing.py -- text addon for Blender VSE"""
from os import path
import bpy
import blf

bl_info = {
    "name": "Quicker Text Editing for VSE",
    "author": "bertieb",
    "version": (0, 10, 1),
    "blender": (3, 3, 0),
    "location": "Video Sequence Editor > Text Strip",
    "description": "Quicker editing of text strips: position, colour, size, duration",
    "warning": "",
    "doc_url": "",
    "category": "Sequencer",
}

# BEGIN text sequence manipulation (colour/location/etc)


class TextSequenceAction(bpy.types.Operator):
    """Implements operations for quickly manipulating text sequences in VSE"""
    bl_idname = "sequencer.textsequenceaction"
    bl_label = "Text Sequence Action"

    def execute(self, context):
        return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        """Ensure we're in the VSE with at least one sequence selected"""
        return (context.scene and context.scene.sequence_editor
                and context.selected_editable_sequences is not None)


class SetTextColour(TextSequenceAction):
    """Set colour of text sequence[s]"""
    bl_idname = "sequencer.set_text_colour"
    bl_label = "Set Text Colour"

    name: bpy.props.StringProperty(
        name="Name",
        description="Name to identify colour preset",
    )

    colour: bpy.props.FloatVectorProperty(
        name="Text colour",
        subtype='COLOR',
        description="Colour for text",
        size=4,
        min=0.0,
        max=1.0,
        default=(0.0, 0.0, 1.0, 1),  # blue in RGBA
        )

    def execute(self, context):
        for strip in bpy.context.selected_editable_sequences:
            if strip.type == "TEXT":
                strip.color = self.colour

        return {'FINISHED'}


class SetTextLocation(TextSequenceAction):
    """Set location of text sequence[s]"""
    bl_idname = "sequencer.set_text_location"
    bl_label = "Set Text Location"

    name: bpy.props.StringProperty(
        name="Name",
        description="Name for this location preset",
    )

    location: bpy.props.FloatVectorProperty(
        name="Location",
        subtype='COORDINATES',
        description="Location for text",
        size=2,
        min=-2000,
        max=2000,
        default=(0.5, 0.5)  # (x,y)
        )

    def execute(self, context):
        for strip in bpy.context.selected_editable_sequences:
            if strip.type == "TEXT":
                strip.location = self.location

        return {'FINISHED'}


class SetTextDuration(TextSequenceAction):
    """Set location of text sequence[s]"""
    bl_idname = "sequencer.set_text_duration"
    bl_label = "Set Text Duration"

    name: bpy.props.StringProperty(
        name="Name",
        description="Name for this duration preset",
    )

    duration: bpy.props.IntProperty(
        name="Duration",
        subtype='NONE',
        description="Duration for text",
        min=-1048574,
        max=1048574,
        default=60  # frames
        )

    relative: bpy.props.BoolProperty(
        name="Relative",
        description="Is size change relative?",
        default=False,
    )

    def execute(self, context):
        for strip in bpy.context.selected_editable_sequences:
            if strip.type == "TEXT":
                if not self.relative:
                    strip.frame_final_duration = self.duration
                else:
                    strip.frame_final_duration += self.duration

        return {'FINISHED'}


class SetTextSize(TextSequenceAction):
    """Set size of text sequence[s]"""
    bl_idname = "sequencer.set_text_size"
    bl_label = "Set Text Size"

    name: bpy.props.StringProperty(
        name="Name",
        description="Name for this size preset",
    )
    size: bpy.props.FloatProperty(
        name="Size",
        subtype='NONE',
        description="Size for text",
        min=-2000.0,
        max=2000.0,
        default=100.0  # font size
        )

    relative: bpy.props.BoolProperty(
        name="Relative",
        description="Is size change relative?",
        default=False,
    )

    def execute(self, context):
        for strip in bpy.context.selected_editable_sequences:
            if strip.type == "TEXT":
                if not self.relative:
                    strip.font_size = self.size
                else:
                    strip.font_size += self.size

        return {'FINISHED'}


class SAMPLE_OT_DirtyKeymap(bpy.types.Operator):
    """Borrowed operator for getting KeyMapInstance properties to apply"""
    bl_idname = "qte.sample_dirty_keymap"
    bl_label = "Save Keymap"

    def execute(self, context):
        km = context.window_manager.keyconfigs.addon.keymaps["Sequencer"]
        km.show_expanded_items = km.show_expanded_items
        for kmi in km.keymap_items:
            kmi.active = kmi.active
        context.preferences.is_dirty = True
        return {'FINISHED'}


class NewQTEPreset():
    """Common actions for presets (shouldn't be used directly)"""

    _keymap_id = 'SequencerCommon'
    _keymap_space_type = 'SEQUENCE_EDITOR'

    def get_keymap(self, context):
        """Get sequencer keymap"""
        km = context.window_manager.keyconfigs.user.keymaps
        skm = km.get(self._keymap_id)
        if not skm:
            skm = km.new(self._keymap_id, self._keymap_space_type)
        return skm


class NewQTEColourPreset(bpy.types.Operator, NewQTEPreset):
    """Create a new QTE colour preset"""
    bl_idname = "qte.new_colour_preset"
    bl_label = "Add colour preset"

    def newkeymapitem(self, context):
        wm = context.window_manager
        km = wm.keyconfigs.user.keymaps.get("SequencerCommon")
        if km is None:
            km = wm.keyconfigs.user.keymaps.new(
                "SequencerCommon", space_type='SEQUENCE_EDITOR')

        kmi = km.keymap_items.new("sequencer.set_text_colour", 'F5', 'PRESS')
        opattrs = getattr(bpy.types,
                          bpy.ops.sequencer.set_text_colour.idname()
                          ).__annotations__
        # The intent here is to get the attributes defined in the operator
        # class; it feels awkward and there may be a better way, but at
        # least *appears* to work
        #
        # See also:
        # https://blender.stackexchange.com/questions/216211/how-to-get-operator-defaults
        # https://developer.blender.org/T87465
        kmi.properties.colour = opattrs['colour'].keywords['default']
        kmi.properties.name = opattrs['name'].keywords['name']

        return kmi

    def execute(self, context):
        self.newkeymapitem(context)

        return {'FINISHED'}


class LocationPresets(bpy.types.PropertyGroup):
    """A PropertyGroup to define the structure of user presets (locations)"""
    name: bpy.props.StringProperty(
        name="Name",
        description="Location preset",
        default="One"
    )

    location: bpy.props.FloatVectorProperty(
        name="Text location",
        subtype='COORDINATES',
        description="Location for text",
        size=2,
        min=0.0,
        max=1.0,
        default=(0.5, 0.5),  # (x, y)
        )


class NewQTELocationPreset(bpy.types.Operator):
    """Create a new QTE location preset"""
    bl_idname = "qte.new_location_preset"
    bl_label = "Add location preset"

    def newkeymapitem(self, context, preset):
        wm = context.window_manager
        km = wm.keyconfigs.user.keymaps.get("SequencerCommon")
        if km is None:
            km = wm.keyconfigs.user.keymaps.new(
                "SequencerCommon", space_type='SEQUENCE_EDITOR')

        kmi = km.keymap_items.new("sequencer.set_text_location", 'F5', 'PRESS')
        kmi.properties.location = preset.location
        kmi.properties.name = ""

        return kmi

    def execute(self, context):
        # this could be refactored (see NewQTEColourPreset)
        addonprefs = context.preferences.addons[__name__].preferences
        newpreset = addonprefs.location_presets.add()
        newpreset.keymapitemid = self.newkeymapitem(context, newpreset).id

        return {'FINISHED'}


class SizePresets(bpy.types.PropertyGroup):
    """A PropertyGroup to define the structure of user presets (sizes)"""
    name: bpy.props.StringProperty(
        name="Name",
        description="Size preset",
        default="One"
    )

    size: bpy.props.FloatProperty(
        name="Size",
        subtype='NONE',
        description="Size for text",
        min=-2000.0,
        max=2000.0,
        default=100.0  # font size
        )

    relative: bpy.props.BoolProperty(
        name="Relative",
        description="Is size change relative?",
        default=False,
    )


class NewQTESizePreset(bpy.types.Operator):
    """Create a new QTE size preset"""
    bl_idname = "qte.new_size_preset"
    bl_label = "Add size preset"

    def newkeymapitem(self, context, preset):
        wm = context.window_manager
        km = wm.keyconfigs.user.keymaps.get("SequencerCommon")
        if km is None:
            km = wm.keyconfigs.user.keymaps.new(
                "SequencerCommon", space_type='SEQUENCE_EDITOR')

        kmi = km.keymap_items.new("sequencer.set_text_size", 'F5', 'PRESS')
        kmi.properties.size = preset.size
        kmi.properties.name = ""
        kmi.properties.relative = preset.relative

        return kmi

    def execute(self, context):
        # this could be refactored (see NewQTEColourPreset)
        addonprefs = context.preferences.addons[__name__].preferences
        newpreset = addonprefs.size_presets.add()
        newpreset.keymapitemid = self.newkeymapitem(context, newpreset).id

        return {'FINISHED'}


class DurationPresets(bpy.types.PropertyGroup):
    """A PropertyGroup to define the structure of user presets (durations)"""
    name: bpy.props.StringProperty(
        name="Name",
        description="Duration preset",
        default="One"
    )

    duration: bpy.props.IntProperty(
        name="Duration",
        subtype='NONE',
        description="Duration for text",
        min=-1048574,
        max=1048574,
        default=60  # 60 frames = 1 sec @ 60 FPS
        )

    relative: bpy.props.BoolProperty(
        name="Relative",
        description="Is duration change relative?",
        default=False,
    )

    keymapitemid: bpy.props.IntProperty(
        name="Key",
    )


class NewQTEDurationPreset(bpy.types.Operator):
    """Create a new QTE duration preset"""
    bl_idname = "qte.new_duration_preset"
    bl_label = "Add duration preset"

    def newkeymapitem(self, context, preset):
        wm = context.window_manager
        km = wm.keyconfigs.user.keymaps.get("SequencerCommon")
        if km is None:
            km = wm.keyconfigs.user.keymaps.new(
                "SequencerCommon", space_type='SEQUENCE_EDITOR')

        kmi = km.keymap_items.new("sequencer.set_text_duration", 'F5', 'PRESS')
        if not kmi:
            self.report({'ERROR', "No KeyMapItem! f{kmi}"})
        kmi.properties.duration = preset.duration
        kmi.properties.relative = preset.relative
        kmi.properties.name = preset.name

        return kmi

    def execute(self, context):
        # this could be refactored (see NewQTEColourPreset)
        addonprefs = context.preferences.addons[__name__].preferences
        newpreset = addonprefs.duration_presets.add()
        newpreset.keymapitemid = self.newkeymapitem(context, newpreset).id

        return {'FINISHED'}


class QTERemoveKeyMapItem(bpy.types.Operator):
    """Remove a kemapitem by id"""
    bl_idname = "qte.remove_keymapitem"
    bl_label = "Remove KeyMapItem (by id)"

    id: bpy.props.IntProperty(
        name="ID",
    )

    _kmi = bpy.context.window_manager.\
        keyconfigs.user.keymaps['SequencerCommon'].keymap_items

    def execute(self, context):
        if self.id is None:
            raise ValueError("Please supply an id to remove!")
        self._kmi.remove(self._kmi.from_id(self.id))

        return {'FINISHED'}


class QTEPreferences(bpy.types.AddonPreferences, NewQTEPreset):
    """Draw preferences for QTE addon. This means an interface for:
    - the presets and their bindings
      - colors
      - positions
      - sizes / relative size changes
      - durations / relative duration changes
    - a 'save bindings' button
    later:
      - export presets + bindings
      - toggle panel[s]
    """
    bl_idname = __name__

    duration_presets: bpy.props.CollectionProperty(type=DurationPresets)
    location_presets: bpy.props.CollectionProperty(type=LocationPresets)
    size_presets: bpy.props.CollectionProperty(type=SizePresets)

    def draw(self, context):
        layout = self.layout

        # Colour presets
        box = layout.box()
        # Walk layouts in SequencerCommon keymap in user keymaps
        # (for set_text_colour operator)
        for kmi in [kmi for kmi in context.window_manager.keyconfigs.user
                    .keymaps['SequencerCommon'].keymap_items.values()
                    if kmi.idname == "sequencer.set_text_colour"]:
            row = box.row()
            row.prop(kmi.properties, "name")
            row.prop(kmi.properties, "colour")
            row.prop(kmi, "type", text="", full_event=True)
            row.operator(
                "qte.remove_keymapitem",
                text="",
                icon='X'
            ).id = kmi.id

        box.operator("qte.new_colour_preset", icon='ADD')

        # Location presets
        box = layout.box()
        for kmi in [kmi for kmi in context.window_manager.keyconfigs.user
                    .keymaps['SequencerCommon'].keymap_items.values()
                    if kmi.idname == "sequencer.set_text_location"]:
            row = box.row()
            row.prop(kmi.properties, "name")
            row.prop(kmi.properties, "location")
            row.prop(kmi, "type", text="", full_event=True)
            row.operator(
                "qte.remove_keymapitem",
                text="",
                icon='X'
            ).id = kmi.id

        box.operator("qte.new_location_preset", icon='ADD')

        # Size presets
        box = layout.box()
        for kmi in [kmi for kmi in context.window_manager.keyconfigs.user
                    .keymaps['SequencerCommon'].keymap_items.values()
                    if kmi.idname == "sequencer.set_text_size"]:
            row = box.row()
            row.prop(kmi.properties, "name")
            row.prop(kmi.properties, "size")
            row.prop(kmi.properties, "relative")
            row.prop(kmi, "type", text="", full_event=True)
            row.operator(
                "qte.remove_keymapitem",
                text="",
                icon='X'
            ).id = kmi.id

        box.operator("qte.new_size_preset", icon='ADD')

        # Duration presets
        box = layout.box()
        for kmi in [kmi for kmi in context.window_manager.keyconfigs.user
                    .keymaps['SequencerCommon'].keymap_items.values()
                    if kmi.idname == "sequencer.set_text_duration"]:
            row = box.row()
            row.prop(kmi.properties, "name")
            row.prop(kmi.properties, "duration")
            row.prop(kmi.properties, "relative")
            row.prop(kmi, "type", text="", full_event=True)
            row.operator(
                "qte.remove_keymapitem",
                text="",
                icon='X'
            ).id = kmi.id

        box.operator("qte.new_duration_preset", icon='ADD')


# END text sequence manipulation (colour/location/etc)

# BEGIN split to appearing words

# TODO: Ask question if it is common / good practice to 'pull out'
# enum items this way
aw_temporal_offset_options = [
    ("Fixed", "Fixed Offset",
     "New strips will be this number of frames / seconds ahead of previous strip"),
    ("RelativeLength", "Time Offset adjusted by word length",
     "Strips will adjust timing based on the length of the previous word \
compared to the average (ie longer words = bigger gap)"),
    ("ParentEqual", "Use Parent Duration (Equally-divided)",
     "New strips will use the duration of the parent sentence strip \
and appear at equally-distributed times"),
    ("ParentRelativeLength", "Use Parent Duration (Relative to word length)",
     "New strips will use the duration of the parent sentence strip \
and appear at times proportional to the word length (longer words = bigger gap)"),
]


class AppearingWordsOptions(bpy.types.PropertyGroup):
    """Holds the options. This is needed as both the operator itself
    and any panels for configuration need access to the options

    See:
    - https://blenderartists.org/t/storing-property-in-operator-which-can-be-set-by-ui-panel/1332800/3
    - https://blenderartists.org/t/is-storing-operator-options-in-the-scene-window-manager-etc-still-the-way-to-go-in-2023/1454103
    """
    def __init__(self, *args, **kwargs):
        self.time_offset = 1.0
        self.frame_offset = int(self.time_offset * self.get_fps())

    def get_fps(self):
        return float(bpy.context.scene.render.fps / bpy.context.scene.render.fps_base)

    def update_frames_from_time(self, context):
        """When time offset changes, update the frame gap to match (based on FPS)"""
        self.frame_offset = int(self.time_offset * self.get_fps())

    def update_time_from_frames(self, context):
        """When frame offset changes, update the time gap to match (based on FPS)"""
        self.time_offset = self.frame_offset / self.get_fps()

    time_offset: bpy.props.FloatProperty(
        name="Time offset",
        default=1,
        min=0.0,
        soft_max=5,
        step=5,
        description="Time between words appearing",
        update=update_frames_from_time,
    )

    frame_offset: bpy.props.IntProperty(
        name="Frame offset",
        default=0,
        min=0,
        soft_max=300,
        step=5,
        description="Frames between words appearing",
        update=update_time_from_frames,
    )

    temporal_offset_type: bpy.props.EnumProperty(
        name="Time offset type",
        description="How to set the time gap between words appearing",
        items=aw_temporal_offset_options,
    )


class SEQUENCER_OT_split_to_appearing_words(TextSequenceAction):
    """Split the text in a text sequence to several text sequences

    The words should appear one after another in both time and space"""

    bl_label = "Convert to appearing words"
    bl_idname = "sequencer.split_to_appearing_words"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        """Ensure we're in the VSE with at least one sequence selected"""
        return (context.scene and context.scene.sequence_editor
                and context.selected_editable_sequences is not None)

    def execute(self, context):
        """Do the actual creation of new strips"""
        # TODO: inter-word spacing adjustments

        def get_strip_text_size(strip, text=None):
            """get the size of supplied text based on strip font in px"""
            def get_fontid_from_path(filepath=None) -> int:
                """given a filepath, use blf to get a fontid -- does not perform sanity checking!
                """
                # this is a horrible workaround, see
                # https://devtalk.blender.org/t/getting-a-font-from-fontid-or-fontid-from-vectorfont-textsequence/28183/2
                # for more info
                return blf.load(path.normpath(bpy.path.abspath(filepath)))

            fontid = get_fontid_from_path(filepath=strip.font.filepath)
            blf.size(fontid, strip.font_size)
            return blf.dimensions(fontid, text)

        prop_group = context.window_manager.appearing_text_options
        scene = context.scene
        rez_x = scene.render.resolution_x

        # sanity check (FUTURE: see if there's a way to work on multiple in a sensible way)
        if len(context.selected_editable_sequences) != 1:
            self.report({"ERROR"}, "This only works on one text sequence at a time")
            return {"CANCELLED"}

        sequence = context.selected_editable_sequences[0]

        # next sanity check: text sequence with > 1 word
        if sequence.type != 'TEXT':
            self.report({"ERROR"}, "This should only be availabe on text sequences!")
            return {"CANCELLED"}

        if len(sequence.text.split(" ")) <= 1:
            self.report({"ERROR"}, "This requires more than one word to split on")
            return {"CANCELLED"}

        # main body of work
        previous_strip = None
        ts_words = sequence.text.split(" ")
        ts_letters_count = sum(map(len, ts_words))
        average_word_length = ts_letters_count / len(ts_words)

        for i, word in enumerate(ts_words):
            # Give new strip the same properties as the old one
            # Assumption: duplicate() changes selection to newly-created strip
            # so we can use that selection to reference the new strip
            bpy.ops.sequencer.duplicate()
            new_strip = context.selected_editable_sequences[0]
            new_strip.name = f"split_word_{i}"

            # Set times for new strip
            # NB since strip is duplicated, no need to set first strip's (i==0) start_frame
            # TODO: minimum length
            if i > 0:
                if prop_group.temporal_offset_type == "Fixed":
                    # All fixed offset
                    offset = prop_group.frame_offset
                if prop_group.temporal_offset_type == "RelativeLength":
                    # relative to the 'fixed offset', some will be shorter and some will be longer
                    # based on the length of word compared to average
                    offset = prop_group.frame_offset * \
                        (len(previous_strip.text) / average_word_length)
                elif prop_group.temporal_offset_type == "ParentEqual":
                    # All the same but based on parent duration
                    offset = int(sequence.frame_final_duration / len(ts_words))
                elif prop_group.temporal_offset_type == "ParentRelativeLength":
                    # Relative to parent duration but modified by previous word length
                    # eg 'of' (short) 'farce' (medium) 'narrativism' (long)
                    # use average from 'ParentEqual' multipled by wordlength/averagelength
                    offset = int(sequence.frame_final_duration / len(ts_words)) * \
                        (len(previous_strip.text) / average_word_length)
                new_strip.frame_start = int(previous_strip.frame_start + offset)
            new_strip.frame_final_end = int(sequence.frame_final_end)
            new_strip.channel = (sequence.channel+1+i)

            # Set position for new strip
            # For the first strip (i=0), set location to 'parent' strip. For subsequent
            # strips, use the position of the previous strip plus the length of the word
            # plus an inter-word offset.
            #
            # Start from parent strip's location and alignment
            #
            # Maybe TO DO: line splitting
            if i == 0:
                new_strip.location[0] = sequence.location[0]
            else:
                # New location is previous strip location
                #  + previous strip width
                #  + width of space
                new_strip.location[0] = previous_strip.location[0] + \
                    (get_strip_text_size(sequence, text=previous_strip.text)[0] / rez_x) + \
                    (get_strip_text_size(sequence, text=" ")[0] / rez_x)

            new_strip.text = word

            # feels smelly, but keep a reference for the next loop for location
            previous_strip = new_strip

        sequence.mute = True

        context.scene.frame_current = int(sequence.frame_start + sequence.frame_final_duration - 1)

        return {'FINISHED'}


class SEQUENCER_PT_appearing_text(bpy.types.Panel):
    """Panel for appearing text"""
    bl_label = "Appearing Words"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        """Draw the appearing text panel"""
        prop_group = context.window_manager.appearing_text_options
        layout = self.layout

        layout.label(text="Time Offset Type", icon='TEMP')
        layout.prop(prop_group, "temporal_offset_type", text="")
        # identifiers = [enum_item[0] for enum_item in aw_temporal_offset_options]
        # selected_item_index = identifiers.index(prop_group.temporal_offset_type)
        # for line in [line for line
        #              in aw_temporal_offset_options[
        # selected_item_index][2].split(".") if len(line)]:
        #     # layout.label(text=aw_temporal_offset_options[selected_item_index][2])
        #     layout.label(text=line)
        layout.separator()

        if prop_group.temporal_offset_type != "ParentEqual":
            layout.prop(prop_group, "time_offset", slider=True)
            layout.prop(prop_group, "frame_offset", slider=True)
        layout.separator(factor=2.0)
        box = layout.box()
        box.operator("sequencer.split_to_appearing_words", icon='OUTLINER')


def appearing_text_panel_layout(self, context):
    """Set up panel for appearing text: operator button plus options"""
    self.layout.separator()
    self.layout.operator("sequencer.split_to_appearing_words")


REGISTER_CLASSES = [SetTextLocation, SetTextDuration,
                    SetTextSize, SetTextColour,
                    NewQTEColourPreset, NewQTELocationPreset,
                    NewQTESizePreset, NewQTEDurationPreset,
                    SAMPLE_OT_DirtyKeymap, QTERemoveKeyMapItem,
                    SEQUENCER_OT_split_to_appearing_words,
                    SEQUENCER_PT_appearing_text]
DYNAMIC_CLASSES = []
PREFERENCES_CLASSES = [LocationPresets,
                       SizePresets, DurationPresets,
                       AppearingWordsOptions,
                       QTEPreferences]


def register():
    for classname in REGISTER_CLASSES:
        bpy.utils.register_class(classname)
    for classname in PREFERENCES_CLASSES:
        bpy.utils.register_class(classname)
    bpy.types.SEQUENCER_PT_effect.append(appearing_text_panel_layout)

    bpy.types.WindowManager.appearing_text_options = \
        bpy.props.PointerProperty(type=AppearingWordsOptions)


def unregister():
    for classname in REGISTER_CLASSES:
        bpy.utils.unregister_class(classname)
    for classname in PREFERENCES_CLASSES:
        bpy.utils.unregister_class(classname)
    bpy.types.SEQUENCER_PT_effect.remove(appearing_text_panel_layout)

    del bpy.types.WindowManager.appearing_text_options


if __name__ == "__main__":
    register()
