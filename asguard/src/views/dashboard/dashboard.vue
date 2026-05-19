<template>
  <v-app id="inspire">
    <base-layout :title="t('sideBar.dashboard')" active-menu="home">
      <template #content>
        <helpModal help="Dashboard" />
        <div class="mr-3">
          <v-overlay v-model="state.loading">
            <v-dialog
              v-model="state.isLoadingDialogue"
              :scrim="false"
              persistent
              width="auto"
            >
              <v-card color="#193286">
                <v-card-text>
                  {{ $t("requiredfield.attente") }}
                  <v-progress-linear
                    indeterminate
                    color="white"
                    class="mb-0"
                  ></v-progress-linear>
                </v-card-text>
              </v-card>
            </v-dialog>
          </v-overlay>
          <v-overlay v-model="state.viewModal">
            <v-dialog v-model="state.isviewModal" :scrim="false" width="auto">
              <v-card color="#193286" class="alert-box">
                <v-card-title class="img-containter">
                  <img
                    src="@/assets/images/view.png"
                    alt="logo"
                    class="img-view"
                    width="100"
                    height="100"
                /></v-card-title>
                <v-card-text>
                  {{ $t("profil.NoPermission") }}
                  <br />
                  {{ $t("profil.ContactAdmin") }}
                </v-card-text>

                <div class="mr-3 mb-5 d-flex justify-end">
                  <VButton
                    rounded
                    outlined
                    color="#ffffff"
                    label-color="#213E9F"
                    :label="$t('buttons.close')"
                    :isLarge="true"
                    @click="close"
                  />
                </div>
              </v-card>
            </v-dialog>
          </v-overlay>
          <div
            class="certificats-management mt-6 ml-5"
            style="display: flex; flex-direction: column"
          >
            <h4>{{ t("home.systemInformation") }}</h4>
            <v-divider></v-divider>

            <ag-grid-vue
              id="grid-wrapper"
              domLayout="autoHeight"
              class="ag-theme-alpine mt-3"
              :columnDefs="columns"
              :alwaysShowHorizontalScroll="false"
              :alwaysShowVarticalScroll="false"
              :defaultColDef="defaultColDef"
              :rowData="rowData.value"
              :overlayNoRowsTemplate="overlayTemplate"
              style="width: 100%; height: 100%"
              @grid-ready="onGridReadyInfo"
            />
          </div>
          <div id="chart" class="mt-3 mr-2">
            <apexchart
              ref="apexChart"
              height="350"
              :options="state.chartOptions"
              :series="state.chartOptions.series"
            ></apexchart>
          </div>

          <!-- ── Watchdog Panel ────────────────────────────────── -->
          <div class="wd-panel mt-6 ml-2 mr-2">
            <div class="wd-header">
              <div class="wd-header-left">
                <span class="wd-icon">🛡</span>
                <span class="wd-title">Watchdog Asguard</span>
                <span :class="['wd-daemon-badge', watchdog.daemonActive ? 'wd-badge-ok' : 'wd-badge-off']">
                  {{ watchdog.daemonActive ? '● Actif' : '○ Inactif' }}
                </span>
              </div>
              <div class="wd-header-right">
                <button class="wd-btn-sm" @click="toggleWatchdogDaemon">
                  {{ watchdog.daemonActive ? 'Arrêter' : 'Démarrer' }}
                </button>
                <button class="wd-btn-sm wd-btn-cfg" @click="watchdog.showConfig = !watchdog.showConfig">
                  ⚙ Config alertes
                </button>
              </div>
            </div>

            <!-- services grid -->
            <div class="wd-services-grid">
              <div v-for="svc in watchdog.services" :key="svc.name"
                   :class="['wd-svc-card', svc.active ? 'wd-svc-ok' : 'wd-svc-down']">
                <div class="wd-svc-top">
                  <span :class="['wd-dot', svc.active ? 'wd-dot-ok' : 'wd-dot-down']"></span>
                  <span class="wd-svc-name">{{ svc.display }}</span>
                  <span v-if="svc.critical" class="wd-critical-tag">CRITIQUE</span>
                </div>
                <div class="wd-svc-bottom">
                  <span class="wd-svc-status">{{ svc.active ? 'Opérationnel' : '⚠ Hors service' }}</span>
                  <span class="wd-restart-count" v-if="svc.restart_count > 0">
                    ↺ {{ svc.restart_count }} redémarrage{{ svc.restart_count > 1 ? 's' : '' }}
                  </span>
                </div>
              </div>
            </div>

            <!-- email config (collapsible) -->
            <div v-if="watchdog.showConfig" class="wd-config-block">
              <div class="wd-config-row">
                <label class="wd-cfg-label">Alertes email</label>
                <label class="wd-toggle">
                  <input type="checkbox" v-model="watchdog.notif.email_enabled" />
                  <span class="wd-toggle-slider"></span>
                </label>
              </div>
              <div v-if="watchdog.notif.email_enabled" class="wd-config-fields">
                <div class="wd-sender-row">
                  <div class="wd-sender-field">
                    <label class="wd-field-label">Nom expéditeur</label>
                    <input class="wd-input" v-model="watchdog.notif.sender_name"
                           placeholder="Asguard Watchdog" />
                  </div>
                  <div class="wd-sender-field">
                    <label class="wd-field-label">Email expéditeur (bot)</label>
                    <input class="wd-input" v-model="watchdog.notif.sender_email"
                           placeholder="noreply@asguard.com" />
                  </div>
                </div>
                <div>
                  <label class="wd-field-label">Destinataires</label>
                  <input class="wd-input" v-model="watchdog.notif.recipients_str"
                         placeholder="email1@domaine.com, email2@domaine.com" />
                </div>
                <div class="wd-config-row">
                  <label class="wd-cfg-label">Alerte en cas de panne</label>
                  <label class="wd-toggle">
                    <input type="checkbox" v-model="watchdog.notif.alert_on_failure" />
                    <span class="wd-toggle-slider"></span>
                  </label>
                </div>
                <div class="wd-config-row">
                  <label class="wd-cfg-label">Alerte à la reprise</label>
                  <label class="wd-toggle">
                    <input type="checkbox" v-model="watchdog.notif.alert_on_recovery" />
                    <span class="wd-toggle-slider"></span>
                  </label>
                </div>
              </div>
              <button class="wd-btn-save" @click="saveWatchdogConfig">Enregistrer</button>
            </div>

            <!-- recent incidents -->
            <div class="wd-incidents" v-if="watchdog.incidents.length > 0">
              <div class="wd-incidents-title">Incidents récents</div>
              <div v-for="inc in watchdog.incidents" :key="inc.ts" class="wd-inc-row">
                <span :class="['wd-inc-dot', inc.event === 'RECOVERED' ? 'wd-dot-ok' : 'wd-dot-down']"></span>
                <span class="wd-inc-time">{{ formatIncidentTime(inc.ts) }}</span>
                <span class="wd-inc-msg">
                  <b>{{ inc.display }}</b>
                  {{ inc.event === 'FAILED'
                    ? (inc.recovered ? '— panne → redémarré ✓' : '— panne → redémarrage échoué ✗')
                    : '— service rétabli' }}
                </span>
              </div>
            </div>
            <div v-else-if="!watchdog.loading" class="wd-no-incidents">
              Aucun incident enregistré — tout fonctionne normalement.
            </div>
          </div>
          <!-- ── Fin Watchdog Panel ─────────────────────────────── -->

          <div style="margin-bottom: 150px">
            <v-row class="mt-6 ml-2">
              <v-col cols="12">
                Services
                <v-divider></v-divider>

                <ag-grid-vue
                  id="grid-wrapper"
                  domLayout="autoHeight"
                  class="ag-theme-alpine mt-3"
                  :columnDefs="columnsService"
                  :defaultColDef="defaultColDef"
                  :alwaysShowHorizontalScroll="false"
                  :alwaysShowVerticalScroll="false"
                  :rowData="rowDataServices.value"
                  :overlayNoRowsTemplate="overlayTemplate"
                  style="width: 100%; height: 100%"
                  @grid-ready="onGridReady"
                />
              </v-col>
            </v-row>
            <v-row class="mt-6 ml-2">
              <v-col cols="6">
                Interfaces
                <v-divider></v-divider>

                <ag-grid-vue
                  id="grid-wrapper"
                  domLayout="autoHeight"
                  class="ag-theme-alpine mt-3"
                  :columnDefs="columnInterfaces"
                  :defaultColDef="defaultColDef"
                  :rowData="rowDataInterfaces.value"
                  @grid-ready="onGridReady"
                  :alwaysShowHorizontalScroll="false"
                  :alwaysShowVerticalScroll="false"
                  :overlayNoRowsTemplate="overlayTemplate"
                  style="width: 100%; height: 100%"
                />
              </v-col>
              <v-col cols="6">
                Gateways
                <v-divider></v-divider>

                <ag-grid-vue
                  id="grid-wrapper"
                  domLayout="autoHeight"
                  class="ag-theme-alpine mt-3"
                  :columnDefs="columnGateways"
                  :defaultColDef="defaultColDef"
                  :rowData="rowDataGateways.value"
                  @grid-ready="onGridReady"
                  :alwaysShowHorizontalScroll="false"
                  :alwaysShowVerticalScroll="false"
                  :overlayNoRowsTemplate="overlayTemplate"
                  style="width: 100%; height: 100%"
                />
              </v-col>
              <v-snackbar
                :timeout="2000"
                v-model="state.snackbar"
                location="bottom right"
                :color="state.color"
              >
                {{ state.textAlert }}
              </v-snackbar>
            </v-row>
          </div>
        </div>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import axios from "axios";
