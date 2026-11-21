# The Dare Game v2.3

A mobile-first, offline-friendly friends party game. The core loop is simple: **play a fair group mini-game → decide the winner and loser from the result → reveal a dare for the loser.**

## Party Arena
- 3–8 players on one phone (three sample players are prefilled; rename or add players)
- Six group mini-games: Reflex Rush, Memory Flash, Category Clash, Emoji Decode, Secret Target, and Act It Out
- Each game has its own flow and scoring; every player participates
- Ties lead to a rematch — no dare is assigned on a tied round
- A dare is shown only after a completed game identifies a loser
- Dares can be skipped or swapped; no forced changes or purchases

## Dare library
- 100 explained dares across Makeup & Beauty, Clothes & Fashion, Hairstyle, Accessories, Funny & Special, and Special Challenges
- Completed dare history is saved locally and excluded from future draws

## Android APK
Pushes to the Android app source trigger the GitHub Actions debug APK build. Download **The-Dare-Game-APK** from the latest successful workflow run.

## Current scope
The current build is offline pass-and-play on one device. It does not include online matchmaking or a remote multiplayer server.
