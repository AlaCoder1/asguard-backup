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

<style scoped>
:root {
  --am-accent:       #1e293b;
  --am-accent-soft:  #f1f5f9;
  --am-border:       #e2e8f0;
  --am-text:         #0f172a;
  --am-text-muted:   #64748b;
}

.am-root {
  padding: 20px 22px 40px;
  color: #0f172a;
  font-size: 13px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* ── Header ───────────────────────────────────────────── */
.am-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  gap: 24px;
  padding: 18px 22px;
  margin-bottom: 22px;
  background: #fff;
  border: 1px solid #e9d5ff;
  border-radius: 10px;
  position: relative;
  overflow: hidden;
}
.am-header::before {
  content: ""; position: absolute;
  left: 0; top: 0; bottom: 0; width: 4px;
  background: linear-gradient(180deg, #7c3aed 0%, #5b21b6 100%);
}
.am-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.01em;
}
.am-header p {
  margin: 4px 0 0;
  font-size: 12.5px;
  color: #64748b;
  line-height: 1.5;
  max-width: 620px;
}
.am-header-actions { display: flex; gap: 8px; flex-shrink: 0; }

/* ── Buttons ──────────────────────────────────────────── */
.am-btn {
  display: inline-flex; align-items: center; justify-content: center;
  padding: 8px 16px;
  font-size: 12.5px; font-weight: 600;
  border-radius: 6px;
  border: 1px solid transparent;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
}
.am-btn:disabled { opacity: 0.55; cursor: not-allowed; }
.am-btn-primary {
  background: linear-gradient(180deg, #7c3aed 0%, #6d28d9 100%);
  color: #fff; border-color: #6d28d9;
  box-shadow: 0 1px 0 rgba(255,255,255,0.15) inset, 0 4px 10px rgba(124, 58, 237, 0.25);
}
.am-btn-primary:hover:not(:disabled) {
  background: linear-gradient(180deg, #8b5cf6 0%, #7c3aed 100%);
  border-color: #7c3aed;
}
.am-btn-secondary {
  background: #fff; color: #0f172a; border-color: #cbd5e1;
}
.am-btn-secondary:hover:not(:disabled) { background: #f8fafc; border-color: #94a3b8; }
.am-btn-test {
  background: #fff; color: #0f172a;
  border: 1px solid #cbd5e1;
  padding: 7px 14px;
  font-weight: 600;
}
.am-btn-test:hover:not(:disabled) { background: #f1f5f9; border-color: #64748b; }

/* ── Sections ─────────────────────────────────────────── */
.am-section {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  margin-bottom: 18px;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}
.am-section-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 13px 18px 13px 16px;
  border-bottom: 1px solid #e2e8f0;
  background: linear-gradient(180deg, #ffffff 0%, #faf5ff 100%);
  position: relative;
}
.am-section-header::before {
  content: ""; position: absolute;
  left: 0; top: 8px; bottom: 8px; width: 3px;
  background: #7c3aed; border-radius: 0 3px 3px 0;
}
.am-section-header h3 {
  margin: 0;
  font-size: 13.5px; font-weight: 700; color: #0f172a;
  letter-spacing: -0.005em;
}
.am-section-meta {
  font-size: 11px; font-weight: 600;
  color: #5b21b6;
  background: #f5f3ff;
  border: 1px solid #ddd6fe;
  padding: 3px 10px;
  border-radius: 999px;
}

/* ── Channels ─────────────────────────────────────────── */
.am-channels { display: flex; flex-direction: column; }
.am-channel {
  border-bottom: 1px solid #e2e8f0;
}
.am-channel:last-child { border-bottom: none; }
.am-channel-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 18px;
  gap: 16px;
}
.am-channel-bar-left {
  display: flex; align-items: center; gap: 14px;
  flex: 1; min-width: 0;
}
.am-channel-icon {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  color: #475569;
  flex-shrink: 0;
}
.am-channel.enabled .am-channel-icon {
  background: #f5f3ff; border-color: #c4b5fd; color: #6d28d9;
}
.am-channel-name {
  font-size: 13.5px; font-weight: 700; color: #0f172a;
}
.am-channel-tagline {
  font-size: 11.5px; color: #64748b; margin-top: 1px; line-height: 1.4;
}
.am-channel-bar-right { display: flex; align-items: center; gap: 14px; flex-shrink: 0; }
.am-status {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 11.5px; font-weight: 600;
  padding: 3px 9px;
  border-radius: 999px;
  border: 1px solid;
}
.am-status.on  { color: #047857; border-color: #6ee7b7; background: #ecfdf5; }
.am-status.off { color: #475569; border-color: #cbd5e1; background: #f8fafc; }
.am-status-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: currentColor;
}

/* Switch */
.am-switch { position: relative; display: inline-block; width: 34px; height: 19px; }
.am-switch-sm { width: 30px; height: 17px; }
.am-switch input { opacity: 0; width: 0; height: 0; }
.am-switch span {
  position: absolute; cursor: pointer; inset: 0;
  background: #cbd5e1; border-radius: 999px;
  transition: background 0.2s;
}
.am-switch span::before {
  content: ""; position: absolute;
  height: 15px; width: 15px; left: 2px; bottom: 2px;
  background: #fff; border-radius: 50%;
  transition: transform 0.2s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}
.am-switch-sm span::before { height: 13px; width: 13px; }
.am-switch input:checked + span { background: #7c3aed; }
.am-switch input:checked + span::before { transform: translateX(15px); }
.am-switch-sm input:checked + span::before { transform: translateX(13px); }

/* Channel body */
.am-channel-body {
  padding: 4px 18px 18px;
  background: #fafbfc;
  border-top: 1px solid #e2e8f0;
}
.am-grid-2 {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 12px;
}
.am-field { display: flex; flex-direction: column; gap: 4px; margin-top: 12px; }
.am-grid-2 > .am-field { margin-top: 0; }
.am-field label {
  font-size: 11px; font-weight: 700; color: #475569;
  text-transform: uppercase; letter-spacing: 0.5px;
}
.am-field input, .am-field select, .am-field textarea {
  padding: 7px 11px;
  border: 1px solid #cbd5e1;
  border-radius: 5px;
  font-size: 12.5px;
  font-family: inherit;
  background: #fff;
  color: #0f172a;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.am-field input:focus, .am-field select:focus, .am-field textarea:focus {
  outline: none;
  border-color: #475569;
  box-shadow: 0 0 0 3px rgba(71, 85, 105, 0.12);
}
.am-field textarea { font-family: ui-monospace, "SF Mono", monospace; font-size: 12px; resize: vertical; }
.am-hint { font-size: 11px; color: #94a3b8; line-height: 1.5; }
.am-hint code, .am-hint em { background: #f1f5f9; padding: 1px 5px; border-radius: 3px; font-size: 10.5px; color: #475569; font-style: normal; }
.am-channel-foot { margin-top: 14px; }

.am-info-note, .am-warn-note {
  margin-top: 12px;
  padding: 10px 12px;
  border-radius: 5px;
  font-size: 11.5px; line-height: 1.5;
  border-left: 3px solid;
}
.am-info-note { background: #f0f9ff; color: #075985; border-color: #38bdf8; }
.am-warn-note { background: #fffbeb; color: #78350f; border-color: #f59e0b; }

/* ── Matrix ───────────────────────────────────────────── */
/* Channel accent palette — each channel gets its own subtle hue used in:
   • the column header chip   • the column background "track"
   • the active checkbox fill • the per-channel "Inverser" button */
.am-col-email   { --col-hue: #4338ca; --col-bg: #eef2ff; --col-track: rgba(67, 56, 202, 0.04); }
.am-col-ntfy    { --col-hue: #b45309; --col-bg: #fffbeb; --col-track: rgba(180, 83, 9, 0.04); }
.am-col-slack   { --col-hue: #047857; --col-bg: #ecfdf5; --col-track: rgba(4, 120, 87, 0.04); }
.am-col-twilio  { --col-hue: #b91c1c; --col-bg: #fef2f2; --col-track: rgba(185, 28, 28, 0.04); }

.am-matrix-actions {
  display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between;
  gap: 12px;
  padding: 14px 18px;
  background: linear-gradient(180deg, #faf5ff 0%, #f5f3ff 100%);
  border-bottom: 1px solid #e9d5ff;
}
.am-mx-actions-left, .am-mx-actions-right {
  display: flex; align-items: center; gap: 6px; flex-wrap: wrap;
}
.am-mx-label {
  font-size: 11px; font-weight: 700; color: #5b21b6;
  text-transform: uppercase; letter-spacing: 0.5px;
  margin-right: 4px;
}
.am-mini-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 12px;
  background: #fff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 11.5px; font-weight: 600;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s;
}
.am-mini-btn:hover { background: #f1f5f9; border-color: #7c3aed; color: #5b21b6; }
.am-mini-btn-strong {
  background: #7c3aed; color: #fff; border-color: #7c3aed;
}
.am-mini-btn-strong:hover { background: #6d28d9; border-color: #6d28d9; color: #fff; }
.am-col-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 5px 11px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  font-size: 11px; font-weight: 600;
  color: var(--col-hue);
  cursor: pointer;
  transition: all 0.15s;
}
.am-col-btn:hover { background: var(--col-bg); border-color: var(--col-hue); }
.am-col-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--col-hue);
}

.am-matrix-wrap {
  overflow: auto;
  max-height: 620px;
  /* Subtle inset so the sticky header has a backdrop edge */
  position: relative;
}
.am-matrix {
  width: 100%; border-collapse: separate; border-spacing: 0;
  background: #fff;
}
.am-matrix th, .am-matrix td {
  padding: 11px 14px;
  text-align: left;
  border-bottom: 1px solid #f1f5f9;
  font-size: 12px;
}

/* Sticky header bar */
.am-matrix thead th {
  position: sticky; top: 0; z-index: 3;
  background: #fff;
  border-bottom: 2px solid #ddd6fe;
  padding-top: 10px; padding-bottom: 10px;
  font-size: 10.5px; font-weight: 700;
  color: #475569;
  text-transform: uppercase; letter-spacing: 0.6px;
  text-align: center;
}

.am-mx-cat { text-align: left !important; min-width: 240px; }
.am-mx-sev { width: 92px; text-align: center !important; }
.am-mx-ch  { width: 110px; }
.am-mx-cov { width: 110px; text-align: right !important; padding-right: 18px !important; }

/* Channel column header chip with icon */
.am-mx-ch-head {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 4px 10px;
  background: var(--col-bg, #f1f5f9);
  color: var(--col-hue, #475569);
  border-radius: 999px;
  font-size: 10.5px; font-weight: 700;
  letter-spacing: 0.4px;
}
.am-mx-ch-icon {
  width: 16px; height: 16px;
  display: inline-flex; align-items: center; justify-content: center;
}
.am-mx-ch-icon svg { width: 14px; height: 14px; }
.am-mx-ch-name { white-space: nowrap; }

/* Channel column tinted track */
.am-mx-cell-email,  .am-mx-ch.am-mx-ch-email   { background: var(--col-track, transparent); }
.am-mx-cell-email   { --col-track: rgba(67, 56, 202, 0.035); }
.am-mx-cell-ntfy,   .am-mx-ch.am-mx-ch-ntfy    { background: rgba(180, 83, 9, 0.035); }
.am-mx-cell-slack,  .am-mx-ch.am-mx-ch-slack   { background: rgba(4, 120, 87, 0.035); }
.am-mx-cell-twilio, .am-mx-ch.am-mx-ch-twilio  { background: rgba(185, 28, 28, 0.04); }
/* Slightly stronger when active */
.am-mx-cell.active.am-mx-cell-email   { background: rgba(67, 56, 202, 0.075); }
.am-mx-cell.active.am-mx-cell-ntfy    { background: rgba(180, 83, 9, 0.075); }
.am-mx-cell.active.am-mx-cell-slack   { background: rgba(4, 120, 87, 0.075); }
.am-mx-cell.active.am-mx-cell-twilio  { background: rgba(185, 28, 28, 0.085); }

/* Group header — violet accent bar */
.am-mx-group td {
  background: #fff;
  border-bottom: 1px solid #e9d5ff;
  padding: 0 !important;
  position: sticky; top: 40px; z-index: 2;
}
.am-mx-group-inner {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 18px;
  background: linear-gradient(90deg, #faf5ff 0%, #ffffff 60%);
  border-left: 3px solid #7c3aed;
}
.am-mx-group-bar { display: none; }
.am-mx-group-name {
  font-size: 11px; font-weight: 800;
  color: #4c1d95;
  text-transform: uppercase; letter-spacing: 1.2px;
}
.am-mx-group-count {
  margin-left: auto;
  font-size: 10.5px; font-weight: 600;
  color: #7c3aed;
  background: #f5f3ff;
  border: 1px solid #ddd6fe;
  padding: 2px 9px;
  border-radius: 999px;
}

/* Row hover state */
.am-mx-row { transition: background 0.12s; }
.am-mx-row:hover td { background: #faf5ff; }
.am-mx-row:hover .am-mx-cell-email   { background: rgba(67, 56, 202, 0.08); }
.am-mx-row:hover .am-mx-cell-ntfy    { background: rgba(180, 83, 9, 0.08); }
.am-mx-row:hover .am-mx-cell-slack   { background: rgba(4, 120, 87, 0.08); }
.am-mx-row:hover .am-mx-cell-twilio  { background: rgba(185, 28, 28, 0.09); }

.am-mx-cat-cell { padding-left: 18px !important; }
.am-mx-cat-label { font-weight: 600; color: #0f172a; }
.am-mx-cat-id    { font-size: 10.5px; color: #94a3b8; background: transparent; padding: 0; }
.am-mx-sev-cell  { text-align: center; }
.am-mx-cell      { text-align: center; transition: background 0.12s; }
.am-mx-cov-cell  { text-align: right; padding-right: 18px !important; }

.am-sev {
  display: inline-block;
  padding: 2px 9px; border-radius: 4px;
  font-size: 10px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.5px;
  border: 1px solid;
}
.am-sev.info     { color: #1e3a8a; background: #eff6ff; border-color: #bfdbfe; }
.am-sev.warning  { color: #78350f; background: #fffbeb; border-color: #fde68a; }
.am-sev.critical { color: #7f1d1d; background: #fef2f2; border-color: #fecaca; }

/* Custom checkbox — channel-colored when active */
.am-mx-check { display: inline-block; cursor: pointer; position: relative; }
.am-mx-check input { position: absolute; opacity: 0; pointer-events: none; }
.am-mx-check span {
  display: inline-block;
  width: 18px; height: 18px;
  border: 1.5px solid #cbd5e1;
  border-radius: 4px;
  background: #fff;
  position: relative;
  transition: all 0.15s;
}
.am-mx-check:hover span { border-color: var(--col-hue, #7c3aed); transform: scale(1.06); }
.am-mx-check input:checked + span {
  background: var(--col-hue, #7c3aed);
  border-color: var(--col-hue, #7c3aed);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}
.am-mx-check input:checked + span::after {
  content: ""; position: absolute;
  left: 5px; top: 1px;
  width: 5px; height: 10px;
  border: solid #fff; border-width: 0 2.5px 2.5px 0;
  transform: rotate(45deg);
}

/* Coverage badge per row */
.am-mx-cov-wrap {
  display: inline-flex; flex-direction: column; align-items: flex-end;
  gap: 4px;
  min-width: 70px;
}
.am-mx-cov-val {
  font-size: 12px; font-weight: 700;
  color: #4c1d95;
  font-variant-numeric: tabular-nums;
}
.am-mx-cov-total { color: #c4b5fd; font-weight: 500; }
.am-mx-cov-bar {
  width: 70px; height: 4px;
  background: #ede9fe;
  border-radius: 2px;
  overflow: hidden;
}
.am-mx-cov-bar > span {
  display: block; height: 100%;
  background: linear-gradient(90deg, #a78bfa 0%, #7c3aed 100%);
  border-radius: 2px;
  transition: width 0.25s ease;
}

/* ── Filters ──────────────────────────────────────────── */
.am-filters {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 0;
}
.am-filter {
  padding: 16px 18px;
  border-right: 1px solid #e2e8f0;
}
.am-filter:last-child { border-right: none; }
.am-filter-label {
  font-size: 11.5px; font-weight: 700; color: #0f172a;
  margin-bottom: 12px;
  display: flex; align-items: center; justify-content: space-between;
  text-transform: uppercase; letter-spacing: 0.5px;
}

.am-seg { display: flex; flex-direction: column; gap: 6px; }
.am-seg-item {
  display: flex; align-items: center; gap: 12px;
  padding: 9px 12px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 12px; font-weight: 500;
  text-align: left;
  cursor: pointer;
  transition: all 0.15s;
}
.am-seg-item:hover { border-color: #94a3b8; }
.am-seg-item.active {
  border-color: #7c3aed;
  background: #faf5ff;
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.1);
}
.am-seg-desc { color: #64748b; font-size: 11.5px; }

.am-quiet { transition: opacity 0.2s; }
.am-quiet.off { opacity: 0.5; pointer-events: none; }
.am-line-check {
  display: flex; align-items: flex-start; gap: 8px;
  margin-top: 14px;
  font-size: 11.5px; color: #475569;
  line-height: 1.5; cursor: pointer;
}
.am-line-check input { accent-color: #7c3aed; margin-top: 2px; }
.am-line-check strong { color: #7f1d1d; }

/* ── Toast ────────────────────────────────────────────── */
.am-toast {
  position: fixed; bottom: 20px; right: 20px;
  padding: 11px 18px;
  background: #fff;
  border-radius: 6px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.12);
  font-size: 12.5px; font-weight: 600;
  border-left: 3px solid;
  z-index: 9999;
}
.am-toast.success { color: #047857; border-color: #10b981; }
.am-toast.error   { color: #b91c1c; border-color: #dc2626; }
.am-toast.info    { color: #1e40af; border-color: #2563eb; }
.am-toast-enter-active, .am-toast-leave-active { transition: all 0.25s; }
.am-toast-enter-from, .am-toast-leave-to { opacity: 0; transform: translateX(20px); }

/* Responsive */
@media (max-width: 760px) {
  .am-grid-2 { grid-template-columns: 1fr; }
  .am-filters { grid-template-columns: 1fr; }
  .am-filter { border-right: none; border-bottom: 1px solid #e2e8f0; }
  .am-filter:last-child { border-bottom: none; }
  .am-header { flex-direction: column; }
}
</style>