import { getCookie } from "@/mixins/csrftoken.js";
import { useI18n } from "vue-i18n";
import { reactive, ref, onMounted, computed } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import VueApexCharts from "vue3-apexcharts";
import BaseLayout from "../../layouts/layout.vue";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import { user_privilege } from "@/mixins/user_privilege.js";
import VButton from "@/components/VButton.vue";
import helpModal from "@/components/modals/help.vue";
import { checkFunctionality } from "@/mixins/checkFunctionality.js";

export default {
  name: "HomeComponent",
  components: {
    BaseLayout,
    AgGridVue,
    apexchart: VueApexCharts,
    VButton,
    helpModal,
  },

  setup() {
    const { t } = useI18n();
    const overlayTemplate = ref("");
    const paginationLocalization = reactive({
      of: "/",
    });
    const state = reactive({
      isviewModal: false,
      viewModal: false,
      snackbar: false,
      color: "",
      textAlert: "",
      isLoadingDialogue: false,
      loading: false,
      information: null,
      infoParser: null,
      socket: null,
      dataChart: null,
      chartOptions: {
        chart: {
          type: "area",
          zoom: {
            enabled: false,
          },
        },
        yaxis: {
          min: 0,
          max: 100,
          labels: {
            formatter: function (value) {
              return value.toFixed(0) + "%";
            },
          },
          // title: {
          //   text: "Percentage (%)",
          // },
        },
        xaxis: {
          type: "datetime",
        },

        series: [
          {
            name: "",
            data: [],
          },
          {
            name: "",
            data: [],
          },
        ],
      },
    });
    const name = computed(() => {
      return t("agGrid.name");
    });
    const cpuType = computed(() => {
      return t("agGrid.cpuType");
    });
    const systemLoad = computed(() => {
      return t("agGrid.systemLoad");
    });
    const lConfChange = computed(() => {
      return t("agGrid.lConfChange");
    });
    const operatingTime = computed(() => {
      return t("agGrid.operatingTime");
    });
    const speed = computed(() => {
      return t("agGrid.speedUplex");
    });
    const address = computed(() => {
      return t("agGrid.address");
    });
    const status = computed(() => {
      return t("agGrid.status");
    });
    const NoRow = computed(() => {
      return t("agGrid.noRowsToShow");
    });

    const columns = ref([
      { headerName: name, field: "nom", width: 90, minWidth: 50, flex: 1 },
      {
        headerName: "Version",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
        cellRenderer: actionCellRenderer,
      },
      {
        headerName: cpuType,
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
        cellRenderer: actionCpuType,
      },
      {
        headerName: systemLoad,
        field: "system_load",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: lConfChange,
        field: "last_cong",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: operatingTime,
        field: "operating",
        editable: false,
        sortable: false,
        filter: false,
        width: 250,
      },
    ]);
    const columnsService = ref([
      {
        headerName: "Service",
        field: "service",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Description",
        field: "description",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Actions",
        width: 150,
        lockPosition: "right",
        cellClass: "locked-col",
        cellRenderer: actionCellRendererService,
      },
    ]);
    const columnInterfaces = ref([
      {
        headerName: name,
        field: "name_interface",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: speed,
        field: "speed_duplex",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: address,
        field: "ip_address",
        width: 150,
        minWidth: 50,
      },
    ]);
    const columnGateways = ref([
      { headerName: name, field: "name", width: 90, minWidth: 50, flex: 1 },
      {
        headerName: address,
        field: "address",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      { headerName: status, field: "status", width: 150, minWidth: 50 },
    ]);
    // ── Watchdog state ────────────────────────────────────────────────────────
    const watchdog = reactive({
      loading: false,
      daemonActive: false,
      enabled: true,
      services: [],
      incidents: [],
      showConfig: false,
      notif: {
        email_enabled: false,
        alert_on_failure: true,
        alert_on_recovery: true,
        recipients_str: "",
        sender_name: "Asguard Watchdog",
        sender_email: "noreply@asguard.com",
      },
    });

    const fetchWatchdogStatus = () => {
      watchdog.loading = true;
      axios.get("/monitoring/watchdog")
        .then((res) => {
          watchdog.daemonActive = res.data.daemon_active;
          watchdog.enabled      = res.data.enabled;
          watchdog.services     = res.data.services || [];
          watchdog.incidents    = res.data.recent_incidents || [];
          const notif = res.data.notifications || {};
          watchdog.notif.email_enabled      = !!notif.email_enabled;
          watchdog.notif.alert_on_failure   = notif.alert_on_failure !== false;
          watchdog.notif.alert_on_recovery  = notif.alert_on_recovery !== false;
          watchdog.notif.recipients_str     = (notif.recipients || []).join(", ");
          watchdog.notif.sender_name        = notif.sender_name  || "Asguard Watchdog";
          watchdog.notif.sender_email       = notif.sender_email || "noreply@asguard.com";
        })
        .catch(() => {})
        .finally(() => { watchdog.loading = false; });
    };

    const saveWatchdogConfig = () => {
      const recipients = watchdog.notif.recipients_str
        .split(",").map((s) => s.trim()).filter(Boolean);
      axios.put("/monitoring/watchdog/config", {
        notifications: {
          email_enabled:    watchdog.notif.email_enabled,
          alert_on_failure: watchdog.notif.alert_on_failure,
          alert_on_recovery: watchdog.notif.alert_on_recovery,
          recipients,
          sender_name:  watchdog.notif.sender_name,
          sender_email: watchdog.notif.sender_email,
        },
      }).then(() => {
        state.snackbar   = true;
        state.color      = "success";
        state.textAlert  = "Configuration watchdog enregistrée";
        watchdog.showConfig = false;
      }).catch(() => {
        state.snackbar  = true;
        state.color     = "red";
        state.textAlert = "Erreur lors de la sauvegarde";
      });
    };

    const toggleWatchdogDaemon = () => {
      const action = watchdog.daemonActive ? "stop" : "start";
      axios.post("/monitoring/watchdog/daemon", { action })
        .then((res) => {
          watchdog.daemonActive = res.data.active;
          state.snackbar  = true;
          state.color     = "success";
          state.textAlert = res.data.msg;
        })
        .catch(() => {
          state.snackbar  = true;
          state.color     = "red";
          state.textAlert = "Erreur watchdog daemon";
        });
    };

    const formatIncidentTime = (ts) => {
      if (!ts) return "";
      try {
        const d = new Date(ts);
        return d.toLocaleString("fr-FR", { day: "2-digit", month: "2-digit",
          year: "numeric", hour: "2-digit", minute: "2-digit" });
      } catch { return ts; }
    };
    // ─────────────────────────────────────────────────────────────────────────

    const gridApi = ref(null);

    const rowData = reactive([]);
    const rowDataServices = reactive([]);
    const rowDataInterfaces = reactive([]);
    const rowDataGateways = reactive([]);

    const gridOptions = ref({
      pagination: true,
      paginationPageSize: 5,
      rowSelection: "single",
    });

    function actionCellRenderer() {
      let eGui = document.createElement("div");

      eGui.innerHTML = `Asguard V${state.infoParser.version_asguard}<br/> System V${state.infoParser.system_version}
          <br/>${state.infoParser.version_openssl}
          `;
      eGui.style.lineHeight = "2";

      return eGui;
    }
    const apexChart = ref(null);
    function actionCpuType() {
      const longString = state.infoParser.cpu_type;
      const chunks = longString.match(/.{1,20}/g);

      const resultWithBr = chunks.map((chunk) => chunk + "<br>").join("");

      let eGui = document.createElement("div");

      eGui.innerHTML = `${resultWithBr}
        `;
      eGui.style.lineHeight = "2";
      return eGui;
    }
    function actionCellRendererService(params) {
      let eGui = document.createElement("div");

      if (params.data.status_started) {
        eGui.innerHTML = `
         <button class="action-button stop" data-action="stop">
            <span class="mdi mdi-stop-circle fa-2x" style="color: red"></span>
          </button>
          <button class="action-button restart" data-action="restart">
            <span class="mdi mdi-reload fa-2x"></span>
          </button>

        `;
      } else if (!params.data.status_started) {
        eGui.innerHTML = `
          <button class="action-button start" data-action="start">
            <span class="mdi mdi-play-circle fa-2x" style="color: green"></span>
          </button>
          <button class="action-button restart" data-action="restart">
            <span class="mdi mdi-reload fa-2x"></span>
          </button>

        `;
      }

      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          handleActionServer(action, params.node.data);
        });
      });

      return eGui;
    }
    const handleActionServer = (action, rowData, index) => {
      const user = user_privilege();
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      switch (action) {
        case "start":
          if (user === "viewer") {
            state.isviewModal = true;
            state.viewModal = true;
          } else {
            state.loading = true;
            state.isLoadingDialogue = true;
            let payloadStart = {
              action: "start",
              service: rowData.service,
            };

            axios
              .put("/monitoring/action", payloadStart)
              .then((response) => {
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.msg;
                state.loading = false;
                state.isLoadingDialogue = false;

                setTimeout(() => {
                  location.reload();
                }, 1000);
              })
              .catch((i) => {
                state.loading = false;
                state.isLoadingDialogue = false;

                if (i.response.status === 500) {
                  state.snackbar = true;
                  state.color = "red";
                  state.textAlert = t("errors.errorServer");
                } else {
                  state.snackbar = true;
                  state.color = "red";
                  state.textAlert = i.response.data.msg;
                }
              });
          }

          break;
        case "restart":
          if (user === "viewer") {
            state.isviewModal = true;
            state.viewModal = true;
          } else {
            state.loading = true;
            state.isLoadingDialogue = true;
            let payloadRestart = {
              action: "restart",
              service: rowData.service,
            };
            axios
              .put("/monitoring/action", payloadRestart)
              .then((response) => {
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.msg;
                state.loading = false;
                state.isLoadingDialogue = false;
                setTimeout(() => {
                  location.reload();
                }, 1000);
              })
              .catch((i) => {
                state.loading = false;
                state.isLoadingDialogue = false;

                if (i.response.status === 500) {
                  state.snackbar = true;
                  state.color = "red";
                  state.textAlert = t("errors.errorServer");
                } else {
                  state.snackbar = true;
                  state.color = "red";
                  state.textAlert = i.response.data.msg;
                }
              });
          }
          break;
        case "stop":
          if (user === "viewer") {
            state.isviewModal = true;
            state.viewModal = true;
          } else {
            state.loading = true;
            state.isLoadingDialogue = true;

            let payloadStop = {
              action: "stop",
              service: rowData.service,
            };
            axios
              .put("/monitoring/action", payloadStop)
              .then((response) => {
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.msg;
                state.loading = false;
                state.isLoadingDialogue = false;

                setTimeout(() => {
                  location.reload();
                }, 1000);
              })
              .catch((i) => {
                state.loading = false;
                state.isLoadingDialogue = false;

                if (i.response.status === 500) {
                  state.snackbar = true;
                  state.color = "red";
                  state.textAlert = t("errors.errorServer");
                } else {
                  state.snackbar = true;
                  state.color = "red";
                  state.textAlert = i.response.data.msg;
                }
              });
          }
          break;

        default:
          break;
      }
    };

    const close = () => {
      state.isviewModal = false;
      state.viewModal = false;
    };
    const onGridReady = (params) => {
      gridApi.value = params.api;
    };
    const onGridReadyInfo = (params) => {
      gridApi.value = params.api;
      if (gridApi.value) {
        gridApi.value.setRowData(rowData.value);
      } else {
      }
    };
    const defaultColDef = {
      // flex: 2,
    };

    const initializeWebSocket = () => {
      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      state.socket = new WebSocket(
        protocol + "://" + window.location.host + "/ws/data/"
      );

      state.socket.onopen = () => {
      };

      state.socket.onmessage = (event) => {
        if (state.socket.readyState === WebSocket.OPEN) {
          const data = JSON.parse(event.data);
          state.dataChart = data;

          const currentDate = new Date();
          const currentTime = currentDate.toLocaleTimeString();
          rowData.value = [
            {
              nom: "Asguard",
              system_load: data.load_average || data.uptime,
              last_cong: currentTime,
              operating: data.current_date,
            },
          ];

          const timestamp = new Date(data.timestamp * 1000).getTime();

          state.chartOptions.series[0].name = t("home.cpuPercentage");
          state.chartOptions.series[1].name = t("home.memoryPercentage");

          state.chartOptions.series[0].data.push([
            timestamp,
            data.cpu_percentage.toFixed(2),
          ]);
          state.chartOptions.series[1].data.push([
            timestamp,
            data.memory_percentage.toFixed(2),
          ]);

          const maxDataPoints = 10;
          if (state.chartOptions.series[0].data.length > maxDataPoints) {
            state.chartOptions.series[0].data.shift();
            state.chartOptions.series[1].data.shift();
          }

          apexChart.value.updateOptions({});
        } else {
          
        }
      };

      state.socket.onclose = () => {
      };
    };

    onMounted(async () => {
      checkFunctionality();
      fetchWatchdogStatus();
      setInterval(fetchWatchdogStatus, 30000);

      const lastSubscription =
        document.getElementById("app").attributes["last_subscription"].value;
      localStorage.setItem("lastSubscription", lastSubscription);

      overlayTemplate.value = `<span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
    </svg></span>`;
      let infoData =
        document.getElementById("app").attributes["informations"].value;
      let gateways =
        document.getElementById("app").attributes["gateways"].value;
      let interfaces =
        document.getElementById("app").attributes["interfaces"].value;

      initializeWebSocket();
      let information = infoData;
      const info = JSON.parse(information);

      state.infoParser = info;

      let infoService = info.list_info_services.map((i) => {
        const element = JSON.parse(i);
        return {
          service: element.service_name,
          description: element.description,
          status_enabled: element.status_enabled,
          status_started: element.status_started,
          status_install: element.status_install,
        };
      });
      rowDataServices.value = infoService;

      const element = JSON.parse(gateways);

      let infoGateways = element.map((i) => {
        return {
          name: i?.gwname,
          address: i?.gwaddress,
          status: i?.gwstatus ?? "Online",
        };
      });
      rowDataGateways.value = infoGateways;
      let parsedArray = JSON.parse(interfaces);
      rowDataInterfaces.value = parsedArray;
    });

    return {
      t,
      overlayTemplate,
      NoRow,
      state,
      close,
      columns,
      rowData,
      defaultColDef,
      columnsService,
      rowDataInterfaces,
      rowDataGateways,
      rowDataServices,
      columnGateways,
      actionCpuType,
      gridApi,
      paginationLocalization,
      apexChart,
      gridOptions,
      actionCellRenderer,
      onGridReady,
      onGridReadyInfo,
      columnInterfaces,
      initializeWebSocket,
      actionCellRendererService,
      watchdog,
      fetchWatchdogStatus,
      saveWatchdogConfig,
      toggleWatchdogDaemon,
      formatIncidentTime,
    };
  },
};
</script>
<style>
/* .alert-box {
  margin-top: 20px;
  padding: 20px;
  background-color: #e3f2fd;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.alert-box p {
  margin-bottom: 10px;
  font-weight: bold;
} */
.img-view {
  border-style: none;
  width: 100%;
  height: 250px;
  object-fit: cover;
  overflow: hidden;
}
.img-containter {
  display: flex;
  width: 100%;
  /* height: 100%; */
  padding: 0px !important;
}

