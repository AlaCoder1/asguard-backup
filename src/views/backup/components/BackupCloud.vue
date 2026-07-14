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

<style scoped lang="scss" src="../../../assets/scss/BackupCloud.scss"></style>
