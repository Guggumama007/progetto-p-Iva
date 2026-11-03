"""paperlib - libreria comune del mondo di carta per "Sono un contratto".
Caricata nelle scene con: exec(open(".../blender/paperlib.py").read())
(funziona sia via MCP dentro la sessione viva, sia da riga di comando).

Contiene: palette, materiali di carta, fondale curvo, oggetti di carta, il personaggio
(foglio con volto animato a sequenza di immagini) e l'impostazione del render stop-motion.
"""
import bpy, math, os, json, random
from PIL import Image, ImageDraw, ImageFilter

ROOT = "/home/user/APEX-AI-Terminal/video-shadow-ai"
TEX = f"{ROOT}/blender/tex"
FPS = 12  # stop-motion

PAL = {
    # casa / azienda: kraft caldo
    "home": dict(bg=(0.28, 0.18, 0.11), desk=(0.45, 0.3, 0.18), paper=(0.95, 0.93, 0.87), acc=(0.75, 0.2, 0.08),
                 obj=(0.2, 0.25, 0.35), warm=(1.0, 0.85, 0.65), cold=(0.8, 0.85, 1.0), sun=3.5),
    # fuori: blu notte
    "out": dict(bg=(0.01, 0.02, 0.045), desk=(0.04, 0.07, 0.14), paper=(0.93, 0.9, 0.82), acc=(0.75, 0.2, 0.08),
                obj=(0.08, 0.12, 0.22), warm=(1.0, 0.6, 0.35), cold=(0.45, 0.6, 1.0), sun=0.8),
}


def timeline():
    return json.load(open(f"{ROOT}/timeline.json"))


def scene_span(tl, sid):
    s = next(x for x in tl["scenes"] if x["id"] == sid)
    return s["start"], s["end"]


def lines_of(tl, sid):
    return [l for l in tl["lines"] if l["scene"] == sid]


def reset_scene():
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.images,
                 bpy.data.worlds, bpy.data.curves, bpy.data.actions):
        for b in list(coll): coll.remove(b)


