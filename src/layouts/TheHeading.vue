<template>
  <!-- Toast stack — fixed top-right, outside app bar -->
  <Teleport to="body">
    <div class="notif-toast-stack" aria-live="assertive">
      <transition-group name="notif-toast" tag="div" class="notif-toast-inner">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="['notif-toast', `notif-toast--${toast.severity}`]"
        >
          <span class="notif-toast-icon">
            <!-- Critical: circle-bang -->
            <svg v-if="toast.severity === 'critical'" viewBox="0 0 20 20" fill="none" width="15" height="15">
              <circle cx="10" cy="10" r="8.5" stroke="currentColor" stroke-width="1.6"/>
              <path d="M10 6v4.5M10 13.5v.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
            <!-- Warning: triangle -->
            <svg v-else viewBox="0 0 20 20" fill="none" width="15" height="15">
              <path d="M10 3.5L17 16H3L10 3.5z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
              <path d="M10 9v3M10 13.5v.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
            </svg>
          </span>
          <div class="notif-toast-body">
            <strong>{{ toast.title }}</strong>
            <span>{{ toast.message }}</span>
          </div>
          <button class="notif-toast-close" type="button" @click="dismissToast(toast.id)" aria-label="Fermer">
            <svg viewBox="0 0 12 12" fill="none" width="10" height="10">
              <path d="M2 2l8 8M10 2L2 10" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
      </transition-group>
    </div>
  </Teleport>

  <v-app-bar>
    <v-toolbar>
      <v-toolbar-title class="ml-8">
        <img src="../assets/images/logo.svg" alt="logo" height="50" />
      </v-toolbar-title>
      <v-spacer />

      <!-- Notification bell -->
      <v-menu
        v-model="notifPanelOpen"
        :close-on-content-click="false"
        location="bottom end"
        offset="12"
        @update:model-value="handleNotifMenuToggle"
      >
        <template v-slot:activator="{ props }">
          <div class="notif-bell-wrap" v-bind="props">
            <button
              class="notif-bell-btn"
              :class="{ 'notif-bell-btn--active': notifCount > 0, 'notif-bell-btn--open': notifPanelOpen }"
              type="button"
            >
              <span class="notif-bell-icon">
                <svg viewBox="0 0 24 24" fill="none" width="18" height="18">
                  <path d="M12 3a7 7 0 0 1 7 7v3.5l1.4 2.1a1 1 0 0 1-.84 1.4H4.44a1 1 0 0 1-.84-1.4L5 13.5V10a7 7 0 0 1 7-7z" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round" fill="none"/>
                  <path d="M10 17a2 2 0 0 0 4 0" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>
                </svg>
                <span v-if="notifCount > 0" class="notif-ring"></span>
              </span>
              <span v-if="notifCount > 0" class="notif-badge">
                {{ notifCount > 99 ? '99+' : notifCount }}
              </span>
            </button>
          </div>
        </template>

        <div class="notif-panel">
          <!-- Panel header -->
          <div class="notif-panel-head">
            <div class="notif-panel-head-left">
              <strong>Alertes actives</strong>
              <span :class="['notif-panel-count', notifCount > 0 ? 'has-alerts' : 'no-alerts']">
                {{ notifCount > 0 ? `${notifCount} non résolue${notifCount > 1 ? 's' : ''}` : 'Tout est calme' }}
              </span>
            </div>
            <button
              v-if="inAppUnread.length > 0"
              class="notif-mark-read-btn"
              type="button"
              @click.stop="markAllRead"
            >
              Tout marquer lu
            </button>
          </div>

          <div v-if="notifLoading" class="notif-panel-loading">
            <div class="notif-spinner"></div>
            <span>Chargement...</span>
          </div>

          <template v-else>
            <!-- No alerts at all -->
            <div v-if="notifCount === 0" class="notif-panel-empty">
              <svg viewBox="0 0 32 32" fill="none" width="28" height="28">
                <circle cx="16" cy="16" r="13" stroke="currentColor" stroke-width="1.4" opacity=".2"/>
                <path d="M10 16l4 4 8-8" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" opacity=".35"/>
              </svg>
              <strong>Aucune alerte</strong>
              <span>Tout fonctionne correctement.</span>
            </div>

            <div v-else class="notif-list">
              <!-- In-app persistent alerts (events that happened) -->
              <template v-if="inAppUnread.length > 0">
                <div class="notif-section-label">
                  <svg viewBox="0 0 14 14" fill="none" width="11" height="11">
                    <circle cx="7" cy="7" r="6" stroke="currentColor" stroke-width="1.4"/>
                    <path d="M7 4v3.5L9 9" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
                  </svg>
                  Événements récents
                </div>
                <a
                  v-for="alert in inAppUnread.slice(0, 5)"
                  :key="alert.id"
                  :class="['notif-item', 'notif-item--link', `notif-item--${alert.severity}`]"
                  :href="alertHref(alert)"
                  @click="onAlertClick(alert)"
                >
                  <span :class="['notif-dot', alert.severity]"></span>
                  <div class="notif-item-body">
                    <strong>{{ alert.title }}</strong>
                    <span>{{ alert.message }}</span>
                    <small>{{ formatAlertTime(alert.time || alert.timestamp) }}</small>
                  </div>
                  <span :class="['notif-severity', alert.severity]">
                    {{ alert.severity === 'critical' ? 'Critique' : 'Attention' }}
                  </span>
                </a>
                <div v-if="inAppUnread.length > 5" class="notif-more">
                  + {{ inAppUnread.length - 5 }} événement{{ inAppUnread.length - 5 > 1 ? 's' : '' }} supplémentaire{{ inAppUnread.length - 5 > 1 ? 's' : '' }}
                </div>
              </template>

              <!-- Separator between sections -->
              <div v-if="inAppUnread.length > 0 && notifications.length > 0" class="notif-separator"></div>

              <!-- Dashboard live metrics alerts -->
              <template v-if="notifications.length > 0">
                <div class="notif-section-label">
                  <svg viewBox="0 0 14 14" fill="none" width="11" height="11">
                    <rect x="1" y="1" width="12" height="12" rx="2" stroke="currentColor" stroke-width="1.4"/>
                    <path d="M4 10l2-4 2 2 2-5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  Métriques actives
                </div>
                <div
                  v-for="(alert, i) in notifications.slice(0, 5)"
                  :key="`dash-${i}`"
                  :class="['notif-item', `notif-item--${alert.severity}`]"
                >
                  <span :class="['notif-dot', alert.severity]"></span>
                  <div class="notif-item-body">
                    <strong>{{ alert.service }}</strong>
                    <span>{{ alert.message }}</span>
                    <small>{{ alert.cause }}</small>
                  </div>
                  <span :class="['notif-severity', alert.severity]">
                    {{ alert.severity === 'critical' ? 'Critique' : 'Attention' }}
                  </span>
                </div>
                <div v-if="notifications.length > 5" class="notif-more">
                  + {{ notifications.length - 5 }} alerte{{ notifications.length - 5 > 1 ? 's' : '' }} supplémentaire{{ notifications.length - 5 > 1 ? 's' : '' }}
                </div>
              </template>
            </div>
          </template>

          <a href="/backup/" class="notif-panel-footer">
            Voir le tableau de bord backup
            <svg viewBox="0 0 12 12" fill="none" width="10" height="10">
              <path d="M2 6h8M7 3l3 3-3 3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </a>
        </div>
      </v-menu>

      <div
        class="lang d-flex align-center"
        style="gap: 5px; cursor: pointer"
        id="language-btn"
      >
        <span
          v-if="selectedLang.length"
          v-html="selectedLang[0].icon"
          style="margin-top: 4px"
        ></span>

        <span v-if="selectedLang.length">{{
          $t(selectedLang[0].language)
        }}</span>
        <v-icon>mdi-chevron-down</v-icon>

        <v-menu activator="#language-btn">
          <v-list v-model:selected="selectedLang">
            <v-list-item
              v-for="lang in langs"
              :key="lang.lang"
              :value="lang"
              @click="updateLang(lang)"
            >
              <v-list-item-title
                class="d-flex align-center ml-4"
                style="gap: 10px"
              >
                <span v-html="lang.icon"></span> {{ $t(lang.language) }}
              </v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </div>
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-avatar
            class="ml-3 mr-3"
            size="40"
            v-bind="props"
            style="
              border: 2px solid #fff;
              cursor: pointer;
              overflow: hidden;
              border-radius: 50%;
            "
          >
            <img
              :src="state.imageURL"
              alt="avatar"
              style="width: 100%; height: 100%; object-fit: cover"
            />
          </v-avatar>
        </template>
        <v-list style="cursor: pointer; padding: 15px">
          <a :href="'/profile'" style="text-decoration: none; color: black">
            <v-list-item>
              {{ $t("header.profile") }}
            </v-list-item>
          </a>
          <v-list-item>
            <span @click="logout">{{ $t("header.logout") }}</span>
          </v-list-item>
        </v-list>
      </v-menu>

      <div class="userInfo">
        <span class="white-color">{{ state.currentInfo.username }}</span>
        <span class="white-color">{{ state.currentInfo.email }}</span>
      </div>

      <br />
    </v-toolbar>
  </v-app-bar>
