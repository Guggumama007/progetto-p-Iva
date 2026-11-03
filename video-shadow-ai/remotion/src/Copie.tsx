// Scena 6 - Il rischio è doppio: il contratto viene fotocopiato (1→2→4→…→120) con un lampo,
// poi le copie esplodono e fluttuano intorno; su "Firmate da te, eh." le firme si accendono di rame.
// Tempi presi da timeline.json (battute della voce); animazione con una timeline GSAP in pausa.
import React, { useMemo } from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import gsap from "gsap";
import tl from "../public/timeline.json";
import { C, rng, Sheet, usePreload } from "./paper";

const S = tl.scenes.find((s) => s.id === "rischio")!;
const L = tl.lines.filter((l) => l.scene === "rischio").map((l) => ({ a: l.start - S.start, b: l.end - S.start }));
const N = 120;

const Cam: React.FC<{ z: number; y: number }> = ({ z, y }) => {
  const { camera } = useThree(); camera.position.set(0, y, z); camera.lookAt(0, y * 0.6, 0); return null;
};

type Copy = { x: number; y: number; z: number; rx: number; ry: number; rz: number; s: number; flash: number };

export const Copie: React.FC = () => {
  const frame = useCurrentFrame(); const { fps, width, height, durationInFrames } = useVideoConfig();
  const D = durationInFrames / fps;
  const { st, copies, tline } = useMemo(() => {
    const r = rng(23);
    const st = { camZ: 1.15, camY: 0.0, mainS: 1.4, sig: 0, shake: 0 };
    const copies: Copy[] = Array.from({ length: N }, () => ({ x: 0, y: 0, z: -0.01, rx: 0, ry: 0, rz: 0, s: 0.001, flash: 0 }));
    const t = gsap.timeline({ paused: true });
    // fotocopie a raddoppio: 1,2,4,8,16,32,64,120 — ogni ondata con un lampo
    const t0 = L[0].a + 0.25; const waves = [1, 2, 4, 8, 16, 32, 64, N];
    let made = 0;
    waves.forEach((count, w) => {
      const tw = t0 + w * 0.22;
      for (let i = made; i < count; i++) {
        const ang = i * 2.399; const rad = 0.18 + Math.sqrt(i) * 0.085;          // spirale di Fermat dietro al foglio
        t.fromTo(copies[i], { s: 0.001, flash: 1.6 }, { x: Math.cos(ang) * rad * 1.6, y: Math.sin(ang) * rad, z: -0.05 - i * 0.002, s: 0.9, rz: (r() - 0.5) * 0.3, flash: 0, duration: 0.35, ease: "back.out(1.6)" }, tw);
      }
      made = count;
    });
    // esplosione: le copie volano via e fluttuano (alcune passano davanti alla camera)
    const tb = t0 + waves.length * 0.22 + 0.15;
    copies.forEach((c, i) => {
      const th = r() * Math.PI * 2, ph = (r() - 0.5) * 1.6, rad = 0.9 + r() * 2.2;
      const front = r() < 0.12;
      t.to(c, { x: Math.cos(th) * rad * 1.3, y: Math.sin(ph) * rad * 0.7, z: front ? 0.6 + r() * 1.2 : -0.6 - r() * 3.5,
                rx: (r() - 0.5) * 6, ry: (r() - 0.5) * 6, rz: (r() - 0.5) * 6, s: 1.0, duration: 1.1 + r() * 0.6, ease: "power3.out" }, tb + r() * 0.15);
      t.to(c, { y: `-=${0.3 + r() * 0.6}`, rx: `+=${(r() - 0.5) * 3}`, ry: `+=${(r() - 0.5) * 3}`, duration: D - tb - 1.2, ease: "none" }, tb + 1.3);
    });
    t.to(st, { shake: 1, duration: 0.12, yoyo: true, repeat: 3 }, tb);
    t.to(st, { camZ: 1.9, camY: 0.05, mainS: 1.15, duration: 1.4, ease: "power2.inOut" }, tb + 0.2);     // spazio per le due colonne
    t.to(st, { camZ: 1.0, camY: -0.02, duration: 0.9, ease: "power2.inOut" }, L[3].a - 0.4);            // "Firmate da te, eh."
    t.to(st, { sig: 1, duration: 0.25, ease: "power1.out" }, L[3].a + 0.1);
    return { st, copies, tline: t };
  }, [D]);
  tline.seek(frame / fps);
  const ready = usePreload(["fiber.png", "face_worried.png", "face_copy.png", "face_deadpan.png"]);
  if (!ready) return null;
  const deadpan = frame / fps > L[3].a;
  const shakeX = Math.sin(frame * 2.1) * 0.01 * st.shake;
  return (
    <AbsoluteFill style={{ background: "#0b1526" }}>
      <ThreeCanvas width={width} height={height} camera={{ position: [0, 0, 1.15], fov: 45, near: 0.01, far: 30 }}>
        <Cam z={st.camZ} y={st.camY} />
        <color attach="background" args={[C.navy]} />
        <fog attach="fog" args={[C.navy, 1.5, 6.5]} />
        <hemisphereLight args={["#a8bfff", "#1a1208", 1.25]} />
        <pointLight position={[1.2, 1.0, 1.5]} intensity={2.4} decay={0} color="#ffc89a" />
        <pointLight position={[-1.5, -0.4, 0.8]} intensity={0.8} decay={0} color="#6f8fff" />
        {copies.map((c, i) => (
          <group key={i} position={[c.x, c.y, c.z]} rotation={[c.rx, c.ry, c.rz]} scale={c.s}>
            <Sheet face="face_copy.png" color={new THREE.Color("#e8dfcf")} />
            {c.flash > 0.01 && <mesh position={[0, 0, 0.002]}><planeGeometry args={[0.21, 0.297]} /><meshBasicMaterial color="#ffffff" transparent opacity={Math.min(1, c.flash)} /></mesh>}
            {st.sig > 0 && <mesh position={[0.045, -0.105, 0.0015]}><planeGeometry args={[0.07, 0.02]} /><meshBasicMaterial color={C.copper} transparent opacity={0.9 * st.sig} /></mesh>}
          </group>
        ))}
        <Sheet face={deadpan ? "face_deadpan.png" : "face_worried.png"} position={[shakeX, -0.02, 0.05]} scale={st.mainS} />
      </ThreeCanvas>
    </AbsoluteFill>
  );
};
