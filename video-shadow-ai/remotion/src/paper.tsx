// Elementi comuni del mondo di carta in Three.js (Remotion + @remotion/three).
import React, { useMemo, useState } from "react";
import * as THREE from "three";
import { staticFile, delayRender, continueRender } from "remotion";

export const C = {
  kraft: new THREE.Color("#a8794f"),
  kraftLight: new THREE.Color("#d9b68c"),
  navy: new THREE.Color("#0b1526"),
  navyLight: new THREE.Color("#1d2d4a"),
  cream: new THREE.Color("#f1ebde"),
  copper: new THREE.Color("#b5562a"),
};

// RNG deterministico: ogni render e' identico (niente Math.random)
export const rng = (seed: number) => () => {
  seed = (seed * 16807) % 2147483647;
  return (seed - 1) / 2147483646;
};

const loader = new THREE.TextureLoader();
const cache: Record<string, { t: THREE.Texture; ready: Promise<void> }> = {};
const load = (name: string) => {
  if (!cache[name]) {
    let done!: () => void; const ready = new Promise<void>((r) => (done = r));
    const t = loader.load(staticFile(name), () => done());
    t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4;
    if (name === "fiber.png") { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(2, 2); }
    cache[name] = { t, ready };
  }
  return cache[name];
};
// Precarica le texture PRIMA di montare la scena 3D (ThreeCanvas ridisegna solo al cambio di fotogramma):
// la composizione resta in delayRender finche' tutte le immagini non sono pronte.
export const usePreload = (names: string[]) => {
  const [ready, setReady] = useState(false);
  useState(() => {
    const h = delayRender(`textures ${names.join(",")}`);
    Promise.all(names.map((n) => load(n).ready)).then(() => { setReady(true); continueRender(h); });
    return h;
  });
  return ready;
};
export const useTex = (name: string) => load(name).t;

// Foglio A4 con volto (inchiostro su trasparente) sopra la carta crema
export const Sheet: React.FC<{ face?: string; color?: THREE.Color; curl?: number } & JSX.IntrinsicElements["group"]> = ({ face = "face_open.png", color = C.cream, curl = 0.12, ...g }) => {
  const geo = useMemo(() => {
    const geom = new THREE.PlaneGeometry(0.21, 0.297, 16, 1);
    const p = geom.attributes.position as THREE.BufferAttribute;
    for (let i = 0; i < p.count; i++) { const x = p.getX(i); p.setZ(i, -curl * (x / 0.105) ** 2 * 0.02 * 10); }
    geom.computeVertexNormals();
    return geom;
  }, [curl]);
  const fiber = useTex("fiber.png"); const faceT = useTex(face);
  return (
    <group {...g}>
      <mesh geometry={geo}>
        <meshStandardMaterial color={color} map={fiber} roughness={0.9} side={THREE.DoubleSide} />
      </mesh>
      <mesh geometry={geo} position={[0, 0, 0.0008]}>
        <meshStandardMaterial map={faceT} transparent roughness={0.9} depthWrite={false} side={THREE.FrontSide} />
      </mesh>
    </group>
  );
};
