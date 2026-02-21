"use client";

import { useEffect, useRef } from "react";
import lottie, { type AnimationItem } from "lottie-web";

/* ═══════════════════════════════════════════════════════════════════
   Custom Lottie Animations — hand-crafted JSON for micro-moments
   Origami bird seal, lock icon, loading pulse
   ═══════════════════════════════════════════════════════════════════ */

// Origami bird — draws itself from a single point
const ORIGAMI_BIRD_DATA = {
  v: "5.7.0",
  fr: 30,
  ip: 0,
  op: 60,
  w: 120,
  h: 120,
  assets: [],
  layers: [
    {
      ty: 4,
      nm: "bird",
      ip: 0,
      op: 60,
      st: 0,
      ks: {
        o: { a: 0, k: 100 },
        r: { a: 0, k: 0 },
        p: { a: 0, k: [60, 60, 0] },
        a: { a: 0, k: [0, 0, 0] },
        s: { a: 0, k: [100, 100, 100] },
      },
      shapes: [
        {
          ty: "gr",
          it: [
            {
              ty: "sh",
              ks: {
                a: 0,
                k: {
                  c: true,
                  v: [[0, -30], [-35, 20], [0, 10], [35, 20]],
                  i: [[0, 0], [0, 0], [0, 0], [0, 0]],
                  o: [[0, 0], [0, 0], [0, 0], [0, 0]],
                },
              },
            },
            {
              ty: "st",
              c: { a: 0, k: [0.165, 0.145, 0.161, 1] },
              o: { a: 0, k: 100 },
              w: { a: 0, k: 2 },
              lc: 2,
              lj: 2,
            },
            {
              ty: "tm",
              s: { a: 0, k: 0 },
              e: {
                a: 1,
                k: [
                  { t: 0, s: [0], i: { x: [0.4], y: [1] }, o: { x: [0.6], y: [0] } },
                  { t: 40, s: [100] },
                ],
              },
              o: { a: 0, k: 0 },
            },
            { ty: "tr", p: { a: 0, k: [0, 0] }, a: { a: 0, k: [0, 0] }, s: { a: 0, k: [100, 100] }, r: { a: 0, k: 0 }, o: { a: 0, k: 100 } },
          ],
        },
        {
          ty: "gr",
          it: [
            {
              ty: "sh",
              ks: {
                a: 0,
                k: {
                  c: false,
                  v: [[0, -30], [0, 10]],
                  i: [[0, 0], [0, 0]],
                  o: [[0, 0], [0, 0]],
                },
              },
            },
            {
              ty: "st",
              c: { a: 0, k: [0.165, 0.145, 0.161, 1] },
              o: { a: 0, k: 100 },
              w: { a: 0, k: 1.5 },
              lc: 2,
              lj: 2,
            },
            {
              ty: "tm",
              s: { a: 0, k: 0 },
              e: {
                a: 1,
                k: [
                  { t: 20, s: [0], i: { x: [0.4], y: [1] }, o: { x: [0.6], y: [0] } },
                  { t: 45, s: [100] },
                ],
              },
              o: { a: 0, k: 0 },
            },
            { ty: "tr", p: { a: 0, k: [0, 0] }, a: { a: 0, k: [0, 0] }, s: { a: 0, k: [100, 100] }, r: { a: 0, k: 0 }, o: { a: 0, k: 100 } },
          ],
        },
      ],
    },
  ],
};

