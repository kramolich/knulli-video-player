#!/usr/bin/env python3
"""
Knulli Video Player — RG40XXV
Author: KRAMOLICH
Engine: ffmpeg + pygame
"""

import os, sys, subprocess, signal, threading, json, re
import pygame

def first_run_setup():
    """Auto-setup on first run."""
    player_dir = '/userdata/roms/ports/knulli_player'
    flag = os.path.join(player_dir, '.setup_done')
    if os.path.exists(flag): return
    try:
        # Make scripts executable
        for f in ['launch.sh', 'player.py', 'setup.sh']:
            p = os.path.join(player_dir, f)
            if os.path.exists(p): os.chmod(p, 0o755)
        # Create ES-DE launcher
        launcher = '/userdata/roms/ports/Knulli Video Player.sh'
        if not os.path.exists(launcher):
            with open(launcher, 'w') as f:
                f.write('#!/bin/bash\nbash "/userdata/roms/ports/knulli_player/launch.sh"\n')
            os.chmod(launcher, 0o755)
        # Create videos dir
        os.makedirs('/userdata/videos', exist_ok=True)
        # Mark done
        with open(flag, 'w') as f: f.write('ok')
    except: pass

# ── Config ────────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 640, 480
FPS        = 30
FB_DEV     = '/dev/fb0'
AUDIO_OUT  = 'default'
VIDEO_DIR  = '/userdata/videos'
RESUME_FILE = '/userdata/roms/ports/knulli_player/.resume.json'
PREFS_FILE  = '/userdata/roms/ports/knulli_player/.prefs.json'

def get_volume():
    try:
        r = subprocess.run(['amixer','get','Master'],
            capture_output=True, text=True, timeout=2)
        import re
        m = re.search(r'\[(\d+)%\]', r.stdout)
        return int(m.group(1)) if m else 50
    except: return 50

def set_volume(vol):
    vol = max(0, min(100, vol))
    try:
        subprocess.run(['amixer','set','Master',f'{vol}%'],
            capture_output=True, timeout=2)
    except: pass
    return vol

VIDEO_EXTS = {'.mp4','.mkv','.avi','.mov','.wmv','.flv',
              '.webm','.m4v','.ts','.mpg','.mpeg','.3gp'}

# Gamepad (Anbernic RG40XX-V)
BTN_A=3; BTN_B=4; BTN_X=5; BTN_Y=6
BTN_L1=7; BTN_R1=8; BTN_L2=13; BTN_R2=14
BTN_SELECT=9; BTN_START=10
AXIS_LY=1; AXIS_LX=0
HAT_UP=(0,1); HAT_DOWN=(0,-1); HAT_LEFT=(-1,0); HAT_RIGHT=(1,0)

THEMES = {
    'terminal': {
        'name': 'Terminal',
        'C_BG':      (0,0,0),
        'C_ACCENT':  (0,255,70),
        'C_TEXT':    (200,255,200),
        'C_DIM':     (0,140,40),
        'C_SEL_BG':  (0,30,0),
        'C_SEL_LINE':(0,255,70),
        'C_BAR_BG':  (0,40,0),
        'C_BAR_FG':  (0,255,70),
    },
    'dracula': {
        'name': 'Dracula',
        'C_BG':      (40,42,54),
        'C_ACCENT':  (189,147,249),
        'C_TEXT':    (248,248,242),
        'C_DIM':     (98,114,164),
        'C_SEL_BG':  (68,71,90),
        'C_SEL_LINE':(255,121,198),
        'C_BAR_BG':  (55,57,69),
        'C_BAR_FG':  (189,147,249),
    },
    'solarized': {
        'name': 'Solarized',
        'C_BG':      (0,43,54),
        'C_ACCENT':  (38,139,210),
        'C_TEXT':    (131,148,150),
        'C_DIM':     (88,110,117),
        'C_SEL_BG':  (7,54,66),
        'C_SEL_LINE':(42,161,152),
        'C_BAR_BG':  (0,33,43),
        'C_BAR_FG':  (38,139,210),
    },
    'monokai': {
        'name': 'Monokai',
        'C_BG':      (39,40,34),
        'C_ACCENT':  (166,226,46),
        'C_TEXT':    (248,248,242),
        'C_DIM':     (117,113,94),
        'C_SEL_BG':  (62,61,50),
        'C_SEL_LINE':(249,38,114),
        'C_BAR_BG':  (49,48,40),
        'C_BAR_FG':  (166,226,46),
    },
    'nord': {
        'name': 'Nord',
        'C_BG':      (46,52,64),
        'C_ACCENT':  (136,192,208),
        'C_TEXT':    (236,239,244),
        'C_DIM':     (76,86,106),
        'C_SEL_BG':  (59,66,82),
        'C_SEL_LINE':(129,161,193),
        'C_BAR_BG':  (46,52,64),
        'C_BAR_FG':  (136,192,208),
    },
    'gruvbox': {
        'name': 'Gruvbox',
        'C_BG':      (40,40,40),
        'C_ACCENT':  (184,187,38),
        'C_TEXT':    (235,219,178),
        'C_DIM':     (146,131,116),
        'C_SEL_BG':  (60,56,54),
        'C_SEL_LINE':(214,93,14),
        'C_BAR_BG':  (50,48,47),
        'C_BAR_FG':  (184,187,38),
    },
    'onedark': {
        'name': 'One Dark',
        'C_BG':      (40,44,52),
        'C_ACCENT':  (97,175,239),
        'C_TEXT':    (171,178,191),
        'C_DIM':     (92,99,112),
        'C_SEL_BG':  (44,47,55),
        'C_SEL_LINE':(198,120,221),
        'C_BAR_BG':  (33,37,43),
        'C_BAR_FG':  (97,175,239),
    },
    'cyberpunk': {
        'name': 'Cyberpunk',
        'C_BG':      (10,0,20),
        'C_ACCENT':  (255,0,200),
        'C_TEXT':    (0,255,220),
        'C_DIM':     (100,0,120),
        'C_SEL_BG':  (30,0,50),
        'C_SEL_LINE':(255,220,0),
        'C_BAR_BG':  (20,0,35),
        'C_BAR_FG':  (255,0,200),
    },
}
THEME_KEYS = list(THEMES.keys())

