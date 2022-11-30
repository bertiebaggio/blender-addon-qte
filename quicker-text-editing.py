"""quicker-text-editing.py -- text addon for Blender VSE"""
import bpy

bl_info = {
    "name": "Quicker Text Editing for VSE",
    "author": "bertieb",
    "version": (0, 9),
    "blender": (3, 3, 0),
    "location": "Video Sequence Editor > Text Strip",
    "description": "Quicker editing of text strips: position, colour, size, duration",
    "warning": "",
    "doc_url": "",
    "category": "Sequencer",
}


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


REGISTER_CLASSES = [SetTextLocation, SetTextDuration,
                    SetTextSize, SetTextColour,
                    NewQTEColourPreset, NewQTELocationPreset,
                    NewQTESizePreset, NewQTEDurationPreset,
                    SAMPLE_OT_DirtyKeymap, QTERemoveKeyMapItem]
DYNAMIC_CLASSES = []
PREFERENCES_CLASSES = [LocationPresets,
                       SizePresets, DurationPresets,
                       QTEPreferences]


def register():
    for classname in REGISTER_CLASSES:
        bpy.utils.register_class(classname)
    for classname in PREFERENCES_CLASSES:
        bpy.utils.register_class(classname)


def unregister():
    for classname in REGISTER_CLASSES:
        bpy.utils.unregister_class(classname)
    for classname in PREFERENCES_CLASSES:
        bpy.utils.unregister_class(classname)


if __name__ == "__main__":
    register()
