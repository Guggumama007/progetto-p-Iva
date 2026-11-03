"""Scena 3 - Nessuno. Primo piano frontale e basso: guarda a sinistra ("vietato"), a destra
("autorizzato"), alza le "spalle" (saltello + sopracciglio su); "Diciamo che... nessuno ha chiesto": occhiata furba."""
exec(open("/home/user/APEX-AI-Terminal/video-shadow-ai/blender/paperlib.py").read())

SID = "nessuno"
tl = timeline(); t0, t1 = scene_span(tl, SID); DUR = t1 - t0
L = [(l["start"] - t0, l["end"] - t0) for l in lines_of(tl, SID)]
pal = PAL["home"]
reset_scene(); sc = bpy.context.scene
setup_render(sc, DUR, f"/opt/render/{SID}", pal)
mats = home_desk(sc, pal); screen_image(mats["screen"], f"{TEX}/screen_gratis.png")

a, b = L[0]; mid = a + (b - a) * 0.5
face = [
    (0.0, dict(squint=0.6)),
    (a, dict(px=-1.0, py=0.2, brow=-10, brow_y=12, squint=0.0)),    # "Nessuno l'ha vietato" -> sinistra
    (mid, dict(px=1.0, py=0.2, brow=10, brow_y=12)),                # "Nessuno l'ha autorizzato" -> destra
    (b, dict(px=0.0, py=0.0, brow=0, brow_y=30)),                   # spallucce
    (L[1][0] + 0.2, dict(px=-0.9, py=-0.2, brow=14, brow_y=6, squint=0.4)),   # "Diciamo che..."
    (L[1][1] - 0.5, dict(px=0.0, py=0.0, squint=0.65, brow=-8, brow_y=0)),   # "...nessuno ha chiesto" in camera
    (DUR, dict(squint=0.65, brow=-8)),
] + blink_keys([mid - 0.25, b + 0.5])
fdir = f"/opt/render/{SID}_face"; n = render_face_sequence(face, DUR, fdir)
rig, sheet, curl, lean = character(sc, pal, fdir, n, loc=(0.0, 0.0), rotz=0)
key_body(rig, curl, lean, [
    (0.0, dict(curl=22)), (a, dict(turn=-12)), (mid, dict(turn=12)),
    (b - 0.15, dict(turn=0, hop=0.0, squash=0.94)), (b, dict(hop=0.035, squash=1.08)),   # spallucce
    (b + 0.25, dict(hop=0.0, squash=0.97)), (b + 0.45, dict(squash=1.0)),
    (L[1][0] + 0.2, dict(lean=-8, turn=-6)), (L[1][1] - 0.5, dict(lean=6, turn=0)), (DUR, dict(lean=6)),
])
cam, tgt = camera(sc, (-0.05, -1.05, 0.2), (0.0, 0.0, 0.155), lens=45, fstop=2.4)
cam.keyframe_insert("location", frame=1)
cam.location = (0.02, -0.92, 0.19); cam.keyframe_insert("location", frame=sc.frame_end)
lights(pal)
sc.frame_set(1 + round(b * FPS))
bpy.ops.wm.save_as_mainfile(filepath=f"{ROOT}/blender/{SID}.blend", copy=True)
print(f"SCENA {SID} PRONTA: {sc.frame_end} fotogrammi")
