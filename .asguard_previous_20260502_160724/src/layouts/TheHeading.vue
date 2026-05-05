<template>
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
        offset="8"
        @update:model-value="handleNotifMenuToggle"
      >
        <template v-slot:activator="{ props }">
          <div class="notif-bell-wrap">
            <button class="notif-bell-btn" type="button" v-bind="props">
              <svg viewBox="0 0 22 22" fill="none" width="20" height="20">
                <path d="M11 2a6 6 0 0 1 6 6v4l1.5 2.5H3.5L5 12V8a6 6 0 0 1 6-6z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
                <path d="M9 18a2 2 0 0 0 4 0" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
              </svg>
              <span v-if="notifCount > 0" class="notif-badge">{{ notifCount > 99 ? '99+' : notifCount }}</span>
            </button>
          </div>
        </template>

        <div class="notif-panel">
          <div class="notif-panel-head">
            <strong>Alertes actives</strong>
            <span :class="['notif-panel-count', notifCount > 0 ? 'has-alerts' : 'no-alerts']">
              {{ notifCount > 0 ? `${notifCount} non résolue${notifCount > 1 ? 's' : ''}` : 'Tout est calme' }}
            </span>
          </div>

          <div v-if="notifLoading" class="notif-panel-loading">
            <div class="notif-spinner"></div>
            <span>Chargement...</span>
          </div>

          <div v-else-if="notifications.length === 0" class="notif-panel-empty">
            <svg viewBox="0 0 32 32" fill="none" width="28" height="28"><path d="M16 3l13 23H3L16 3z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round" opacity=".2"/><path d="M10 10l12 12M22 10L10 22" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" opacity=".2"/></svg>
            <strong>Aucune alerte</strong>
            <span>Tout fonctionne correctement.</span>
          </div>

          <div v-else class="notif-list">
            <div
              v-for="(alert, i) in notifications.slice(0, 8)"
              :key="i"
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
            <div v-if="notifications.length > 8" class="notif-more">
              + {{ notifications.length - 8 }} alerte{{ notifications.length - 8 > 1 ? 's' : '' }} supplémentaire{{ notifications.length - 8 > 1 ? 's' : '' }}
            </div>
          </div>

          <a href="/backup/" class="notif-panel-footer">
            Voir le tableau de bord backup
            <svg viewBox="0 0 12 12" fill="none" width="10" height="10"><path d="M2 6h8M7 3l3 3-3 3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>
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
          <!-- <v-avatar class="ml-3 mr-3" size="30" v-bind="props">
            <v-icon size="30" class="white--text" color="white">mdi-account-circle-outline</v-icon>
          </v-avatar> -->
        </template>
        <v-list style="cursor: pointer; padding: 15px">
          <a :href="'/profile'" style="text-decoration: none; color: black">
            <v-list-item>
              {{ $t("header.profile") }}
            </v-list-item>
          </a>

          <!-- <v-list-item> {{ $t("subtitle.settings") }} </v-list-item> -->

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
import { onBeforeUnmount, onMounted, reactive, ref } from "vue";
import { get_lang } from "@/mixins/storage_language.js";
import { useI18n } from "vue-i18n";

export default {
  name: "ToolbarComponent",
  inject: ["emitter"],

  setup() {
    const { t } = useI18n();

    const notifications = ref([]);
    const notifCount = ref(0);
    const notifPanelOpen = ref(false);
    const notifLoading = ref(false);
    let notifInterval = null;

    const fetchNotifications = async () => {
      try {
        notifLoading.value = true;
        const res = await axios.get("/backup/dashboard-overview", { params: { skip_sync_scan: true } });
        const alerts = res.data?.alerts || [];
        notifications.value = alerts;
        notifCount.value = alerts.length;
      } catch (_) {
        // silently fail — endpoint may not be available on all pages
      } finally {
        notifLoading.value = false;
      }
    };

    const handleNotifMenuToggle = (isOpen) => {
      notifPanelOpen.value = isOpen;
      if (isOpen) {
        fetchNotifications();
      }
    };

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

      fetchNotifications();
      notifInterval = setInterval(fetchNotifications, 60000);
    });

    onBeforeUnmount(() => {
      if (notifInterval) {
        clearInterval(notifInterval);
      }
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
      } catch (error) {
      }
    };
    const getUserById = async (userId) => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios
        .get(`/users/getUser/${userId}`)
        .then((response) => {
          state.imageURL = response.data.profile.photo_url;
        })
        .catch((e) => {});
    };

    return {
      state,
      langs,
      selectedLang,
      logout,
      notifications,
      notifCount,
      notifPanelOpen,
      notifLoading,
      handleNotifMenuToggle,
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

        let payload = {
          language: choosedLang.toLowerCase(),
        };

        axios
          .put(`/users/modifyLanguage/${this.state.currentInfo.id}`, payload)
          .then((response) => {})
          .catch((i) => {});
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

.notif-bell-wrap {
  margin-right: 4px;
  position: relative;
}

.notif-bell-btn {
  align-items: center;
  background: rgba(255, 255, 255, 0.12);
  border: none;
  border-radius: 50%;
  color: #fff;
  cursor: pointer;
  display: flex;
  height: 36px;
  justify-content: center;
  position: relative;
  transition: background 0.15s;
  width: 36px;
}

.notif-bell-btn:hover {
  background: rgba(255, 255, 255, 0.22);
}

.notif-badge {
  align-items: center;
  background: #e53935;
  border: 2px solid #193286;
  border-radius: 99px;
  color: #fff;
  display: flex;
  font-size: 9px;
  font-weight: 700;
  height: 16px;
  justify-content: center;
  min-width: 16px;
  padding: 0 3px;
  position: absolute;
  right: -2px;
  top: -2px;
}

/* ── Dropdown panel ── */
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
  max-height: 320px;
  overflow-y: auto;
  padding: 6px 0;
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