def setup_render(sc, seconds, out_dir, pal, pct=67, samples=14):
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, pct
    sc.render.fps = FPS; sc.frame_start = 1; sc.frame_end = max(1, round(seconds * FPS))
    ee = sc.eevee
    ee.taa_render_samples = samples; ee.use_gtao = True; ee.gtao_distance = 0.25; ee.gtao_factor = 1.2
    ee.use_soft_shadows = True; ee.shadow_cube_size = "1024"; ee.shadow_cascade_size = "2048"; ee.use_bloom = pal is PAL["out"]
    ee.bloom_intensity = 0.04
    sc.view_settings.view_transform = "Filmic"; sc.view_settings.look = "Medium Contrast"
    sc.render.image_settings.file_format = "JPEG"; sc.render.image_settings.quality = 93
    os.makedirs(out_dir, exist_ok=True); sc.render.filepath = os.path.join(out_dir, "f_")
    w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (*pal["bg"], 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.8


def paper_mat(name, color, fiber=0.06, rough=0.85, emission=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    b.inputs["Specular IOR Level"].default_value = 0.2
    b.inputs["Subsurface Weight"].default_value = 0.08
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 180; n.inputs["Detail"].default_value = 8
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = fiber; mix.inputs["A"].default_value = (*color, 1)
    nt.links.new(n.outputs["Color"], mix.inputs["B"]); nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    n2 = nt.nodes.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 6; n2.inputs["Detail"].default_value = 3
    add = nt.nodes.new("ShaderNodeMath"); add.operation = "MULTIPLY_ADD"; add.inputs[1].default_value = 0.35
    nt.links.new(n.outputs["Fac"], add.inputs[0]); nt.links.new(n2.outputs["Fac"], add.inputs[2])
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.12
    nt.links.new(add.outputs[0], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    if emission:
        b.inputs["Emission Color"].default_value = (*emission[0], 1); b.inputs["Emission Strength"].default_value = emission[1]
    m.use_backface_culling = False
    return m


def sweep(sc, mat, width=6.0, depth=3.0, r=0.9, back=1.4, height=3.0, steps=24):
    """Unico foglio curvo: piano + fondale, come la carta di uno studio fotografico."""
    prof = [(-depth, 0.0), (back - r, 0.0)]
    for k in range(1, steps):
        a = (math.pi / 2) * k / steps
        prof.append((back - r + r * math.sin(a), r - r * math.cos(a)))
    prof += [(back, r), (back, height)]
    xs = [-width / 2 + width * i / 40 for i in range(41)]
    verts = [(x, y, z) for (y, z) in prof for x in xs]
    n = len(xs); faces = []
    for j in range(len(prof) - 1):
        for i in range(n - 1):
            faces.append((j * n + i, j * n + i + 1, (j + 1) * n + i + 1, (j + 1) * n + i))
    me = bpy.data.meshes.new("Sweep"); me.from_pydata(verts, [], faces); me.update()
    o = bpy.data.objects.new("Sweep", me); sc.collection.objects.link(o)
    for poly in me.polygons: poly.use_smooth = True
    me.materials.append(mat)
    return o


def folded_box(name, size, loc, mat, rot=0.0, bevel=0.004):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object; o.name = name; o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    o.rotation_euler = (0, 0, math.radians(rot)); bpy.ops.object.transform_apply(scale=True)
    md = o.modifiers.new("b", "BEVEL"); md.width = bevel; md.segments = 1
    o.data.materials.append(mat)
    return o


def paper_mug(loc, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.07, depth=0.13, location=(loc[0], loc[1], 0.065))
    mug = bpy.context.object; mug.data.materials.append(mat)
    mug.modifiers.new("th", "SOLIDIFY").thickness = 0.003
    bpy.ops.mesh.primitive_torus_add(major_radius=0.035, minor_radius=0.008, major_segments=10, minor_segments=4,
                                     location=(loc[0] + 0.075, loc[1], 0.07))
    h = bpy.context.object; h.rotation_euler = (math.radians(90), 0, 0); h.data.materials.append(mat)
    return mug


def paper_laptop(loc, mat_body, mat_screen, rot=14):
    x, y = loc
    folded_box("Lap", (0.42, 0.28, 0.012), (x, y, 0.006), mat_body, rot=rot)
    r = math.radians(rot)
    ox, oy = -0.176 * math.sin(r), 0.176 * math.cos(r)          # centro del coperchio rispetto alla base
    scr = folded_box("Scr", (0.42, 0.28, 0.008), (x + ox, y + oy, 0.147), mat_body, rot=rot)
    scr.rotation_euler = (math.radians(75), 0, r)
    # schermo: foglio chiaro incollato sul coperchio (lato verso la camera)
    fx, fy = 0.0045 * 0.966 * math.sin(r), -0.0045 * 0.966 * math.cos(r)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x + ox + fx, y + oy + fy, 0.147 + 0.0012))
    s = bpy.context.object; s.name = "ScreenFace"; s.scale = (0.38, 0.24, 1)
    s.rotation_euler = (math.radians(75), 0, r); s.data.materials.append(mat_screen)
    return scr, s


# ---------------------------------------------------------------- volto animato
FACE_W, FACE_H = 600, 849  # A4 in proporzione


def _lerp(a, b, t): return a + (b - a) * t


def face_params(keys, t):
    """keys: lista di (tempo_s, {param: valore}); interpolazione morbida tra chiavi."""
    base = dict(open=1.0, px=0.0, py=0.0, brow=0.0, brow_y=0.0, squint=0.0)
    cur = dict(base)
    for k in sorted(keys, key=lambda k: k[0]):
        if k[0] <= t: cur.update(k[1])
    prev = sorted([k for k in keys if k[0] <= t], key=lambda k: k[0])
    nxt = sorted([k for k in keys if k[0] > t], key=lambda k: k[0])
    if prev and nxt:
        t0, t1 = prev[-1][0], nxt[0][0]
        u = (t - t0) / max(1e-6, t1 - t0); u = u * u * (3 - 2 * u)
        before = dict(base)
        for k in prev: before.update(k[1])
        after = dict(before); after.update(nxt[0][1])
        cur = {p: _lerp(before[p], after[p], u) for p in base}
    return cur


def draw_face(p, path):
    """Inchiostro su trasparente: sopracciglio (ex riga del titolo), occhi, righe di testo, firma."""
    s = FACE_W / 840
    im = Image.new("RGBA", (FACE_W, FACE_H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ink = (22, 26, 38, 255); soft = (22, 26, 38, 150); copper = (170, 70, 30, 255); white = (255, 255, 255, 255)
    cx, cy = FACE_W / 2, 380 * s
    # sopracciglio unico: angolo (brow, gradi; >0 = perplesso/alzato a destra) e quota (brow_y, px)
    ang = math.radians(p["brow"]); L = 170 * s; by = 135 * s - p["brow_y"] * s
    dx, dy = L * math.cos(ang), L * math.sin(ang)
    d.line((cx - dx, by + dy, cx + dx, by - dy), fill=ink, width=int(22 * s))
    for e in (-1, 1):
        ex = cx + e * 120 * s + p["px"] * 22 * s
        h = 62 * s * max(0.0, min(1.0, p["open"])) * (1 - 0.35 * p["squint"])
        if h < 8 * s:  # chiuso: arco
            d.arc((ex - 46 * s, cy - 20 * s, ex + 46 * s, cy + 40 * s), 200, 340, fill=ink, width=int(14 * s))
        else:
            ey = cy - p["py"] * 10 * s
            d.ellipse((ex - 42 * s, ey - h, ex + 42 * s, ey + h), fill=ink)
            gx, gy = ex + (16 + p["px"] * 14) * s, cy - (29 - p["py"] * 12) * s * h / (62 * s)
            r = 10 * s
            d.ellipse((gx - r, gy - r, gx + r, gy + r), fill=white)
    for i, wdt in enumerate([520, 560, 500, 545, 470, 530, 380]):
        y = (610 + i * 52) * s; x0 = (FACE_W - 560 * s) / 2
        d.rounded_rectangle((x0, y, x0 + wdt * s, y + 14 * s), int(7 * s), fill=soft)
    pts = [((470 + t * 4) * s, (1035 + 22 * math.sin(t / 5.5) - t * 0.6) * s) for t in range(60)]
    d.line(pts, fill=copper, width=int(7 * s), joint="curve")
    d.line((440 * s, 1075 * s, 740 * s, 1075 * s), fill=soft, width=int(4 * s))
    im.filter(ImageFilter.GaussianBlur(0.5)).save(path)


def blink_keys(times, dur=0.17):
    k = []
    for t in times:
        k += [(t - 0.01, {"open": 1.0}), (t, {"open": 0.0}), (t + dur, {"open": 0.0}), (t + dur + 0.01, {"open": 1.0})]
    return k


def render_face_sequence(keys, seconds, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    n = max(1, round(seconds * FPS))
    for f in range(1, n + 1):
        draw_face(face_params(keys, (f - 1) / FPS), os.path.join(out_dir, f"face_{f:04d}.png"))
    return n


def character(sc, pal, face_dir, nframes, loc=(0, 0), rotz=-8):
    """Il contratto: foglio in piedi, curvo, volto a sequenza. Restituisce (rig, foglio, modificatore curl)."""
    bpy.ops.object.empty_add(location=(loc[0], loc[1], 0)); rig = bpy.context.object; rig.name = "Rig"
    rig.rotation_euler = (0, 0, math.radians(rotz))
    # foglio verticale (piano XZ, faccia verso -Y = verso la camera), base a z=0:
    # cosi' BEND asse Z arriccia la larghezza e BEND asse X inchina il foglio dalla base
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0), rotation=(math.radians(90), 0, 0))
    c = bpy.context.object; c.name = "Contratto"
    bpy.ops.object.transform_apply(rotation=True)
    c.scale = (0.21, 1, 0.297); bpy.ops.object.transform_apply(scale=True)
    for v in c.data.vertices: v.co.z += 0.1485
    c.parent = rig
    c.modifiers.new("sub", "SUBSURF").levels = 3; c.modifiers["sub"].subdivision_type = "SIMPLE"; c.modifiers["sub"].render_levels = 3
    curl = c.modifiers.new("curl", "SIMPLE_DEFORM"); curl.deform_method = "BEND"; curl.deform_axis = "Z"; curl.angle = math.radians(22)
    lean = c.modifiers.new("lean", "SIMPLE_DEFORM"); lean.deform_method = "BEND"; lean.deform_axis = "X"; lean.angle = 0
    c.modifiers.new("th", "SOLIDIFY").thickness = 0.0015
    m = bpy.data.materials.new("Face"); m.use_nodes = True
    nt = m.node_tree; bf = nt.nodes["Principled BSDF"]
    bf.inputs["Roughness"].default_value = 0.85; bf.inputs["Specular IOR Level"].default_value = 0.2
    bf.inputs["Subsurface Weight"].default_value = 0.08
    tx = nt.nodes.new("ShaderNodeTexImage")
    img = bpy.data.images.load(os.path.join(face_dir, "face_0001.png")); img.source = "SEQUENCE"
    tx.image = img; tx.image_user.frame_duration = nframes; tx.image_user.frame_start = 1
    tx.image_user.use_auto_refresh = True; tx.image_user.use_cyclic = False
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.inputs["A"].default_value = (*pal["paper"], 1)
    nt.links.new(tx.outputs["Alpha"], mx.inputs["Factor"]); nt.links.new(tx.outputs["Color"], mx.inputs["B"])
    nt.links.new(mx.outputs["Result"], bf.inputs["Base Color"])
    m.use_backface_culling = False
    c.data.materials.append(m)
    # piede: piccola piega sul piano
    foot = folded_box("Piede", (0.2, 0.05, 0.002), (0, -0.02, 0.001), paper_mat("Foot", pal["paper"], 0.04))
    foot.parent = rig
    return rig, c, curl, lean


def key_body(rig, curl, lean, keys):
    """keys: lista di (tempo_s, dict) con hop (m), squash, curl (gradi), lean (gradi), turn (gradi), x, y."""
    state = dict(hop=0.0, squash=1.0, curl=22.0, lean=0.0, turn=0.0, x=rig.location.x, y=rig.location.y)
    base_rot = rig.rotation_euler.z
    for t, kv in sorted(keys, key=lambda k: k[0]):
        state.update(kv); f = 1 + round(t * FPS)
        rig.location = (state["x"], state["y"], state["hop"]); rig.keyframe_insert("location", frame=f)
        rig.scale = (1 / math.sqrt(state["squash"]), 1 / math.sqrt(state["squash"]), state["squash"]); rig.keyframe_insert("scale", frame=f)
        rig.rotation_euler = (0, 0, base_rot + math.radians(state["turn"])); rig.keyframe_insert("rotation_euler", frame=f)
        curl.angle = math.radians(state["curl"]); curl.keyframe_insert("angle", frame=f)
        lean.angle = math.radians(-state["lean"]); lean.keyframe_insert("angle", frame=f)


def camera(sc, loc, target, lens=50, fstop=2.8):
    bpy.ops.object.camera_add(location=loc); cam = bpy.context.object; sc.camera = cam
    cam.data.lens = lens; cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = fstop
    bpy.ops.object.empty_add(location=target); tgt = bpy.context.object; tgt.name = "CamTarget"
    cam.data.dof.focus_object = tgt
    t = cam.constraints.new("TRACK_TO"); t.target = tgt; t.track_axis = "TRACK_NEGATIVE_Z"; t.up_axis = "UP_Y"
    return cam, tgt


def lights(pal, sun_energy=None):
    bpy.ops.object.light_add(type="SUN", location=(2, -2, 3)); sun = bpy.context.object
    sun.data.energy = sun_energy if sun_energy is not None else pal["sun"]; sun.data.color = pal["warm"]; sun.data.angle = math.radians(6)
    sun.rotation_euler = (math.radians(58), math.radians(8), math.radians(55))
    bpy.ops.object.light_add(type="AREA", location=(-1.5, -1.2, 1.4)); fl = bpy.context.object
    fl.data.energy = 80; fl.data.size = 2.5; fl.data.color = pal["cold"]; fl.rotation_euler = (math.radians(60), 0, math.radians(-50))
    bpy.ops.object.light_add(type="AREA", location=(0.2, 1.2, 0.8)); rim = bpy.context.object
    rim.data.energy = 40; rim.data.size = 1.0; rim.data.color = pal["warm"]; rim.rotation_euler = (math.radians(-60), 0, 0)
    return sun, fl, rim


def home_desk(sc, pal):
    """La scrivania di casa: fondale kraft, tazza, portatile, matita, due fogli sparsi, cavo verso il bordo."""
    m_desk = paper_mat("Desk", pal["desk"], fiber=0.18)
    m_paper = paper_mat("Paper", pal["paper"], fiber=0.04)
    m_acc = paper_mat("Accent", pal["acc"], fiber=0.08)
    m_obj = paper_mat("Obj", pal["obj"], fiber=0.08)
    m_scr = paper_mat("Screen", (0.85, 0.9, 0.95), fiber=0.02, emission=((0.75, 0.85, 1.0), 0.6))
    sweep(sc, m_desk)
    paper_mug((0.33, 0.4), m_acc)
    scr, face = paper_laptop((-0.5, 0.42), m_obj, m_scr)
    bpy.ops.curve.primitive_bezier_curve_add(location=(0, 0, 0)); cab = bpy.context.object; cab.name = "Cavo"
    pts = cab.data.splines[0].bezier_points
    pts[0].co = (-0.72, 0.5, 0.012); pts[0].handle_left = (-0.6, 0.55, 0.012); pts[0].handle_right = (-0.9, 0.3, 0.012)
    pts[1].co = (-1.3, -0.5, 0.012); pts[1].handle_left = (-1.0, -0.2, 0.012); pts[1].handle_right = (-1.6, -0.8, 0.012)
    cab.data.bevel_depth = 0.012; cab.data.bevel_resolution = 1; cab.data.materials.append(m_obj)
    folded_box("Pen", (0.2, 0.016, 0.016), (0.25, -0.16, 0.008), m_acc, rot=-28)
    for (x, y, rz) in [(-0.95, 0.55, 0.4), (0.9, 0.7, -0.3)]:
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, 0.001))
        sh = bpy.context.object; sh.scale = (0.21, 0.297, 1); sh.rotation_euler = (0, 0, rz); sh.data.materials.append(m_paper)
    return dict(desk=m_desk, paper=m_paper, acc=m_acc, obj=m_obj, screen=m_scr, screen_face=face)