def apply_theme(name):
    global C_BG,C_ACCENT,C_TEXT,C_DIM,C_SEL_BG,C_SEL_LINE,C_BAR_BG,C_BAR_FG
    t = THEMES.get(name, THEMES['terminal'])
    C_BG=t['C_BG']; C_ACCENT=t['C_ACCENT']; C_TEXT=t['C_TEXT']
    C_DIM=t['C_DIM']; C_SEL_BG=t['C_SEL_BG']; C_SEL_LINE=t['C_SEL_LINE']
    C_BAR_BG=t['C_BAR_BG']; C_BAR_FG=t['C_BAR_FG']

# Default theme (overridden by prefs on startup)
C_BG=(0,0,0); C_ACCENT=(0,255,70); C_TEXT=(200,255,200)
C_DIM=(0,140,40); C_SEL_BG=(0,30,0); C_SEL_LINE=(0,255,70)
C_BAR_BG=(0,40,0); C_BAR_FG=(0,255,70)

# ── Helpers ───────────────────────────────────────────────────────────────────

def fmt(s):
    if s is None or s<0: return "--:--"
    s=int(s); h=s//3600; m=(s%3600)//60; s=s%60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

def trunc(t,n): return t if len(t)<=n else t[:n-1]+"…"

FONT_SIZES = {
    'small':  {'lg':18,'md':14,'sm':11, 'label':'Small'},
    'medium': {'lg':20,'md':16,'sm':13, 'label':'Medium'},
    'large':  {'lg':23,'md':19,'sm':15, 'label':'Large'},
}
FONT_SIZE_KEYS = list(FONT_SIZES.keys())

def make_fonts(size='medium'):
    sz = FONT_SIZES.get(size, FONT_SIZES['medium'])
    try:
        return {k:pygame.font.SysFont("dejavusans",sz[k],bold=b)
                for k,b in [('lg',True),('md',False),('sm',False)]}
    except:
        return {'lg':pygame.font.Font(None,sz['lg']+4),
                'md':pygame.font.Font(None,sz['md']+4),
                'sm':pygame.font.Font(None,sz['sm']+4)}

# ── Persistence ───────────────────────────────────────────────────────────────

def load_json(path):
    try:
        with open(path) as f: return json.load(f)
    except: return {}

def save_json(path, data):
    try:
        with open(path,'w') as f: json.dump(data, f)
    except: pass

def load_resume(): return load_json(RESUME_FILE)
def save_resume(data): save_json(RESUME_FILE, data)
def load_prefs(): return load_json(PREFS_FILE)
def save_prefs(data): save_json(PREFS_FILE, data)

# ── File scanning ─────────────────────────────────────────────────────────────

def scan_dir(folder):
    """Returns (folders, files) in folder — not recursive."""
    folders, files = [], []
    try:
        for e in sorted(os.scandir(folder), key=lambda x: x.name.lower()):
            if e.is_dir():
                folders.append(e.path)
            elif e.is_file() and os.path.splitext(e.name)[1].lower() in VIDEO_EXTS:
                files.append(e.path)
    except: pass
    return folders, files

def count_all_videos(folder):
    """Recursively count all videos."""
    count = 0
    try:
        for e in os.scandir(folder):
            if e.is_file() and os.path.splitext(e.name)[1].lower() in VIDEO_EXTS:
                count += 1
            elif e.is_dir():
                count += count_all_videos(e.path)
    except: pass
    return count

def probe(path):
    try:
        r=subprocess.run(['ffprobe','-v','quiet','-print_format','json',
            '-show_streams','-show_format',path],
            capture_output=True,text=True,timeout=8)
        data=json.loads(r.stdout)
        duration=float(data.get('format',{}).get('duration',0))
        audio=[]
        for s in data.get('streams',[]):
            if s.get('codec_type')=='audio':
                lang=(s.get('tags',{}).get('language','') or
                      s.get('tags',{}).get('title','') or
                      f"Track {len(audio)+1}")
                audio.append({'index':s['index'],'lang':lang})
        return {'duration':duration,'audio':audio}
    except: return {'duration':0.0,'audio':[]}

# ── ffmpeg Backend ────────────────────────────────────────────────────────────

