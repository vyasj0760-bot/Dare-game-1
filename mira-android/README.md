# Mira Android Companion — v0.1

This is a separate Android app project. It does not modify the original Dare Game HTML app or the Mira cloud-brain folder.

## Included in this first APK
- User-started floating overlay with Android's "Display over other apps" permission.
- Drag the character around the screen.
- Tap to switch between idle, walking and talking poses.
- Bundled 3-pose character atlas, decoded once and kept in an in-memory LruCache.
- Foreground notification while the overlay is active.

## Not included yet
- Live AI/cloud connection, voice input/output, persistent chat memory, phone actions, sitting animation, and full emotion set.
- The three poses are an initial animation pass, not a complete frame-by-frame animation rig.

## Build
The GitHub Actions workflow builds a debug APK at:
`app/build/outputs/apk/debug/app-debug.apk`

The artwork is bundled locally, so no artwork download or network cache is needed at runtime. The decoded bitmap is cached in memory while the process is alive.

## Android permissions
The app asks the user to enable "Display over other apps". The floating character only starts after the user taps Start. Android shows a foreground notification while it is active.
