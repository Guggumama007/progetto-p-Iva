"""Scene 8-9 - La versione giusta + finale. Stessa scrivania kraft. Una cupola di carta da lucido scende
sull'azienda; lo schermo mostra l'assistente aziendale; un timbro rame stampa tre cartellini, ognuno sulla
sua parola; "E io resto a casa": occhi felici, saltello, la camera si allontana."""
exec(open("/home/user/APEX-AI-Terminal/video-shadow-ai/blender/paperlib.py").read())

SID = "giusta"
tl = timeline(); g0, g1 = scene_span(tl, "giusta"); f0, f1 = scene_span(tl, "finale")
T0 = g0; DUR = f1 - T0
LG = lines_of(tl, "giusta"); LF = lines_of(tl, "finale")
pal = PAL["home"]
reset_scene(); sc = bpy.context.scene
setup_render(sc, DUR, f"/opt/render/{SID}", pal)
mats = home_desk(sc, pal); screen_image(mats["screen"], f"{TEX}/screen_azienda.png")
loc = lambda t: t - T0

dome_t = loc(LG[0]["start"]) + 0.2
stamps = [loc(word_time(LG[1], "approvato")), loc(word_time(LG[1], "chiare")), loc(word_time(LG[1], "formate"))]
happy_t = loc(LF[1]["start"])

# cupola di carta da lucido (sfaccettata come una lanterna di carta)
bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=7, radius=0.9, location=(0, 0.2, 0))
dome = bpy.context.object; dome.name = "Cupola"; dome.scale = (1.0, 0.85, 0.6)
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="DESELECT"); bpy.ops.object.mode_set(mode="OBJECT")
for v in dome.data.vertices: v.select = v.co.z < -0.01
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.delete(type="VERT"); bpy.ops.object.mode_set(mode="OBJECT")
md = dome.modifiers.new("th", "SOLIDIFY"); md.thickness = 0.004
m_d = bpy.data.materials.new("Lucido"); m_d.use_nodes = True; m_d.blend_method = "BLEND"; m_d.shadow_method = "HASHED"
bd = m_d.node_tree.nodes["Principled BSDF"]; bd.inputs["Base Color"].default_value = (0.95, 0.93, 0.88, 1)
bd.inputs["Roughness"].default_value = 0.6; bd.inputs["Alpha"].default_value = 0.1
m_d.show_transparent_back = False; m_d.use_backface_culling = True
bd.inputs["Emission Color"].default_value = (1.0, 0.75, 0.45, 1); bd.inputs["Emission Strength"].default_value = 0.0
dome.data.materials.append(m_d)
for t, z, e in ((0.0, 1.6, 0.0), (dome_t, 1.6, 0.0), (dome_t + 0.6, -0.02, 0.0), (dome_t + 0.75, 0.015, 0.15), (dome_t + 0.95, 0.0, 0.05)):
    f = 1 + round(t * FPS); dome.location.z = z; dome.keyframe_insert("location", frame=f)
    bd.inputs["Emission Strength"].default_value = e; bd.inputs["Emission Strength"].keyframe_insert("default_value", frame=f)

# tre cartellini sul piano, davanti al personaggio
tags = [tag_card("tag1", "STRUMENTO", "APPROVATO", (-0.2, -0.27), 6, mats["paper"]),
        tag_card("tag2", "REGOLE", "CHIARE", (0.0, -0.33), -3, mats["paper"]),
        tag_card("tag3", "PERSONE", "FORMATE", (0.2, -0.27), -8, mats["paper"])]
for (o, mx), t in zip(tags, stamps):
    for tt, v in ((t - 0.01, 0.0), (t, 1.0)):
        mx.inputs["Factor"].default_value = v; mx.inputs["Factor"].keyframe_insert("default_value", frame=1 + round(tt * FPS))
