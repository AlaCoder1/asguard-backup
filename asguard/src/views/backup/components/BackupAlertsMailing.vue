<template>
  <div class="am-root">

    <!-- ─── Header ─── -->
    <header class="am-header">
      <div class="am-header-text">
        <h2>Alertes &amp; Mailing</h2>
        <p>Configuration des canaux de notification, de la matrice d'abonnement et des règles de silence.</p>
      </div>
      <div class="am-header-actions">
        <button class="am-btn am-btn-secondary" @click="reload" :disabled="loading">Recharger</button>
        <button class="am-btn am-btn-primary"   @click="save"   :disabled="saving">
          {{ saving ? 'Enregistrement…' : 'Enregistrer les modifications' }}
        </button>
      </div>
    </header>

    <!-- ─── Channels ─── -->
    <section class="am-section">
      <div class="am-section-header">
        <h3>Canaux de notification</h3>
        <span class="am-section-meta">{{ enabledChannelsCount }} actif{{ enabledChannelsCount > 1 ? 's' : '' }} sur {{ channels.length }}</span>
      </div>

      <div class="am-channels">

        <!-- Email -->
        <article class="am-channel" :class="{ enabled: config.email_enabled }">
          <div class="am-channel-bar">
            <div class="am-channel-bar-left">
              <span class="am-channel-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="5" width="18" height="14" rx="2"/>
                  <path d="M3 7l9 6 9-6"/>
                </svg>
              </span>
              <div>
                <div class="am-channel-name">Email SMTP</div>
                <div class="am-channel-tagline">Notifications structurées HTML avec rapport complet</div>
              </div>
            </div>
            <div class="am-channel-bar-right">
              <span class="am-status" :class="config.email_enabled ? 'on' : 'off'">
                <span class="am-status-dot"></span>{{ config.email_enabled ? 'Actif' : 'Désactivé' }}
              </span>
              <label class="am-switch">
                <input type="checkbox" v-model="config.email_enabled"/><span></span>
              </label>
            </div>
          </div>
          <div class="am-channel-body" v-show="config.email_enabled">
            <div class="am-grid-2">
              <div class="am-field">
                <label>Serveur SMTP</label>
                <input v-model="config.smtp_host" placeholder="smtp.exemple.com"/>
              </div>
              <div class="am-field">
                <label>Port</label>
                <input v-model.number="config.smtp_port" type="number" min="1" max="65535"/>
              </div>
              <div class="am-field">
                <label>Identifiant</label>
                <input v-model="config.smtp_user" placeholder="user@exemple.com"/>
              </div>
              <div class="am-field">
                <label>Mot de passe</label>
                <input v-model="config.smtp_password" type="password" placeholder="••••••••"/>
                <span class="am-hint" v-if="config.smtp_password === '' && hadStoredPassword">
                  Mot de passe enregistré conservé — laissez vide pour le garder.
                </span>
              </div>
            </div>
            <div class="am-field">
              <label>Destinataires</label>
              <textarea v-model="recipientsRaw" rows="3" placeholder="admin@exemple.com&#10;ops@exemple.com"></textarea>
              <span class="am-hint">Un destinataire par ligne. Séparateurs autorisés : virgule, point-virgule.</span>
            </div>
            <div class="am-channel-foot">
              <button class="am-btn am-btn-test" @click="testChannel('email')" :disabled="testingChannel==='email'">
                {{ testingChannel === 'email' ? 'Envoi en cours…' : 'Envoyer un email de test' }}
              </button>
            </div>
          </div>
        </article>

        <!-- ntfy -->
        <article class="am-channel" :class="{ enabled: ntfy.enabled }">
          <div class="am-channel-bar">
            <div class="am-channel-bar-left">
              <span class="am-channel-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/>
                  <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
                </svg>
              </span>
              <div>
                <div class="am-channel-name">ntfy.sh</div>
                <div class="am-channel-tagline">Notifications push mobiles via topic public ou auto-hébergé</div>
              </div>
            </div>
            <div class="am-channel-bar-right">
              <span class="am-status" :class="ntfy.enabled ? 'on' : 'off'">
                <span class="am-status-dot"></span>{{ ntfy.enabled ? 'Actif' : 'Désactivé' }}
              </span>
              <label class="am-switch">
                <input type="checkbox" v-model="ntfy.enabled"/><span></span>
              </label>
            </div>
          </div>
          <div class="am-channel-body" v-show="ntfy.enabled">
            <div class="am-field">
              <label>Nom du topic</label>
              <input v-model="ntfy.topic" placeholder="asguard-prod"/>
              <span class="am-hint">URL générée : <code>https://ntfy.sh/{{ ntfy.topic || '<topic>' }}</code></span>
            </div>
            <div class="am-info-note">
              Installez l'application <strong>ntfy</strong> (iOS / Android / desktop) et abonnez-vous au topic ci-dessus.
              Le topic agit comme un canal privé — choisissez un nom long et non-devinable.
            </div>
            <div class="am-channel-foot">
              <button class="am-btn am-btn-test" @click="testChannel('ntfy')" :disabled="testingChannel==='ntfy'">
                {{ testingChannel === 'ntfy' ? 'Envoi en cours…' : 'Envoyer une notification de test' }}
              </button>
            </div>
          </div>
        </article>

        <!-- Slack -->
        <article class="am-channel" :class="{ enabled: slack.enabled }">
          <div class="am-channel-bar">
            <div class="am-channel-bar-left">
              <span class="am-channel-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
              </span>
              <div>
                <div class="am-channel-name">Slack</div>
                <div class="am-channel-tagline">Canal d'incidents d'équipe via webhook entrant</div>
              </div>
            </div>
            <div class="am-channel-bar-right">
              <span class="am-status" :class="slack.enabled ? 'on' : 'off'">
                <span class="am-status-dot"></span>{{ slack.enabled ? 'Actif' : 'Désactivé' }}
              </span>
              <label class="am-switch">
                <input type="checkbox" v-model="slack.enabled"/><span></span>
              </label>
            </div>
          </div>
          <div class="am-channel-body" v-show="slack.enabled">
            <div class="am-field">
              <label>Webhook entrant Slack</label>
              <input v-model="slack.webhook_url" placeholder="https://hooks.slack.com/services/..."/>
              <span class="am-hint" v-if="slack.has_webhook && !slack.webhook_url">
                Webhook enregistré conservé : <code>{{ slack.webhook_url_masked }}</code>
              </span>
              <span class="am-hint" v-else>
                Créez le webhook dans <em>Slack &gt; Apps &gt; Incoming Webhooks</em> et collez l'URL ici.
              </span>
            </div>
            <div class="am-channel-foot">
              <button class="am-btn am-btn-test" @click="testChannel('slack')" :disabled="testingChannel==='slack'">
                {{ testingChannel === 'slack' ? 'Envoi en cours…' : 'Envoyer un message Slack de test' }}
              </button>
            </div>
          </div>
        </article>

        <!-- Twilio SMS -->
        <article class="am-channel" :class="{ enabled: twilio.enabled }">
          <div class="am-channel-bar">
            <div class="am-channel-bar-left">
              <span class="am-channel-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="5" y="2" width="14" height="20" rx="2"/>
                  <path d="M12 18h.01"/>
                </svg>
              </span>
              <div>
                <div class="am-channel-name">Twilio SMS</div>
                <div class="am-channel-tagline">Escalade d'astreinte par SMS — réservé aux événements critiques</div>
              </div>
            </div>
            <div class="am-channel-bar-right">
              <span class="am-status" :class="twilio.enabled ? 'on' : 'off'">
                <span class="am-status-dot"></span>{{ twilio.enabled ? 'Actif' : 'Désactivé' }}
              </span>
              <label class="am-switch">
                <input type="checkbox" v-model="twilio.enabled"/><span></span>
              </label>
            </div>
          </div>
          <div class="am-channel-body" v-show="twilio.enabled">
            <div class="am-grid-2">
              <div class="am-field">
                <label>Account SID</label>
                <input v-model="twilio.account_sid" placeholder="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"/>
              </div>
              <div class="am-field">
                <label>Auth Token</label>
                <input v-model="twilio.auth_token" type="password" placeholder="••••••••"/>
                <span class="am-hint" v-if="twilio.has_auth_token && !twilio.auth_token">
                  Token enregistré : <code>{{ twilio.auth_token_masked }}</code>
                </span>
              </div>
              <div class="am-field">
                <label>Numéro émetteur</label>
                <input v-model="twilio.from_number" placeholder="+15551234567"/>
                <span class="am-hint">Format E.164. Numéro Twilio vérifié obligatoire.</span>
              </div>
              <div class="am-field">
                <label>Gravité minimum</label>
                <select v-model="twilio.min_severity">
                  <option value="critical">Critique uniquement (recommandé)</option>
                  <option value="warning">Avertissement et plus</option>
                  <option value="info">Tout événement</option>
                </select>
                <span class="am-hint">Garde-fou SMS : seuls les événements à cette gravité déclenchent un envoi.</span>
              </div>
            </div>
            <div class="am-field">
              <label>Destinataires</label>
              <textarea v-model="twilioRecipientsRaw" rows="2" placeholder="+33612345678&#10;+33712345678"></textarea>
              <span class="am-hint">Numéros au format E.164, un par ligne.</span>
            </div>
            <div class="am-warn-note">
              SMS facturé par Twilio. Limitez l'abonnement aux catégories vraiment critiques (Pression ressources, IDS).
            </div>
            <div class="am-channel-foot">
              <button class="am-btn am-btn-test" @click="testChannel('twilio')" :disabled="testingChannel==='twilio'">
                {{ testingChannel === 'twilio' ? 'Envoi en cours…' : 'Envoyer un SMS de test' }}
              </button>
            </div>
          </div>
        </article>

      </div>
    </section>

    <!-- ─── Subscription matrix ─── -->
    <section class="am-section">
      <div class="am-section-header">
        <h3>Matrice d'abonnement</h3>
        <span class="am-section-meta">{{ totalSubs }} abonnements actifs sur {{ categories.length * channels.length }}</span>
      </div>

      <div class="am-matrix-actions">
        <div class="am-mx-actions-left">
          <button class="am-mini-btn am-mini-btn-strong" @click="toggleAll(true)">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
            Tout activer
          </button>
          <button class="am-mini-btn" @click="toggleAll(false)">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            Tout désactiver
          </button>
        </div>
        <div class="am-mx-actions-right">
          <span class="am-mx-label">Inverser une colonne :</span>
          <button v-for="ch in channels" :key="'col-'+ch" class="am-col-btn" :class="'am-col-'+ch"
                  @click="toggleColumn(ch)">
            <span class="am-col-dot"></span>{{ channelLabel(ch) }}
          </button>
        </div>
      </div>

      <div class="am-matrix-wrap">
        <table class="am-matrix">
          <thead>
            <tr>
              <th class="am-mx-cat">Événement</th>
              <th class="am-mx-sev">Gravité</th>
              <th v-for="ch in channels" :key="'h-'+ch" class="am-mx-ch" :class="'am-mx-ch-'+ch">
                <div class="am-mx-ch-head">
                  <span class="am-mx-ch-icon" :class="'am-col-'+ch">
                    <svg v-if="ch==='email'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>
                    <svg v-else-if="ch==='ntfy'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
                    <svg v-else-if="ch==='slack'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                    <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="5" y="2" width="14" height="20" rx="2"/><path d="M12 18h.01"/></svg>
                  </span>
                  <span class="am-mx-ch-name">{{ channelLabel(ch) }}</span>
                </div>
              </th>
              <th class="am-mx-cov">Couverture</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="(group, gIdx) in groupedCategories" :key="group.name">
              <tr class="am-mx-group">
                <td :colspan="3 + channels.length">
                  <div class="am-mx-group-inner">
                    <span class="am-mx-group-bar"></span>
                    <span class="am-mx-group-name">{{ group.name }}</span>
                    <span class="am-mx-group-count">{{ group.items.length }} événement{{ group.items.length>1?'s':'' }}</span>
                  </div>
                </td>
              </tr>
              <tr v-for="cat in group.items" :key="cat.id"
                  class="am-mx-row"
                  :class="{ 'am-mx-last': cat === group.items[group.items.length-1] && gIdx < groupedCategories.length-1 }">
                <td class="am-mx-cat-cell">
                  <div class="am-mx-cat-label">{{ cat.label }}</div>
                  <code class="am-mx-cat-id">{{ cat.id }}</code>
                </td>
                <td class="am-mx-sev-cell">
                  <span class="am-sev" :class="cat.severity_default">{{ severityLabel(cat.severity_default) }}</span>
                </td>
                <td v-for="ch in channels" :key="cat.id + ch" class="am-mx-cell" :class="['am-mx-cell-'+ch, { active: (subs[cat.id]||{})[ch] }]">
                  <label class="am-mx-check" :class="'am-col-'+ch">
                    <input type="checkbox"
                           :checked="(subs[cat.id]||{})[ch]"
                           @change="setSub(cat.id, ch, $event.target.checked)"/>
                    <span></span>
                  </label>
                </td>
                <td class="am-mx-cov-cell">
                  <div class="am-mx-cov-wrap" :title="rowCoverageLabel(cat.id)">
                    <span class="am-mx-cov-val">{{ rowActiveCount(cat.id) }}<span class="am-mx-cov-total">/{{ channels.length }}</span></span>
                    <span class="am-mx-cov-bar"><span :style="{ width: rowCoveragePct(cat.id) + '%' }"></span></span>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </section>

    <!-- ─── Global filters ─── -->
    <section class="am-section">
      <div class="am-section-header">
        <h3>Filtres globaux</h3>
        <span class="am-section-meta">Seuil de gravité et heures de silence</span>
      </div>

      <div class="am-filters">

        <div class="am-filter">
          <div class="am-filter-label">Seuil de gravité minimum</div>
          <div class="am-seg">
            <button v-for="s in severities" :key="s.id"
                    class="am-seg-item" :class="{ active: alerts.severity_threshold === s.id }"
                    @click="alerts.severity_threshold = s.id">
              <span class="am-sev" :class="s.id">{{ s.label }}</span>
              <span class="am-seg-desc">{{ s.desc }}</span>
            </button>
          </div>
        </div>

        <div class="am-filter">
          <div class="am-filter-label">
            Heures de silence
            <label class="am-switch am-switch-sm">
              <input type="checkbox" v-model="alerts.quiet_hours.enabled"/><span></span>
            </label>
          </div>
          <div class="am-quiet" :class="{ off: !alerts.quiet_hours.enabled }">
            <div class="am-grid-2">
              <div class="am-field">
                <label>Début</label>
                <select v-model.number="alerts.quiet_hours.start_hour">
                  <option v-for="h in 24" :key="'s'+h" :value="h-1">{{ String(h-1).padStart(2,'0') }}:00</option>
                </select>
              </div>
              <div class="am-field">
                <label>Fin</label>
                <select v-model.number="alerts.quiet_hours.end_hour">
                  <option v-for="h in 24" :key="'e'+h" :value="h-1">{{ String(h-1).padStart(2,'0') }}:00</option>
                </select>
              </div>
            </div>
            <label class="am-line-check">
              <input type="checkbox" v-model="alerts.quiet_hours.exempt_critical"/>
              <span>Toujours notifier en cas d'événement <strong>critique</strong> (bypass des heures de silence)</span>
            </label>
          </div>
        </div>

      </div>
    </section>

    <!-- Toast -->
    <transition name="am-toast">
      <div v-if="toast.show" class="am-toast" :class="toast.kind">{{ toast.message }}</div>
    </transition>

  </div>
