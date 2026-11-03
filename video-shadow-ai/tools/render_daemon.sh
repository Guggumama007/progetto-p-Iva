#!/bin/bash
# Esegue in ordine le scene elencate in /opt/render/queue.txt (una per riga), una alla volta.
cd /home/user/APEX-AI-Terminal/video-shadow-ai
touch /opt/render/queue.txt /opt/render/done.txt
while true; do
  next=$(grep -vxF -f /opt/render/done.txt /opt/render/queue.txt | head -1)
  if [ -z "$next" ]; then sleep 5; continue; fi
  [ "$next" = "END" ] && { echo QUEUE_END; exit 0; }
  while pgrep -x blender >/dev/null && pgrep -af "blender -b" | grep -q "\.blend -a"; do sleep 5; done
  echo "START $next $(date +%T)"
  xvfb-run -a -s "-screen 0 1920x1080x24" blender -b blender/$next.blend -P blender/render_override.py -a 2>&1 | grep -c "Saved" | sed "s/^/frames $next: /"
  echo "$next" >> /opt/render/done.txt
  echo "DONE $next $(date +%T)"
done
