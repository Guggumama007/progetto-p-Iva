"""Scena 4b + 5 - La sala server sconosciuta (blu notte) e "Shadow AI".
Armadi di cartone con luci a scatti, nebbia, cartellino "PAESE: ?". Il contratto, piccolo nel corridoio,
si guarda intorno; poi guarda in camera per il titolo."""
exec(open("/home/user/APEX-AI-Terminal/video-shadow-ai/blender/paperlib.py").read())

SID = "server"
tl = timeline(); v0, v1 = scene_span(tl, "viaggio"); n0, n1 = scene_span(tl, "nome")
T0 = v0 + 3.3; DUR = n1 - T0                        # inizia a fine tunnel, finisce con il titolo
lv = [(l["start"] - T0, l["end"] - T0) for l in lines_of(tl, "viaggio")]
ln = [(l["start"] - T0, l["end"] - T0) for l in lines_of(tl, "nome")]
pal = PAL["out"]; random.seed(21)
reset_scene(); sc = bpy.context.scene
setup_render(sc, DUR, f"/opt/render/{SID}", pal)
w = sc.world.node_tree
vol = w.nodes.new("ShaderNodeVolumePrincipled"); vol.inputs["Density"].default_value = 0.06
vol.inputs["Color"].default_value = (0.35, 0.45, 0.7, 1); w.links.new(vol.outputs[0], w.nodes["World Output"].inputs["Volume"])
sc.eevee.use_volumetric_lights = True; sc.eevee.volumetric_tile_size = "8"

m_floor = paper_mat("Floor", pal["desk"], fiber=0.2)
m_box = paper_mat("Cardboard", (0.06, 0.09, 0.16), fiber=0.25)
sweep(sc, m_floor, width=12, depth=6, back=9, r=1.5, height=6)
# luci LED: materiali emissivi (rame, rosso, azzurro) con lampeggio a scatti
led_mats = []
for name, col in (("LedCu", (1.0, 0.45, 0.15)), ("LedRed", (1.0, 0.12, 0.08)), ("LedBlue", (0.35, 0.6, 1.0))):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Emission Color"].default_value = (*col, 1)
    led_mats.append((m, b))
for (m, b) in led_mats:
    for f in range(1, round(DUR * FPS) + 2, 3):
        b.inputs["Emission Strength"].default_value = random.choice([0.2, 2.5, 6.0, 6.0])
        b.inputs["Emission Strength"].keyframe_insert("default_value", frame=f)
        fc = m.node_tree.animation_data.action.fcurves[-1]
    for fc in m.node_tree.animation_data.action.fcurves:
        for k in fc.keyframe_points: k.interpolation = "CONSTANT"
# due file di armadi lungo il corridoio
for side in (-1, 1):
    for i in range(7):
        x = side * random.uniform(0.55, 0.62); y = 0.3 + i * 0.9
        h = random.uniform(1.1, 1.6)
        rack = folded_box(f"Rack{side}{i}", (0.5, 0.7, h), (x + side * 0.25, y, h / 2), m_box, bevel=0.01)
        for r in range(int(h / 0.08)):
            for c in range(3):
                if random.random() < 0.55:
                    bpy.ops.mesh.primitive_cube_add(size=1, location=(x - side * 0.003, y - 0.25 + c * 0.05, 0.1 + r * 0.08))
                    led = bpy.context.object; led.scale = (0.006, 0.012, 0.008)
                    led.data.materials.append(random.choice(led_mats)[0])
# cavi di carta sul pavimento che entrano nel corridoio
m_cable = paper_mat("Cable", (0.15, 0.2, 0.32), fiber=0.1)
for k, xo in enumerate((-0.42, -0.3, 0.3, 0.42)):
    bpy.ops.curve.primitive_bezier_curve_add(location=(0, 0, 0)); cb = bpy.context.object
    p = cb.data.splines[0].bezier_points
    p[0].co = (xo, -2.0, 0.01); p[0].handle_right = (xo, -1.0, 0.01); p[0].handle_left = (xo, -2.5, 0.01)
    p[1].co = (xo * 0.8, 6.0, 0.01); p[1].handle_left = (xo * 0.8, 4.0, 0.01); p[1].handle_right = (xo * 0.8, 7, 0.01)
    cb.data.bevel_depth = 0.01; cb.data.materials.append(m_cable)
