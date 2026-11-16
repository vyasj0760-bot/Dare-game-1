# Mira Android Companion — v0.2

This is a separate Android app project. It does not modify the original Dare Game HTML app or the Mira cloud-brain folder.

## Included
- User-started floating overlay using Android's "Display over other apps" permission.
- Drag Mira around the screen.
- Tap to switch between idle, walking, and expressive/talking animation groups.
- 3×3 character atlas bundled in the APK and cropped into nine animation frames.
- Smooth bobbing / motion scaling between frames.
- Decoded artwork reused through an 8 MiB in-memory LRU bitmap cache.
- Foreground notification while the overlay is active.

## Not included yet
- Live AI/cloud connection, voice input/output, persistent chat memory, phone actions, and sitting animation.
- Emotion-specific controls and a full animation rig. Current animation groups use the nine bundled atlas poses.

## Storage and cache
The artwork is bundled in the APK, so Mira does not download it again at runtime. The decoded atlas is cached in memory while the process is alive; Android may clear that memory when it needs it. No large AI model is stored on the phone.

## Build and test
GitHub Actions builds a debug APK at `app/build/outputs/apk/debug/app-debug.apk`. The workflow checks that the APK exists and that its package name is `com.mvyas.mira`. This CI check does not replace a real install-and-run test on a physical Android phone.

## Permissions
The user must manually enable "Display over other apps" and tap Start. Android displays an ongoing foreground-service notification while Mira floats.
