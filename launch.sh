#!/bin/bash
# Knulli Video Player launcher

XDG_DATA_HOME=${XDG_DATA_HOME:-$HOME/.local/share}

# Найдём PortMaster
if [ -d "/opt/system/Tools/PortMaster/" ]; then
  controlfolder="/opt/system/Tools/PortMaster"
elif [ -d "$XDG_DATA_HOME/PortMaster/" ]; then
  controlfolder="$XDG_DATA_HOME/PortMaster"
else
  controlfolder="/roms/ports/PortMaster"
fi

# Подключаем PortMaster если есть
if [ -f "$controlfolder/control.txt" ]; then
  source "$controlfolder/control.txt"
  [ -f "${controlfolder}/mod_${CFW_NAME}.txt" ] && source "${controlfolder}/mod_${CFW_NAME}.txt"
  get_controls 2>/dev/null || true
fi

PLAYER_DIR="/userdata/roms/ports/knulli_player"
VIDEO_DIR="${1:-/userdata/videos}"

# Очищаем экран
printf "\033c" > /dev/tty0

# Запускаем gptokeyb2 чтобы он перехватил геймпад от ES-DE
GPTOKEYB="$controlfolder/gptokeyb2"
if [ -f "$GPTOKEYB" ]; then
  "$GPTOKEYB" "python3" -c "$PLAYER_DIR/keys.gptk" > /dev/null 2>&1 &
  GPTK_PID=$!
fi

# Запускаем плеер
python3 "$PLAYER_DIR/player.py" "$VIDEO_DIR" > /dev/null 2>"$PLAYER_DIR/player.log"

# Убиваем gptokeyb
if [ -n "$GPTK_PID" ]; then
  kill "$GPTK_PID" 2>/dev/null
fi

# Возвращаем управление ES-DE
printf "\033c" > /dev/tty0