# il timbro: manico di carta arrotolata + base rame; scende su ogni cartellino
m_acc = mats["acc"]
bpy.ops.object.empty_add(location=(0.6, -0.3, 0.6)); st = bpy.context.object; st.name = "Timbro"
bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.018, depth=0.07, location=(0, 0, 0.055)); h = bpy.context.object; h.parent = st
h.data.materials.append(mats["obj"])
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.01)); bs = bpy.context.object; bs.scale = (0.035, 0.025, 0.01); bs.parent = st
bs.data.materials.append(m_acc)
def skey(t, x, y, z):
    st.location = (x, y, z); st.keyframe_insert("location", frame=1 + round(t * FPS))
skey(0.0, 0.7, -0.3, 0.7); skey(stamps[0] - 0.6, 0.7, -0.3, 0.7)
for (o, _), t in zip(tags, stamps):
    x, y = o.location.x + 0.11, o.location.y
    skey(t - 0.3, x, y, 0.2); skey(t, x, y, 0.004); skey(t + 0.2, x, y, 0.12)
skey(stamps[-1] + 0.6, 0.75, -0.2, 0.8)

face = [
    (0.0, dict(brow=0, brow_y=6)),
    (dome_t + 0.6, dict(py=1.0, brow_y=24, open=1.1)),            # guarda la cupola che scende
    (stamps[0] - 0.4, dict(py=-0.8, px=-0.6, brow_y=10, open=1.0)),
    (stamps[1] - 0.2, dict(px=0.0, py=-0.9)), (stamps[2] - 0.2, dict(px=0.7, py=-0.8)),
    (loc(LF[0]["start"]), dict(px=0.0, py=0.0, brow=-4, brow_y=14, squint=0.2)),   # "Il lavoro si fa lo stesso..."
    (happy_t, dict(open=0.0, brow_y=26, squint=0.0)),             # "E io resto a casa": occhi felici
    (DUR, dict(open=0.0, brow_y=26)),
] + blink_keys([1.0, stamps[2] + 0.6])
fdir = f"/opt/render/{SID}_face"; n = render_face_sequence(face, DUR, fdir)
rig, sheet, curl, lean = character(sc, pal, fdir, n, loc=(0.0, 0.0), rotz=0)
body = [(0.0, dict(curl=22)), (dome_t + 0.6, dict(squash=0.92)), (dome_t + 0.85, dict(squash=1.0))]
for t in stamps: body += [(t, dict(squash=0.96, lean=-6)), (t + 0.2, dict(squash=1.0, lean=0))]
body += [(loc(LF[0]["start"]) + 0.3, dict(lean=8)), (loc(LF[0]["start"]) + 0.8, dict(lean=0)),       # annuisce
         (happy_t, dict(hop=0.0, squash=0.92)), (happy_t + 0.2, dict(hop=0.05, squash=1.1)),
         (happy_t + 0.45, dict(hop=0.0, squash=0.95)), (happy_t + 0.65, dict(squash=1.0)), (DUR, dict(turn=0))]
key_body(rig, curl, lean, body)

cam, tgt = camera(sc, (0.1, -1.15, 0.45), (0.0, -0.05, 0.13), lens=45, fstop=3.5)
cam.keyframe_insert("location", frame=1); tgt.keyframe_insert("location", frame=1)
cam.location = (0.04, -1.05, 0.38); tgt.location = (0.0, -0.18, 0.07)                        # sui timbri
for k in (1 + round((stamps[0] - 0.8) * FPS),): cam.keyframe_insert("location", frame=k); tgt.keyframe_insert("location", frame=k)
k = 1 + round(happy_t * FPS)
cam.location = (0.05, -1.0, 0.36); tgt.location = (0.0, 0.0, 0.15); cam.keyframe_insert("location", frame=k); tgt.keyframe_insert("location", frame=k)
cam.location = (0.3, -2.4, 1.05); tgt.location = (0.0, 0.2, 0.25); cam.keyframe_insert("location", frame=sc.frame_end); tgt.keyframe_insert("location", frame=sc.frame_end)
lights(pal)
sc.frame_set(1 + round((stamps[1] + 0.1) * FPS))
bpy.ops.wm.save_as_mainfile(filepath=f"{ROOT}/blender/{SID}.blend", copy=True)
print(f"SCENA {SID} PRONTA: {sc.frame_end} fotogrammi, timbri a {[round(s,2) for s in stamps]}")
