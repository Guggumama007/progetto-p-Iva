"""Style frame - "Sono un contratto", mondo di carta.
Costruito nella sessione Blender viva via MCP. Tutto e' carta: scrivania in cartoncino
con pieghe, tazza e portatile di carta, il contratto-personaggio con occhi minimali.
PALETTE viene sostituita dal client prima dell'invio.
"""
import bpy, math, random, os

PALETTE = "brand"
HERE = "/home/user/APEX-AI-Terminal/video-shadow-ai/blender"
random.seed(5)

PAL = {
    # sfondo, piano, carta contratto, accento, oggetti secondari, luce calda, luce fredda
    "brand":  dict(bg=(0.02, 0.035, 0.07), desk=(0.06, 0.09, 0.16), paper=(0.93, 0.9, 0.82), acc=(0.62, 0.22, 0.08), obj=(0.55, 0.42, 0.3), warm=(1.0, 0.78, 0.55), cold=(0.55, 0.7, 1.0)),
    "kraft":  dict(bg=(0.28, 0.18, 0.11), desk=(0.45, 0.3, 0.18), paper=(0.95, 0.93, 0.87), acc=(0.75, 0.2, 0.08), obj=(0.2, 0.25, 0.35), warm=(1.0, 0.85, 0.65), cold=(0.8, 0.85, 1.0)),
    "pastel": dict(bg=(0.55, 0.68, 0.7), desk=(0.82, 0.78, 0.7), paper=(0.98, 0.97, 0.94), acc=(0.85, 0.38, 0.22), obj=(0.25, 0.45, 0.5), warm=(1.0, 0.92, 0.8), cold=(0.75, 0.88, 1.0)),
}[PALETTE]

for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.images, bpy.data.worlds, bpy.data.curves):
    for b in list(coll): coll.remove(b)

sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 67
ee = sc.eevee
ee.taa_render_samples = 32; ee.use_gtao = True; ee.gtao_distance = 0.25; ee.gtao_factor = 1.2
ee.use_soft_shadows = True; ee.shadow_cube_size = "1024"; ee.shadow_cascade_size = "2048"
ee.use_bloom = False
sc.view_settings.view_transform = "Filmic"; sc.view_settings.look = "Medium Contrast"