/* ── Watchdog Panel ──────────────────────────────────────────── */
.wd-panel {
  background: #0f172a;
  border: 1px solid #1e293b;
  border-radius: 12px;
  padding: 20px;
}
.wd-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.wd-header-left { display: flex; align-items: center; gap: 10px; }
.wd-header-right { display: flex; gap: 8px; }
.wd-icon { font-size: 20px; }
.wd-title { font-size: 16px; font-weight: 700; color: #f1f5f9; }
.wd-daemon-badge {
  font-size: 12px; font-weight: 600; padding: 2px 10px;
  border-radius: 20px; letter-spacing: .4px;
}
.wd-badge-ok  { background: #14532d; color: #86efac; }
.wd-badge-off { background: #3b1a1a; color: #f87171; }

.wd-btn-sm {
  font-size: 12px; padding: 4px 12px; border-radius: 6px; cursor: pointer;
  background: #1e293b; color: #94a3b8; border: 1px solid #334155;
  transition: background .15s;
}
.wd-btn-sm:hover { background: #334155; color: #f1f5f9; }
.wd-btn-cfg { border-color: #6366f1; color: #a5b4fc; }
.wd-btn-save {
  margin-top: 10px; padding: 6px 18px; background: #6366f1;
  color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: 13px;
}
.wd-btn-save:hover { background: #4f46e5; }

.wd-services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 10px;
  margin-bottom: 16px;
}
.wd-svc-card {
  border-radius: 8px; padding: 12px 14px;
  border: 1px solid transparent;
}
.wd-svc-ok   { background: #0d2210; border-color: #166534; }
.wd-svc-down { background: #2a0a0a; border-color: #7f1d1d; }
.wd-svc-top  { display: flex; align-items: center; gap: 6px; margin-bottom: 6px; }
.wd-svc-name { font-size: 13px; font-weight: 600; color: #e2e8f0; flex: 1; }
.wd-critical-tag {
  font-size: 9px; font-weight: 700; background: #451a03;
  color: #fb923c; padding: 1px 5px; border-radius: 4px; letter-spacing: .4px;
}
.wd-svc-bottom { display: flex; justify-content: space-between; align-items: center; }
.wd-svc-status { font-size: 11px; color: #94a3b8; }
.wd-restart-count { font-size: 11px; color: #fb923c; }

.wd-dot {
  width: 8px; height: 8px; border-radius: 50%; display: inline-block; flex-shrink: 0;
}
.wd-dot-ok   { background: #22c55e; box-shadow: 0 0 6px #22c55e88; }
.wd-dot-down { background: #ef4444; box-shadow: 0 0 6px #ef444488; animation: wd-blink 1s infinite; }
@keyframes wd-blink {
  0%, 100% { opacity: 1; } 50% { opacity: .3; }
}

.wd-config-block {
  background: #1e293b; border-radius: 8px; padding: 14px 16px; margin-bottom: 14px;
}
.wd-config-row   { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.wd-cfg-label    { font-size: 13px; color: #cbd5e1; }
.wd-config-fields { display: flex; flex-direction: column; gap: 8px; margin-top: 8px; }
.wd-input {
  background: #0f172a; border: 1px solid #334155; border-radius: 6px;
  color: #e2e8f0; padding: 6px 10px; font-size: 13px; width: 100%;
}
.wd-toggle { position: relative; display: inline-block; width: 36px; height: 20px; }
.wd-toggle input { opacity: 0; width: 0; height: 0; }
.wd-toggle-slider {
  position: absolute; inset: 0; background: #334155; border-radius: 20px; cursor: pointer; transition: .2s;
}
.wd-toggle-slider::before {
  content: ""; position: absolute; width: 14px; height: 14px;
  left: 3px; bottom: 3px; background: #94a3b8; border-radius: 50%; transition: .2s;
}
.wd-toggle input:checked + .wd-toggle-slider { background: #22c55e; }
.wd-toggle input:checked + .wd-toggle-slider::before { transform: translateX(16px); background: #fff; }

.wd-incidents { margin-top: 4px; }
.wd-incidents-title {
  font-size: 12px; font-weight: 600; color: #64748b;
  text-transform: uppercase; letter-spacing: .6px; margin-bottom: 8px;
}
.wd-inc-row {
  display: flex; align-items: center; gap: 8px;
  padding: 5px 0; border-bottom: 1px solid #1e293b; font-size: 12px;
}
.wd-inc-time { color: #64748b; white-space: nowrap; }
.wd-inc-msg  { color: #cbd5e1; }
.wd-sender-row   { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.wd-sender-field { display: flex; flex-direction: column; gap: 4px; }
.wd-field-label  { font-size: 11px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: .4px; }
.wd-no-incidents {
  font-size: 12px; color: #475569; padding: 8px 0;
  font-style: italic;
}
/* ─────────────────────────────────────────────────────────────── */
</style>
