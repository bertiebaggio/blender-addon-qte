# 🔤 QTE: Quicker Text Editing for Blender VSE

Do you make videos in Blender? Do you work with lots of text sequences in the VSE? Do you wish it was faster to do common actions? Then QTE (pronounced 'cutie') is the Blender addon for you!

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
# Table of Contents

  - [Summary](#summary)
  - [Installation](#installation)
  - [Usage](#usage)
      - [Setting Presets and Hotkeys](#setting-presets-and-hotkeys)
      - [Splitting Text to Appearing Words](#splitting-text-to-appearing-words)
          - [Options](#options)
  - [Roadmap](#roadmap)
  - [Background and Development](#background-and-development)

<!-- markdown-toc end -->

## Summary

[![QTE 0.9b overview](https://i.imgur.com/1knC5wF.jpeg)](https://i.imgur.com/1knC5wF.jpeg)

QTE lets you bind hotkeys for common actions on text strips, like setting colour or location. This is helpful if you have a lot of text sequences, such as for subtitles.

## Installation

Download quicker-text-editing.py from the releases section, then add it to Blender from Preferences > Add-ons > Install... (from file)

QTE was developed against the [Blender 3.3 API](https://docs.blender.org/api/current/index.html), and has not been tested with earlier versions. If you are on an earlier version, either upgrade or use at your own risk!

## Usage

### Setting Presets and Hotkeys
To add an action, go to Preferences > Add-ons, make sure 'Quicker text editing for VSE' is enabled, then add a colour, location, size or duration preset. You can then set what it to be applied (eg a colour), and the key combo to apply this.

### Splitting Text to Appearing Words

The 'Convert to appearing words' button is located in the 'Style' section of the N panel (sidebar), with further options in the 'QTE' tab.

This operator takes a text strip with multiple words and splits it into individual text strips. These created strips are offset in both time (so they 'appear' as playback progresses) and space (so they appear in the same place they would as if they were in the original text strip.

#### Options

There are options to adjust the timing of words appearing:

  - Fixed: New strips will be this number of frames / seconds ahead of previous strip _(default: 0.5)_
  - Offset adjusted by word length: Strips will adjust timing based on the length of the previous word compared to the average (longer words = bigger gap)
  - Parent Duration (Equally-divided): New strips will appear at equally-distributed times based on parent strip duration divided by number of words
  - Parent Duration (Relative to word length): New strips will use the duration of the parent sentence strip and appear at times proportional to the word length (longer words = bigger gap)

There is also an option to adjust the inter-word spacing:

 - Extra word spacing: Increase or decrease horizontal space between words _(default: 0)_

## Roadmap

The following features are one of: planned, nice-to-have, or pie-in-the-sky. Not all have been evaulated for how feasible they are.

- change focus to new text sequence when copying and pasting a strip
- quick focus on text property in sidebar for entering text
- auto-size text to fit screen

## Background and Development

Improvements, feature suggestions and PRs are very welcome.

If you want to know more about the background for this addon, I have a [series of posts](https://blog.roberthallam.org/tag/qte) that cover the why, how and what.