w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (*PAL["bg"], 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.8


def paper_mat(name, color, fiber=0.06, rough=0.85):
    """Carta: colore + fibra (noise) + leggero rilievo, un po' di traslucenza."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    b.inputs["Specular IOR Level"].default_value = 0.2
    b.inputs["Subsurface Weight"].default_value = 0.08
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 180; n.inputs["Detail"].default_value = 8
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = fiber
    mix.inputs["A"].default_value = (*color, 1)
    nt.links.new(n.outputs["Color"], mix.inputs["B"]); nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    n2 = nt.nodes.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 6; n2.inputs["Detail"].default_value = 3
    add = nt.nodes.new("ShaderNodeMath"); add.operation = "MULTIPLY_ADD"; add.inputs[1].default_value = 0.35
    nt.links.new(n.outputs["Fac"], add.inputs[0]); nt.links.new(n2.outputs["Fac"], add.inputs[2])
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.12
    nt.links.new(add.outputs[0], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    m.use_backface_culling = False
    return m


def folded_box(name, size, loc, mat, rot=0.0, bevel=0.004):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object; o.name = name; o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    o.rotation_euler = (0, 0, math.radians(rot)); bpy.ops.object.transform_apply(scale=True)
    md = o.modifiers.new("b", "BEVEL"); md.width = bevel; md.segments = 1   # spigolo "piegato", non arrotondato
    o.data.materials.append(mat)
    return o

m_desk = paper_mat("Desk", PAL["desk"], fiber=0.18)
m_paper = paper_mat("Paper", PAL["paper"], fiber=0.04)
m_acc = paper_mat("Accent", PAL["acc"], fiber=0.08)
m_obj = paper_mat("Obj", PAL["obj"], fiber=0.08)
m_ink = bpy.data.materials.new("Ink"); m_ink.use_nodes = True
m_ink.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.01, 0.012, 0.02, 1)
m_ink.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.35
m_line = paper_mat("Lines", tuple(c * 0.55 for c in PAL["paper"]), fiber=0.0)

# --- mondo: un unico foglio di carta curvo (piano + fondale, come uno studio fotografico)
def sweep(mat, width=6.0, depth=3.0, r=0.9, back=1.4, height=3.0, steps=24):
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
sweep(m_desk)

# --- il contratto-personaggio: foglio in piedi, leggermente curvo, con le righe e gli occhi
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.297 / 2 + 0.002))
c = bpy.context.object; c.name = "Contratto"
c.scale = (0.21, 0.297, 1); c.rotation_euler = (math.radians(84), 0, math.radians(-8))
bpy.ops.object.transform_apply(scale=True)
md = c.modifiers.new("sub", "SUBSURF"); md.levels = 3; md.subdivision_type = "SIMPLE"
md = c.modifiers.new("curl", "SIMPLE_DEFORM"); md.deform_method = "BEND"; md.deform_axis = "Y"; md.angle = math.radians(22)
sol = c.modifiers.new("th", "SOLIDIFY"); sol.thickness = 0.0015
c.data.materials.append(m_paper)
# volto e testo: texture d'inchiostro (segue la curvatura del foglio)
m_face = bpy.data.materials.new("Face"); m_face.use_nodes = True
nt = m_face.node_tree; bf = nt.nodes["Principled BSDF"]
bf.inputs["Roughness"].default_value = 0.85; bf.inputs["Specular IOR Level"].default_value = 0.2
bf.inputs["Subsurface Weight"].default_value = 0.08
tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = bpy.data.images.load(os.path.join(HERE, "tex", "face_open.png"))
tx.name = "FaceTex"
mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.inputs["A"].default_value = (*PAL["paper"], 1)
nt.links.new(tx.outputs["Alpha"], mx.inputs["Factor"]); nt.links.new(tx.outputs["Color"], mx.inputs["B"])
nt.links.new(mx.outputs["Result"], bf.inputs["Base Color"])
m_face.use_backface_culling = False
c.data.materials.clear(); c.data.materials.append(m_face)
# ombra di contatto: il foglio "poggia" su una piccola base piegata
folded_box("Piede", (0.2, 0.05, 0.002), (0.0, -0.02, 0.001), m_paper, rot=-8)

# --- tazza di carta (cilindro a 10 facce = pieghe visibili) e manico a nastro
bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.07, depth=0.13, location=(0.33, 0.4, 0.065))
mug = bpy.context.object; mug.data.materials.append(m_acc)
sol = mug.modifiers.new("th", "SOLIDIFY"); sol.thickness = 0.003
bpy.ops.mesh.primitive_torus_add(major_radius=0.035, minor_radius=0.008, major_segments=10, minor_segments=4, location=(0.405, 0.4, 0.07))
hd = bpy.context.object; hd.rotation_euler = (math.radians(90), 0, 0); hd.data.materials.append(m_acc)
# --- portatile di carta piegata, chiuso a meta'
lap = folded_box("Lap", (0.42, 0.28, 0.012), (-0.5, 0.42, 0.006), m_obj, rot=14)
scr = folded_box("Scr", (0.42, 0.28, 0.008), (-0.465, 0.6, 0.15), m_obj, rot=14)
scr.rotation_euler = (math.radians(75), 0, math.radians(14))
# cavo di carta che esce dal portatile verso il bordo: il "viaggio" futuro
bpy.ops.curve.primitive_bezier_curve_add(location=(0, 0, 0)); cab = bpy.context.object
sp = cab.data.splines[0]; pts = sp.bezier_points
pts[0].co = (-0.72, 0.5, 0.012); pts[0].handle_left = (-0.6, 0.55, 0.012); pts[0].handle_right = (-0.9, 0.3, 0.012)
pts[1].co = (-1.3, -0.5, 0.012); pts[1].handle_left = (-1.0, -0.2, 0.012); pts[1].handle_right = (-1.6, -0.8, 0.012)
cab.data.bevel_depth = 0.012; cab.data.bevel_resolution = 1; cab.data.materials.append(m_obj)

# --- matita di carta
pen = folded_box("Pen", (0.2, 0.016, 0.016), (0.25, -0.16, 0.008), m_acc, rot=-28)

# --- due fogli sparsi sul piano, fuori fuoco (profondita')
for (x, y, rz) in [(-0.95, 0.55, 0.4), (0.9, 0.7, -0.3)]:
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, 0.001))
    sh = bpy.context.object; sh.scale = (0.21, 0.297, 1); sh.rotation_euler = (0, 0, rz); sh.data.materials.append(m_paper)

# --- luci: sole caldo dal lato (mattino) + riempimento freddo
bpy.ops.object.light_add(type="SUN", location=(2, -2, 3)); sun = bpy.context.object
sun.data.energy = 3.5; sun.data.color = PAL["warm"]; sun.data.angle = math.radians(6)
sun.rotation_euler = (math.radians(58), math.radians(8), math.radians(55))
bpy.ops.object.light_add(type="AREA", location=(-1.5, -1.2, 1.4)); fl = bpy.context.object
fl.data.energy = 80; fl.data.size = 2.5; fl.data.color = PAL["cold"]; fl.rotation_euler = (math.radians(60), 0, math.radians(-50))
bpy.ops.object.light_add(type="AREA", location=(0.2, 1.2, 0.8)); rim = bpy.context.object
rim.data.energy = 40; rim.data.size = 1.0; rim.data.color = PAL["warm"]; rim.rotation_euler = (math.radians(-60), 0, 0)

# --- camera all'altezza del personaggio, teleobiettivo morbido
bpy.ops.object.camera_add(location=(0.22, -1.15, 0.45)); cam = bpy.context.object; sc.camera = cam
cam.data.lens = 50; cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 2.8
bpy.ops.object.empty_add(location=(0.0, 0.05, 0.15)); tgt = bpy.context.object
cam.data.dof.focus_object = tgt
t = cam.constraints.new("TRACK_TO"); t.target = tgt; t.track_axis = "TRACK_NEGATIVE_Z"; t.up_axis = "UP_Y"

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, f"style_{PALETTE}.blend"), copy=True)
print("STYLE FRAME COSTRUITO:", PALETTE)