</template>

<script>
import axios from "axios";
import { getCookie } from "@/mixins/csrftoken.js";
import { onBeforeUnmount, onMounted, reactive, ref, computed } from "vue";
import { get_lang } from "@/mixins/storage_language.js";
import { useI18n } from "vue-i18n";
import { useNotifStore } from "@/store/modules/notifications.js";

let _toastSeq = 0;

export default {
  name: "ToolbarComponent",
  inject: ["emitter"],

  setup() {
    const { t } = useI18n();
    const notifStore = useNotifStore();

    const notifications = ref([]);
    const inAppAlerts  = ref([]);
    const inAppUnread  = computed(() => inAppAlerts.value.filter(a => !a.read));
    const notifCount   = computed(() => notifications.value.length + inAppUnread.value.length);

    // Map alert type → tab inside /backup so user lands on the right view
    const alertHref = (alert) => {
      const type = alert?.type || "";
      if (type === "resource_risk") {
        try { localStorage.setItem("backup-tab", "AI Risk Center"); } catch {}
        return "/backup";
      }
      try { localStorage.setItem("backup-tab", "Dashboard & Monitoring"); } catch {}
      return "/backup";
    };

    const onAlertClick = (alert) => {
      // Optimistic mark-as-read so the badge updates instantly before navigation
      if (alert && !alert.read) {
        alert.read = true;
        const idx = inAppAlerts.value.findIndex(a => a.id === alert.id);
        if (idx !== -1) inAppAlerts.value[idx] = { ...inAppAlerts.value[idx], read: true };
      }
    };

    const toasts         = ref([]);
    const notifPanelOpen = ref(false);
    const notifLoading   = ref(false);

    let notifInterval  = null;
    let inAppInterval  = null;
    const seenAlertIds = new Set();
    let firstInAppFetch = true;

    // ── Dashboard metrics alerts ───────────────────────────────────────────
    const fetchNotifications = async () => {
      try {
        notifLoading.value = true;
        const res = await axios.get("/backup/dashboard-overview", { params: { skip_sync_scan: true } });
        notifications.value = res.data?.alerts || [];
        notifStore.update(res.data);
      } catch (_) {
        // silently fail
      } finally {
        notifLoading.value = false;
      }
    };

    // ── Persistent in-app alerts ───────────────────────────────────────────
    const fetchInAppAlerts = async (showToasts = true) => {
      try {
        const res = await axios.get("/backup/in-app-alerts");
        const all = res.data?.alerts || [];
        inAppAlerts.value = all;
        notifStore.setInAppCount(all.filter(a => !a.read).length);

        if (!showToasts || firstInAppFetch) {
          // Seed the seen set without showing toasts on the very first load
          all.forEach(a => seenAlertIds.add(a.id));
          firstInAppFetch = false;
          return;
        }

        // Show a toast for every unread alert we haven't seen yet
        const newOnes = all.filter(a => !a.read && !seenAlertIds.has(a.id));
        newOnes.forEach(a => {
          seenAlertIds.add(a.id);
          addToast(a);
        });
      } catch (_) {
        // endpoint may not exist in all deployments
      }
    };

    // ── Mark all in-app alerts as read ────────────────────────────────────
    const markAllRead = async () => {
      try {
        const csrfToken = getCookie("csrftoken");
        await axios.post("/backup/in-app-alerts/mark-read", {}, {
          headers: { "X-CSRFToken": csrfToken },
        });
        // Optimistic update
        inAppAlerts.value = inAppAlerts.value.map(a => ({ ...a, read: true }));
        notifStore.setInAppCount(0);
      } catch (_) {}
    };

    // ── Toast helpers ──────────────────────────────────────────────────────
    const addToast = (alert) => {
      const id = ++_toastSeq;
      toasts.value.push({
        id,
        title:    alert.title   || "Alerte",
        message:  alert.message || "",
        severity: alert.severity || "warning",
      });
      // Auto-dismiss after 7 s
      setTimeout(() => dismissToast(id), 7000);
    };

    const dismissToast = (id) => {
      const idx = toasts.value.findIndex(t => t.id === id);
      if (idx !== -1) toasts.value.splice(idx, 1);
    };

    // ── Format alert timestamp ─────────────────────────────────────────────
    const formatAlertTime = (ts) => {
      if (!ts) return "";
      try {
        const d = new Date(ts);
        const diffMs  = Date.now() - d.getTime();
        const diffMin = Math.floor(diffMs / 60000);
        if (diffMin < 1)   return "à l'instant";
        if (diffMin < 60)  return `il y a ${diffMin} min`;
        const diffH = Math.floor(diffMin / 60);
        if (diffH < 24)    return `il y a ${diffH} h`;
        return d.toLocaleDateString("fr-FR", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });
      } catch (_) {
        return "";
      }
    };

    // ── Panel toggle ───────────────────────────────────────────────────────
    const handleNotifMenuToggle = (isOpen) => {
      notifPanelOpen.value = isOpen;
      if (isOpen) {
        fetchNotifications();
        fetchInAppAlerts(false);
      }
    };

    // ── Lifecycle ──────────────────────────────────────────────────────────
    onMounted(() => {
      let retriveInfo = localStorage.getItem("user-info");
      let userInfo = JSON.parse(retriveInfo);
      let user = userInfo;
      state.currentInfo = { ...user.currentUser };
      let id = userInfo?.currentUser?.id;
      getUserById(id);

      (async () => {
        let lang = await get_lang();
        selectedLang.value =
          lang === "fr" ? [langs.value[1]] : [langs.value[0]];
      })();

      // Initial fetch — seed seenAlertIds without toasts
      fetchNotifications();
      fetchInAppAlerts(false);

      // Poll dashboard metrics every 30 s (was 60s — keep bell count fresher)
      notifInterval = setInterval(fetchNotifications, 30000);
      // Poll in-app alerts every 10 s, show toasts for new ones
      inAppInterval = setInterval(() => fetchInAppAlerts(true), 10000);
    });

    onBeforeUnmount(() => {
      if (notifInterval) clearInterval(notifInterval);
      if (inAppInterval) clearInterval(inAppInterval);
    });

    const state = reactive({
      currentInfo: {},
      imageURL: null,
    });
    const selectedLang = ref([]);
    const langs = ref([
      {
        icon: ` <svg
                xmlns="http://www.w3.org/2000/svg"
                version="1.1"
                x="0px"
                y="0px"
                viewBox="0 0 512 512"
                style="enable-background: new 0 0 512 512; width: 20px;margin-top:5px"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                xml:space="preserve"
            >
                <circle
                style="fill: #f0f0f0"
                cx="256"
                cy="256"
                r="256"
                ></circle>
                <g>
                <path
                    style="fill: #0052b4"
                    d="M52.92,100.142c-20.109,26.163-35.272,56.318-44.101,89.077h133.178L52.92,100.142z"
                ></path>
                <path
                    style="fill: #0052b4"
                    d="M503.181,189.219c-8.829-32.758-23.993-62.913-44.101-89.076l-89.075,89.076H503.181z"
                ></path>
                <path
                    style="fill: #0052b4"
                    d="M8.819,322.784c8.83,32.758,23.993,62.913,44.101,89.075l89.074-89.075L8.819,322.784L8.819,322.784   z"
                ></path>
                <path
                    style="fill: #0052b4"
                    d="M411.858,52.921c-26.163-20.109-56.317-35.272-89.076-44.102v133.177L411.858,52.921z"
                ></path>
                <path
                    style="fill: #0052b4"
                    d="M100.142,459.079c26.163,20.109,56.318,35.272,89.076,44.102V370.005L100.142,459.079z"
                ></path>
                <path
                    style="fill: #0052b4"
                    d="M189.217,8.819c-32.758,8.83-62.913,23.993-89.075,44.101l89.075,89.075V8.819z"
                ></path>
                <path
                    style="fill: #0052b4"
                    d="M322.783,503.181c32.758-8.83,62.913-23.993,89.075-44.101l-89.075-89.075V503.181z"
                ></path>
                <path
                    style="fill: #0052b4"
                    d="M370.005,322.784l89.075,89.076c20.108-26.162,35.272-56.318,44.101-89.076H370.005z"
                ></path>
                </g>
                <g>
                <path
                    style="fill: #d80027"
                    d="M509.833,222.609h-220.44h-0.001V2.167C278.461,0.744,267.317,0,256,0   c-11.319,0-22.461,0.744-33.391,2.167v220.44v0.001H2.167C0.744,233.539,0,244.683,0,256c0,11.319,0.744,22.461,2.167,33.391   h220.44h0.001v220.442C233.539,511.256,244.681,512,256,512c11.317,0,22.461-0.743,33.391-2.167v-220.44v-0.001h220.442   C511.256,278.461,512,267.319,512,256C512,244.683,511.256,233.539,509.833,222.609z"
                ></path>
                <path
                    style="fill: #d80027"
                    d="M322.783,322.784L322.783,322.784L437.019,437.02c5.254-5.252,10.266-10.743,15.048-16.435   l-97.802-97.802h-31.482V322.784z"
                ></path>
                <path
                    style="fill: #d80027"
                    d="M189.217,322.784h-0.002L74.98,437.019c5.252,5.254,10.743,10.266,16.435,15.048l97.802-97.804   V322.784z"
                ></path>
                <path
                    style="fill: #d80027"
                    d="M189.217,189.219v-0.002L74.981,74.98c-5.254,5.252-10.266,10.743-15.048,16.435l97.803,97.803   H189.217z"
                ></path>
                <path
                    style="fill: #d80027"
                    d="M322.783,189.219L322.783,189.219L437.02,74.981c-5.252-5.254-10.743-10.266-16.435-15.047   l-97.802,97.803V189.219z"
                ></path>
                </g></svg
            >`,
        lang: "En",
        language: "english",
      },
      {
        icon: `<svg xmlns="http://www.w3.org/2000/svg" style="enable-background: new 0 0 512 512; width: 20px;height: 20px;margin-top:5px" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" width="256" height="256" viewBox="0 0 256 256" xml:space="preserve">
              <defs>
              </defs>
              <g style="stroke: none; stroke-width: 0; stroke-dasharray: none; stroke-linecap: butt; stroke-linejoin: miter; stroke-miterlimit: 10; fill: none; fill-rule: nonzero; opacity: 1;" transform="translate(1.4065934065934016 1.4065934065934016) scale(2.81 2.81)" >
                <path d="M 59.999 2.571 l 0 84.859 c 17.466 -6.175 29.985 -22.818 30 -42.396 v -0.068 C 89.985 25.389 77.465 8.745 59.999 2.571 z" style="stroke: none; stroke-width: 1; stroke-dasharray: none; stroke-linecap: butt; stroke-linejoin: miter; stroke-miterlimit: 10; fill: rgb(243,24,48); fill-rule: nonzero; opacity: 1;" transform=" matrix(1 0 0 1 0 0) " stroke-linecap="round" />
                <path d="M 30 87.429 l 0 -84.858 C 12.524 8.75 0 25.408 0 45 S 12.524 81.25 30 87.429 z" style="stroke: none; stroke-width: 1; stroke-dasharray: none; stroke-linecap: butt; stroke-linejoin: miter; stroke-miterlimit: 10; fill: rgb(0,38,127); fill-rule: nonzero; opacity: 1;" transform=" matrix(1 0 0 1 0 0) " stroke-linecap="round" />
                <path d="M 30 87.429 C 34.693 89.088 39.739 90 45 90 c 5.261 0 10.307 -0.911 15 -2.571 l 0 -84.859 C 55.307 0.911 50.261 0 45 0 c -5.261 0 -10.307 0.912 -15 2.571 L 30 87.429 z" style="stroke: none; stroke-width: 1; stroke-dasharray: none; stroke-linecap: butt; stroke-linejoin: miter; stroke-miterlimit: 10; fill: rgb(243,244,245); fill-rule: nonzero; opacity: 1;" transform=" matrix(1 0 0 1 0 0) " stroke-linecap="round" />
              </g>
              </svg>`,
        lang: "Fr",
        language: "french",
      },
    ]);

    const logout = async () => {
      try {
        await axios.get("/auth/logout");
        window.location.href = "/";
        localStorage.removeItem("href-path");
      } catch (error) {}
    };

    const getUserById = async (userId) => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      axios
        .get(`/users/getUser/${userId}`)
        .then((response) => {
          state.imageURL = response.data.profile.photo_url;
        })
        .catch(() => {});
    };

    return {
      state,
      langs,
      selectedLang,
      logout,
      notifications,
      inAppAlerts,
      inAppUnread,
      notifCount,
      toasts,
      notifPanelOpen,
      notifLoading,
      handleNotifMenuToggle,
      markAllRead,
      dismissToast,
      formatAlertTime,
      alertHref,
      onAlertClick,
    };
  },

  methods: {
    changeLang(lang) {
      location.reload();
      this.$i18n.locale = lang.toLowerCase();
      this.emitter.emit("reload-tabs");
    },
    updateLang(lang) {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      const val = [lang];
      if (val.length) {
        let choosedLang = val[0].lang;
        this.changeLang(choosedLang);
        axios
          .put(`/users/modifyLanguage/${this.state.currentInfo.id}`, {
            language: choosedLang.toLowerCase(),
          })
          .catch(() => {});
      }
    },
  },
};
</script>