TIME_RE=re.compile(r'time=(\d+):(\d+):(\d+\.\d+)')

class Backend:
    def __init__(self):
        self._proc=None; self._lock=threading.Lock()
        self.position=0.0; self.duration=0.0
        self._current_path=None; self.audio_idx=None
        self._seek_start=0.0

    def load(self, path, seek=0.0, audio_idx=None):
        self._current_path=path; self._seek_start=seek
        self.stop()
        self.position=seek; self.audio_idx=audio_idx
        cmd=['ffmpeg','-loglevel','info']
        if seek>1.0: cmd+=['-ss',str(seek)]
        cmd+=['-re','-i',path,
              '-vf',f'scale={SCREEN_W}:{SCREEN_H}',
              '-pix_fmt','bgra','-f','fbdev',FB_DEV]
        if audio_idx is not None: cmd+=['-map',f'0:{audio_idx}']
        else: cmd+=['-map','0:a:0']
        cmd+=['-f','alsa',AUDIO_OUT]
        with self._lock:
            self._proc=subprocess.Popen(cmd,stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,text=True)
        threading.Thread(target=self._read,daemon=True).start()

    def _read(self):
        try:
            for line in self._proc.stderr:
                m=TIME_RE.search(line)
                if m:
                    h,mi,s=int(m.group(1)),int(m.group(2)),float(m.group(3))
                    self.position=self._seek_start+h*3600+mi*60+s
        except: pass

    def seek(self, delta):
        if not self._current_path: return
        new=max(0.0, self.position+delta)
        if self.duration>0: new=min(new, self.duration-2)
        self.load(self._current_path, seek=new, audio_idx=self.audio_idx)

    def set_audio(self, path, audio_idx):
        self.load(path, seek=self.position, audio_idx=audio_idx)

    def stop(self):
        with self._lock:
            if self._proc:
                try:
                    self._proc.terminate(); self._proc.wait(timeout=2)
                except:
                    try: self._proc.kill()
                    except: pass
                self._proc=None

    @property
    def is_eof(self):
        with self._lock:
            return self._proc is not None and self._proc.poll() is not None

# ── Drawing ───────────────────────────────────────────────────────────────────

