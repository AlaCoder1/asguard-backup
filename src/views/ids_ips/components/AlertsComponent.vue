<template>
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
          You do not have the required permissions to perform any actions.<br />
          Please contact the administrator if you believe this is an error.
        </v-card-text>

        <div class="mr-3 mb-5 d-flex justify-end">
          <VButton
            rounded
            outlined
            color="#ffffff"
            label-color="#213E9F"
            label="Close"
            :isLarge="true"
            @click="close"
          />
        </div>
      </v-card>
    </v-dialog>
  </v-overlay>
  <div class="mt-3 ml-3 mr-3">
    <v-overlay v-model="state.loading">
      <v-dialog
        v-model="state.isLoadingDialogue"
        :scrim="false"
        persistent
        width="auto"
      >
        <v-card color="#193286">
          <v-card-text>
            {{ $t("sdwan.pleaseWait") }}
            <v-progress-linear
              indeterminate
              color="white"
              class="mb-0"
            ></v-progress-linear>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-overlay>
    <v-row>
      <v-col cols="12">
        <h4>{{ $t("suricata.listOfAlerts") }}</h4>
        <v-divider></v-divider>
        <div style="display: flex; flex-direction: column" class="mb-10">
          <div v-for="(message, index) in state.messages" :key="index">
            <v-alert
              v-model="message.snackbar"
              :type="message.color"
              class="d-flex mt-3"
              :style="{
                position: 'fixed',
                marginTop: '10 px',
                top: `${100 + index * 80}px`,
                right: '10px',
                zIndex: 9999,
              }"
            >
              <!-- style="position: fixed; top: 80px; right: 10px;"> -->
              <span class="c-o ml-3">
                <strong>{{ message.color }} </strong> {{ message.text }}
              </span>
              <span class="ml-16" style="margin-top: 20px !important">
                <i
                  class="fas fa-times justify-end cursor"
                  @click="handleRemove(index)"
                ></i>
              </span>
            </v-alert>
          </div>
          <v-card class="mt-3">
            <v-card-title>
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    id="filter-text-box"
                    class="mb-3"
                    v-model="filterText"
                    :placeholder="$t('squid.search')"
                    density="compact"
                    rounded
                    variant="solo"
                    hide-details
                    dense
                    prepend-inner-icon="mdi-magnify"
                    @input="onFilterTextBoxChanged"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" md="6" class="text-right">
                  <v-btn @click="reloadData" icon>
                    <v-icon class="small-refresh-icon">mdi-refresh</v-icon>
                  </v-btn>
                </v-col>
              </v-row>
            </v-card-title>
            <v-card-text>
              <div>
                <ag-grid-vue
                  id="grid-wrapper"
                  domLayout="autoHeight"
                  class="ag-theme-alpine mt-3"
                  :columnDefs="columnRules"
                  :rowData="rowDataAlerts.value"
                  :gridOptions="gridOptions"
                  :defaultColDef="defaultColDef"
                  :autoGroupColumnDef="autoGroupColumnDef"
                  :rowGroupPanelShow="rowGroupPanelShow"
                  @cell-clicked="cellWasClicked"
                  @grid-ready="onGridReady"
                  :overlayNoRowsTemplate="overlayTemplate"
                />
              </div>
              <v-pagination
                class="mt-5"
                v-model="state.page"
                :length="state.nombrePageAlerts"
                @update:model-value="getData"
              ></v-pagination>
            </v-card-text>
          </v-card>
        </div>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { useI18n } from "vue-i18n";
import VButton from "@/components/VButton.vue";
import { AgGridVue } from "ag-grid-vue3";
import { onMounted, reactive, ref, computed } from "vue";
import { inject } from "vue";
import { user_privilege } from "@/mixins/user_privilege.js";

