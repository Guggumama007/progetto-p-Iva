#!/bin/bash
# Prepara le clip per HyperFrames con l'FFmpeg compilato dal repo:
# - sequenze Blender (12 fps, 1280x720) -> mp4 1920x1080 a 30 fps (ogni posa tenuta: stop-motion)
# - clip Remotion copiate; "rewind" = montaggio all'indietro e accelerato delle scene precedenti
# - una scena non ancora renderizzata diventa un segnaposto (per poter controllare il montaggio)
FF=/opt/ffmpeg-src/bin/ffmpeg
P=/home/user/APEX-AI-Terminal/video-shadow-ai
OUT=$P/hyperframes/assets/clips; mkdir -p $OUT
dur() { python3 -c "import json;t=json.load(open('$P/timeline.json'));s={x['id']:x for x in t['scenes']};print($1)"; }
placeholder() { /usr/bin/ffmpeg -v error -y -f lavfi -i "color=c=0x2a3346:s=1920x1080:r=30:d=$2" -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='$1 · in render':fontcolor=0xf1ebde:fontsize=64:x=(w-tw)/2:y=(h-th)/2" -c:v libx264 -pix_fmt yuv420p $OUT/$1.mp4; echo "segnaposto $1"; }
for s in buongiorno fretta nessuno server giusta; do
  case $s in
    buongiorno) d=$(dur "s['buongiorno']['end']-s['buongiorno']['start']");; fretta) d=$(dur "s['fretta']['end']-s['fretta']['start']");;
    nessuno) d=$(dur "s['nessuno']['end']-s['nessuno']['start']");; server) d=$(dur "s['nome']['end']-s['viaggio']['start']-3.3");;
    giusta) d=$(dur "s['finale']['end']-s['giusta']['start']");;
  esac
  need=$(python3 -c "print(max(1, round($d*12)))"); n=$(ls /opt/render/$s 2>/dev/null | wc -l)
  if [ "$n" -ge "$need" ]; then
    $FF -v error -y -framerate 12 -i /opt/render/$s/f_%04d.jpg -vf "scale=1920:1080:flags=lanczos,fps=30,tpad=stop_mode=clone:stop_duration=0.5,format=yuv420p" -c:v libx264 -crf 15 -preset medium $OUT/$s.mp4 && echo "clip $s ($n pose)"
  else
    placeholder $s $(python3 -c "print($d+0.5)"); echo "  ($s: $n/$need pose)"
  fi
done
for s in tunnel copie; do
  if [ -f /opt/render/$s.mp4 ]; then cp /opt/render/$s.mp4 $OUT/$s.mp4; echo "clip $s"; else placeholder $s $(dur "s['rischio']['end']-s['rischio']['start']"); fi
done
# riavvolgimento: fretta..copie all'indietro, accelerate fino a durare quanto la scena "riavvolgi"
RW=$(dur "s['riavvolgi']['end']-s['riavvolgi']['start']")
$FF -v error -y -i $OUT/fretta.mp4 -i $OUT/nessuno.mp4 -i $OUT/tunnel.mp4 -i $OUT/server.mp4 -i $OUT/copie.mp4 \
  -filter_complex "[0]fps=30,setsar=1[a];[1]fps=30,setsar=1[b];[2]fps=30,setsar=1[c];[3]fps=30,setsar=1[d];[4]fps=30,setsar=1[e];[a][b][c][d][e]concat=n=5:v=1:a=0,setpts=PTS/16,fps=30,reverse,trim=duration=$RW,eq=saturation=0.55:contrast=1.08,format=yuv420p" \
  -c:v libx264 -crf 16 $OUT/rewind.mp4
echo "clip rewind"
for a in voice music sfx; do src=$P/audio/$a.wav; [ $a = voice ] && src=$P/audio/voice_v2.wav; cp $src $P/hyperframes/assets/audio/$a.wav; done
echo "audio copiato"