class Draw:
    def __init__(self,s,f): self.s=s; self.f=f

    def browser(self, folders, files, sel, cur_file, durations, resume,
                current_folder, root_folder, total_root, sort_mode, audio_counts={}):
        s,f=self.s,self.f; s.fill(C_BG)

        # Header
        is_root = current_folder == root_folder
        if is_root:
            right_txt = f"{total_root} videos total"
        else:
            local_count = len(files) + sum(count_all_videos(d) for d in folders)
            right_txt = f"{local_count} videos here"

        pygame.draw.line(s,C_ACCENT,(0,36),(SCREEN_W,36),1)
        s.blit(f['lg'].render("> VIDEO PLAYER_",True,C_ACCENT),(12,9))
        rt=f['sm'].render(right_txt,True,C_DIM)
        s.blit(rt,(SCREEN_W-rt.get_width()-12,12))

        # Sort indicator
        sort_lbl = f['sm'].render("[X] ↓dur" if sort_mode==1 else ("[X] ↑dur" if sort_mode==2 else ""),True,C_DIM)
        s.blit(sort_lbl,(SCREEN_W-sort_lbl.get_width()-12,24))

        # Build item list: [..] parent + folders + files
        items = []
        if current_folder != root_folder:
            items.append({'type':'parent','path':os.path.dirname(current_folder)})
        for d in folders:
            items.append({'type':'folder','path':d})
        for fp in files:
            items.append({'type':'file','path':fp})

        ih=34; vis=(SCREEN_H-72)//ih
        start=max(0,sel-vis//2); end=min(len(items),start+vis)

        for i,idx in enumerate(range(start,end)):
            y=40+i*ih; item=items[idx]
            issel=idx==sel
            if issel:
                pygame.draw.rect(s,C_SEL_BG,(0,y,SCREEN_W,ih-2))
                pygame.draw.rect(s,C_SEL_LINE,(0,y,2,ih-2))

            if item['type']=='parent':
                label="[..] .."
                color=C_ACCENT if issel else C_DIM
                s.blit(f['md'].render(label,True,color),(10,y+9))

            elif item['type']=='folder':
                name=os.path.basename(item['path'])
                label=f"[{trunc(name,40)}]"
                color=C_ACCENT if issel else C_TEXT
                s.blit(f['md'].render(label,True,color),(10,y+9))

            else:
                fp=item['path']
                name=os.path.splitext(os.path.basename(fp))[0]
                is_cur=fp==cur_file
                color=C_ACCENT if issel else (C_TEXT if is_cur else C_DIM)
                icon="▶ " if is_cur else "  "

                dur=durations.get(fp,0)
                pos=resume.get(fp,0.0)
                if dur>0:
                    time_str=f"{fmt(pos)}/{fmt(dur)}"
                    # audio count badge
                    # (shown later)
                else:
                    time_str=f"{fmt(pos)}/--:--" if pos>0 else ""

                acount=audio_counts.get(fp,0)
                badge=f" [{acount}]" if acount>1 else ""
                max_name=26 if time_str else (38 if badge else 42)
                s.blit(f['md'].render(icon+trunc(name,max_name)+badge,True,color),(10,y+9))
                if time_str:
                    ts=f['sm'].render(time_str,True,C_DIM if not issel else C_ACCENT)
                    s.blit(ts,(SCREEN_W-ts.get_width()-12,y+11))

        # Scrollbar
        if len(items)>vis:
            sh=SCREEN_H-72; th=max(20,sh*vis//len(items))
            ty=40+sh*start//len(items)
            pygame.draw.rect(s,(0,20,0),(SCREEN_W-5,40,5,sh))
            pygame.draw.rect(s,C_ACCENT,(SCREEN_W-5,ty,5,th))

        # Bottom hint
        pygame.draw.line(s,C_DIM,(0,SCREEN_H-34),(SCREEN_W,SCREEN_H-34),1)
        h=f['sm'].render("A:Play  B:Back  X:Audio  Y:Sort  START:Menu  SELECT:Rescan",True,C_DIM)
        s.blit(h,((SCREEN_W-h.get_width())//2,SCREEN_H-22))

        return items  # return for hit-testing

    def audio_menu(self,tracks,sel,cur):
        s,f=self.s,self.f; s.fill(C_BG)
        w=320; h=min(len(tracks)*32+52,300)
        x=(SCREEN_W-w)//2; y=(SCREEN_H-h)//2
        pygame.draw.rect(s,C_SEL_BG,(x,y,w,h))
        pygame.draw.rect(s,C_ACCENT,(x,y,w,h),1)
        t=f['lg'].render("Audio Tracks",True,C_ACCENT)
        s.blit(t,(x+(w-t.get_width())//2,y+8))
        pygame.draw.line(s,C_DIM,(x,y+28),(x+w,y+28),1)
        for i,(idx,lang) in enumerate(tracks):
            ty=y+32+i*32; issel=i==sel; iact=i==cur
            if issel:
                pygame.draw.rect(s,C_SEL_BG,(x+2,ty,w-4,28))
                pygame.draw.rect(s,C_SEL_LINE,(x+2,ty,2,28))
            color=C_ACCENT if iact else (C_TEXT if issel else C_DIM)
            s.blit(f['md'].render(("✓ " if iact else "  ")+trunc(lang,28),True,color),(x+12,ty+6))
        h2=f['sm'].render("A:Select  B:Close",True,C_DIM)
        s.blit(h2,(x+(w-h2.get_width())//2,y+h-18))

    def main_menu(self, items, sel):
        s,f=self.s,self.f; s.fill(C_BG)
        pygame.draw.line(s,C_ACCENT,(0,36),(SCREEN_W,36),1)
        s.blit(f['lg'].render("> MENU_",True,C_ACCENT),(12,9))
        ih=40
        for i,item in enumerate(items):
            y=60+i*ih; issel=i==sel
            if issel:
                pygame.draw.rect(s,C_SEL_BG,(0,y,SCREEN_W,ih-2))
                pygame.draw.rect(s,C_SEL_LINE,(0,y,2,ih-2))
            color=C_ACCENT if issel else C_TEXT
            s.blit(f['md'].render(("  > " if issel else "    ")+item,True,color),(10,y+11))
        pygame.draw.line(s,C_DIM,(0,SCREEN_H-34),(SCREEN_W,SCREEN_H-34),1)
        h=f['sm'].render("A:Select  B:Close",True,C_DIM)
        s.blit(h,((SCREEN_W-h.get_width())//2,SCREEN_H-22))

    def info_page(self, title, lines):
        s,f=self.s,self.f; s.fill(C_BG)
        pygame.draw.line(s,C_ACCENT,(0,36),(SCREEN_W,36),1)
        s.blit(f['lg'].render(f"> {title}_",True,C_ACCENT),(12,9))
        for i,line in enumerate(lines):
            color=C_ACCENT if line.startswith("  #") else (C_TEXT if ":" in line else C_DIM)
            text=line.replace("  #","  ")
            s.blit(f['md'].render(text,True,color),(20,46+i*24))
        pygame.draw.line(s,C_DIM,(0,SCREEN_H-34),(SCREEN_W,SCREEN_H-34),1)
        h=f['sm'].render("Any button to go back",True,C_DIM)
        s.blit(h,((SCREEN_W-h.get_width())//2,SCREEN_H-22))

    def theme_page(self, theme_sel):
        s,f=self.s,self.f; s.fill(C_BG)
        pygame.draw.line(s,C_ACCENT,(0,36),(SCREEN_W,36),1)
        s.blit(f['lg'].render("> THEME_",True,C_ACCENT),(12,9))
        ih=44
        for i,key in enumerate(THEME_KEYS):
            t=THEMES[key]; y=50+i*ih; issel=i==theme_sel
            # Preview swatch
            pygame.draw.rect(s,t['C_BG'],(20,y,80,32))
            pygame.draw.rect(s,t['C_ACCENT'],(20,y,80,32),1)
            pygame.draw.rect(s,t['C_ACCENT'],(24,y+4,20,24))
            pygame.draw.rect(s,t['C_TEXT'],(50,y+4,16,8))
            pygame.draw.rect(s,t['C_DIM'],(50,y+16,24,8))
            # Name
            color=C_ACCENT if issel else C_TEXT
            prefix="  > " if issel else "    "
            s.blit(f['md'].render(prefix+t['name'],True,color),(108,y+9))
            if issel:
                pygame.draw.rect(s,C_SEL_LINE,(0,y,2,32))
        pygame.draw.line(s,C_DIM,(0,SCREEN_H-34),(SCREEN_W,SCREEN_H-34),1)
        h=f['sm'].render("A:Apply  B:Back  Stick/D-pad:Navigate",True,C_DIM)
        s.blit(h,((SCREEN_W-h.get_width())//2,SCREEN_H-22))

    def fontsize_page(self, sel, current):
        s,f=self.s,self.f; s.fill(C_BG)
        pygame.draw.line(s,C_ACCENT,(0,36),(SCREEN_W,36),1)
        s.blit(f['lg'].render("> FONT SIZE_",True,C_ACCENT),(12,9))
        ih=70
        for i,key in enumerate(FONT_SIZE_KEYS):
            sz=FONT_SIZES[key]; y=50+i*ih; issel=i==sel; isact=key==current
            if issel:
                pygame.draw.rect(s,C_SEL_BG,(0,y,SCREEN_W,ih-2))
                pygame.draw.rect(s,C_SEL_LINE,(0,y,2,ih-2))
            color=C_ACCENT if isact else (C_TEXT if issel else C_DIM)
            label=("✓ " if isact else "  ")+sz['label']
            s.blit(f['lg'].render(label,True,color),(20,y+6))
            # Preview text
            try:
                pf=pygame.font.SysFont("dejavusans",sz['md'])
            except:
                pf=pygame.font.Font(None,sz['md']+4)
            s.blit(pf.render("The quick brown fox...",True,C_DIM),(20,y+30))
        pygame.draw.line(s,C_DIM,(0,SCREEN_H-34),(SCREEN_W,SCREEN_H-34),1)
        h=f['sm'].render("A:Apply  B:Back  Stick/D-pad:Navigate",True,C_DIM)
        s.blit(h,((SCREEN_W-h.get_width())//2,SCREEN_H-22))

    def confirm_delete(self, path):
        s,f=self.s,self.f; s.fill(C_BG)
        pygame.draw.line(s,C_ACCENT,(0,36),(SCREEN_W,36),1)
        s.blit(f['lg'].render("> DELETE_",True,(255,60,60)),(12,9))
        # Warning
        w=pygame.Surface((SCREEN_W-40,80),pygame.SRCALPHA)
        w.fill((60,0,0,200)); s.blit(w,(20,60))
        pygame.draw.rect(s,(255,60,60),(20,60,SCREEN_W-40,80),1)
        s.blit(f['md'].render("Are you sure you want to delete:",True,C_TEXT),(30,72))
        name=os.path.basename(path)
        s.blit(f['md'].render(trunc(name,44),True,(255,60,60)),(30,96))
        s.blit(f['lg'].render("A  —  YES, DELETE",True,(255,60,60)),(20,170))
        s.blit(f['lg'].render("B  —  Cancel",True,C_ACCENT),(20,210))
        pygame.draw.line(s,C_DIM,(0,SCREEN_H-34),(SCREEN_W,SCREEN_H-34),1)
        s.blit(f['sm'].render("This action cannot be undone",True,C_DIM),(20,SCREEN_H-22))

    def message(self,text):
        self.s.fill(C_BG)
        t=self.f['lg'].render(text,True,C_ACCENT)
        self.s.blit(t,((SCREEN_W-t.get_width())//2,(SCREEN_H-t.get_height())//2))

# ── App ───────────────────────────────────────────────────────────────────────

MENU_ITEMS = ["About", "Controls", "Theme", "Font Size", "Exit"]

ABOUT_LINES = [
    "  # KNULLI VIDEO PLAYER",
    "",
    "  Author   : KRAMOLICH",
    "  Platform : Anbernic RG40XXV",
    "  OS       : Knulli / Batocera",
    "  Video    : ffmpeg → /dev/fb0",
    "  UI       : pygame (SDL2 / Mali)",
]

CONTROLS_LINES = [
    "  A          - Play file / Confirm",
    "  B          - Back",
    "  X          - Audio track selection",
    "  Y          - Sort by duration",
    "  L1 / R1    - Seek -30s / +30s",
    "  L2 / R2    - Prev / Next file",
    "  SELECT     - Rescan / Restart video",
    "  START      - Main menu",
    "  L1 + R1    - Delete file (with confirm)",
    "  D-pad ↑↓   - Navigate / Volume in video",
    "  D-pad ←→   - Navigate / Seek 5s in video",
    "  Stick      - Navigate",
]

class App:
    def __init__(self, start_path=None):
        pygame.init(); pygame.joystick.init()
        self.screen=pygame.display.set_mode((SCREEN_W,SCREEN_H),pygame.NOFRAME)
        self.clock=pygame.time.Clock()
        self.f=make_fonts('medium'); self.draw=Draw(self.screen,self.f)  # updated after prefs load
        self.be=Backend()

        self.joy=None
        if pygame.joystick.get_count()>0:
            self.joy=pygame.joystick.Joystick(0); self.joy.init()

        self.root_folder = start_path if (start_path and os.path.isdir(start_path)) else VIDEO_DIR
        self.current_folder = self.root_folder

        # Prefs
        prefs = load_prefs()
        self.preferred_audio_lang = prefs.get('audio_lang', None)
        self.current_theme = prefs.get('theme', 'terminal')
        apply_theme(self.current_theme)
        self.theme_sel = THEME_KEYS.index(self.current_theme) if self.current_theme in THEME_KEYS else 0
        self.current_font_size = prefs.get('font_size', 'medium')
        self.font_size_sel = FONT_SIZE_KEYS.index(self.current_font_size) if self.current_font_size in FONT_SIZE_KEYS else 1
        self.f = make_fonts(self.current_font_size)
        self.draw = Draw(self.screen, self.f)

        # State
        self.mode      = 'browser'
        self.sel       = 0
        self.items     = []   # current rendered items list
        self.cur_file  = None
        self.pending_file = None  # file selected for audio track change
        self.audio_tracks = []
        self.audio_sel = 0
        self.cur_audio = 0
        self.sort_mode = 0   # 0=name, 1=dur desc, 2=dur asc
        self.menu_sel  = 0

        self.resume    = load_resume()
        self.durations = {}
        self.total_root = 0

        self.axis_dir  = 0; self.axis_t = 0.0; self.axis_moved = False
        self.volume = get_volume()
        self.l1_held = False; self.r1_held = False  # for L1+R1 combo
        self.confirm_delete = None  # path pending deletion
        self.running   = True
        self.audio_counts = {}  # path -> int, кол-во аудио дорожек

        # Background tasks
        threading.Thread(target=self._bg_scan, daemon=True).start()

    def _bg_scan(self):
        """Scan durations and total count in background."""
        self.total_root = count_all_videos(self.root_folder)
        folders, files = scan_dir(self.root_folder)
        all_files = []
        def collect(folder):
            fds, fls = scan_dir(folder)
            all_files.extend(fls)
            for d in fds: collect(d)
        collect(self.root_folder)
        for path in all_files:
            if path not in self.durations:
                info = probe(path)
                if info['duration']>0:
                    self.durations[path]=info['duration']
                if path not in self.audio_counts:
                    self.audio_counts[path]=len(info['audio'])

    def _delete_combo(self):
        """L1+R1 — ask to delete selected item."""
        if self.mode=='browser' and self.items and self.sel<len(self.items):
            item=self.items[self.sel]
            if item['type'] in ('file','folder'):
                self.confirm_delete=item['path']
                self.mode='confirm_delete'
        elif self.mode=='video' and self.cur_file:
            self.confirm_delete=self.cur_file
            self.be.stop()
            self._show_pygame()
            self.mode='confirm_delete'

    def _current_path_for_restart(self):
        return self.be._current_path

    def _hide_pygame(self):
        self.screen=pygame.display.set_mode((1,1),pygame.NOFRAME)
        self.draw.s=self.screen

    def _show_pygame(self):
        self.screen=pygame.display.set_mode((SCREEN_W,SCREEN_H),pygame.NOFRAME)
        self.draw.s=self.screen

    def _get_items(self):
        folders, files = scan_dir(self.current_folder)
        # Sort files
        if self.sort_mode==1:
            files.sort(key=lambda p: self.durations.get(p,0), reverse=True)
        elif self.sort_mode==2:
            files.sort(key=lambda p: self.durations.get(p,0))
        return folders, files

    # ── Main loop ─────────────────────────────────────────────────────────────

    def run(self):
        while self.running:
            dt=self.clock.tick(FPS)/1000.0
            self._events(dt); self._update(dt)
            if self.mode=='video':
                continue
            self._render()
            pygame.display.flip()
        self.be.stop()
        self._show_pygame()
        self.screen.fill((0,0,0)); pygame.display.flip()
        pygame.quit()

    def _update(self, dt):
        if self.mode=='video':
            if self.be.is_eof: self._next(); return
        if self.axis_dir and self.mode in ('browser','audio_menu','main_menu'):
            self.axis_t+=dt
            if self.axis_t>0.3: self._nav(self.axis_dir); self.axis_t=0.15

    def _nav(self, d):
        if self.mode=='browser':
            n=len(self.items)
            if n: self.sel=(self.sel+d)%n
        elif self.mode=='audio_menu':
            if self.audio_tracks:
                self.audio_sel=(self.audio_sel+d)%len(self.audio_tracks)
        elif self.mode=='main_menu':
            self.menu_sel=(self.menu_sel+d)%len(MENU_ITEMS)
        elif self.mode=='theme':
            self.theme_sel=(self.theme_sel+d)%len(THEME_KEYS)
        elif self.mode=='fontsize':
            self.font_size_sel=(self.font_size_sel+d)%len(FONT_SIZE_KEYS)

    def _events(self, dt):
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: self.running=False

            elif ev.type==pygame.JOYBUTTONDOWN:
                if ev.button==BTN_L1: self.l1_held=True
                if ev.button==BTN_R1: self.r1_held=True
                if self.l1_held and self.r1_held:
                    self._delete_combo()
                else:
                    self._btn(ev.button)
            elif ev.type==pygame.JOYBUTTONUP:
                if ev.button==BTN_L1: self.l1_held=False
                if ev.button==BTN_R1: self.r1_held=False

            elif ev.type==pygame.JOYAXISMOTION:
                if ev.axis==AXIS_LY:
                    if ev.value>0.5:
                        self.axis_dir=1
                        if not self.axis_moved: self._nav(1); self.axis_moved=True; self.axis_t=0
                    elif ev.value<-0.5:
                        self.axis_dir=-1
                        if not self.axis_moved: self._nav(-1); self.axis_moved=True; self.axis_t=0
                    else:
                        self.axis_dir=0; self.axis_moved=False; self.axis_t=0

            elif ev.type==pygame.JOYHATMOTION:
                hx,hy=ev.value
                if self.mode=='video':
                    if hy==1:    self.volume=set_volume(self.volume+5)
                    elif hy==-1: self.volume=set_volume(self.volume-5)
                    elif hx==-1: self.be.seek(-5)
                    elif hx==1:  self.be.seek(5)
                else:
                    if hy==1:   self._nav(-1)
                    elif hy==-1: self._nav(1)
                    elif hx==-1 and self.mode=='browser': self._go_parent()
                    elif hx==1  and self.mode=='browser': self._enter_selected()

            elif ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_ESCAPE: self._btn(BTN_B)
                elif ev.key==pygame.K_RETURN: self._btn(BTN_A)
                elif ev.key==pygame.K_UP:   self._nav(-1)
                elif ev.key==pygame.K_DOWN: self._nav(1)

    def _btn(self, b):
        # ── video mode ──
        if self.mode=='video':
            if b==BTN_B:      self._stop_video()
            elif b==BTN_L1:   self.be.seek(-30)
            elif b==BTN_R1:   self.be.seek(30)
            elif b==BTN_L2:   self._prev()
            elif b==BTN_R2:   self._next()
            elif b==BTN_X:
                pass  # no UI during playback
            elif b==BTN_SELECT:
                self.be.load(self._current_path_for_restart(), seek=0.0, audio_idx=self.be.audio_idx)
            return

        # ── audio menu ──
        if self.mode=='audio_menu':
            if b==BTN_A:
                # Save selection and return to browser
                self.cur_audio=self.audio_sel
                lang=self.audio_tracks[self.audio_sel]['lang']
                prefs=load_prefs(); prefs['audio_lang']=lang; save_prefs(prefs)
                self.preferred_audio_lang=lang
                self.mode='browser'
            elif b==BTN_B:
                # Cancel — return to browser without saving
                self.mode='browser'
            return

        # ── main menu ──
        if self.mode=='main_menu':
            if b in (BTN_B, BTN_START):
                self.mode='browser'
            elif b==BTN_A:
                item=MENU_ITEMS[self.menu_sel]
                if item=='About':    self.mode='about'
                elif item=='Controls': self.mode='controls'
                elif item=='Theme':  self.mode='theme'
                elif item=='Font Size': self.mode='fontsize'
                elif item=='Exit':   self.running=False
            return

        # ── confirm delete ──
        if self.mode=='confirm_delete':
            if b==BTN_A and self.confirm_delete:
                path=self.confirm_delete
                try:
                    if os.path.isfile(path):
                        os.remove(path)
                        # Remove from resume/durations
                        self.resume.pop(path,None); save_resume(self.resume)
                        self.durations.pop(path,None)
                        self.audio_counts.pop(path,None)
                    elif os.path.isdir(path):
                        import shutil; shutil.rmtree(path)
                except Exception as e:
                    pass
                self.confirm_delete=None
                self.cur_file=None
                self.mode='browser'
            elif b==BTN_B:
                self.confirm_delete=None
                self.mode='browser'
            return

        # ── info pages ──
        if self.mode in ('about','controls'):
            self.mode='main_menu'; return

        # ── font size page ──
        if self.mode=='fontsize':
            if b==BTN_A:
                key=FONT_SIZE_KEYS[self.font_size_sel]
                self.current_font_size=key
                self.f=make_fonts(key)
                self.draw=Draw(self.screen,self.f)
                prefs=load_prefs(); prefs['font_size']=key; save_prefs(prefs)
                self.mode='main_menu'
            elif b==BTN_B:
                self.mode='main_menu'
            else:
                self.font_size_sel=(self.font_size_sel+(1 if b not in (BTN_L1,BTN_SELECT) else -1))%len(FONT_SIZE_KEYS)
            return

        # ── theme page ──
        if self.mode=='theme':
            if b==BTN_A:
                key=THEME_KEYS[self.theme_sel]
                self.current_theme=key
                apply_theme(key)
                prefs=load_prefs(); prefs['theme']=key; save_prefs(prefs)
                self.draw=Draw(self.screen,self.f)  # refresh draw with new colors
                self.mode='main_menu'
            elif b==BTN_B:
                self.mode='main_menu'
            elif b in (BTN_L1, BTN_SELECT):
                self.theme_sel=(self.theme_sel-1)%len(THEME_KEYS)
            else:
                self.theme_sel=(self.theme_sel+1)%len(THEME_KEYS)
            return

        # ── browser ──
        if self.mode=='browser':
            if b==BTN_A:      self._enter_selected()
            elif b==BTN_B:    self._go_parent()
            elif b==BTN_START: self.mode='main_menu'; self.menu_sel=0
            elif b==BTN_SELECT:
                folders,files=self._get_items()
                self.items=self._build_items(folders,files)
                self.sel=min(self.sel,max(0,len(self.items)-1))
            elif b==BTN_Y:
                # Audio menu for selected file
                if self.items and self.sel<len(self.items):
                    item=self.items[self.sel]
                    if item['type']=='file':
                        info=probe(item['path'])
                        if info['audio']:
                            self.audio_tracks=info['audio']
                            self.pending_file=item['path']
                            self.audio_sel=self._preferred_audio_idx()
                            self.cur_audio=self.audio_sel
                            self.mode='audio_menu'
            elif b==BTN_X:
                self.sort_mode=(self.sort_mode+1)%3

    def _build_items(self, folders, files):
        items=[]
        if self.current_folder!=self.root_folder:
            items.append({'type':'parent','path':os.path.dirname(self.current_folder)})
        for d in folders: items.append({'type':'folder','path':d})
        for fp in files:  items.append({'type':'file','path':fp})
        return items

    def _enter_selected(self):
        if not self.items or self.sel>=len(self.items): return
        item=self.items[self.sel]
        if item['type']=='parent':
            self._go_parent()
        elif item['type']=='folder':
            self.current_folder=item['path']
            self.sel=0
        elif item['type']=='file':
            self._play(item['path'])

    def _go_parent(self):
        if self.mode=='browser':
            if self.current_folder!=self.root_folder:
                self.current_folder=os.path.dirname(self.current_folder)
                self.sel=0
            else:
                pass  # already at root, do nothing

    def _preferred_audio_idx(self):
        """Find preferred audio track by saved language."""
        if not self.audio_tracks: return 0
        if self.preferred_audio_lang:
            for i,t in enumerate(self.audio_tracks):
                if t['lang']==self.preferred_audio_lang:
                    return i
        return 0

    def _play(self, path):
        self.draw.message("Loading..."); pygame.display.flip()
        info=probe(path)
        self.be.duration=info['duration']
        self.durations[path]=info['duration']
        self.audio_counts[path]=len(info['audio'])
        self.audio_tracks=info['audio']
        self.cur_audio=self._preferred_audio_idx()
        self.cur_file=path

        seek=self.resume.get(path,0.0)
        audio_idx=self.audio_tracks[self.cur_audio]['index'] if self.audio_tracks else None
        self.be.load(path, seek=seek, audio_idx=audio_idx)
        self.mode='video'
        self._hide_pygame()

    def _stop_video(self):
        # Save position
        if self.cur_file:
            self.resume[self.cur_file]=self.be.position
            save_resume(self.resume)
        self.be.stop()
        self.mode='browser'
        self._show_pygame()

    def _files_in_current(self):
        _, files = scan_dir(self.current_folder)
        if self.sort_mode==1:
            files.sort(key=lambda p:self.durations.get(p,0), reverse=True)
        elif self.sort_mode==2:
            files.sort(key=lambda p:self.durations.get(p,0))
        return files

    def _next(self):
        files=self._files_in_current()
        if not files: return
        if self.cur_file in files:
            idx=(files.index(self.cur_file)+1)%len(files)
        else:
            idx=0
        self._stop_video_silent()
        self._play(files[idx])

    def _prev(self):
        files=self._files_in_current()
        if not files: return
        if self.cur_file in files:
            idx=(files.index(self.cur_file)-1)%len(files)
        else:
            idx=0
        self._stop_video_silent()
        self._play(files[idx])

    def _stop_video_silent(self):
        if self.cur_file:
            self.resume[self.cur_file]=self.be.position
            save_resume(self.resume)
        self.be.stop()

    def _render(self):
        if self.mode=='browser':
            folders,files=self._get_items()
            self.items=self._build_items(folders,files)
            self.sel=min(self.sel,max(0,len(self.items)-1))
            self.draw.browser(
                folders, files, self.sel, self.cur_file,
                self.durations, self.resume,
                self.current_folder, self.root_folder,
                self.total_root, self.sort_mode,
                self.audio_counts
            )
        elif self.mode=='audio_menu':
            tracks=[(t['index'],t['lang']) for t in self.audio_tracks]
            self.draw.audio_menu(tracks, self.audio_sel, self.cur_audio)
        elif self.mode=='main_menu':
            self.draw.main_menu(MENU_ITEMS, self.menu_sel)
        elif self.mode=='confirm_delete':
            self.draw.confirm_delete(self.confirm_delete)
        elif self.mode=='about':
            self.draw.info_page("ABOUT", ABOUT_LINES)
        elif self.mode=='controls':
            self.draw.info_page("CONTROLS", CONTROLS_LINES)
        elif self.mode=='theme':
            self.draw.theme_page(self.theme_sel)
        elif self.mode=='fontsize':
            self.draw.fontsize_page(self.font_size_sel, self.current_font_size)

if __name__=='__main__':
    first_run_setup()
    path = sys.argv[1] if len(sys.argv)>1 else None
    App(start_path=path).run()
