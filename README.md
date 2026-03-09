# Knulli Video Player

A terminal-style video player for Anbernic handhelds running Knulli or Batocera firmware. No extra dependencies — everything needed is already included in Knulli/Batocera out of the box.

Built with ffmpeg (direct framebuffer output) and pygame for the UI.

**Tested on:** Anbernic RG40XXV / Knulli

---

## Features

- Gamepad-only navigation
- Folder browser with nested directory support
- Resume playback from last position
- Multi audio track selection (saved as preference)
- Sort files by duration or name
- Background duration scanning on startup
- 5 terminal color themes: Terminal, Dracula, Solarized, Monokai, Nord
- Adjustable font size: Small / Medium / Large
- Restart current video with SELECT

---

## Requirements

No installation needed. The following are already included in Knulli/Batocera:

- Python 3.11+
- pygame 2.5+
- ffmpeg 7.x
- ffprobe

---

## Installation

1. Copy the `knulli_player/` folder to your device via SSH or SD card:

```
/userdata/roms/ports/knulli_player/
```

2. Run setup once via SSH:

```bash
bash /userdata/roms/ports/knulli_player/setup.sh
```

This sets permissions, creates the ES-DE launcher, and creates the `/userdata/videos/` folder automatically.

3. Put your videos in:

```
/userdata/videos/
```

The player will appear in the **Ports** section in ES-DE.

---

## Controls

| Button | Action |
|--------|--------|
| A | Play / Confirm |
| B | Back |
| X | Audio track selection |
| Y | Sort by duration |
| L1 / R1 | Seek −30s / +30s |
| L2 / R2 | Previous / Next file |
| SELECT | Rescan folder / Restart video |
| START | Main menu |
| D-pad / Stick | Navigate |

---

## Supported formats

`.mp4` `.mkv` `.avi` `.mov` `.wmv` `.flv` `.webm` `.m4v` `.ts` `.mpg` `.mpeg` `.3gp`

---

## Main menu (START)

| Item | Description |
|------|-------------|
| About | Author and engine info |
| Controls | Button reference |
| Theme | Choose color theme |
| Font Size | Small / Medium / Large |
| Exit | Quit the player |

---

## Manual launch

```bash
python3 /userdata/roms/ports/knulli_player/player.py /userdata/videos
```

---

## File structure

```
knulli_player/
├── player.py     — main player
├── launch.sh     — Knulli / ES-DE launcher
├── setup.sh      — first-run setup script
├── keys.gptk     — gamepad mapping for gptokeyb2
├── LICENSE
└── README.md
```

---

## Author

**KRAMOLICH**  
Built for Knulli / Batocera handheld gaming devices.
