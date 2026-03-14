#!/bin/bash
# Knulli Video Player — first-run setup
# Run once as root on the device. Deletes itself when done.

PLAYER_DIR="/userdata/roms/ports/knulli_player"
VIDEOS_DIR="/userdata/videos"
XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"

echo "=== Knulli Video Player Setup ==="

# 1. Create directories
mkdir -p "$PLAYER_DIR"
mkdir -p "$VIDEOS_DIR"
echo "[OK] Directories created"

# 2. Make player executable
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

# 5. Find PortMaster / gptokeyb2
GPTOKEYB=""
if [ -f "/opt/system/Tools/PortMaster/gptokeyb2" ]; then
    GPTOKEYB="/opt/system/Tools/PortMaster/gptokeyb2"
elif [ -f "$XDG_DATA_HOME/PortMaster/gptokeyb2" ]; then
    GPTOKEYB="$XDG_DATA_HOME/PortMaster/gptokeyb2"
elif [ -f "/roms/ports/PortMaster/gptokeyb2" ]; then
    GPTOKEYB="/roms/ports/PortMaster/gptokeyb2"
fi

if [ -n "$GPTOKEYB" ]; then
    echo "[OK] gptokeyb2 found: $GPTOKEYB"
else
    echo "[!!] gptokeyb2 not found — gamepad may not work correctly from ES-DE"
    echo "     Install PortMaster to fix this"
fi

# 6. Create ES-DE launcher that runs player.py directly
LAUNCHER="/userdata/roms/ports/Knulli Video Player.sh"
cat > "$LAUNCHER" << LAUNCH
#!/bin/bash
# Knulli Video Player — ES-DE launcher

XDG_DATA_HOME=\${XDG_DATA_HOME:-\$HOME/.local/share}
PLAYER_DIR="/userdata/roms/ports/knulli_player"
VIDEO_DIR="/userdata/videos"

# Find PortMaster
if [ -d "/opt/system/Tools/PortMaster/" ]; then
    controlfolder="/opt/system/Tools/PortMaster"
elif [ -d "\$XDG_DATA_HOME/PortMaster/" ]; then
    controlfolder="\$XDG_DATA_HOME/PortMaster"
else
    controlfolder="/roms/ports/PortMaster"
fi

# Source PortMaster controls if available
if [ -f "\$controlfolder/control.txt" ]; then
    source "\$controlfolder/control.txt"
    [ -f "\${controlfolder}/mod_\${CFW_NAME}.txt" ] && source "\${controlfolder}/mod_\${CFW_NAME}.txt"
    get_controls 2>/dev/null || true
fi

# Clear screen
printf "\033c" > /dev/tty0

# Start gptokeyb2 for gamepad capture
GPTOKEYB="\$controlfolder/gptokeyb2"
if [ -f "\$GPTOKEYB" ]; then
    "\$GPTOKEYB" "python3" -c "\$PLAYER_DIR/keys.gptk" > /dev/null 2>&1 &
    GPTK_PID=\$!
fi

# Run player directly
python3 "\$PLAYER_DIR/player.py" "\$VIDEO_DIR" > /dev/null 2>"\$PLAYER_DIR/player.log"

# Kill gptokeyb2
if [ -n "\$GPTK_PID" ]; then
    kill "\$GPTK_PID" 2>/dev/null
fi

# Restore screen for ES-DE
printf "\033c" > /dev/tty0
LAUNCH

chmod +x "$LAUNCHER"
echo "[OK] ES-DE launcher created: $LAUNCHER"

# 7. Remove setup.sh and launch.sh — no longer needed
echo "[OK] Put your videos in: $VIDEOS_DIR"
echo ""
echo "=== Setup complete! ==="
echo "Launch from ES-DE → Ports → Knulli Video Player"
echo ""

# Self-destruct: remove this script and launch.sh
rm -f "$PLAYER_DIR/launch.sh"
rm -f "$PLAYER_DIR/Setup Knulli Video Player.sh"
