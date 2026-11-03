"""Scena 2 - La fretta. Un cursore di carta scende, "clicca" sul contratto; una copia fantasma
si stacca e vola dentro lo schermo del chatbot gratis. Su "Gratis. Che fortuna." sguardo in camera, impassibile."""
exec(open("/home/user/APEX-AI-Terminal/video-shadow-ai/blender/paperlib.py").read())

SID = "fretta"
tl = timeline(); t0, t1 = scene_span(tl, SID); DUR = t1 - t0
L = [(l["start"] - t0, l["end"] - t0) for l in lines_of(tl, SID)]
pal = PAL["home"]
reset_scene(); sc = bpy.context.scene
setup_render(sc, DUR, f"/opt/render/{SID}", pal)
mats = home_desk(sc, pal)
screen_image(mats["screen"], f"{TEX}/screen_gratis.png")

copy_t = L[1][0] + 0.15          # "Mi copia"
paste_t = L[1][0] + 1.25         # "...e mi incolla"
face = [
    (0.0, dict(brow=0, brow_y=8)),
    (L[0][0] + 0.6, dict(px=-0.8, py=0.3, brow=-6, brow_y=14)),       # guarda in su: chi ha fretta?
    (copy_t, dict(px=0.0, py=0.6, brow_y=26, brow=0, open=1.15)),     # sorpresa: occhi grandi
    (paste_t, dict(px=-1.0, py=0.0, brow=12, brow_y=10)),             # segue la copia verso lo schermo
    (L[2][0], dict(px=0.0, py=0.0, brow=0, brow_y=0, squint=0.7)),    # "Gratis. Che fortuna." impassibile
    (DUR, dict(squint=0.75, brow=-3, brow_y=-2)),
] + blink_keys([0.5, L[2][0] + 0.9])
fdir = f"/opt/render/{SID}_face"; n = render_face_sequence(face, DUR, fdir)
rig, sheet, curl, lean = character(sc, pal, fdir, n, loc=(0.05, 0.0), rotz=-4)
key_body(rig, curl, lean, [
    (0.0, dict(lean=0, curl=22)),
    (copy_t - 0.1, dict(squash=1.0)),
    (copy_t, dict(squash=0.9, lean=-8)),          # il click lo schiaccia
    (copy_t + 0.25, dict(squash=1.05, lean=0)),
    (copy_t + 0.5, dict(squash=1.0)),
    (paste_t, dict(turn=18, lean=6)),             # si gira verso lo schermo
    (L[2][0], dict(turn=0, lean=0)),
    (DUR, dict(turn=-2)),
])

# cursore di carta (freccia ritagliata, inchiostro scuro)
m_ink = paper_mat("CursorInk", (0.04, 0.05, 0.08), fiber=0.1)
arrow = [(0, 0), (0, -0.11), (0.03, -0.083), (0.05, -0.125), (0.066, -0.118), (0.046, -0.077), (0.083, -0.077)]
cur = cut_shape("Cursore", arrow, m_ink, thick=0.004)
def ckey(t, loc, s=1.0):
    cur.location = loc; cur.scale = (s, s, s); f = 1 + round(t * FPS)
    cur.keyframe_insert("location", frame=f); cur.keyframe_insert("scale", frame=f)
ckey(0.0, (0.35, -0.05, 0.75)); ckey(L[0][0] + 0.3, (0.3, -0.05, 0.62))
ckey(copy_t - 0.35, (0.1, -0.05, 0.33)); ckey(copy_t, (0.08, -0.05, 0.3), 0.85); ckey(copy_t + 0.2, (0.08, -0.05, 0.31), 1.0)
ckey(paste_t + 0.4, (-0.35, 0.3, 0.42)); ckey(L[2][0], (-0.9, 0.2, 0.9))

# copia fantasma: si stacca dal contratto e "entra" nello schermo
g, gb = ghost_sheet("Copia", f"{TEX}/face_open.png")
g.parent = None
def gkey(t, loc, s, a, rz=0):
    g.location = loc; g.scale = (s, s, s); g.rotation_euler = (0, 0, math.radians(rz)); f = 1 + round(t * FPS)
    g.keyframe_insert("location", frame=f); g.keyframe_insert("scale", frame=f); g.keyframe_insert("rotation_euler", frame=f)
    gb.inputs["Alpha"].default_value = a; gb.inputs["Alpha"].keyframe_insert("default_value", frame=f)
scr = bpy.data.objects["ScreenFace"].location
gkey(0.0, (0.05, 0.0, 0.0), 0.001, 0.0); gkey(copy_t, (0.05, -0.01, 0.0), 1.0, 0.0)
gkey(copy_t + 0.2, (0.02, -0.03, 0.02), 1.0, 0.6, 6)
gkey(paste_t, (-0.28, 0.25, 0.2), 0.6, 0.6, 20)
gkey(paste_t + 0.45, (scr.x, scr.y - 0.01, scr.z - 0.06), 0.18, 0.0, 14)

cam, tgt = camera(sc, (0.15, -1.35, 0.55), (-0.18, 0.12, 0.17), lens=45, fstop=3.2)
cam.keyframe_insert("location", frame=1); tgt.keyframe_insert("location", frame=1)
cam.location = (0.12, -1.25, 0.5); cam.keyframe_insert("location", frame=1 + round(paste_t * FPS))
cam.location = (0.2, -0.95, 0.38); tgt.location = (0.03, 0.0, 0.17)     # su "Gratis": stringe sul volto
cam.keyframe_insert("location", frame=1 + round((L[2][0] + 0.3) * FPS)); tgt.keyframe_insert("location", frame=1 + round((L[2][0] + 0.3) * FPS))
lights(pal)
sc.frame_set(1 + round((paste_t - 0.1) * FPS))
bpy.ops.wm.save_as_mainfile(filepath=f"{ROOT}/blender/{SID}.blend", copy=True)
print(f"SCENA {SID} PRONTA: {sc.frame_end} fotogrammi")
