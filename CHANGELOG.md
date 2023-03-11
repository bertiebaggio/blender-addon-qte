# Changelog

## beta2 (2023-03-11)


### Features

* add additional temporal offset modes b4c4610
* add config panel for appearing words 8c1968f
* add linked time and frame offset options for splitting 4b29677
* add option to modify inter-word spacing 9bb1bed
* add split_to_appearing_words() operator 7876c0b


### Bug Fixes

* default setting of frame_offset in panel was bugged cf9f9c5
* defer getting a reference to 'SequencerCommon' keymap_items 35b7e59
* guard against negative frame_offset values d68cd2a
* hide offset options when using parent strip 11313d7
* remove circular update() on time/frame offsets aa981f2


## beta1 (2022-11-30)


### Features

* add presets with keybindings for: colour, location, size, duration
* give size and duration presets option to be relative
