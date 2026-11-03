"""Scena 1 - Buongiorno. Il contratto dorme piegato sulla scrivania kraft, si sveglia, si stiracchia,
saluta e, su "dati riservati", lancia un'occhiata complice di lato.
Costruita via Blender MCP; render da CLI a 12 fps."""
exec(open("/home/user/APEX-AI-Terminal/video-shadow-ai/blender/paperlib.py").read())

SID = "buongiorno"
tl = timeline(); t0, t1 = scene_span(tl, SID); DUR = t1 - t0
L = [(l["start"] - t0, l["end"] - t0) for l in lines_of(tl, SID)]   # tempi locali delle battute
pal = PAL["home"]

reset_scene(); sc = bpy.context.scene
setup_render(sc, DUR, f"/opt/render/{SID}", pal)
mats = home_desk(sc, pal)

wake = 0.7
face = [
    (0.0, dict(open=0.0, brow=0.0, brow_y=-18, px=0, py=0)),          # dorme
    (wake, dict(open=0.0, brow_y=-18)),
    (wake + 0.25, dict(open=1.0, brow_y=10, brow=0)),                    # si sveglia, sopracciglio su
    (L[0][0], dict(brow_y=22, brow=-4, px=0, py=0)),                     # "Buongiorno"
    (L[0][0] + 0.9, dict(brow_y=8, brow=0)),
    (L[1][0], dict(brow=6, brow_y=12)),                                  # "Tre pagine, due firme..."
    (L[1][1] - 1.1, dict(px=-1.0, py=-0.3, squint=0.6, brow=10, brow_y=4)),  # "...dati riservati": occhiata
    (L[1][1] + 0.1, dict(px=-1.0, squint=0.6)),
    (DUR, dict(px=0.0, squint=0.0, brow=0, brow_y=8)),
] + blink_keys([wake + 0.55, L[1][0] - 0.2, DUR - 0.4])
fdir = f"/opt/render/{SID}_face"
n = render_face_sequence(face, DUR, fdir)

rig, sheet, curl, lean = character(sc, pal, fdir, n)
key_body(rig, curl, lean, [
    (0.0, dict(lean=38, curl=30, squash=0.96)),                 # piegato in avanti, addormentato
    (wake, dict(lean=38, curl=30, squash=0.96)),
    (wake + 0.35, dict(lean=-12, curl=10, squash=1.07, hop=0.01)),  # stiracchiata
    (wake + 0.8, dict(lean=4, curl=22, squash=1.0, hop=0.0)),
    (L[0][0], dict(hop=0.025, squash=1.04)),                    # saluto: saltello
    (L[0][0] + 0.25, dict(hop=0.0, squash=0.97)),
    (L[0][0] + 0.45, dict(squash=1.0, lean=0)),
    (L[1][0], dict(turn=8)),
    (L[1][1] - 1.1, dict(turn=-6, lean=6)),                     # si sporge per confidare il segreto
    (DUR, dict(turn=-4, lean=4)),
])

cam, tgt = camera(sc, (0.42, -1.6, 0.62), (0.0, 0.05, 0.14), lens=50, fstop=2.8)
cam.keyframe_insert("location", frame=1)
cam.location = (0.2, -1.05, 0.4); cam.keyframe_insert("location", frame=sc.frame_end)
lights(pal)

sc.frame_set(1 + round(L[1][1] * FPS) - 8)
bpy.ops.wm.save_as_mainfile(filepath=f"{ROOT}/blender/{SID}.blend", copy=True)
print(f"SCENA {SID} PRONTA: {sc.frame_end} fotogrammi a {FPS} fps, volto {n} immagini")