<style scoped>
.userInfo {
  display: flex;
  flex-direction: column;
  margin-right: 10px;
  margin-left: 10px;
}

.white-color {
  color: white;
}

.v-toolbar {
  background-color: #193286;
  color: white;
  font-size: 18.16px;
  font-family: Nunito;
  font-weight: 400;
  word-wrap: break-word;
}

/* ── Bell button ─────────────────────────────────────────────────────────── */
.notif-bell-wrap {
  margin-right: 6px;
  position: relative;
}

.notif-bell-btn {
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  color: rgba(255,255,255,0.85);
  cursor: pointer;
  display: flex;
  height: 38px;
  justify-content: center;
  position: relative;
  transition: background 0.18s, border-color 0.18s, color 0.18s, transform 0.15s;
  width: 38px;
}

.notif-bell-btn:hover {
  background: rgba(255, 255, 255, 0.18);
  border-color: rgba(255, 255, 255, 0.3);
  color: #fff;
  transform: translateY(-1px);
}

.notif-bell-btn--active {
  background: rgba(229, 57, 53, 0.15);
  border-color: rgba(229, 57, 53, 0.4);
  color: #fff;
}

.notif-bell-btn--open {
  background: rgba(255, 255, 255, 0.22);
  border-color: rgba(255, 255, 255, 0.4);
  color: #fff;
  transform: translateY(-1px);
}

