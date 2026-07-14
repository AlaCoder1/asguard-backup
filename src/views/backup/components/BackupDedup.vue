<template>
  <div class="bd-root">
    <!-- Floating action button -->
    <button class="bd-fab" :class="{ 'bd-fab-open': open, 'bd-fab-pulse': hasDuplicates }"
            @click="toggle" title="Optimisation du stockage">
      <transition name="bd-swap" mode="out-in">
        <svg v-if="!open" key="broom" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19.4 4.6a2 2 0 0 0-2.8 0l-6 6"/><path d="M13 7l4 4"/>
          <path d="M11 10.5 4.5 17a2.1 2.1 0 0 0 0 3 2.1 2.1 0 0 0 3 0L14 13.5"/>
          <path d="M6 20c-1.5 0-2.5-1-3-2"/><path d="M9 22c-1 0-2-.5-2.7-1.3"/>
        </svg>
        <svg v-else key="close" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round">
          <path d="M6 6l12 12M18 6L6 18"/>
        </svg>
      </transition>
      <span v-if="hasDuplicates && !open" class="bd-fab-badge">{{ analysis.redundant_backups }}</span>
    </button>

    <!-- Backdrop flouté : clic en dehors = fermeture -->
    <transition name="bd-fade">
      <div v-if="open" class="bd-backdrop" @click="close"></div>
    </transition>

    <!-- Panel -->
    <transition name="bd-pop">
      <div v-if="open" class="bd-panel">
        <!-- Header -->
        <div class="bd-head">
          <div class="bd-head-ico">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7c0-1.7 3.6-3 8-3s8 1.3 8 3-3.6 3-8 3-8-1.3-8-3z"/><path d="M4 7v10c0 1.7 3.6 3 8 3s8-1.3 8-3V7"/><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/></svg>
          </div>
          <div class="bd-head-txt">
            <div class="bd-head-title">Optimisation du stockage</div>
            <div class="bd-head-sub">Détection intelligente des doublons</div>
          </div>
          <button class="bd-refresh" :disabled="loading" @click="resetAll" title="Réinitialiser">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :class="{ 'bd-spin': loading }"><path d="M21 12a9 9 0 1 1-2.6-6.4"/><path d="M21 3v6h-6"/></svg>
          </button>
        </div>

        <div class="bd-body">
          <!-- Loading -->
          <div v-if="loading && !analysis.groups.length" class="bd-loading">Analyse du contenu…</div>

          <!-- Summary -->
          <div class="bd-summary">
            <div class="bd-stat">
              <div class="bd-stat-val">{{ analysis.duplicate_groups }}</div>
              <div class="bd-stat-lbl">groupes</div>
            </div>
            <div class="bd-stat">
              <div class="bd-stat-val">{{ analysis.redundant_backups }}</div>
              <div class="bd-stat-lbl">redondants</div>
            </div>
            <div class="bd-stat bd-stat-accent">
              <div class="bd-stat-val">{{ analysis.reclaimable_mb }}<small>MB</small></div>
              <div class="bd-stat-lbl">récupérables</div>
            </div>
          </div>

          <button v-if="hasDuplicates" class="bd-clean-all" :disabled="cleaning" @click="confirmCleanup(null)">
            🧹 Tout nettoyer ({{ analysis.reclaimable_mb }} MB)
          </button>

          <!-- Empty -->
          <div v-if="!loading && !hasDuplicates" class="bd-empty">
            <div class="bd-empty-ico">✓</div>
            <div class="bd-empty-t">Stockage optimal</div>
            <div class="bd-empty-s">Aucune sauvegarde en double.</div>
          </div>

          <!-- Groups -->
          <div v-for="g in analysis.groups" :key="g.fingerprint" class="bd-group">
            <div class="bd-group-top">
              <span :class="['bd-type', 'bd-type-' + g.backup_type]">{{ typeLabel(g.backup_type) }}</span>
              <span class="bd-group-txt">{{ g.count }} copies identiques</span>
              <span class="bd-group-mb">{{ g.reclaimable_mb }} MB</span>
            </div>
            <div v-for="m in g.members" :key="m.id" class="bd-item" :class="{ 'bd-item-keep': m.keep }">
              <span class="bd-item-dot" :class="m.keep ? 'bd-dot-keep' : 'bd-dot-del'"></span>
              <span class="bd-item-id">{{ shortId(m.id) }}</span>
              <span class="bd-item-date">{{ formatDate(m.modified_at) }}</span>
              <span class="bd-item-tag" :class="m.keep ? 'bd-tag-keep' : 'bd-tag-del'">
                {{ m.keep ? 'gardée' : 'redond.' }}
              </span>
            </div>
            <button class="bd-clean-one" :disabled="cleaning" @click="confirmCleanup(g)">
              Nettoyer ce groupe
            </button>
          </div>

          <!-- Compare tool -->
          <div class="bd-compare">
            <button class="bd-compare-toggle" @click="toggleCompare">
              <span>Comparer deux sauvegardes</span>
              <span :class="{ 'bd-rot': showCompare }">▾</span>
            </button>
            <div v-if="showCompare" class="bd-compare-body">
              <p class="bd-cmp-help">On compare la <b>configuration</b> de chaque module (pare-feu, NAT, VPN…) — pas les fichiers volatils (logs, dumps).</p>
              <select v-model="cmpA" class="bd-sel" @change="comparison = null; cmpErr = ''">
                <option value="">Sauvegarde A…</option>
                <option v-for="b in backupIds" :key="'a'+b" :value="b">{{ shortId(b) }}</option></select>
              <select v-model="cmpB" class="bd-sel" @change="comparison = null; cmpErr = ''">
                <option value="">Sauvegarde B…</option>
                <option v-for="b in backupIds" :key="'b'+b" :value="b">{{ shortId(b) }}</option></select>
              <button class="bd-cmp-btn" :disabled="!cmpA || !cmpB || cmpA === cmpB || comparing" @click="doCompare">
                {{ comparing ? 'Comparaison…' : 'Comparer' }}
              </button>

              <div v-if="cmpErr" class="bd-cmp-err">⚠ {{ cmpErr }}</div>

              <div v-if="comparison" class="bd-cmp-res">
                <!-- Verdict -->
                <div class="bd-verdict" :class="verdictClass">
                  <div class="bd-verdict-pct">{{ comparison.similarity_pct }}%</div>
                  <div class="bd-verdict-txt">
                    <div class="bd-verdict-lbl">{{ verdictLabel }}</div>
                    <div class="bd-verdict-sub">{{ comparison.identical_count }}/{{ comparison.total }} modules identiques</div>
                  </div>
                </div>
                <div class="bd-cmp-bar-bg"><div class="bd-cmp-bar" :class="comparison.is_identical ? 'bd-cmp-full' : ''" :style="{ width: comparison.similarity_pct + '%' }"></div></div>

                <!-- Différents -->
                <div v-if="comparison.changed_labels.length" class="bd-cmp-block">
                  <div class="bd-cmp-block-h bd-h-diff">✗ {{ comparison.changed_labels.length }} module(s) différent(s)</div>
                  <div class="bd-chips">
                    <span v-for="c in comparison.changed_labels" :key="c" class="bd-chip bd-chip-diff">{{ c }}</span>
                  </div>
                </div>
                <!-- Présents d'un seul côté -->
                <div v-if="comparison.only_in_a_labels.length || comparison.only_in_b_labels.length" class="bd-cmp-block">
                  <div class="bd-cmp-block-h bd-h-warn">≠ Modules présents d'un seul côté</div>
                  <div class="bd-chips">
                    <span v-for="c in comparison.only_in_a_labels" :key="'a'+c" class="bd-chip bd-chip-warn">{{ c }} (A)</span>
                    <span v-for="c in comparison.only_in_b_labels" :key="'b'+c" class="bd-chip bd-chip-warn">{{ c }} (B)</span>
                  </div>
                </div>
                <!-- Identiques -->
                <div v-if="comparison.identical_labels.length" class="bd-cmp-block">
                  <div class="bd-cmp-block-h bd-h-same">✓ {{ comparison.identical_labels.length }} module(s) identique(s)</div>
                  <div class="bd-chips">
                    <span v-for="c in comparison.identical_labels" :key="c" class="bd-chip bd-chip-same">{{ c }}</span>
                  </div>
                </div>

                <div v-if="comparison.is_identical" class="bd-cmp-note bd-note-ok">
                  ✓ Configuration <b>100% identique</b> — l'une des deux peut être supprimée sans perte.
                </div>
                <div v-else class="bd-cmp-note">
                  Configurations différentes — à conserver toutes les deux.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- Confirm modal -->
    <transition name="bd-pop">
      <div v-if="modal.show" class="bd-mask" @click.self="modal.show = false">
        <div class="bd-modal">
          <div class="bd-modal-t">Confirmer le nettoyage</div>
          <p class="bd-modal-b">
            <template v-if="modal.group">Supprimer <b>{{ modal.group.count - 1 }}</b> copie(s) redondante(s) ({{ modal.group.reclaimable_mb }} MB) ?</template>
            <template v-else>Supprimer <b>{{ analysis.redundant_backups }}</b> sauvegarde(s) redondante(s) ({{ analysis.reclaimable_mb }} MB) ?</template>
            <br />La plus récente de chaque groupe est <b>toujours conservée</b>.
          </p>
          <div class="bd-modal-a">
            <button class="bd-mbtn bd-mbtn-ghost" @click="modal.show = false">Annuler</button>
            <button class="bd-mbtn bd-mbtn-danger" :disabled="cleaning" @click="runCleanup">{{ cleaning ? 'Suppression…' : 'Confirmer' }}</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Toast -->
    <transition name="bd-fade">
      <div v-if="toast.show" :class="['bd-toast', 'bd-toast-' + toast.type]">{{ toast.msg }}</div>
    </transition>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "BackupDedup",
  data() {
    return {
      open: false,
      showCompare: false,
      loading: false,
      cleaning: false,
      comparing: false,
      analysis: { groups: [], duplicate_groups: 0, redundant_backups: 0, reclaimable_mb: 0 },
      backupIds: [],
      cmpA: "",
      cmpB: "",
      comparison: null,
      cmpErr: "",
      modal: { show: false, group: null },
      toast: { show: false, msg: "", type: "success" },
    };
  },
  computed: {
    hasDuplicates() {
      return this.analysis.redundant_backups > 0;
    },
    verdictLabel() {
      const p = this.comparison?.similarity_pct ?? 0;
      if (this.comparison?.is_identical) return "Identiques";
      if (p >= 80) return "Quasi-identiques";
      if (p >= 40) return "Partiellement similaires";
      return "Très différentes";
    },
    verdictClass() {
      const p = this.comparison?.similarity_pct ?? 0;
      if (this.comparison?.is_identical) return "bd-v-ok";
      if (p >= 80) return "bd-v-warn";
      return "bd-v-diff";
    },
  },
  mounted() {
    const csrf = document.cookie.match(/csrftoken=([^;]+)/);
    if (csrf) axios.defaults.headers.common["X-CSRFToken"] = csrf[1];
    this.loadAnalysis();
  },
  methods: {
    toggle() {
      this.open = !this.open;
      if (this.open) {
        this.loadAnalysis();
        this.loadBackupIds();
      }
    },
    close() {
      // Ne pas fermer si une confirmation de suppression est ouverte.
      if (this.modal.show) return;
      this.open = false;
    },
    resetAll() {
      // Réinitialise complètement le panneau à son état d'origine, puis recharge.
      this.comparison = null;
      this.cmpErr = "";
      this.cmpA = "";
      this.cmpB = "";
      this.showCompare = false;
      this.loadAnalysis();
      this.loadBackupIds();
    },
    toggleCompare() {
      this.showCompare = !this.showCompare;
      if (this.showCompare) this.loadBackupIds(); // fresh list (avoid deleted ids)
    },
    async loadAnalysis() {
      this.loading = true;
      try {
        const res = await axios.get("/backup/dedup/analysis");
        this.analysis = res.data;
      } catch (e) {
        this.showToast(e.response?.data?.message || "Backend indisponible", "error");
      } finally {
        this.loading = false;
      }
    },
    async loadBackupIds() {
      try {
        const res = await axios.get("/backup/getAllBackups");
        const list = res.data?.results || res.data || [];
        const ids = list.map((b) => b.id || b.filename).filter((id) => id && id.startsWith("backup_"));
        this.backupIds = ids;
        // Drop selections that no longer exist (e.g. just cleaned up).
        if (this.cmpA && !ids.includes(this.cmpA)) { this.cmpA = ""; this.comparison = null; }
        if (this.cmpB && !ids.includes(this.cmpB)) { this.cmpB = ""; this.comparison = null; }
      } catch { /* optional */ }
    },
    async doCompare() {
      this.comparing = true;
      this.comparison = null;
      this.cmpErr = "";
      try {
        const res = await axios.get("/backup/dedup/compare", { params: { a: this.cmpA, b: this.cmpB } });
        this.comparison = res.data;
      } catch (e) {
        this.cmpErr = e.response?.data?.message || "Comparaison impossible. Rafraîchissez la liste.";
        this.loadBackupIds(); // refresh in case a backup was deleted
      } finally {
        this.comparing = false;
      }
    },
    confirmCleanup(group) { this.modal = { show: true, group }; },
    async runCleanup() {
      this.cleaning = true;
      try {
        const body = this.modal.group ? { fingerprint: this.modal.group.fingerprint } : {};
        const res = await axios.post("/backup/dedup/cleanup", body);
        this.showToast(res.data.message || "Nettoyage effectué", "success");
        this.modal.show = false;
        await this.loadAnalysis();
        await this.loadBackupIds(); // deleted backups must leave the compare list
        this.emitter?.emit?.("reload-tabs");
      } catch (e) {
        this.showToast(e.response?.data?.message || "Erreur de nettoyage", "error");
      } finally {
        this.cleaning = false;
      }
    },
    typeLabel(t) { return { full: "Full DR", safe: "Safe", custom: "Custom" }[t] || t; },
    shortId(id) { return (id || "").replace(/^backup_(safe_|custom_)?/, "").replace(/_/g, " "); },
    formatMB(bytes) {
      const mb = (bytes || 0) / (1024 * 1024);
      return mb >= 1 ? mb.toFixed(1) + " MB" : ((bytes || 0) / 1024).toFixed(0) + " KB";
    },
    formatDate(iso) {
      if (!iso) return "—";
      const d = new Date(iso);
      return isNaN(d) ? iso : d.toLocaleDateString("fr-FR", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });
    },
    showToast(msg, type = "success") {
      this.toast = { show: true, msg, type };
      setTimeout(() => { this.toast.show = false; }, 3500);
    },
  },
  inject: { emitter: { default: null } },
};
</script>

