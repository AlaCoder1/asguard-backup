<template>
  <div class="rpf" ref="wrap" :class="`rpf-${level}`">
    <canvas ref="cv" class="rpf-canvas"></canvas>
    <div class="rpf-core">
      <div class="rpf-ring"></div>
      <div class="rpf-score">{{ Math.round(score) }}</div>
      <div class="rpf-sub">/100 · {{ levelLabel }}</div>
    </div>
    <div class="rpf-tag">Cœur de santé système · live</div>
  </div>
</template>

<script>
export default {
  name: "RiskParticleField",
  props: {
    score: { type: Number, default: 0 },
    level: { type: String, default: "stable" },
  },
  data() {
    return { _raf: null, _ro: null, particles: [], W: 0, H: 0, dpr: 1, sparks: [], t: 0 };
  },
  computed: {
    levelLabel() {
      return { stable: "stable", watch: "à surveiller", high: "élevé", critical: "critique" }[this.level] || "stable";
    },
    accent() {
      return { stable: [34, 197, 94], watch: [245, 158, 11], high: [249, 115, 22], critical: [239, 68, 68] }[this.level] || [34, 197, 94];
    },
  },
  mounted() {
    this.setup();
    this._ro = new ResizeObserver(() => this.resize());
    this._ro.observe(this.$refs.wrap);
    this.loop();
  },
  beforeUnmount() {
    cancelAnimationFrame(this._raf);
    if (this._ro) this._ro.disconnect();
  },
  methods: {
    setup() {
      this.resize();
      const count = 68;
      this.particles = Array.from({ length: count }, () => this.spawn());
    },
    spawn() {
      const cx = this.W / 2, cy = this.H / 2;
      const a = Math.random() * Math.PI * 2;
      const r = 40 + Math.random() * Math.min(this.W, this.H) * 0.45;
      return {
        x: cx + Math.cos(a) * r,
        y: cy + Math.sin(a) * r,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        z: 0.4 + Math.random() * 0.8, // depth → size/parallax (fake 3D)
      };
    },
    resize() {
      const el = this.$refs.wrap;
      if (!el) return;
      this.dpr = Math.min(window.devicePixelRatio || 1, 2);
      this.W = el.clientWidth;
      this.H = el.clientHeight;
      const cv = this.$refs.cv;
      cv.width = this.W * this.dpr;
      cv.height = this.H * this.dpr;
      cv.style.width = this.W + "px";
      cv.style.height = this.H + "px";
    },
    loop() {
      this._raf = requestAnimationFrame(this.loop);
      const ctx = this.$refs.cv?.getContext("2d");
      if (!ctx) return;
      this.t += 0.016;
      const [r, g, b] = this.accent;
      const agit = 0.35 + (this.score / 100) * 1.7; // higher risk = more agitated
      const cx = this.W / 2, cy = this.H / 2;
      const linkDist = 108;

      ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
      ctx.clearRect(0, 0, this.W, this.H);

      // update
      for (const p of this.particles) {
        // gentle pull to center + tangential swirl (orbit)
        const dx = cx - p.x, dy = cy - p.y;
        const dist = Math.hypot(dx, dy) || 1;
        p.vx += (dx / dist) * 0.012 * agit - (dy / dist) * 0.02 * agit;
        p.vy += (dy / dist) * 0.012 * agit + (dx / dist) * 0.02 * agit;
        p.vx += (Math.random() - 0.5) * 0.05 * agit;
        p.vy += (Math.random() - 0.5) * 0.05 * agit;
        p.vx *= 0.94; p.vy *= 0.94;
        p.x += p.vx * agit; p.y += p.vy * agit;
        // keep in bounds (respawn if lost)
        if (p.x < -20 || p.x > this.W + 20 || p.y < -20 || p.y > this.H + 20) Object.assign(p, this.spawn());
      }

      // links (constellation)
      for (let i = 0; i < this.particles.length; i++) {
        for (let j = i + 1; j < this.particles.length; j++) {
          const a = this.particles[i], c = this.particles[j];
          const d = Math.hypot(a.x - c.x, a.y - c.y);
          if (d < linkDist) {
            const o = (1 - d / linkDist) * 0.5;
            ctx.strokeStyle = `rgba(${r},${g},${b},${o})`;
            ctx.lineWidth = 0.7;
            ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(c.x, c.y); ctx.stroke();
          }
        }
      }

      // particles (depth → size + glow)
      for (const p of this.particles) {
        const sz = p.z * 2.4;
        ctx.beginPath();
        ctx.arc(p.x, p.y, sz, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${r},${g},${b},${0.5 + p.z * 0.4})`;
        ctx.shadowColor = `rgba(${r},${g},${b},0.9)`;
        ctx.shadowBlur = 8 * p.z;
        ctx.fill();
      }
      ctx.shadowBlur = 0;

      // central core glow (pulsing with risk)
      const pulse = 1 + Math.sin(this.t * (2 + this.score / 30)) * 0.08;
      const coreR = (46 + (this.score / 100) * 20) * pulse;
      const grad = ctx.createRadialGradient(cx, cy, 4, cx, cy, coreR);
      grad.addColorStop(0, `rgba(${r},${g},${b},0.55)`);
      grad.addColorStop(0.5, `rgba(${r},${g},${b},0.14)`);
      grad.addColorStop(1, `rgba(${r},${g},${b},0)`);
      ctx.fillStyle = grad;
      ctx.beginPath(); ctx.arc(cx, cy, coreR, 0, Math.PI * 2); ctx.fill();
    },
  },
  watch: {
    score() { /* reactive via loop reading this.score */ },
  },
};
</script>

<style scoped>
.rpf { position: relative; width: 100%; height: 300px; border-radius: 14px; overflow: hidden;
  background: radial-gradient(circle at 50% 45%, #0b1020 0%, #070a14 70%, #05060d 100%); }
.rpf-canvas { position: absolute; inset: 0; }
.rpf-core { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center;
  justify-content: center; pointer-events: none; }
.rpf-ring { position: absolute; width: 132px; height: 132px; border-radius: 50%;
  border: 1px solid rgba(255,255,255,.14); box-shadow: inset 0 0 30px rgba(255,255,255,.05);
  animation: rpf-spin 18s linear infinite; }
.rpf-ring::before { content: ""; position: absolute; top: -3px; left: 50%; width: 6px; height: 6px;
  border-radius: 50%; background: #fff; box-shadow: 0 0 10px #fff; transform: translateX(-50%); }
@keyframes rpf-spin { to { transform: rotate(360deg); } }
.rpf-score { font-size: 54px; font-weight: 800; line-height: 1; color: #fff;
  text-shadow: 0 0 24px currentColor; font-variant-numeric: tabular-nums;
  letter-spacing: -2px; }
.rpf-sub { font-size: 12px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;
  margin-top: 6px; color: rgba(255,255,255,.7); }
.rpf-tag { position: absolute; bottom: 12px; left: 14px; font-size: 10.5px; font-weight: 700;
  letter-spacing: .5px; text-transform: uppercase; color: rgba(255,255,255,.45); }
/* level tints the core number glow */
.rpf-stable .rpf-score { color: #4ade80; } .rpf-watch .rpf-score { color: #fbbf24; }
.rpf-high .rpf-score { color: #fb923c; } .rpf-critical .rpf-score { color: #f87171; }
</style>
