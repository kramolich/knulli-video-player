#!/bin/bash
# Knulli Video Player — first-run setup
# Run once as root on the device

PLAYER_DIR="/userdata/roms/ports/knulli_player"
VIDEOS_DIR="/userdata/videos"
PM_DIR="/userdata/system/.local/share/PortMaster"

echo "=== Knulli Video Player Setup ==="

# 1. Create directories
mkdir -p "$PLAYER_DIR"
mkdir -p "$VIDEOS_DIR"
echo "[OK] Directories created"

# 2. Make scripts executable
chmod +x "$PLAYER_DIR/launch.sh"
chmod +x "$PLAYER_DIR/player.py"
echo "[OK] Permissions set"

# 3. Check ffmpeg
if command -v ffmpeg &>/dev/null; then
    echo "[OK] ffmpeg found: $(ffmpeg -version 2>&1 | head -1)"
else
    echo "[!!] ffmpeg not found — video playback will not work"
fi

# 4. Check python3 + pygame
if python3 -c "import pygame" &>/dev/null; then
    echo "[OK] python3 + pygame found"
else
    echo "[!!] pygame not found — trying to install..."
    pip install pygame --break-system-packages 2>/dev/null || \
        echo "[!!] Could not install pygame"
fi

# 5. Check gptokeyb2 for gamepad capture
if [ -f "$PM_DIR/gptokeyb2" ]; then
    echo "[OK] gptokeyb2 found"
else
    echo "[!!] gptokeyb2 not found at $PM_DIR/gptokeyb2"
    echo "     Gamepad may not work correctly from ES-DE"
    echo "     Install PortMaster to fix this"
fi

# 6. Create .knulli_player.sh launcher in ports root (ES-DE picks it up)
LAUNCHER="/userdata/roms/ports/Knulli Video Player.sh"
cat > "$LAUNCHER" << 'LAUNCH'
#!/bin/bash
bash "/userdata/roms/ports/knulli_player/launch.sh"
LAUNCH
chmod +x "$LAUNCHER"
echo "[OK] ES-DE launcher created: $LAUNCHER"

# 7. Create videos dir symlink hint
echo "[OK] Put your videos in: $VIDEOS_DIR"

echo ""
echo "=== Setup complete! ==="
echo "Launch from ES-DE → Ports → Knulli Video Player"
