import React from "react";
import { Composition } from "remotion";
import { Tunnel } from "./Tunnel";
import { Copie } from "./Copie";
import tl from "../public/timeline.json";
const rischio = tl.scenes.find((s) => s.id === "rischio")!;
export const Root: React.FC = () => (
  <>
    <Composition id="Tunnel" component={Tunnel} durationInFrames={96} fps={30} width={1920} height={1080} />
    <Composition id="Copie" component={Copie} durationInFrames={Math.round((rischio.end - rischio.start) * 30)} fps={30} width={1920} height={1080} />
  </>
);