# cartellino appeso "PAESE: ?"
m_tag = paper_mat("Tag", (0.92, 0.88, 0.8), fiber=0.05)
tx = m_tag.node_tree.nodes.new("ShaderNodeTexImage"); tx.image = bpy.data.images.load(f"{TEX}/tag_paese.png")
m_tag.node_tree.links.new(tx.outputs["Color"], m_tag.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
bpy.ops.mesh.primitive_plane_add(size=1, location=(0.24, 0.75, 0.42), rotation=(math.radians(90), 0, math.radians(-10)))
tag = bpy.context.object; tag.scale = (0.2, 0.1, 1); tag.data.materials.append(m_tag)
bpy.ops.mesh.primitive_cylinder_add(radius=0.0015, depth=1.2, location=(0.24, 0.76, 1.07)); bpy.context.object.data.materials.append(m_cable)
for f, rz in ((1, -10), (round(DUR * FPS * 0.5), 6), (round(DUR * FPS), -8)):      # dondola
    tag.rotation_euler.z = math.radians(rz); tag.keyframe_insert("rotation_euler", frame=f)

look_t = lv[1][0]; tag_t = lv[1][0] + 1.6
face = [
    (0.0, dict(open=1.2, brow_y=28, px=0, py=0.3)),                   # appena arrivato: occhi grandi
    (look_t, dict(px=-1.0, py=0.2, brow=-12, brow_y=16, open=1.0)),   # "Peccato che adesso io sia qui"
    (look_t + 0.8, dict(px=1.0, brow=12)),
    (tag_t, dict(px=0.6, py=1.0, brow=16, brow_y=22)),                # guarda il cartellino
    (ln[0][0] - 0.2, dict(px=0.0, py=0.0, brow=0, brow_y=4, squint=0.5)),   # "Questa si chiama Shadow AI"
    (DUR, dict(squint=0.5)),
] + blink_keys([1.0, tag_t + 0.9])
fdir = f"/opt/render/{SID}_face"; n = render_face_sequence(face, DUR, fdir)
rig, sheet, curl, lean = character(sc, PAL["home"], fdir, n, loc=(0.0, 0.6), rotz=0)
key_body(rig, curl, lean, [
    (0.0, dict(hop=0.06, squash=1.1, curl=26)), (0.25, dict(hop=0.0, squash=0.9)), (0.5, dict(squash=1.0)),   # atterra
    (look_t, dict(turn=-25)), (look_t + 0.8, dict(turn=25)), (tag_t, dict(turn=10, lean=-10)),
    (ln[0][0] - 0.2, dict(turn=0, lean=0)), (DUR, dict(turn=0)),
])
# luce: taglio freddo dall'alto e un'ombra rossa dal fondo; un piccolo spot caldo sul personaggio
bpy.ops.object.light_add(type="SPOT", location=(0, -0.6, 2.6)); s1 = bpy.context.object
s1.data.energy = 120; s1.data.spot_size = math.radians(35); s1.data.color = (0.6, 0.72, 1.0); s1.rotation_euler = (math.radians(-12), 0, 0)
bpy.ops.object.light_add(type="POINT", location=(0, 6.5, 0.8)); s2 = bpy.context.object; s2.data.energy = 300; s2.data.color = (1.0, 0.25, 0.12)
bpy.ops.object.light_add(type="AREA", location=(0.3, -0.3, 0.5)); s3 = bpy.context.object
s3.data.energy = 6; s3.data.size = 0.4; s3.data.color = (1.0, 0.8, 0.6); s3.rotation_euler = (math.radians(70), 0, math.radians(20))
cam, tgt = camera(sc, (0.0, -0.9, 0.35), (0.0, 0.6, 0.2), lens=32, fstop=4.0)
cam.keyframe_insert("location", frame=1)
cam.location = (0.04, -0.2, 0.25); cam.keyframe_insert("location", frame=1 + round(ln[0][0] * FPS))
cam.location = (0.03, -0.05, 0.22); cam.keyframe_insert("location", frame=sc.frame_end)
sc.frame_set(1 + round(tag_t * FPS))
bpy.ops.wm.save_as_mainfile(filepath=f"{ROOT}/blender/{SID}.blend", copy=True)
print(f"SCENA {SID} PRONTA: {sc.frame_end} fotogrammi")
