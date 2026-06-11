"use client";

import { useEffect, useRef } from "react";

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  r: number;
  color: string;
  alpha: number;
}

// Colour palette — matches CSS tokens
const COLOURS = [
  "61,124,246",   // blue  (most common)
  "61,124,246",   // blue
  "61,124,246",   // blue
  "168,216,255",  // sky
  "168,216,255",  // sky
  "194,255,77",   // lime  (rare)
  "255,255,255",  // white (rare)
];

const CONNECTION_DISTANCE = 130;

export default function AnimatedBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let rafId: number;
    let particles: Particle[] = [];

    function resize() {
      canvas!.width  = window.innerWidth;
      canvas!.height = window.innerHeight;
    }

    function spawnParticles() {
      const count = Math.max(40, Math.floor((canvas!.width * canvas!.height) / 16000));
      particles = Array.from({ length: count }, () => ({
        x:     Math.random() * canvas!.width,
        y:     Math.random() * canvas!.height,
        vx:    (Math.random() - 0.5) * 0.28,
        vy:    (Math.random() - 0.5) * 0.28,
        r:     Math.random() * 1.4 + 0.4,
        color: COLOURS[Math.floor(Math.random() * COLOURS.length)],
        alpha: Math.random() * 0.35 + 0.08,
      }));
    }

    function tick() {
      ctx!.clearRect(0, 0, canvas!.width, canvas!.height);

      // Draw connection lines
      for (let i = 0; i < particles.length; i++) {
        const pi = particles[i];
        for (let j = i + 1; j < particles.length; j++) {
          const pj = particles[j];
          const dx = pi.x - pj.x;
          const dy = pi.y - pj.y;
          const dist = Math.hypot(dx, dy);
          if (dist < CONNECTION_DISTANCE) {
            const t = 1 - dist / CONNECTION_DISTANCE;
            ctx!.beginPath();
            ctx!.strokeStyle = `rgba(61,124,246,${t * 0.12})`;
            ctx!.lineWidth   = 0.6;
            ctx!.moveTo(pi.x, pi.y);
            ctx!.lineTo(pj.x, pj.y);
            ctx!.stroke();
          }
        }
      }

      // Draw + move particles
      for (const p of particles) {
        ctx!.beginPath();
        ctx!.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx!.fillStyle = `rgba(${p.color},${p.alpha})`;
        ctx!.fill();

        p.x += p.vx;
        p.y += p.vy;

        // Wrap edges
        if (p.x < -10)                 p.x = canvas!.width  + 10;
        if (p.x > canvas!.width  + 10) p.x = -10;
        if (p.y < -10)                 p.y = canvas!.height + 10;
        if (p.y > canvas!.height + 10) p.y = -10;
      }

      rafId = requestAnimationFrame(tick);
    }

    function handleResize() {
      resize();
      spawnParticles();
    }

    resize();
    spawnParticles();
    tick();

    window.addEventListener("resize", handleResize, { passive: true });
    return () => {
      cancelAnimationFrame(rafId);
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      style={{
        position:      "fixed",
        inset:         0,
        zIndex:        0,
        pointerEvents: "none",
      }}
    />
  );
}