import "ag-grid-community/styles/ag-grid.css"; // Core grid CSS, always needed
import "ag-grid-community/styles/ag-theme-alpine.css"; // Optional theme CSS
import axios from "axios";
export default {
  name: "AlertsComponent",
  components: {
    AgGridVue,
    VButton,
  },
  props: {
    configInfo: String,
  },
  setup(props) {
    const emitter = inject("emitter");
    const overlayTemplate = ref("");
    const { t } = useI18n();
    const state = reactive({
      isviewModal: false,
      viewModal: false,
      nombrePageAlerts: null,
      page: 1,
      loading: false,
      isLoadingDialogue: false,
      snackbar: false,
      color: "",
      textAlert: "",
      messages: [],
    });
    const currentIndex = ref(0);

    const protocol = computed(() => {
      return t("suricata.protocol");
    });
    const severity = computed(() => {
      return t("suricata.severity");
    });
    const LINUXTimestamp = computed(() => {
      return t("suricata.LINUXTimestamp");
    });

    const columnRules = ref([
      // {
      //   width: 50,
      //   minWidth: 50,
      //   maxWidth: 50,
      //   rowDrag: true,
      //   editable: false,
      // },
      // {
      //   headerCheckboxSelection: false,
      //   checkboxSelection: true,
      //   editable: false,
      //   width: 50,
      //   minWidth: 50,
      //   maxWidth: 50,
      //   sortable: false,
      // },
      {
        headerName: LINUXTimestamp,
        field: "timestamp",
        sortable: true,
        sort: "desc",
        minWidth: 250,
      },
      {
        headerName: "Sid",
        field: "sid",
        minWidth: 150,
        sortable: false,
      },
      {
        headerName: "Message",
        field: "message",
        minWidth: 420,
        autoHeight: true,
        cellStyle: { whiteSpace: "pre-wrap", lineHeight: "2" },
        sortable: false,
      },
      {
        headerName: severity,
        field: "priority",
        minWidth: 120,
        sortable: false,
      },
      {
        headerName: protocol,
        field: "protocol",
        minWidth: 120,
        sortable: false,
      },
      {
        headerName: "Source",
        field: "src_addr",
        minWidth: 150,
        sortable: false,
      },
      {
        headerName: "Port",
        field: "src_port",
        minWidth: 100,
        sortable: false,
      },
      {
        headerName: "Destination",
        field: "dst_addr",
        minWidth: 150,
        sortable: false,
      },
      {
        headerName: "Port",
        field: "dst_port",
        minWidth: 100,
        sortable: false,
      },
    ]);
    const onFilterTextBoxChanged = () => {
      gridApi.value.setQuickFilter(
        document.getElementById("filter-text-box").value
      );
    };
    const rowDataAlerts = reactive({});
    const handleRemove = (index) => {
      const user = user_privilege("Suricata");
      if (user && user !== "viewer") {
        state.messages[index].snackbar = false;
      } else {
        state.isviewModal = true;
        state.viewModal = true;
      }
    };
    const gridApi = ref(null); // Optional - for accessing Grid's API
    const gridOptions = ref({
      rowSelection: "single",
    });
    // Obtain API from grid's onGridReady event
    const onGridReady = (params) => {
      gridApi.value = params.api;
    };

    const close = () => {
      state.isviewModal = false;
      state.viewModal = false;
    };

    // DefaultColDef sets props common to all Columns
    const defaultColDef = {
      sortable: true,
      filter: true,
      flex: 1,
    };
    const autoGroupColumnDef = {
      headerName: "Server Name",
      field: "serverNname",
      cellRenderer: "agGroupCellRenderer",
      cellRendererParams: {
        checkbox: true,
      },
    };
    const rowGroupPanelShow = ref("always");

    const publishServer = () => {
      console.log("publishServer");
    };

    const saveAlertSuricata = () => {
      emitter.emit("add-alert");
    };
    const showMessage = (message) => {
      // Show a new message in the alert
      state.messages.push({
        color: message.color,
        text: message.text,
        snackbar: true,
      });
      // Automatically close the alert after a specified delay
      const lastIndex = state.messages.length - 1;
      setTimeout(() => {
        state.messages[lastIndex].snackbar = false;
        state.messages[lastIndex].read = true; // Mark the message as read
        updateIndex(); // Update the index after setting a message as read
      }, 2000 * (lastIndex + 1));
    };

    const updateIndex = () => {
      // Check if all messages are read
      const allRead = state.messages.every((message) => message.read);
      // If all messages are read, reset the index to 0
      if (allRead) {
        state.messages = [];
        currentIndex.value = 0;
        setTimeout(() => {
          location.reload();
        }, 1000);
      } else {
        // Increment the index if not all messages are read
        currentIndex.value += 1;
      }
    };
    const publishClient = () => {
      console.log("publishClient");
    };
    function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === name + "=") {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
    const reloadData = async () => {
      const user = user_privilege("Suricata");
      if (user && user !== "viewer") {
        const csrfToken = getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
        state.loading = true;
        state.isLoadingDialogue = true;
        try {
          const response = await axios.post(
            "/ids-ips/addalertsToDatabase/" + props.configInfo
          );
          if (response.status === 200) {
            state.loading = false;
            state.isLoadingDialogue = false;
            state.snackbar = true;
            // state.messages=response.data.message
            showMessage({
              color: "success",
              text: t("suricata.allAlertsuccessfully"),
            });
          } else {
            state.loading = false;
            state.isLoadingDialogue = false;
            state.snackbar = true;
            showMessage({
              color: "error",
              text: t("suricata.failed"),
            });
          }
        } catch (i) {
          state.loading = false;
          state.isLoadingDialogue = false;

          if (i.response.status === 500) {
            state.snackbar = true;
            showMessage({
              color: "error",
              text: t("errors.errorServer"),
            });
          } else {
            state.snackbar = true;
            showMessage({
              color: "error",
              text: i.response,
            });
          }
        }
      } else {
        state.isviewModal = true;
        state.viewModal = true;
      }
    };

    const getData = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios
        .get(`/ids-ips/GetAlertsFromDatabase/${state.page}`)
        .then((response) => {
          rowDataAlerts.value = response.data.alerts;
          state.nombrePageAlerts = response.data.nombrePageAlerts;
        })
        .catch((e) => {
          console.log("e", e.response);
        });
    };

    onMounted(async () => {
      overlayTemplate.value = `<span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
    </svg></span>`;
      getData();
      // try {
      //   rowDataAlerts.value=document.getElementById("app").attributes["alerts_suricata"].value;
      //   let validJsonString3 =  rowDataAlerts.value
      //     .replace(/True/g, "true")
      //     .replace(/False/g, "false")
      //     .replace(/None/g, "null");
      //   let parsedArray3 = JSON.parse(validJsonString3);
      //   rowDataAlerts.value = parsedArray3;
      // } catch (error) {
      //   console.error("Error setting rowDataAlerts:", error);
      // }
    });

    return {
      columnRules,
      overlayTemplate,
      rowDataAlerts,
      defaultColDef,
      autoGroupColumnDef,
      rowGroupPanelShow,
      emitter,
      gridOptions,
      state,

      cellWasClicked: (event) => {
        // Example of consuming Grid Event
        console.log("cell was clicked", event);
      },
      deselectRows: () => {
        gridApi.value.deselectAll();
      },
      onGridReady,
      publishServer,
      saveAlertSuricata,
      publishClient,
      onFilterTextBoxChanged,
      close,
      reloadData,
      showMessage,
      handleRemove,
      updateIndex,
      getData,
    };
  },
};
</script>

<style scoped>
.grid-container {
  height: 400px;
  max-height: 100%; /* Ajustez cette valeur en fonction de vos besoins */
  overflow-y: auto;
  overflow-x: auto; /* Ajoutez cette ligne pour la défilement horizontal */
}
</style>
<style lang="scss">
.small-refresh-icon {
  font-size: 16px; /* Ajustez la taille selon vos besoins */
}
</style>
