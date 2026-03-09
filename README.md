# Knulli Video Player — RG40XXV

Видео плеер для Anbernic RG40XXV с прошивкой Knulli.
Управление геймпадом, плейлист, субтитры, аудио треки.

## Зависимости

- Python 3.8+
- mpv (уже есть в Knulli)
- python-mpv
- pygame

## Установка

### 1. Скопируй файлы на устройство

Через SSH или SD карту скопируй папку `knulli_player/` в:

```
/userdata/roms/ports/knulli_player/
```

### 2. Установи зависимости (через SSH)

```bash
pip install python-mpv pygame --break-system-packages
```

### 3. Сделай скрипт исполняемым

```bash
chmod +x /userdata/roms/ports/knulli_player/launch.sh
```

### 4. Зарегистрируй как порт в Knulli

Создай файл `/userdata/roms/ports/KnulliPlayer.sh`:

```bash
#!/bin/bash
/userdata/roms/ports/knulli_player/launch.sh /userdata/videos
```

```bash
chmod +x /userdata/roms/ports/KnulliPlayer.sh
```

После этого плеер появится в разделе **Ports** в ES-DE/Batocera.

### 5. Видео файлы

Положи видео в:
```
/userdata/videos/
```

Поддерживаемые форматы: `.mp4 .mkv .avi .mov .wmv .flv .webm .m4v .ts .mpg .mpeg .3gp`

---

## Управление геймпадом

| Кнопка | Действие |
|--------|----------|
| **A** | Воспроизведение / Пауза |
| **B** | Назад / Стоп |
| **X** | Меню субтитров |
| **Y** | Меню аудио треков |
| **L1** | Перемотка −30 сек |
| **R1** | Перемотка +30 сек |
| **L2** | Предыдущий файл |
| **R2** | Следующий файл |
| **SELECT** | Плейлист / Список файлов |
| **START** | Показать OSD |
| **Левый стик ↑↓** | Навигация по списку |

---

## Запуск с параметром

```bash
python3 player.py /path/to/video.mkv      # конкретный файл
python3 player.py /path/to/folder/        # папка с видео
python3 player.py                          # ~/videos по умолчанию
```

---

## Структура

```
knulli_player/
├── player.py     — основной плеер
├── launch.sh     — лаунчер для Knulli
└── README.md     — этот файл
```

## Маппинг кнопок

Если кнопки работают неправильно, проверь через:
```bash
python3 -c "
import pygame; pygame.init(); pygame.joystick.init()
j = pygame.joystick.Joystick(0); j.init()
while True:
    pygame.event.pump()
    for i in range(j.get_numbuttons()):
        if j.get_button(i): print('Button:', i)
"
```

И поправь константы `BTN_*` в начале `player.py`.
