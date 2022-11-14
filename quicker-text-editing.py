"""quicker-text-editing.py -- text addon for Blender VSE"""
import bpy

bl_info = {
    "name": "Quicker Text Editing for VSE",
    "author": "bertieb",
    "version": (0, 5),
    "blender": (3, 3, 0),
    "location": "Video Sequence Editor > Text Strip",
    "description": "Quicker editing of text: position, colour, size, duration",
    "warning": "",
    "doc_url": "",
    "category": "Sequencer",
}


class TextSequenceAction(bpy.types.Operator):
    """Implements operations for quickly manipulating text sequences in VSE"""
    bl_idname = "sequencer.textsequenceaction"
    bl_label = "Text Sequence Action"

    def execute(self, context):
        """One works on a text sequence... but does nothing!"""
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

    colour: bpy.props.FloatVectorProperty(
        name="Text colour",
        subtype='COLOR',
        description="Colour for text",
        size=4,
        min=0.0,
        max=1.0,
        default=(0.0, 0.0, 0.0, 1),  # black in RGBA
        )

    _colour = None

    _keymaps = []

    def __init__(self):
        super().__init__()
        if self._colour:
            self.colour = self._colour

    def execute(self, context):
        for strip in bpy.context.selected_editable_sequences:
            if strip.type == "TEXT":
                strip.color = self.colour

        return {'FINISHED'}


class SetTextLocation(TextSequenceAction):
    """Set location of text sequence[s]"""
    bl_idname = "sequencer.set_text_location"
    bl_label = "Set Text Location"

    _location = None

    location: bpy.props.FloatVectorProperty(
        name="Text location",
        subtype='COORDINATES',
        description="Location for text",
        size=2,
        min=-2000,
        max=2000,
        default=(0.5, 0.5)  # (x,y)
        )

    _location = None

    def __init__(self):
        super().__init__()
        if self._location:
            self.location = self._location

    def execute(self, context):
        for strip in bpy.context.selected_editable_sequences:
            if strip.type == "TEXT":
                strip.location = self.location

        return {'FINISHED'}


class SetTextDuration(TextSequenceAction):
    """Set location of text sequence[s]"""
    bl_idname = "sequencer.set_text_duration"
    bl_label = "Set Text Duration"

    duration: bpy.props.IntProperty(
        name="Duration (frames)",
        subtype='TIME_ABSOLUTE',
        description="Duration for text",
        min=1,
        max=1048574,
        default=60  # frames
        )

    _duration = None

    def __init__(self):
        super().__init__()
        if self._duration:
            self.duration = self._duration

    def execute(self, context):
        for strip in bpy.context.selected_editable_sequences:
            if strip.type == "TEXT":
                strip.frame_final_duration = self.duration

        return {'FINISHED'}


class SetTextSize(TextSequenceAction):
    """Set size of text sequence[s]"""
    bl_idname = "sequencer.set_text_size"
    bl_label = "Set Text Size"

    size: bpy.props.FloatProperty(
        name="Text font size",
        subtype='UNSIGNED',
        description="Size for text",
        min=0.0,
        max=2000.0,
        default=100.0  # font size
        )

    _size = None

    def __init__(self):
        super().__init__()
        if self._size:
            self.size = self._size

    def execute(self, context):
        for strip in bpy.context.selected_editable_sequences:
            if strip.type == "TEXT":
                strip.font_size = self.size

        return {'FINISHED'}


REGISTER_CLASSES = [SetTextLocation, SetTextDuration,
                    SetTextSize, SetTextColour]


def register():
    for classname in REGISTER_CLASSES:
        bpy.utils.register_class(classname)


def unregister():
    for classname in REGISTER_CLASSES:
        bpy.utils.unregister_class(classname)


if __name__ == "__main__":
    register()
