<template>
  <div class="aia">
    <!-- Floating launcher -->
    <button class="aia-fab" :class="{ open }" type="button" @click="toggle"
            :aria-label="open ? 'Fermer' : 'Ouvrir l\'assistant'">
      <span class="aia-fab-ring"></span>
      <span class="aia-fab-ring aia-fab-ring2"></span>
      <transition name="aia-swap" mode="out-in">
        <svg v-if="!open" key="bot" class="aia-fab-svg" viewBox="0 0 24 24" fill="none">
          <path d="M12 2l7 3v6c0 4.5-3 8-7 9-4-1-7-4.5-7-9V5z" fill="url(#g1)"/>
          <circle cx="9" cy="11" r="1.3" fill="#fff"/><circle cx="15" cy="11" r="1.3" fill="#fff"/>
          <path d="M9 15c1 .8 5 .8 6 0" stroke="#fff" stroke-width="1.4" stroke-linecap="round"/>
          <defs><linearGradient id="g1" x1="5" y1="2" x2="19" y2="20">
            <stop stop-color="#a78bfa"/><stop offset="1" stop-color="#6366f1"/></linearGradient></defs>
        </svg>
        <span v-else key="x" class="aia-fab-x">✕</span>
      </transition>
      <span v-if="!open" class="aia-fab-dot"></span>
    </button>

    <!-- Chat panel -->
    <transition name="aia-pop">
      <div v-if="open" class="aia-panel">
        <div class="aia-glow"></div>
        <header class="aia-head">
          <div class="aia-orb"><span class="aia-orb-core">🛡️</span></div>
          <div class="aia-head-txt">
            <strong>Assistant Asguard <span class="aia-ai">IA</span></strong>
            <span class="aia-status"><i class="aia-live"></i> En ligne · backup, DR, firewall</span>
          </div>
        </header>

        <div class="aia-body" ref="body">
          <transition-group name="aia-msg" tag="div">
            <div v-for="(m, i) in messages" :key="i" class="aia-row" :class="m.role">
              <div v-if="m.role === 'bot'" class="aia-mini">🛡️</div>
              <div class="aia-bubble" v-html="render(m.text)"></div>
            </div>
          </transition-group>
          <div v-if="loading" class="aia-row bot">
            <div class="aia-mini">🛡️</div>
            <div class="aia-bubble aia-typing"><span></span><span></span><span></span></div>
          </div>
        </div>

        <div class="aia-chips" v-if="messages.length <= 1">
          <button v-for="s in suggestions" :key="s" class="aia-chip" type="button" @click="send(s)">{{ s }}</button>
        </div>

        <form class="aia-input" @submit.prevent="send()">
          <input v-model="draft" type="text" placeholder="Pose ta question…" :disabled="loading" />
          <button type="submit" :disabled="loading || !draft.trim()" aria-label="Envoyer">
            <svg viewBox="0 0 24 24" width="17" height="17" fill="none"><path d="M4 12l16-8-6 8 6 8z" fill="#fff"/></svg>
          </button>
        </form>
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  name: "AsguardAssistant",
  data() {
    return {
      open: false,
      draft: "",
      loading: false,
      messages: [
        { role: "bot", text: "Bonjour 👋 Je suis l'assistant **Asguard**. Je conseille tes backups, j'évalue ta **préparation au sinistre (DR)**, j'explique les **risques d'une restauration** et le firewall — le tout **hors-ligne**. Pose ta question ou choisis ci-dessous." },
      ],
      suggestions: [
        "Suis-je prêt pour un sinistre ?",
        "Risques si je restaure la database ?",
        "Quel backup pour le firewall ?",
        "Comment bloquer un port ?",
      ],
    };
  },
  methods: {
    toggle() { this.open = !this.open; if (this.open) this.scroll(); },
    async send(preset) {
      const text = (preset || this.draft).trim();
      if (!text || this.loading) return;
      this.messages.push({ role: "user", text });
      this.draft = "";
      this.loading = true;
      this.scroll();
      const botIdx = this.messages.push({ role: "bot", text: "" }) - 1;
      try {
        const resp = await fetch("/backup/assistant/stream", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text }),
        });
        if (!resp.ok || !resp.body) throw new Error("no stream");
        const reader = resp.body.getReader();
        const dec = new TextDecoder();
        this.loading = false;
        for (;;) {
          const { done, value } = await reader.read();
          if (done) break;
          this.messages[botIdx].text += dec.decode(value, { stream: true });
          this.scroll();
        }
        if (!this.messages[botIdx].text) this.messages[botIdx].text = "Je n'ai pas de réponse pour ça.";
      } catch (e) {
        this.messages[botIdx].text = "⚠️ Impossible de joindre l'assistant. Réessaie.";
      } finally {
        this.loading = false;
        this.scroll();
      }
    },
    render(text) {
      const esc = String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
      return esc
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/`([^`]+)`/g, "<code>$1</code>")
        .replace(/^\s*→ (.*)$/gm, '<span class="aia-reco">↳ $1</span>')
        .replace(/^\s*[-•] (.*)$/gm, '<span class="aia-li">• $1</span>')
        .replace(/\n/g, "<br>");
    },
    scroll() { this.$nextTick(() => { const b = this.$refs.body; if (b) b.scrollTop = b.scrollHeight; }); },
  },
};
</script>

<style scoped>
.aia { position: fixed; right: 24px; bottom: 24px; z-index: 4000; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }

/* ── Launcher ─────────────────────────────────────── */
.aia-fab { position: relative; width: 60px; height: 60px; border-radius: 50%; border: none; cursor: pointer;
  background: radial-gradient(circle at 30% 25%, #8b5cf6, #4f46e5 70%); color: #fff;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 10px 30px rgba(79,70,229,.45), inset 0 1px 2px rgba(255,255,255,.4);
  transition: transform .2s cubic-bezier(.34,1.56,.64,1); animation: aia-float 4s ease-in-out infinite; }
.aia-fab:hover { transform: scale(1.08) translateY(-2px); }
.aia-fab.open { background: radial-gradient(circle at 30% 25%, #7c3aed, #5b21b6 70%); animation: none; }
.aia-fab-svg { width: 30px; height: 30px; filter: drop-shadow(0 1px 2px rgba(0,0,0,.25)); }
.aia-fab-x { font-size: 20px; font-weight: 300; }
.aia-fab-ring { position: absolute; inset: 0; border-radius: 50%; border: 2px solid rgba(139,92,246,.5); animation: aia-pulse 2.4s ease-out infinite; }
.aia-fab-ring2 { animation-delay: 1.2s; }
.aia-fab.open .aia-fab-ring { display: none; }
.aia-fab-dot { position: absolute; top: 6px; right: 6px; width: 12px; height: 12px; border-radius: 50%;
  background: #34d399; border: 2px solid #fff; box-shadow: 0 0 8px #34d399; }
@keyframes aia-float { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
@keyframes aia-pulse { 0% { transform: scale(1); opacity: .7; } 100% { transform: scale(1.8); opacity: 0; } }
.aia-swap-enter-active, .aia-swap-leave-active { transition: transform .2s, opacity .2s; }
.aia-swap-enter-from, .aia-swap-leave-to { opacity: 0; transform: rotate(-90deg) scale(.5); }

/* ── Panel ────────────────────────────────────────── */
.aia-panel { position: absolute; right: 0; bottom: 76px; width: 384px; max-width: calc(100vw - 48px);
  height: 588px; max-height: calc(100vh - 140px); display: flex; flex-direction: column; overflow: hidden;
  border-radius: 22px; background: rgba(255,255,255,.86); backdrop-filter: blur(18px) saturate(1.4);
  border: 1px solid rgba(255,255,255,.6);
  box-shadow: 0 24px 60px rgba(49,46,129,.32), 0 2px 8px rgba(49,46,129,.14); }
.aia-glow { position: absolute; top: -60px; left: -40px; width: 220px; height: 220px; pointer-events: none;
  background: radial-gradient(circle, rgba(139,92,246,.45), transparent 65%); filter: blur(10px);
  animation: aia-drift 9s ease-in-out infinite; }
@keyframes aia-drift { 0%,100% { transform: translate(0,0); } 50% { transform: translate(60px,30px); } }
.aia-pop-enter-active { transition: opacity .22s, transform .22s cubic-bezier(.34,1.56,.64,1); }
.aia-pop-leave-active { transition: opacity .16s, transform .16s ease; }
.aia-pop-enter-from, .aia-pop-leave-to { opacity: 0; transform: translateY(16px) scale(.96); }

/* Header */
.aia-head { position: relative; display: flex; align-items: center; gap: 13px; padding: 16px 18px; color: #fff;
  background: linear-gradient(120deg, #6d28d9, #4f46e5 55%, #7c3aed); overflow: hidden; }
.aia-head::after { content: ""; position: absolute; inset: 0;
  background: linear-gradient(120deg, transparent 30%, rgba(255,255,255,.22) 50%, transparent 70%);
  background-size: 220% 100%; animation: aia-shine 5s linear infinite; }
@keyframes aia-shine { 0% { background-position: 120% 0; } 100% { background-position: -120% 0; } }
.aia-orb { position: relative; width: 42px; height: 42px; border-radius: 13px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; font-size: 21px;
  background: rgba(255,255,255,.18); border: 1px solid rgba(255,255,255,.35);
  box-shadow: 0 0 20px rgba(167,139,250,.6); animation: aia-breathe 3s ease-in-out infinite; }
@keyframes aia-breathe { 0%,100% { box-shadow: 0 0 16px rgba(167,139,250,.5); } 50% { box-shadow: 0 0 28px rgba(167,139,250,.9); } }
.aia-head-txt { position: relative; z-index: 1; }
.aia-head strong { display: block; font-size: 14.5px; letter-spacing: .2px; }
.aia-ai { font-size: 9px; font-weight: 800; letter-spacing: 1px; background: rgba(255,255,255,.25);
  padding: 1px 6px; border-radius: 6px; vertical-align: middle; margin-left: 4px; }
.aia-status { font-size: 11px; opacity: .92; display: flex; align-items: center; gap: 6px; margin-top: 2px; }
.aia-live { width: 7px; height: 7px; border-radius: 50%; background: #34d399; box-shadow: 0 0 8px #34d399; animation: aia-blink 1.6s infinite; }
@keyframes aia-blink { 0%,100% { opacity: 1; } 50% { opacity: .35; } }

/* Body */
.aia-body { flex: 1; overflow-y: auto; padding: 18px 16px; display: flex; flex-direction: column; gap: 13px;
  background: linear-gradient(180deg, rgba(245,243,255,.5), rgba(255,255,255,.2)); }
.aia-body::-webkit-scrollbar { width: 6px; }
.aia-body::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
.aia-row { display: flex; align-items: flex-end; gap: 8px; }
.aia-row.user { justify-content: flex-end; }
.aia-mini { width: 26px; height: 26px; border-radius: 9px; flex-shrink: 0; display: flex; align-items: center;
  justify-content: center; font-size: 14px; background: linear-gradient(135deg,#ede9fe,#ddd6fe); border: 1px solid #ddd6fe; }
.aia-bubble { max-width: 80%; padding: 11px 14px; border-radius: 16px; font-size: 13px; line-height: 1.55; word-break: break-word;
  box-shadow: 0 2px 10px rgba(49,46,129,.08); }
.aia-row.bot .aia-bubble { background: #fff; border: 1px solid #eceafe; color: #1f2233; border-bottom-left-radius: 5px; }
.aia-row.user .aia-bubble { background: linear-gradient(135deg,#6366f1,#7c3aed); color: #fff; border-bottom-right-radius: 5px;
  box-shadow: 0 4px 14px rgba(99,102,241,.4); }
.aia-bubble :deep(strong) { font-weight: 700; }
.aia-bubble :deep(code) { background: #f1f0fb; color: #6d28d9; padding: 1px 5px; border-radius: 5px; font-size: 12px; }
.aia-bubble :deep(.aia-li) { display: block; padding-left: 2px; }
.aia-bubble :deep(.aia-reco) { display: block; color: #7c3aed; font-size: 12px; padding-left: 8px; margin-top: 1px; }
.aia-msg-enter-active { transition: opacity .3s, transform .3s cubic-bezier(.34,1.56,.64,1); }
.aia-msg-enter-from { opacity: 0; transform: translateY(10px) scale(.96); }
.aia-typing { display: flex; gap: 5px; padding: 13px 15px; }
.aia-typing span { width: 7px; height: 7px; border-radius: 50%; background: linear-gradient(135deg,#a78bfa,#6366f1); animation: aia-bounce 1s infinite; }
.aia-typing span:nth-child(2) { animation-delay: .15s; } .aia-typing span:nth-child(3) { animation-delay: .3s; }
@keyframes aia-bounce { 0%,60%,100% { opacity: .35; transform: translateY(0) scale(.9); } 30% { opacity: 1; transform: translateY(-4px) scale(1); } }

/* Chips */
.aia-chips { display: flex; flex-wrap: wrap; gap: 7px; padding: 0 16px 12px; }
.aia-chip { font-size: 12px; color: #5b21b6; background: rgba(237,233,254,.8); border: 1px solid #ddd6fe;
  padding: 7px 12px; border-radius: 999px; cursor: pointer; transition: all .15s; }
.aia-chip:hover { background: #ddd6fe; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(124,58,237,.2); }

/* Input */
.aia-input { display: flex; gap: 9px; padding: 12px 14px; border-top: 1px solid rgba(226,232,240,.7); background: rgba(255,255,255,.7); }
.aia-input input { flex: 1; border: 1px solid #e2e0f5; border-radius: 13px; padding: 11px 14px; font-size: 13px; outline: none;
  background: #fff; transition: box-shadow .15s, border-color .15s; }
.aia-input input:focus { border-color: #a78bfa; box-shadow: 0 0 0 4px rgba(167,139,250,.18); }
.aia-input button { width: 44px; border: none; border-radius: 13px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg,#6366f1,#7c3aed); box-shadow: 0 4px 14px rgba(99,102,241,.4); transition: transform .12s; }
.aia-input button:hover:not(:disabled) { transform: scale(1.06); }
.aia-input button:disabled { opacity: .45; cursor: not-allowed; }
</style>
