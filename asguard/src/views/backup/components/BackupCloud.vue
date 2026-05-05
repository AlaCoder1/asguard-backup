<template>
  <div class="bc-wrap">

    <!-- Toast -->
    <transition name="bc-toast-anim">
      <div v-if="toast.show" :class="['bc-toast', toast.type]">
        <span class="bc-toast-icon">{{ toast.icon }}</span>
        {{ toast.msg }}
      </div>
    </transition>

    <!-- ── Header bar ───────────────────────────────────────────────── -->
    <div class="bc-topbar">
      <div class="bc-provider-block">
        <div :class="['bc-status-dot', connectionOk ? 'ok' : 'offline']"></div>
        <div class="bc-provider-info">
          <span class="bc-provider-name">
            {{ config.configured ? providerLabel : 'Non configuré' }}
          </span>
          <span class="bc-provider-sub">
            {{ config.configured ? config.bucket_name + ' · ' + config.endpoint_url : 'Aucun stockage cloud connecté' }}
          </span>
        </div>
      </div>

      <div class="bc-topbar-actions">
        <button class="bc-btn bc-btn-ghost" :disabled="testing" @click="testConnection">
          <span v-if="testing" class="bc-spin">⟳</span>
          <span v-else>⚡</span>
          {{ testing ? 'Test…' : 'Tester connexion' }}
        </button>
        <button class="bc-btn bc-btn-ghost" :disabled="loadingList" @click="fetchCloudList">
          <span v-if="loadingList" class="bc-spin">⟳</span>
          <span v-else>↻</span>
          Actualiser
        </button>
        <button class="bc-btn bc-btn-primary" @click="showConfig = !showConfig">
          ⚙ Configurer
        </button>
      </div>
    </div>

    <!-- ── Stats row ────────────────────────────────────────────────── -->
    <div class="bc-stats-row">
      <div class="bc-stat-card">
        <div class="bc-stat-icon" style="background:#eff6ff;color:#2563eb">☁</div>
        <div class="bc-stat-body">
          <div class="bc-stat-val">{{ cloudBackups.length }}</div>
          <div class="bc-stat-label">Fichiers dans le cloud</div>
        </div>
      </div>
      <div class="bc-stat-card">
        <div class="bc-stat-icon" style="background:#f0fdf4;color:#16a34a">💾</div>
        <div class="bc-stat-body">
          <div class="bc-stat-val">{{ totalCloudSizeMB }}</div>
          <div class="bc-stat-label">Stockage utilisé</div>
        </div>
      </div>
      <div class="bc-stat-card">
        <div class="bc-stat-icon" style="background:#fdf4ff;color:#9333ea">🕐</div>
        <div class="bc-stat-body">
          <div class="bc-stat-val">{{ lastUploadTime }}</div>
          <div class="bc-stat-label">Dernier upload</div>
        </div>
      </div>
      <div class="bc-stat-card">
        <div class="bc-stat-icon" :style="config.auto_upload ? 'background:#f0fdf4;color:#16a34a' : 'background:#fef2f2;color:#dc2626'">
          {{ config.auto_upload ? '✓' : '✗' }}
        </div>
        <div class="bc-stat-body">
          <div class="bc-stat-val" :style="config.auto_upload ? 'color:#16a34a' : 'color:#dc2626'">
            {{ config.auto_upload ? 'Actif' : 'Désactivé' }}
          </div>
          <div class="bc-stat-label">Auto-upload</div>
        </div>
      </div>
    </div>

    <!-- ── Config panel ─────────────────────────────────────────────── -->
    <transition name="bc-slide">
      <div v-if="showConfig" class="bc-card bc-config-card">
        <div class="bc-card-header">
          <span class="bc-card-title">⚙ Configuration Cloud Storage</span>
          <button class="bc-icon-btn" @click="showConfig = false">✕</button>
        </div>
        <div class="bc-config-body">
          <div class="bc-form-row">
            <div class="bc-form-group">
              <label class="bc-label">Fournisseur</label>
              <select v-model="form.provider" class="bc-select">
                <option value="backblaze_b2">Backblaze B2 (gratuit 10 GB)</option>
                <option value="cloudflare_r2">Cloudflare R2 (gratuit 10 GB/mois)</option>
                <option value="aws_s3">AWS S3</option>
                <option value="minio">MinIO (self-hosted)</option>
                <option value="custom">Custom S3-compatible</option>
              </select>
            </div>
            <div class="bc-form-group">
              <label class="bc-label">Endpoint URL</label>
              <input v-model="form.endpoint_url" class="bc-input" placeholder="https://s3.eu-central-003.backblazeb2.com" />
            </div>
          </div>
          <div class="bc-form-row">
            <div class="bc-form-group">
              <label class="bc-label">Key ID (Access Key)</label>
              <input v-model="form.access_key_id" class="bc-input" placeholder="0035e91c..." />
            </div>
            <div class="bc-form-group">
              <label class="bc-label">Application Key (Secret)</label>
              <input v-model="form.secret_access_key" class="bc-input" type="password" placeholder="••••••••" />
            </div>
          </div>
          <div class="bc-form-row">
            <div class="bc-form-group">
              <label class="bc-label">Bucket Name</label>
              <input v-model="form.bucket_name" class="bc-input" placeholder="asguard-backups" />
            </div>
            <div class="bc-form-group">
              <label class="bc-label">Region</label>
              <input v-model="form.region" class="bc-input" placeholder="eu-central-003" />
            </div>
          </div>
          <div class="bc-form-row">
            <div class="bc-form-group">
              <label class="bc-label">Préfixe (dossier dans le bucket)</label>
              <input v-model="form.prefix" class="bc-input" placeholder="asguard-backups/" />
            </div>
            <div class="bc-form-group">
              <label class="bc-label">Max copies cloud</label>
              <input v-model.number="form.max_cloud_copies" class="bc-input" type="number" min="1" max="100" />
            </div>
          </div>
          <div class="bc-form-toggles">
            <label class="bc-toggle-row">
              <input type="checkbox" v-model="form.enabled" class="bc-checkbox" />
              <span>Cloud storage activé</span>
            </label>
            <label class="bc-toggle-row">
              <input type="checkbox" v-model="form.auto_upload" class="bc-checkbox" />
              <span>Auto-upload après chaque backup</span>
            </label>
          </div>
          <div class="bc-config-actions">
            <button class="bc-btn bc-btn-ghost" :disabled="testing" @click="testConnection">
              <span v-if="testing" class="bc-spin">⟳</span>
              {{ testing ? 'Test en cours…' : '⚡ Tester la connexion' }}
            </button>
            <button class="bc-btn bc-btn-primary" :disabled="saving" @click="saveConfig">
              <span v-if="saving" class="bc-spin">⟳</span>
              {{ saving ? 'Enregistrement…' : '✓ Enregistrer' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- ── Main grid ─────────────────────────────────────────────────── -->
    <div class="bc-grid">

      <!-- Cloud backups list -->
      <div class="bc-card bc-card-wide">
        <div class="bc-card-header">
          <span class="bc-card-title">
            ☁ Backups dans le cloud
            <span class="bc-count-badge">{{ cloudBackups.length }}</span>
          </span>
          <span class="bc-provider-badge">{{ config.configured ? config.provider : '—' }}</span>
        </div>

        <div v-if="loadingList" class="bc-state-block">
          <span class="bc-spin-lg">⟳</span>
          <span>Chargement…</span>
        </div>

        <div v-else-if="!config.configured" class="bc-state-block">
          <span class="bc-empty-icon">☁</span>
          <span>Aucun cloud configuré</span>
          <button class="bc-add-link" @click="showConfig = true">Configurer maintenant</button>
        </div>

        <div v-else-if="cloudBackups.length === 0" class="bc-state-block">
          <span class="bc-empty-icon">📭</span>
          <span>Aucun backup dans le cloud</span>
        </div>

        <div v-else class="bc-table-wrap">
          <table class="bc-table">
            <thead>
              <tr>
                <th>Nom</th>
                <th>Taille</th>
                <th>Uploadé le</th>
                <th>Type</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="b in cloudBackups" :key="b.key">
                <td class="bc-filename">
                  <span :class="['bc-type-dot', backupTypeClass(b.filename)]"></span>
                  {{ b.filename }}
                </td>
                <td class="bc-size">{{ formatSize(b.size_mb) }}</td>
                <td class="bc-date">{{ formatDate(b.last_modified) }}</td>
                <td>
                  <span :class="['bc-type-badge', backupTypeClass(b.filename)]">
                    {{ backupTypeLabel(b.filename) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Right column -->
      <div class="bc-col-right">

        <!-- DB history from PostgreSQL -->
        <div class="bc-card">
          <div class="bc-card-header">
            <span class="bc-card-title">🗃 Historique DB (PostgreSQL)</span>
            <span class="bc-count-badge">{{ dbHistory.length }}</span>
          </div>
          <div v-if="loadingHistory" class="bc-state-block bc-state-sm">
            <span class="bc-spin">⟳</span> Chargement…
          </div>
          <div v-else-if="dbHistory.length === 0" class="bc-state-block bc-state-sm">
            <span>Aucun enregistrement</span>
          </div>
          <div v-else class="bc-hist-list">
            <div v-for="r in dbHistory" :key="r.id" class="bc-hist-item">
              <div class="bc-hist-left">
                <span :class="['bc-run-badge', r.status]">{{ r.status }}</span>
                <span class="bc-hist-id">{{ r.backup_id }}</span>
              </div>
              <div class="bc-hist-right">
                <span v-if="r.cloud_uploaded" class="bc-cloud-badge">☁ cloud</span>
                <span class="bc-hist-date">{{ formatDateShort(r.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Local backups sync panel -->
        <div class="bc-card">
          <div class="bc-card-header">
            <span class="bc-card-title">🔄 Sync manuel</span>
          </div>
          <div class="bc-sync-body">
            <p class="bc-sync-desc">
              Pousser un backup local vers le cloud. Les backups futurs s'uploadent automatiquement.
            </p>
            <div v-if="localBackups.length === 0" class="bc-state-block bc-state-sm">
              <span>Chargement des backups locaux…</span>
            </div>
            <div v-else class="bc-sync-list">
              <div
                v-for="b in localBackups"
                :key="b.backup_id"
                class="bc-sync-item"
              >
                <div class="bc-sync-item-info">
                  <span :class="['bc-type-dot', b.type_class]"></span>
                  <span class="bc-sync-name">{{ b.backup_id }}</span>
                </div>
                <button
                  class="bc-sync-btn"
                  :disabled="syncing[b.backup_id]"
                  @click="syncBackup(b.backup_id)"
                >
                  <span v-if="syncing[b.backup_id]" class="bc-spin">⟳</span>
                  <span v-else>↑</span>
                </button>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "BackupCloud",
  data() {
    return {
      showConfig:     false,
      config:         { configured: false, auto_upload: false },
      form:           {
        provider: "backblaze_b2", endpoint_url: "", access_key_id: "",
        secret_access_key: "", bucket_name: "", region: "eu-central-003",
        prefix: "asguard-backups/", enabled: true, auto_upload: true,
        max_cloud_copies: 10,
      },
      cloudBackups:   [],
      dbHistory:      [],
      localBackups:   [],
      loadingList:    false,
      loadingHistory: false,
      connectionOk:   false,
      testing:        false,
      saving:         false,
      syncing:        {},
      toast: { show: false, msg: "", type: "success", icon: "✓" },
    };
  },

  computed: {
    totalCloudSizeMB() {
      const total = this.cloudBackups.reduce((s, b) => s + (b.size_mb || 0), 0);
      return this.formatSize(total);
    },
    lastUploadTime() {
      if (!this.cloudBackups.length) return "—";
      return this.formatDateShort(this.cloudBackups[0].last_modified);
    },
    providerLabel() {
      const map = {
        backblaze_b2:  "Backblaze B2",
        cloudflare_r2: "Cloudflare R2",
        aws_s3:        "AWS S3",
        minio:         "MinIO",
        custom:        "Custom S3",
      };
      return map[this.config.provider] || this.config.provider;
    },
  },

  mounted() {
    this.fetchConfig();
    const csrf = document.cookie.match(/csrftoken=([^;]+)/);
    if (csrf) axios.defaults.headers.common["X-CSRFToken"] = csrf[1];
  },

  methods: {
    async fetchConfig() {
      try {
        const res = await axios.get("/backup/cloud/config");
        this.config = res.data;
        if (res.data.configured) {
          Object.assign(this.form, {
            provider:      res.data.provider,
            endpoint_url:  res.data.endpoint_url,
            access_key_id: res.data.access_key_id,
            bucket_name:   res.data.bucket_name,
            region:        res.data.region,
            prefix:        res.data.prefix,
            enabled:       res.data.enabled,
            auto_upload:   res.data.auto_upload,
            max_cloud_copies: res.data.max_cloud_copies,
          });
          this.fetchCloudList();
          this.fetchHistory();
          this.fetchLocalBackups();
        }
      } catch { /* silent */ }
    },

    async fetchCloudList() {
      this.loadingList = true;
      try {
        const res = await axios.get("/backup/cloud/backups");
        this.cloudBackups = res.data.backups || [];
        this.connectionOk = res.data.ok;
      } catch { this.connectionOk = false; }
      finally  { this.loadingList = false; }
    },

    async fetchHistory() {
      this.loadingHistory = true;
      try {
        const res = await axios.get("/backup/cloud/history");
        this.dbHistory = res.data.records || [];
      } catch { /* silent */ }
      finally  { this.loadingHistory = false; }
    },

    async fetchLocalBackups() {
      try {
        const res = await axios.get("/backup/getAllBackups");
        const raw = res.data.backups || res.data || [];
        this.localBackups = raw.map(b => ({
          backup_id:  b.backup_id || b.id,
          type_class: this.backupTypeClass(b.backup_id || b.id || ""),
        })).slice(0, 15);
      } catch { /* silent */ }
    },

    async testConnection() {
      this.testing = true;
      try {
        const res = await axios.post("/backup/cloud/test");
        this.connectionOk = res.data.ok;
        this.showToast(
          res.data.ok ? "Connexion réussie !" : res.data.message,
          res.data.ok ? "success" : "error"
        );
      } catch (e) {
        this.connectionOk = false;
        this.showToast(e.response?.data?.message || "Erreur de connexion", "error");
      } finally { this.testing = false; }
    },

    async saveConfig() {
      this.saving = true;
      try {
        await axios.post("/backup/cloud/config", this.form);
        this.showToast("Configuration enregistrée !", "success");
        this.showConfig = false;
        await this.fetchConfig();
      } catch { this.showToast("Erreur lors de l'enregistrement", "error"); }
      finally { this.saving = false; }
    },

    async syncBackup(backupId) {
      this.syncing = { ...this.syncing, [backupId]: true };
      try {
        const res = await axios.post(`/backup/cloud/sync/${backupId}`);
        if (res.data.ok) {
          this.showToast(`${backupId} uploadé avec succès !`, "success");
          await this.fetchCloudList();
          await this.fetchHistory();
        } else {
          this.showToast(res.data.error || "Erreur upload", "error");
        }
      } catch { this.showToast("Erreur lors du sync", "error"); }
      finally {
        const s = { ...this.syncing };
        delete s[backupId];
        this.syncing = s;
      }
    },

    // ── Helpers ────────────────────────────────────────────────────────

    backupTypeClass(name) {
      if (!name) return "";
      if (name.includes("safe"))    return "safe_backup";
      if (name.includes(".dump"))   return "db_backup";
      if (name.includes("db"))      return "db_backup";
      return "full_backup";
    },

    backupTypeLabel(name) {
      const t = this.backupTypeClass(name);
      return { safe_backup: "Safe", full_backup: "Full", db_backup: "DB" }[t] || "—";
    },

    formatSize(mb) {
      if (mb == null || mb === 0) return "0 B";
      if (mb < 1) return (mb * 1024).toFixed(1) + " KB";
      if (mb < 1024) return mb.toFixed(2) + " MB";
      return (mb / 1024).toFixed(2) + " GB";
    },

    formatDate(iso) {
      if (!iso) return "—";
      try {
        return new Date(iso).toLocaleString("fr-FR", {
          day: "2-digit", month: "2-digit", year: "numeric",
          hour: "2-digit", minute: "2-digit",
        });
      } catch { return iso; }
    },

    formatDateShort(iso) {
      if (!iso) return "—";
      try {
        return new Date(iso).toLocaleString("fr-FR", {
          day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit",
        });
      } catch { return iso; }
    },

    showToast(msg, type = "success") {
      const icons = { success: "✓", error: "✗", info: "ℹ" };
      this.toast = { show: true, msg, type, icon: icons[type] || "ℹ" };
      setTimeout(() => { this.toast.show = false; }, 4000);
    },
  },
};
</script>

<style scoped>
/* ── Root ────────────────────────────────────────────────────────── */
.bc-wrap { padding: 20px 24px; min-height: 400px; font-family: inherit; }

/* ── Toast ───────────────────────────────────────────────────────── */
.bc-toast {
  position: fixed; bottom: 28px; right: 28px; z-index: 9999;
  display: flex; align-items: center; gap: 10px; padding: 12px 18px;
  border-radius: 10px; font-size: 14px; font-weight: 500;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15); max-width: 420px;
}
.bc-toast.success { background: #166534; color: #dcfce7; }
.bc-toast.error   { background: #7f1d1d; color: #fee2e2; }
.bc-toast.info    { background: #1e3a5f; color: #dbeafe; }
.bc-toast-icon    { font-size: 16px; }
.bc-toast-anim-enter-active, .bc-toast-anim-leave-active { transition: all 0.3s ease; }
.bc-toast-anim-enter-from, .bc-toast-anim-leave-to { opacity: 0; transform: translateY(12px); }

/* ── Top bar ─────────────────────────────────────────────────────── */
.bc-topbar {
  display: flex; align-items: center; gap: 16px;
  background: #f8fafc; border: 1px solid #e2e8f0;
  border-radius: 12px; padding: 12px 16px; margin-bottom: 14px;
}
.bc-provider-block { display: flex; align-items: center; gap: 12px; flex: 1; min-width: 0; }
.bc-status-dot {
  width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
}
.bc-status-dot.ok      { background: #22c55e; box-shadow: 0 0 0 3px #dcfce7; }
.bc-status-dot.offline { background: #94a3b8; box-shadow: 0 0 0 3px #f1f5f9; }
.bc-provider-info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.bc-provider-name { font-size: 13px; font-weight: 700; color: #0f172a; }
.bc-provider-sub  { font-size: 11px; color: #64748b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.bc-topbar-actions { display: flex; gap: 8px; flex-shrink: 0; }

/* ── Buttons ─────────────────────────────────────────────────────── */
.bc-btn {
  display: flex; align-items: center; gap: 6px;
  border-radius: 8px; padding: 7px 14px; font-size: 12.5px; font-weight: 500;
  cursor: pointer; transition: all 0.15s; white-space: nowrap; border: 1px solid transparent;
}
.bc-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.bc-btn-primary { background: #0f172a; color: #fff; border-color: #0f172a; }
.bc-btn-primary:hover:not(:disabled) { background: #1e293b; }
.bc-btn-ghost { background: #fff; color: #374151; border-color: #e2e8f0; }
.bc-btn-ghost:hover:not(:disabled) { background: #f8fafc; }

/* ── Stats row ───────────────────────────────────────────────────── */
.bc-stats-row { display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }
.bc-stat-card {
  display: flex; align-items: center; gap: 12px;
  background: #fff; border: 1px solid #e2e8f0; border-radius: 10px;
  padding: 12px 16px; flex: 1; min-width: 160px;
}
.bc-stat-icon {
  width: 36px; height: 36px; border-radius: 9px; font-size: 18px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.bc-stat-val   { font-size: 16px; font-weight: 700; color: #0f172a; line-height: 1.2; }
.bc-stat-label { font-size: 11px; color: #94a3b8; margin-top: 2px; }

/* ── Config card ─────────────────────────────────────────────────── */
.bc-config-card { margin-bottom: 16px; }
.bc-config-body { padding: 18px; }
.bc-form-row { display: flex; gap: 14px; margin-bottom: 12px; flex-wrap: wrap; }
.bc-form-group { display: flex; flex-direction: column; gap: 5px; flex: 1; min-width: 200px; }
.bc-label { font-size: 12px; font-weight: 600; color: #475569; }
.bc-input, .bc-select {
  padding: 8px 10px; border: 1px solid #e2e8f0; border-radius: 7px;
  font-size: 13px; color: #0f172a; background: #fff; outline: none;
  transition: border-color 0.15s;
}
.bc-input:focus, .bc-select:focus { border-color: #6366f1; }
.bc-form-toggles { display: flex; gap: 24px; margin-bottom: 14px; flex-wrap: wrap; }
.bc-toggle-row { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #374151; cursor: pointer; }
.bc-checkbox { width: 15px; height: 15px; cursor: pointer; }
.bc-config-actions { display: flex; gap: 10px; justify-content: flex-end; }

/* ── Slide transition ────────────────────────────────────────────── */
.bc-slide-enter-active, .bc-slide-leave-active { transition: all 0.25s ease; }
.bc-slide-enter-from, .bc-slide-leave-to { opacity: 0; transform: translateY(-8px); }

/* ── Grid ────────────────────────────────────────────────────────── */
.bc-grid { display: grid; grid-template-columns: 1fr 380px; gap: 16px; }
@media (max-width: 1100px) { .bc-grid { grid-template-columns: 1fr; } }
.bc-col-right { display: flex; flex-direction: column; gap: 16px; }
.bc-card-wide { grid-column: 1; }

/* ── Card ────────────────────────────────────────────────────────── */
.bc-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; }
.bc-card-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 18px; border-bottom: 1px solid #f1f5f9; background: #f8fafc;
}
.bc-card-title { display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 14px; color: #0f172a; }
.bc-count-badge { background: #e0e7ff; color: #3730a3; font-size: 11px; font-weight: 700; padding: 1px 7px; border-radius: 10px; }
.bc-provider-badge { background: #0f172a; color: #94a3b8; font-size: 10px; font-weight: 700; letter-spacing: 1px; padding: 3px 8px; border-radius: 5px; text-transform: uppercase; }
.bc-icon-btn { background: none; border: none; cursor: pointer; font-size: 16px; color: #94a3b8; padding: 2px 6px; border-radius: 5px; }
.bc-icon-btn:hover { background: #f1f5f9; }

/* ── State blocks ────────────────────────────────────────────────── */
.bc-state-block { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; padding: 40px 20px; color: #94a3b8; font-size: 13px; }
.bc-state-sm    { padding: 20px; }
.bc-empty-icon  { font-size: 32px; }
.bc-add-link    { background: none; border: none; color: #6366f1; font-size: 13px; cursor: pointer; text-decoration: underline; }
.bc-spin        { display: inline-block; animation: bc-spin 1s linear infinite; }
.bc-spin-lg     { font-size: 28px; animation: bc-spin 1s linear infinite; display: inline-block; }
@keyframes bc-spin { to { transform: rotate(360deg); } }

/* ── Table ───────────────────────────────────────────────────────── */
.bc-table-wrap { overflow-x: auto; }
.bc-table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
.bc-table thead tr { background: #f8fafc; }
.bc-table th { padding: 9px 14px; text-align: left; font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #e2e8f0; }
.bc-table td { padding: 10px 14px; border-bottom: 1px solid #f8fafc; color: #1e293b; }
.bc-table tbody tr:last-child td { border-bottom: none; }
.bc-table tbody tr:hover td { background: #f8fafc; }
.bc-filename { display: flex; align-items: center; gap: 8px; font-family: monospace; font-size: 12px; max-width: 340px; word-break: break-all; }
.bc-size { white-space: nowrap; font-variant-numeric: tabular-nums; }
.bc-date { white-space: nowrap; color: #64748b; }

/* ── Type dots & badges ──────────────────────────────────────────── */
.bc-type-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.bc-type-dot.safe_backup { background: #22c55e; }
.bc-type-dot.full_backup { background: #3b82f6; }
.bc-type-dot.db_backup   { background: #a855f7; }
.bc-type-badge { font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 8px; text-transform: uppercase; }
.bc-type-badge.safe_backup { background: #dcfce7; color: #166534; }
.bc-type-badge.full_backup { background: #dbeafe; color: #1d4ed8; }
.bc-type-badge.db_backup   { background: #f3e8ff; color: #7e22ce; }

/* ── History list ────────────────────────────────────────────────── */
.bc-hist-list { padding: 4px 0; max-height: 260px; overflow-y: auto; }
.bc-hist-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 16px; border-bottom: 1px solid #f8fafc; gap: 10px;
}
.bc-hist-item:last-child { border-bottom: none; }
.bc-hist-left  { display: flex; align-items: center; gap: 8px; min-width: 0; }
.bc-hist-right { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.bc-hist-id    { font-size: 11px; font-family: monospace; color: #475569; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 180px; }
.bc-hist-date  { font-size: 11px; color: #94a3b8; white-space: nowrap; }
.bc-run-badge  { font-size: 10px; font-weight: 700; padding: 1px 7px; border-radius: 10px; text-transform: uppercase; white-space: nowrap; }
.bc-run-badge.ok, .bc-run-badge.success { background: #dcfce7; color: #166534; }
.bc-run-badge.error   { background: #fee2e2; color: #dc2626; }
.bc-run-badge.partial { background: #fef3c7; color: #92400e; }
.bc-cloud-badge { font-size: 10px; background: #dbeafe; color: #1d4ed8; padding: 1px 6px; border-radius: 8px; font-weight: 600; }

/* ── Sync panel ──────────────────────────────────────────────────── */
.bc-sync-body { padding: 14px 16px; }
.bc-sync-desc { font-size: 12px; color: #64748b; margin: 0 0 12px; }
.bc-sync-list { display: flex; flex-direction: column; gap: 6px; max-height: 220px; overflow-y: auto; }
.bc-sync-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 7px 10px; background: #f8fafc; border: 1px solid #e2e8f0;
  border-radius: 7px; gap: 10px;
}
.bc-sync-item-info { display: flex; align-items: center; gap: 8px; min-width: 0; }
.bc-sync-name { font-size: 11px; font-family: monospace; color: #475569; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.bc-sync-btn {
  background: #6366f1; color: #fff; border: none; border-radius: 6px;
  padding: 4px 10px; font-size: 13px; cursor: pointer; flex-shrink: 0;
  transition: background 0.15s;
}
.bc-sync-btn:hover:not(:disabled) { background: #4f46e5; }
.bc-sync-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
