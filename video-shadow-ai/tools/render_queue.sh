#!/bin/bash
# Coda di render Blender (uno alla volta: la CPU e' condivisa). Uso: render_queue.sh shot1 shot2 ...
cd /home/user/APEX-AI-Terminal/video-shadow-ai
for s in "$@"; do
  echo "START $s $(date +%T)"
  xvfb-run -a -s "-screen 0 1920x1080x24" blender -b blender/$s.blend -a 2>&1 | grep -c "Saved" | sed "s/^/frames $s: /"
  echo "DONE $s $(date +%T)"
done
echo QUEUE_DONE
