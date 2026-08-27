# Transkribator

[![License: MIT](https://img.shields.io/badge/license-MIT-45d8c0.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-45d8c0.svg)](https://www.python.org/downloads/)
[![Powered by faster-whisper](https://img.shields.io/badge/powered%20by-faster--whisper-45d8c0.svg)](https://github.com/SYSTRAN/faster-whisper)

**[Читать по-русски](README.md)**

A simple tool: give it an audio recording (a meeting, a lecture,
anything) — it listens to it and gives you back text with timestamps.
Everything runs on your own computer: the recording itself is never
sent anywhere. The only thing downloaded from the internet is the
speech-recognition model itself, once, on first run.

Example output (`records/meeting.md`):

```
# Transcript: meeting.aac

**[00:00 – 00:07]** Good afternoon, let's start the meeting.

**[00:07 – 00:15]** First item on the agenda — next quarter's budget.
```

## What you need

- A computer (Windows, macOS, or Linux) — a dedicated GPU is not
  required, it also runs on a plain CPU, just slower.
- Python 3.10 or newer.
- An audio file to turn into text: `aac`, `mp3`, `wav`, `m4a`, `flac`,
  `ogg`, `opus`, `wma`, or audio from an `mp4`.
- 1–3 GB of free disk space for the speech-recognition model (depends
  on which model size you pick, see the table below).

No programming knowledge needed — the code is already written, you
just install it and run it.

## Quick start

### 1. Install Python

If Python isn't installed yet, download it from
[python.org](https://www.python.org/downloads/) (3.10 or newer). On
Windows, check "Add Python to PATH" during install.

Check it's installed:

```bash
python --version
```

### 2. Download the project

If you have git installed:

```bash
git clone https://github.com/NickolasZH/transkribator.git
cd transkribator
```

No git? On the GitHub repository page, click the green **Code →
Download ZIP** button, unzip it, and open a terminal in that folder.

### 3. Create a virtual environment and install dependencies

A virtual environment is an isolated "sandbox" for this project's
libraries, so they don't clash with anything else on your machine.

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### 4. Run it

Put your audio file somewhere, e.g. in the `records/` folder, and run:

```bash
python transcribe.py records/meeting.aac
```

On the first run, the program downloads the speech-recognition model
from the internet (can take a few minutes depending on your
connection). After that, it's already on disk, so every next run is
faster.

When it's done, a file with the same name and a `.md` extension
appears next to your audio file — that's your transcript with
timestamps.

## Which model to pick

The `--model` flag picks the size of the speech-recognition model. The
bigger the model, the more accurate it is, but also slower and larger:

| Model       | Accuracy            | Speed               | Disk size |
|-------------|-----------------------|------------------------|------------|
| `tiny`      | low                    | very fast              | ~75 MB     |
| `base`      | below average          | fast                    | ~150 MB    |
| `small`     | average                | medium                 | ~500 MB    |
| `medium`    | good (default)          | slower                 | ~1.5 GB    |
| `large-v3`  | best                   | slowest                | ~3 GB      |

Not sure? Leave the default (`medium`) — a reasonable balance of
quality and speed. For a quick rough draft, `small` or `base` work
well.

## All command-line options

```bash
python transcribe.py path/to/file.mp3 [options]
```

| Option         | What it does                                             | Default            |
|----------------|-------------------------------------------------------------|----------------------|
| `--model`      | model size: `tiny`/`base`/`small`/`medium`/`large-v3`        | `medium`             |
| `--language`   | language code, e.g. `en` or `ru`                              | auto-detected        |
| `--device`     | where to compute: `cpu` or `cuda` (NVIDIA GPU)                 | `cpu`                |
| `--output`     | where to save the result (custom `.md` path)                   | next to the audio    |

Example: quickly transcribe an English recording on a GPU with a small
model, saving to a custom path:

```bash
python transcribe.py records/meeting.aac --model small --language en --device cuda --output result.md
```

## FAQ

**The first run takes a long time — is that normal?**
Yes, the first run downloads the speech-recognition model from the
internet. Every following run with the same model is much faster
since it's already saved on disk.

**No internet — will it work at all?**
Internet is only needed once, to download the model. After that, it
works fully offline.

**I have a GPU — how do I use it?**
If you have an NVIDIA GPU with CUDA support, add `--device cuda` —
recognition will be noticeably faster. Without an NVIDIA GPU, use
`--device cpu` (already the default).

**Where do my recordings go?**
Nowhere. All processing happens locally on your computer. The only
internet request is downloading the model from Hugging Face on first
run.

**The program doesn't recognize my file's format**
The tested formats are listed above. Other formats might still work
(the program will warn you and try anyway), but there's no guarantee.
Easiest fix: convert the file to `mp3` or `wav` first.

**Something fails during install**
Make sure you're on Python 3.10+ (`python --version`) and that the
virtual environment is active (your terminal prompt should start with
`(.venv)`). If you see errors about missing packages, try upgrading
pip first: `python -m pip install --upgrade pip`.

## Project layout

```
transkribator/
├── transcribe.py       — the whole program, one file
├── requirements.txt    — libraries to install with pip
├── records/            — put your audio files here (not tracked by git)
├── README.md           — Russian version
├── README.en.md         — this file
└── CHANGELOG.md         — development log
```

## Built with

- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — a
  fast implementation of OpenAI's Whisper speech-recognition model.
- [PyAV](https://github.com/PyAV-Org/PyAV) — decodes any audio format;
  ffmpeg is bundled inside, no separate install needed.

## License

Released under the [MIT license](LICENSE) — free to use, copy, and
modify, including for commercial purposes.