.notif-bell-icon {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notif-ring {
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  border: 1.5px solid rgba(239, 83, 80, 0.5);
  animation: notif-ring-pulse 2.4s ease-in-out infinite;
  pointer-events: none;
}

@keyframes notif-ring-pulse {
  0%, 100% { opacity: 0.6; transform: scale(1); }
  50%       { opacity: 0;   transform: scale(1.35); }
}

.notif-badge {
  align-items: center;
  background: #ef5350;
  border: 2px solid #193286;
  border-radius: 99px;
  color: #fff;
  display: flex;
  font-size: 9px;
  font-weight: 800;
  height: 17px;
  justify-content: center;
  letter-spacing: 0.2px;
  min-width: 17px;
  padding: 0 3px;
  position: absolute;
  right: -5px;
  top: -5px;
  box-shadow: 0 1px 4px rgba(239,83,80,0.4);
}

/* ── Dropdown panel ───────────────────────────────────────────────────────── */
.notif-panel {
  background: #fff;
  border: 1px solid #e3ebf4;
  border-radius: 14px;
  box-shadow: 0 8px 32px rgba(17, 32, 51, 0.14);
  min-width: 340px;
  overflow: hidden;
}

.notif-panel-head {
  align-items: center;
  border-bottom: 1px solid #eef2f6;
  display: flex;
  gap: 10px;
  justify-content: space-between;
  padding: 14px 16px 12px;
}

.notif-panel-head-left {
  align-items: center;
  display: flex;
  gap: 8px;
}

.notif-panel-head strong {
  color: #112033;
  font-size: 14px;
  font-weight: 700;
}

.notif-panel-count {
  border-radius: 99px;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 9px;
}

.notif-panel-count.has-alerts { background: rgba(229, 57, 53, 0.1); color: #c23b32; }
.notif-panel-count.no-alerts  { background: rgba(7, 132, 91, 0.1);  color: #07845b; }

.notif-mark-read-btn {
  background: none;
  border: 1px solid #cdd6e0;
  border-radius: 6px;
  color: #193286;
  cursor: pointer;
  font-size: 10px;
  font-weight: 600;
  padding: 3px 9px;
  transition: background 0.15s, border-color 0.15s;
  white-space: nowrap;
}

.notif-mark-read-btn:hover {
  background: #f0f4ff;
  border-color: #193286;
}

.notif-panel-loading {
  align-items: center;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 28px 16px;
}

.notif-spinner {
  animation: spin 0.8s linear infinite;
  border: 2px solid #e3ebf4;
  border-radius: 50%;
  border-top-color: #193286;
  height: 20px;
  width: 20px;
}

@keyframes spin { to { transform: rotate(360deg); } }

.notif-panel-empty {
  align-items: center;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 28px 16px;
  text-align: center;
}

.notif-panel-empty strong { color: #3c4e62; font-size: 13px; }
.notif-panel-empty span   { color: #9aabb8; font-size: 12px; }

.notif-list {
  max-height: 360px;
  overflow-y: auto;
  padding: 6px 0;
}

.notif-section-label {
  align-items: center;
  color: #8a9ab0;
  display: flex;
  font-size: 10px;
  font-weight: 700;
  gap: 5px;
  letter-spacing: 0.5px;
  padding: 8px 16px 4px;
  text-transform: uppercase;
}

.notif-separator {
  border-top: 1px solid #eef2f6;
  margin: 6px 0;
}

.notif-item {
  align-items: flex-start;
  border-left: 3px solid transparent;
  display: flex;
  gap: 10px;
  padding: 10px 16px;
  transition: background 0.1s;
}

.notif-item:hover { background: #f8fafc; }
.notif-item--critical { border-left-color: #c23b32; }
.notif-item--warning  { border-left-color: #c78311; }

/* Clickable variant (in-app alerts) */
.notif-item--link {
  color: inherit;
  cursor: pointer;
  text-decoration: none;
}
.notif-item--link:hover { background: #f1f5fb; }
.notif-item--link:focus-visible { outline: 2px solid #193286; outline-offset: -2px; }

.notif-dot {
  border-radius: 50%;
  flex-shrink: 0;
  height: 8px;
  margin-top: 4px;
  width: 8px;
}

.notif-dot.critical { background: #c23b32; box-shadow: 0 0 0 3px rgba(194,59,50,0.15); }
.notif-dot.warning  { background: #c78311; box-shadow: 0 0 0 3px rgba(199,131,17,0.15); }

.notif-item-body {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.notif-item-body strong {
  color: #1a2e42;
  font-size: 12px;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.notif-item-body span {
  color: #4a5a6b;
  font-size: 11px;
  line-height: 1.4;
}

.notif-item-body small {
  color: #9aabb8;
  font-size: 10px;
}

.notif-severity {
  border-radius: 99px;
  font-size: 10px;
  font-weight: 700;
  flex-shrink: 0;
  padding: 2px 7px;
}

.notif-severity.critical { background: rgba(194,59,50,0.1); color: #c23b32; }
.notif-severity.warning  { background: rgba(199,131,17,0.1); color: #c78311; }

.notif-more {
  color: #9aabb8;
  font-size: 11px;
  padding: 8px 16px 4px;
  text-align: center;
}

.notif-panel-footer {
  align-items: center;
  border-top: 1px solid #eef2f6;
  color: #193286;
  display: flex;
  font-size: 12px;
  font-weight: 600;
  gap: 5px;
  justify-content: center;
  padding: 12px 16px;
  text-decoration: none;
  transition: background 0.1s;
}

.notif-panel-footer:hover { background: #f4f7fb; border-radius: 0 0 14px 14px; }
</style>

<!-- Toast styles are NOT scoped so they work inside <Teleport to="body"> -->
<style>
.notif-toast-stack {
  bottom: auto;
  left: auto;
  pointer-events: none;
  position: fixed;
  right: 20px;
  top: 72px;
  z-index: 9999;
}

.notif-toast-inner {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.notif-toast {
  align-items: flex-start;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 6px 24px rgba(17, 32, 51, 0.16), 0 1px 4px rgba(17,32,51,0.08);
  display: flex;
  gap: 10px;
  max-width: 340px;
  min-width: 280px;
  padding: 12px 14px;
  pointer-events: all;
  border-left: 4px solid #c78311;
}

.notif-toast--critical { border-left-color: #c23b32; }
.notif-toast--warning  { border-left-color: #c78311; }

.notif-toast-icon {
  flex-shrink: 0;
  margin-top: 1px;
}

.notif-toast--critical .notif-toast-icon { color: #c23b32; }
.notif-toast--warning  .notif-toast-icon { color: #c78311; }

.notif-toast-body {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.notif-toast-body strong {
  color: #1a2e42;
  font-size: 12px;
  font-weight: 700;
}

.notif-toast-body span {
  color: #4a5a6b;
  font-size: 11px;
  line-height: 1.4;
}

.notif-toast-close {
  background: none;
  border: none;
  color: #9aabb8;
  cursor: pointer;
  flex-shrink: 0;
  padding: 0;
  transition: color 0.15s;
}

.notif-toast-close:hover { color: #4a5a6b; }

/* Transition animations */
.notif-toast-enter-active { transition: all 0.28s cubic-bezier(0.34, 1.56, 0.64, 1); }
.notif-toast-leave-active  { transition: all 0.2s ease-in; }
.notif-toast-enter-from    { opacity: 0; transform: translateX(60px) scale(0.92); }
.notif-toast-leave-to      { opacity: 0; transform: translateX(60px) scale(0.92); }
.notif-toast-move          { transition: transform 0.25s ease; }
</style>
