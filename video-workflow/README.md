# Phone-first video workflow

This folder is the cloud workspace for the Dare Game video experiments.

## Folders
- `Raw-Footage/`: original footage and voice recordings.
- `Reference/`: reference videos used to study pacing, typography, transitions, colors and editing style.
- `Output/`: local workflow output; final files are uploaded as GitHub Actions artifacts.

## Free tools used on GitHub's cloud runner
- **FFmpeg / ffprobe** — media inspection, frame extraction and video processing.
- **OpenAI Whisper** — speech transcription, including multilingual/Hindi audio.
- **HyperFrames** — open-source HTML/CSS-to-MP4 composition/rendering framework. The runner checks that its CLI is available; a project-specific composition will be added after the first media/style analysis.

These tools are installed in the temporary GitHub Actions runner when the workflow runs. They are not installed on your Android phone. GitHub Actions usage has plan/repository limits; it is not unlimited cloud computing.

## Phone workflow
1. Open the repository in Chrome.
2. Upload your original clip(s) into `video-workflow/Raw-Footage/`.
3. Upload the reference clip into `video-workflow/Reference/`.
4. Open **Actions → Video Workflow → Run workflow**.
5. When it finishes, download the `video-workflow-output` artifact from that run.

The first pass creates media metadata, reference stills, and transcripts. It does not pretend to have completed a creative edit: the edit plan and HyperFrames composition are refined from the actual footage and reference.

Supported input: MP4, MOV, M4V, WEBM, MKV, WAV, MP3, M4A, AAC.