// Lock icon — click to lock animation
const LOCK_ICON_DATA = {
  v: "5.7.0",
  fr: 30,
  ip: 0,
  op: 45,
  w: 48,
  h: 48,
  assets: [],
  layers: [
    {
      ty: 4,
      nm: "lock",
      ip: 0,
      op: 45,
      st: 0,
      ks: {
        o: { a: 0, k: 100 },
        r: { a: 0, k: 0 },
        p: { a: 0, k: [24, 24, 0] },
        a: { a: 0, k: [0, 0, 0] },
        s: {
          a: 1,
          k: [
            { t: 0, s: [100, 100, 100], i: { x: [0.4], y: [1] }, o: { x: [0.6], y: [0] } },
            { t: 10, s: [110, 110, 100], i: { x: [0.4], y: [1] }, o: { x: [0.6], y: [0] } },
            { t: 20, s: [100, 100, 100] },
          ],
        },
      },
      shapes: [
        {
          ty: "gr",
          it: [
            {
              ty: "rc",
              d: 1,
              s: { a: 0, k: [20, 16] },
              p: { a: 0, k: [0, 4] },
              r: { a: 0, k: 3 },
            },
            {
              ty: "st",
              c: { a: 0, k: [0.165, 0.145, 0.161, 1] },
              o: { a: 0, k: 100 },
              w: { a: 0, k: 2 },
              lc: 2,
              lj: 2,
            },
            { ty: "tr", p: { a: 0, k: [0, 0] }, a: { a: 0, k: [0, 0] }, s: { a: 0, k: [100, 100] }, r: { a: 0, k: 0 }, o: { a: 0, k: 100 } },
          ],
        },
        {
          ty: "gr",
          it: [
            {
              ty: "sh",
              ks: {
                a: 0,
                k: {
                  c: false,
                  v: [[-6, -4], [-6, -10], [6, -10], [6, -4]],
                  i: [[0, 0], [0, -4], [0, 0], [0, 0]],
                  o: [[0, 0], [0, 0], [0, 4], [0, 0]],
                },
              },
            },
            {
              ty: "st",
              c: { a: 0, k: [0.165, 0.145, 0.161, 1] },
              o: { a: 0, k: 100 },
              w: { a: 0, k: 2 },
              lc: 2,
              lj: 2,
            },
            {
              ty: "tm",
              s: { a: 0, k: 0 },
              e: {
                a: 1,
                k: [
                  { t: 0, s: [0], i: { x: [0.4], y: [1] }, o: { x: [0.6], y: [0] } },
                  { t: 25, s: [100] },
                ],
              },
              o: { a: 0, k: 0 },
            },
            { ty: "tr", p: { a: 0, k: [0, 0] }, a: { a: 0, k: [0, 0] }, s: { a: 0, k: [100, 100] }, r: { a: 0, k: 0 }, o: { a: 0, k: 100 } },
          ],
        },
      ],
    },
  ],
};

interface LottiePlayerProps {
  animationData: object;
  width?: number;
  height?: number;
  loop?: boolean;
  autoplay?: boolean;
  className?: string;
  onComplete?: () => void;
}

export function LottiePlayer({
  animationData,
  width = 48,
  height = 48,
  loop = false,
  autoplay = true,
  className = "",
  onComplete,
}: LottiePlayerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const animRef = useRef<AnimationItem | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    animRef.current = lottie.loadAnimation({
      container: containerRef.current,
      renderer: "svg",
      loop,
      autoplay,
      animationData,
    });

    if (onComplete) {
      animRef.current.addEventListener("complete", onComplete);
    }

    return () => {
      animRef.current?.destroy();
    };
  }, [animationData, loop, autoplay, onComplete]);

  return (
    <div
      ref={containerRef}
      className={className}
      style={{ width, height }}
    />
  );
}

// Pre-built animation exports
export function OrigamiBirdLottie({
  size = 80,
  loop = false,
  autoplay = true,
  className = "",
}: {
  size?: number;
  loop?: boolean;
  autoplay?: boolean;
  className?: string;
}) {
  return (
    <LottiePlayer
      animationData={ORIGAMI_BIRD_DATA}
      width={size}
      height={size}
      loop={loop}
      autoplay={autoplay}
      className={className}
    />
  );
}

export function LockLottie({
  size = 24,
  loop = false,
  autoplay = true,
  className = "",
}: {
  size?: number;
  loop?: boolean;
  autoplay?: boolean;
  className?: string;
}) {
  return (
    <LottiePlayer
      animationData={LOCK_ICON_DATA}
      width={size}
      height={size}
      loop={loop}
      autoplay={autoplay}
      className={className}
    />
  );
}