<style scoped>
.bd-root { position: fixed; z-index: 4000; }

/* ---- Backdrop (glassmorphism) : clic dehors = fermeture ---- */
.bd-backdrop {
  position: fixed; inset: 0; z-index: 1;
  background: radial-gradient(120% 120% at 85% 92%, rgba(79,70,229,.18), rgba(15,23,42,.32));
  backdrop-filter: blur(4px) saturate(1.1);
  -webkit-backdrop-filter: blur(4px) saturate(1.1);
}

/* ---- Floating action button ---- */
.bd-fab {
  position: fixed; right: 26px; bottom: 104px; z-index: 5;
  width: 58px; height: 58px; border-radius: 50%; border: none; cursor: pointer;
  background: linear-gradient(145deg, #7c83ff 0%, #4f46e5 55%, #4338ca 100%);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 10px 22px rgba(79,70,229,.45), 0 3px 6px rgba(0,0,0,.25),
              inset 0 1px 1px rgba(255,255,255,.4), inset 0 -3px 6px rgba(0,0,0,.25);
  transition: transform .25s cubic-bezier(.34,1.56,.64,1), box-shadow .25s;
}
.bd-fab:hover { transform: translateY(-3px) scale(1.05); box-shadow: 0 16px 30px rgba(79,70,229,.55), 0 5px 10px rgba(0,0,0,.3), inset 0 1px 1px rgba(255,255,255,.5); }
.bd-fab-open { background: linear-gradient(145deg, #ef7d7d, #dc2626); box-shadow: 0 10px 22px rgba(220,38,38,.4), inset 0 1px 1px rgba(255,255,255,.4); }
.bd-fab-badge {
  position: absolute; top: -3px; right: -3px; min-width: 21px; height: 21px; padding: 0 5px;
  background: #f59e0b; color: #fff; border-radius: 999px; font-size: 11px; font-weight: 800;
  display: flex; align-items: center; justify-content: center; border: 2px solid #fff;
  box-shadow: 0 2px 5px rgba(0,0,0,.3);
}
.bd-fab-pulse::after {
  content: ""; position: absolute; inset: 0; border-radius: 50%;
  box-shadow: 0 0 0 0 rgba(245,158,11,.55); animation: bd-pulse 2s infinite;
}
@keyframes bd-pulse { 0%{box-shadow:0 0 0 0 rgba(245,158,11,.5);} 70%{box-shadow:0 0 0 14px rgba(245,158,11,0);} 100%{box-shadow:0 0 0 0 rgba(245,158,11,0);} }

/* ---- Panel ---- */
.bd-panel {
  position: fixed; right: 26px; bottom: 174px; width: 380px; max-height: 72vh; z-index: 3;
  background: #fff; border-radius: 20px; overflow: hidden; display: flex; flex-direction: column;
  box-shadow: 0 30px 70px rgba(15,23,42,.35), 0 8px 20px rgba(15,23,42,.2),
              0 0 0 1px rgba(255,255,255,.6) inset;
  transform-origin: bottom right;
}
.bd-head {
  display: flex; align-items: center; gap: 11px; padding: 15px 16px; color: #fff;
  background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%);
  box-shadow: inset 0 -1px 0 rgba(255,255,255,.15);
}
.bd-head-ico { width: 38px; height: 38px; border-radius: 11px; background: rgba(255,255,255,.18); display: flex; align-items: center; justify-content: center; box-shadow: inset 0 1px 1px rgba(255,255,255,.4); }
.bd-head-txt { flex: 1; }
.bd-head-title { font-size: 15px; font-weight: 700; line-height: 1.2; }
.bd-head-sub { font-size: 11.5px; opacity: .85; }
.bd-refresh { background: rgba(255,255,255,.16); border: none; color: #fff; width: 30px; height: 30px; border-radius: 9px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
.bd-refresh:hover { background: rgba(255,255,255,.28); }
.bd-spin { animation: bd-rot 1s linear infinite; }
@keyframes bd-rot { to { transform: rotate(360deg); } }

.bd-body { padding: 14px; overflow-y: auto; }
.bd-loading { text-align: center; color: #6b7280; font-size: 13px; padding: 10px; }

.bd-summary { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 12px; }
.bd-stat { background: #f4f5f9; border-radius: 12px; padding: 10px 8px; text-align: center; box-shadow: inset 0 1px 2px rgba(0,0,0,.03); }
.bd-stat-accent { background: linear-gradient(160deg, #eef2ff, #e0e7ff); }
.bd-stat-val { font-size: 21px; font-weight: 800; color: #1e1b4b; font-variant-numeric: tabular-nums; }
.bd-stat-val small { font-size: 11px; font-weight: 600; color: #6366f1; margin-left: 2px; }
.bd-stat-lbl { font-size: 10.5px; color: #6b7280; text-transform: uppercase; letter-spacing: .3px; margin-top: 1px; }

.bd-clean-all {
  width: 100%; margin-bottom: 14px; padding: 11px; border: none; border-radius: 12px; cursor: pointer;
  background: linear-gradient(135deg, #6366f1, #4338ca); color: #fff; font-size: 13.5px; font-weight: 700;
  box-shadow: 0 6px 14px rgba(79,70,229,.4), inset 0 1px 1px rgba(255,255,255,.35);
  transition: transform .15s, box-shadow .15s;
}
.bd-clean-all:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 9px 20px rgba(79,70,229,.5); }
.bd-clean-all:disabled { opacity: .6; cursor: not-allowed; }

.bd-empty { text-align: center; padding: 26px 8px; }
.bd-empty-ico { width: 46px; height: 46px; margin: 0 auto 10px; border-radius: 50%; background: linear-gradient(160deg,#dcfce7,#bbf7d0); color: #16a34a; font-size: 24px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(22,163,74,.2); }
.bd-empty-t { font-weight: 700; color: #111827; font-size: 14px; }
.bd-empty-s { font-size: 12px; color: #6b7280; }

.bd-group { border: 1px solid #eceef3; border-radius: 13px; padding: 10px; margin-bottom: 10px; background: #fbfbfe; box-shadow: 0 2px 6px rgba(15,23,42,.04); }
.bd-group-top { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.bd-group-txt { font-size: 12.5px; font-weight: 600; color: #374151; }
.bd-group-mb { margin-left: auto; font-size: 12px; font-weight: 700; color: #4f46e5; }
.bd-type { font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 999px; }
.bd-type-full { background: #ede9fe; color: #6d28d9; }
.bd-type-safe { background: #dcfce7; color: #15803d; }
.bd-type-custom { background: #e0f2fe; color: #0369a1; }

.bd-item { display: flex; align-items: center; gap: 8px; padding: 6px 4px; font-size: 12px; border-radius: 8px; }
.bd-item-keep { background: #f3fbf5; }
.bd-item-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.bd-dot-keep { background: #16a34a; box-shadow: 0 0 0 3px rgba(22,163,74,.15); }
.bd-dot-del { background: #dc2626; box-shadow: 0 0 0 3px rgba(220,38,38,.12); }
.bd-item-id { font-family: ui-monospace, monospace; font-size: 11px; color: #374151; }
.bd-item-date { margin-left: auto; color: #9ca3af; font-size: 11px; }
.bd-item-tag { font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 999px; }
.bd-tag-keep { background: #dcfce7; color: #15803d; }
.bd-tag-del { background: #fee2e2; color: #b91c1c; }
.bd-inline { margin-left: 6px; }

.bd-clean-one { width: 100%; margin-top: 8px; padding: 7px; border: 1px solid #ddd6fe; background: #f5f3ff; color: #5b21b6; border-radius: 9px; font-size: 12px; font-weight: 600; cursor: pointer; }
.bd-clean-one:hover:not(:disabled) { background: #ede9fe; }
.bd-clean-one:disabled { opacity: .6; cursor: not-allowed; }

.bd-compare { margin-top: 6px; border-top: 1px dashed #e5e7eb; padding-top: 10px; }
.bd-compare-toggle { width: 100%; display: flex; justify-content: space-between; align-items: center; background: none; border: none; cursor: pointer; font-size: 12.5px; font-weight: 600; color: #4f46e5; padding: 4px 2px; }
.bd-rot { display: inline-block; transform: rotate(180deg); }
.bd-compare-body { padding-top: 8px; display: flex; flex-direction: column; gap: 7px; }
.bd-cmp-help { font-size: 11px; color: #6b7280; line-height: 1.45; margin: 0 0 2px; }
.bd-sel { border: 1px solid #d1d5db; border-radius: 8px; padding: 7px 9px; font-size: 11.5px; background: #fff; }
.bd-cmp-btn { padding: 8px; border: none; border-radius: 8px; background: #4f46e5; color: #fff; font-size: 12px; font-weight: 600; cursor: pointer; }
.bd-cmp-btn:disabled { opacity: .55; cursor: not-allowed; }
.bd-cmp-err { background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; border-radius: 8px; padding: 8px 10px; font-size: 11.5px; font-weight: 600; }
.bd-cmp-res { margin-top: 6px; display: flex; flex-direction: column; gap: 9px; }

.bd-verdict { display: flex; align-items: center; gap: 12px; padding: 10px 12px; border-radius: 12px; }
.bd-v-ok { background: linear-gradient(135deg,#dcfce7,#bbf7d0); }
.bd-v-warn { background: linear-gradient(135deg,#fef3c7,#fde68a); }
.bd-v-diff { background: linear-gradient(135deg,#fee2e2,#fecaca); }
.bd-verdict-pct { font-size: 28px; font-weight: 800; color: #111827; font-variant-numeric: tabular-nums; line-height: 1; }
.bd-verdict-lbl { font-size: 13.5px; font-weight: 700; color: #111827; }
.bd-verdict-sub { font-size: 11.5px; color: #4b5563; }

.bd-cmp-bar-bg { height: 8px; background: #eef0f4; border-radius: 999px; overflow: hidden; }
.bd-cmp-bar { height: 100%; background: linear-gradient(90deg,#f59e0b,#fbbf24); border-radius: 999px; transition: width .4s ease; }
.bd-cmp-full { background: linear-gradient(90deg,#16a34a,#22c55e); }

.bd-cmp-block { }
.bd-cmp-block-h { font-size: 11.5px; font-weight: 700; margin-bottom: 5px; }
.bd-h-diff { color: #b91c1c; }
.bd-h-warn { color: #b45309; }
.bd-h-same { color: #15803d; }
.bd-chips { display: flex; flex-wrap: wrap; gap: 5px; }
.bd-chip { font-size: 10.5px; font-weight: 600; padding: 3px 9px; border-radius: 999px; }
.bd-chip-diff { background: #fee2e2; color: #b91c1c; }
.bd-chip-warn { background: #ffedd5; color: #9a3412; }
.bd-chip-same { background: #dcfce7; color: #15803d; }

.bd-cmp-note { font-size: 11.5px; color: #6b7280; line-height: 1.45; padding: 6px 8px; background: #f9fafb; border-radius: 8px; }
.bd-note-ok { background: #f0fdf4; color: #15803d; font-weight: 600; }

/* ---- Modal ---- */
.bd-mask { position: fixed; inset: 0; background: rgba(15,23,42,.55); display: flex; align-items: center; justify-content: center; z-index: 4200; }
.bd-modal { background: #fff; border-radius: 16px; padding: 22px; width: 90%; max-width: 400px; box-shadow: 0 24px 60px rgba(0,0,0,.35); }
.bd-modal-t { font-size: 16px; font-weight: 700; margin-bottom: 9px; color: #111827; }
.bd-modal-b { font-size: 13px; color: #374151; line-height: 1.6; margin: 0 0 18px; }
.bd-modal-a { display: flex; justify-content: flex-end; gap: 9px; }
.bd-mbtn { border: none; border-radius: 9px; padding: 8px 15px; font-size: 13px; font-weight: 600; cursor: pointer; }
.bd-mbtn-ghost { background: #f3f4f6; color: #374151; }
.bd-mbtn-danger { background: #dc2626; color: #fff; }
.bd-mbtn-danger:disabled { opacity: .6; cursor: not-allowed; }

/* ---- Toast ---- */
.bd-toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); padding: 11px 20px; border-radius: 10px; color: #fff; font-size: 13px; font-weight: 600; z-index: 4300; box-shadow: 0 8px 24px rgba(0,0,0,.25); }
.bd-toast-success { background: #16a34a; }
.bd-toast-error { background: #dc2626; }

/* ---- Transitions ---- */
.bd-pop-enter-active { transition: transform .3s cubic-bezier(.34,1.56,.64,1), opacity .25s; }
.bd-pop-leave-active { transition: transform .2s, opacity .2s; }
.bd-pop-enter-from, .bd-pop-leave-to { opacity: 0; transform: scale(.85) translateY(12px); }
.bd-swap-enter-active, .bd-swap-leave-active { transition: opacity .15s, transform .15s; }
.bd-swap-enter-from, .bd-swap-leave-to { opacity: 0; transform: rotate(-90deg); }
.bd-fade-enter-active, .bd-fade-leave-active { transition: opacity .3s; }
.bd-fade-enter-from, .bd-fade-leave-to { opacity: 0; }

@media (prefers-color-scheme: dark) {
  .bd-panel { background: #1e2532; box-shadow: 0 30px 70px rgba(0,0,0,.6), 0 0 0 1px rgba(255,255,255,.06) inset; }
  .bd-body { color: #e5e7eb; }
  .bd-stat { background: #262f3e; }
  .bd-stat-accent { background: linear-gradient(160deg,#312e81,#3730a3); }
  .bd-stat-val { color: #e0e7ff; }
  .bd-stat-lbl, .bd-item-date, .bd-empty-s, .bd-loading { color: #9ca3af; }
  .bd-group { background: #232b39; border-color: #333c4d; }
  .bd-item-keep { background: #16261c; }
  .bd-sel { background: #262f3e; border-color: #333c4d; color: #e5e7eb; }
  .bd-modal { background: #1e2532; }
  .bd-modal-t { color: #f3f4f6; }
  .bd-modal-b { color: #d1d5db; }
  .bd-mbtn-ghost { background: #333c4d; color: #e5e7eb; }
  .bd-clean-one { background: #2a2550; border-color: #4c3f91; color: #c4b5fd; }
  .bd-empty-t { color: #f3f4f6; }
}
</style>