def screen_image(mat, path, strength=0.9):
    """Mette un'immagine sullo schermo di carta (base color + leggera emissione)."""
    nt = mat.node_tree; b = nt.nodes["Principled BSDF"]
    tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = bpy.data.images.load(path)
    nt.links.new(tx.outputs["Color"], b.inputs["Base Color"]); nt.links.new(tx.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = strength


def cut_shape(name, pts2d, mat, thick=0.003):
    """Sagoma ritagliata nella carta da una lista di punti 2D (piano XZ, faccia verso -Y)."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([(x, 0, z) for x, z in pts2d], [], [list(range(len(pts2d)))]); me.update()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.modifiers.new("th", "SOLIDIFY").thickness = thick
    o.data.materials.append(mat)
    return o


def ghost_sheet(name, face_png, tint=(0.75, 0.85, 1.0), alpha=0.55):
    """Copia 'fantasma' del contratto: foglio semitrasparente con il volto statico."""
    bpy.ops.mesh.primitive_plane_add(size=1, rotation=(math.radians(90), 0, 0)); g = bpy.context.object; g.name = name
    bpy.ops.object.transform_apply(rotation=True); g.scale = (0.21, 1, 0.297); bpy.ops.object.transform_apply(scale=True)
    for v in g.data.vertices: v.co.z += 0.1485
    m = bpy.data.materials.new(name + "M"); m.use_nodes = True; m.blend_method = "BLEND"; m.shadow_method = "NONE"
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = bpy.data.images.load(face_png)
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.inputs["A"].default_value = (*tint, 1)
    nt.links.new(tx.outputs["Alpha"], mx.inputs["Factor"]); nt.links.new(tx.outputs["Color"], mx.inputs["B"])
    nt.links.new(mx.outputs["Result"], b.inputs["Base Color"]); nt.links.new(mx.outputs["Result"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 0.6; b.inputs["Alpha"].default_value = alpha
    g.data.materials.append(m)
    return g, b


def word_time(line, word, edge="end"):
    """Istante (assoluto, s) di una parola nella battuta. Se la timeline ha i tempi parola per parola
    (faster-whisper) li usa; altrimenti stima per proporzione di caratteri dentro i segmenti VAD."""
    if line.get("words"):
        for w in line["words"]:
            if word.lower() in w["w"].lower(): return w["end" if edge == "end" else "start"]
    text = line["caption"]; idx = text.lower().find(word.lower())
    pos = (idx + (len(word) if edge == "end" else 0)) / max(1, len(text))
    segs = line.get("pauses") or [[0, line["speech"]]]
    total = sum(b - a for a, b in segs); target = pos * total; acc = 0.0
    for a, b in segs:
        if acc + (b - a) >= target: return line["start"] + a + (target - acc)
        acc += b - a
    return line["end"]


def tag_card(name, text, sub, loc, rotz, mat_paper):
    """Cartellino di carta con testo; restituisce (oggetto, nodo mix 'timbrato' 0..1)."""
    from PIL import ImageFont
    F = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    for stamped in (0, 1):
        im = Image.new("RGB", (900, 360), (240, 233, 218)); d = ImageDraw.Draw(im)
        d.text((60, 70), text, font=ImageFont.truetype(F, 74), fill=(28, 32, 46))
        d.text((60, 190), sub, font=ImageFont.truetype(F, 74), fill=(28, 32, 46))
        if stamped:
            d.rounded_rectangle((640, 60, 860, 300), 30, outline=(170, 65, 28), width=16)
            d.line([(680, 185), (735, 245), (825, 110)], fill=(170, 65, 28), width=26, joint="curve")
        im.save(f"{TEX}/{name}_{stamped}.png")
    m = paper_mat(name + "M", (0.94, 0.91, 0.85), fiber=0.05)
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    t0 = nt.nodes.new("ShaderNodeTexImage"); t0.image = bpy.data.images.load(f"{TEX}/{name}_0.png")
    t1 = nt.nodes.new("ShaderNodeTexImage"); t1.image = bpy.data.images.load(f"{TEX}/{name}_1.png")
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.inputs["Factor"].default_value = 0.0
    nt.links.new(t0.outputs["Color"], mx.inputs["A"]); nt.links.new(t1.outputs["Color"], mx.inputs["B"])
    nt.links.new(mx.outputs["Result"], b.inputs["Base Color"])
    bpy.ops.mesh.primitive_plane_add(size=1, location=(loc[0], loc[1], 0.0015)); o = bpy.context.object; o.name = name
    o.scale = (0.17, 0.068, 1); o.rotation_euler = (0, 0, math.radians(rotz)); o.data.materials.append(m)
    return o, mx