</template>

<script>
import axios from "axios";

const API = "/backup";

export default {
  name: "BackupAlertsMailing",
  data() {
    return {
      loading: false, saving: false, testingChannel: null,
      config: { smtp_host: "", smtp_port: 587, smtp_user: "", smtp_password: "",
                recipients: [], email_enabled: false, sender_name: "", sender_email: "" },
      hadStoredPassword: false,
      ntfy:   { enabled: false, topic: "" },
      alerts: { severity_threshold: "info",
                quiet_hours: { enabled: false, start_hour: 22, end_hour: 7, exempt_critical: true },
                slack:  { enabled: false, webhook_url: "", has_webhook: false, webhook_url_masked: "" },
                twilio: { enabled: false, account_sid: "", auth_token: "", from_number: "",
                          recipients: [], min_severity: "critical",
                          has_auth_token: false, auth_token_masked: "" } },
      subs: {}, categories: [], channels: ["email", "ntfy", "slack", "twilio"],
      recipientsRaw: "", twilioRecipientsRaw: "",
      severities: [
        { id: "info",     label: "Tout",          desc: "Inclut les événements informatifs" },
        { id: "warning",  label: "Avertissement", desc: "Warnings et critiques uniquement" },
        { id: "critical", label: "Critique",      desc: "Uniquement les vraies urgences" },
      ],
      toast: { show: false, message: "", kind: "info" },
    };
  },
  computed: {
    slack:  { get() { return this.alerts.slack;  }, set(v) { this.alerts.slack = v;  } },
    twilio: { get() { return this.alerts.twilio; }, set(v) { this.alerts.twilio = v; } },
    enabledChannelsCount() {
      return [
        this.config.email_enabled, this.ntfy.enabled,
        this.slack.enabled, this.twilio.enabled,
      ].filter(Boolean).length;
    },
    totalSubs() {
      let n = 0;
      for (const cat of this.categories)
        for (const ch of this.channels)
          if ((this.subs[cat.id] || {})[ch]) n++;
      return n;
    },
    groupedCategories() {
      const order = ["Opérations", "Sécurité", "Identité", "Réseau"];
      const groups = {};
      for (const cat of this.categories) {
        const g = cat.group || "Autres";
        if (!groups[g]) groups[g] = [];
        groups[g].push(cat);
      }
      return order.filter(n => groups[n]).map(n => ({ name: n, items: groups[n] }));
    },
  },
  mounted() { this.reload(); },
  methods: {
    channelLabel(ch) {
      return { email: "Email", ntfy: "ntfy", slack: "Slack", twilio: "SMS Twilio" }[ch] || ch;
    },
    severityLabel(s) {
      return { info: "Info", warning: "Avert.", critical: "Critique" }[s] || s;
    },
    rowActiveCount(catId) {
      const row = this.subs[catId] || {};
      return this.channels.reduce((n, ch) => n + (row[ch] ? 1 : 0), 0);
    },
    rowCoveragePct(catId) {
      return Math.round((this.rowActiveCount(catId) / this.channels.length) * 100);
    },
    rowCoverageLabel(catId) {
      const row = this.subs[catId] || {};
      const active = this.channels.filter(c => row[c]).map(c => this.channelLabel(c));
      return active.length ? active.join(", ") : "Aucun canal abonné";
    },

    async reload() {
      this.loading = true;
      try {
        const { data } = await axios.get(`${API}/alerts/config`);
        this.categories = data.categories || [];
        this.channels   = data.channels   || this.channels;
        const c = data.config || {};
        this.hadStoredPassword = !!c.smtp_password;
        this.config = {
          smtp_host: c.smtp_host || "", smtp_port: c.smtp_port || 587,
          smtp_user: c.smtp_user || "", smtp_password: "",
          recipients: c.recipients || [],
          email_enabled: !!c.email_enabled,
          sender_name: c.sender_name || "Asguard Watchdog",
          sender_email: c.sender_email || "",
        };
        this.recipientsRaw = (c.recipients || []).join("\n");
        this.ntfy = { enabled: !!(c.ntfy && c.ntfy.enabled), topic: (c.ntfy && c.ntfy.topic) || "" };

        const a = c.alerts || {};
        this.alerts = {
          severity_threshold: a.severity_threshold || "info",
          quiet_hours: {
            enabled: !!(a.quiet_hours && a.quiet_hours.enabled),
            start_hour: (a.quiet_hours && a.quiet_hours.start_hour) ?? 22,
            end_hour:   (a.quiet_hours && a.quiet_hours.end_hour)   ?? 7,
            exempt_critical: a.quiet_hours ? !!a.quiet_hours.exempt_critical : true,
          },
          slack: { ...(a.slack || { enabled: false }), webhook_url: "" },
          twilio: { ...(a.twilio || { enabled: false, recipients: [], min_severity: "critical" }),
                    auth_token: "" },
        };
        this.twilioRecipientsRaw = (this.alerts.twilio.recipients || []).join("\n");
        this.subs = a.subscriptions || {};
      } catch (e) {
        this.flash("Impossible de charger la configuration", "error");
      } finally { this.loading = false; }
    },

    setSub(cat, ch, value) {
      if (!this.subs[cat]) this.subs[cat] = {};
      this.subs[cat] = { ...this.subs[cat], [ch]: !!value };
    },
    toggleAll(value) {
      const next = {};
      for (const cat of this.categories) {
        next[cat.id] = {};
        for (const ch of this.channels) next[cat.id][ch] = value;
      }
      this.subs = next;
    },
    toggleColumn(channel) {
      const allOn = this.categories.every(c => (this.subs[c.id]||{})[channel]);
      const next = { ...this.subs };
      for (const cat of this.categories) {
        next[cat.id] = { ...(next[cat.id] || {}), [channel]: !allOn };
      }
      this.subs = next;
    },

    async save() {
      this.saving = true;
      try {
        const recipients       = this.recipientsRaw
          .split(/[\n,;]+/).map(s => s.trim()).filter(Boolean);
        const twilioRecipients = this.twilioRecipientsRaw
          .split(/[\n,;]+/).map(s => s.trim()).filter(Boolean);
        const payload = {
          email_enabled: this.config.email_enabled,
          smtp_host:  this.config.smtp_host,
          smtp_port:  this.config.smtp_port,
          smtp_user:  this.config.smtp_user,
          smtp_password: this.config.smtp_password,
          sender_name:  this.config.sender_name,
          sender_email: this.config.sender_email,
          recipients,
          ntfy: { enabled: this.ntfy.enabled, topic: this.ntfy.topic },
          alerts: {
            severity_threshold: this.alerts.severity_threshold,
            quiet_hours: this.alerts.quiet_hours,
            slack: { enabled: this.alerts.slack.enabled,
                     webhook_url: this.alerts.slack.webhook_url },
            twilio: { enabled: this.alerts.twilio.enabled,
                      account_sid: this.alerts.twilio.account_sid,
                      auth_token:  this.alerts.twilio.auth_token,
                      from_number: this.alerts.twilio.from_number,
                      recipients: twilioRecipients,
                      min_severity: this.alerts.twilio.min_severity },
            subscriptions: this.subs,
          },
        };
        const { data } = await axios.put(`${API}/alerts/config`, payload);
        if (data.ok) {
          this.flash("Configuration enregistrée", "success");
          await this.reload();
        } else { this.flash(data.error || "Échec de la sauvegarde", "error"); }
      } catch (e) { this.flash("Erreur réseau lors de la sauvegarde", "error"); }
      finally    { this.saving = false; }
    },

    async testChannel(channel) {
      this.testingChannel = channel;
      try {
        const { data } = await axios.post(`${API}/alerts/test/${channel}`);
        if (data.ok) this.flash(`Test ${this.channelLabel(channel)} envoyé`, "success");
        else         this.flash(`Échec test ${this.channelLabel(channel)} : ${data.error || ""}`, "error");
      } catch (e) { this.flash(`Erreur réseau lors du test ${this.channelLabel(channel)}`, "error"); }
      finally    { this.testingChannel = null; }
    },

    flash(message, kind = "info") {
      this.toast = { show: true, message, kind };
      clearTimeout(this._toastTimer);
      this._toastTimer = setTimeout(() => { this.toast.show = false; }, 3500);
    },
  },
};
</script>

<style scoped lang="scss" src="../../../assets/scss/BackupAlertsMailing.scss"></style>
