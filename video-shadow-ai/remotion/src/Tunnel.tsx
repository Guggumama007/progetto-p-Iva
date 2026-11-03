// Scena 4a - Il viaggio dentro il cavo: anelli di striscioline di carta, dal kraft di casa al blu notte di fuori.
// GSAP: timeline in pausa, seek al tempo del fotogramma (velocita' della camera, capriole del contratto).
import React, { useMemo } from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import gsap from "gsap";
import { C, rng, Sheet, useTex, usePreload } from "./paper";

const RINGS = 46, STRIPS = 11, SPACING = 0.55, R = 1.0;

const Strips: React.FC = () => {
  const fiber = useTex("fiber.png");
  const data = useMemo(() => {
    const r = rng(7); const out: { pos: [number, number, number]; rot: [number, number, number]; col: THREE.Color; w: number }[] = [];
    for (let i = 0; i < RINGS; i++) {
      const z = -i * SPACING; const mixT = Math.min(1, Math.max(0, (i - 12) / 18));
      const base = C.kraft.clone().lerp(new THREE.Color("#34507f"), mixT);
      for (let k = 0; k < STRIPS; k++) {
        const a = (k / STRIPS) * Math.PI * 2 + i * 0.37 + r() * 0.2;
        const rad = R * (0.92 + r() * 0.16);
        const col = base.clone().offsetHSL(0, 0, (r() - 0.5) * 0.12);
        if (r() < 0.08) col.copy(C.copper);
        out.push({ pos: [Math.cos(a) * rad, Math.sin(a) * rad, z + r() * 0.2], rot: [0, 0, a + Math.PI / 2 + (r() - 0.5) * 0.3], col, w: 0.35 + r() * 0.3 });
      }
    }
    return out;
  }, []);
  return (<>{data.map((s, i) => (
    <mesh key={i} position={s.pos} rotation={s.rot}>
      <boxGeometry args={[s.w, 0.06, 0.004]} />
      <meshStandardMaterial color={s.col} map={fiber} roughness={0.95} emissive={s.col} emissiveIntensity={0.32} />
    </mesh>))}</>);
};

const Particles: React.FC<{ t: number }> = ({ t }) => {
  const data = useMemo(() => { const r = rng(11); return Array.from({ length: 160 }, () => ({ x: (r() - 0.5) * 1.4, y: (r() - 0.5) * 1.4, z: -r() * RINGS * SPACING, s: 0.012 + r() * 0.02, sp: 0.5 + r(), copper: r() < 0.5 })); }, []);
  return (<>{data.map((p, i) => (
    <mesh key={i} position={[p.x, p.y, p.z + t * p.sp * 1.5]} rotation={[t * 3 * p.sp, t * 2, 0]}>
      <planeGeometry args={[p.s, p.s]} />
      <meshStandardMaterial color={p.copper ? C.copper : C.cream} emissive={p.copper ? C.copper : C.cream} emissiveIntensity={0.6} side={THREE.DoubleSide} />
    </mesh>))}</>);
};

// la camera va aggiornata a ogni fotogramma (la prop "camera" di ThreeCanvas vale solo all'avvio)
const Cam: React.FC<{ z: number; roll: number }> = ({ z, roll }) => {
  const { camera } = useThree();
  camera.position.set(0, 0, z); camera.rotation.set(0, 0, roll); camera.updateProjectionMatrix();
  return null;
};

export const Tunnel: React.FC = () => {
  const frame = useCurrentFrame(); const { fps, width, height, durationInFrames } = useVideoConfig();
  const D = durationInFrames / fps;
  const st = useMemo(() => ({ z: 1.2, spin: 0, sheetX: 0, sheetY: 0, fogNear: 1.5, bg: 0 }), []);
  const tl = useMemo(() => gsap.timeline({ paused: true })
      .to(st, { z: -(RINGS - 8) * SPACING, duration: D, ease: "power2.in" }, 0)       // risucchiato: accelera
      .to(st, { spin: Math.PI * 5, duration: D, ease: "power1.in" }, 0)
      .to(st, { sheetX: 0.08, sheetY: -0.05, duration: D * 0.5, ease: "sine.inOut", yoyo: true, repeat: 1 }, 0)
      .to(st, { bg: 1, duration: D * 0.45, ease: "sine.inOut" }, D * 0.25), [st, D]);
  tl.seek(frame / fps);
  const ready = usePreload(["fiber.png", "face_worried.png"]);
  if (!ready) return null;
  const fogCol = C.kraft.clone().lerp(C.navy, st.bg);
  return (
    <AbsoluteFill style={{ background: `#${fogCol.getHexString()}` }}>
      <ThreeCanvas width={width} height={height} camera={{ position: [0, 0, st.z], fov: 70, near: 0.01, far: 40 }}>
        <color attach="background" args={[fogCol]} />
        <fog attach="fog" args={[fogCol, 1.2, 11]} />
        <Cam z={st.z} roll={st.spin * 0.08} />
        <hemisphereLight args={[st.bg > 0.5 ? "#9fb6ff" : "#ffe9cf", "#3a2a1c", 1.6]} />
        <pointLight position={[0, 0, st.z - 0.4]} intensity={2.2} decay={0} distance={5} color="#ffd9b0" />
        <pointLight position={[0, 0, st.z - 5]} intensity={3} decay={0} distance={9} color={st.bg > 0.5 ? "#6f8fff" : "#ffb070"} />
        <Strips />
        <Particles t={frame / fps} />
        <Sheet face="face_worried.png" position={[st.sheetX, st.sheetY, st.z - 0.75]} rotation={[0.3 * Math.sin(st.spin * 0.5), 0.4 * Math.sin(st.spin * 0.3), st.spin]} scale={1.1} />
      </ThreeCanvas>
    </AbsoluteFill>
  );
};
