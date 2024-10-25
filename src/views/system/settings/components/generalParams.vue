<template>
  <div class="mt-3">
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
    <div class="ml-3 mr-3">
      <h4>{{ $t("settings.GENERALPARAMETERS") }}</h4>
      <v-divider class="mb-2"></v-divider>
    </div>
    <v-row>
      <v-col cols="10">
        <v-col cols="8" class="mb-n6">
          <h4>{{ $t("settings.System") }}</h4>

          <v-divider class="mb-2"></v-divider>

          <v-text-field
            :label="$t('settings.Hostname')"
            density="compact"
            v-model="state.hostName"
          ></v-text-field>

          <v-text-field
            :label="$t('settings.Domain')"
            density="compact"
            v-model="state.domain"
          ></v-text-field>
          <p class="error-feedback mb-5" v-if="v$.domain.$errors.length">
            {{ v$.domain.$errors?.[0].$message }}
          </p>
          <v-select
            :label="$t('settings.Timezone')"
            density="compact"
            v-model="state.timeZone"
            item-title="name"
            item-value="id"
            return-object
            :items="state.timeZoneList"
          ></v-select>
        </v-col>

        <v-col cols="8" class="mb-n6">
          <h4>{{ $t("settings.Network") }}</h4>

          <v-divider class="mb-2"></v-divider>
          <div class="d-flex justify-end mt-3">
            <v-btn
              type="submit"
              @click="openModalAdd"
              color="#213E9F"
              density="comfortable"
              rounded
              >{{ $t("buttons.Add") }}</v-btn
            >
          </div>
          <div style="overflow: hidden; flex-grow: 1">
            <ag-grid-vue
              id="grid-wrapper"
              domLayout="autoHeight"
              class="ag-theme-alpine mt-3"
              style="width: 100%"
              @grid-ready="onGridReady"
              :columnDefs="columnGateway"
              :rowData="rowDataGateway.value"
              :overlayNoRowsTemplate="overlayTemplate"
            />
          </div>
        </v-col>
      </v-col>
    </v-row>
    <ModalAddEditGateway
      :isOpen="state.isModalOpen"
      :editRow="state.editRow"
      :modalMode="state.modalMode"
      :rowDataList="rowDataGateway.value"
    />

    <v-row class="flex py-8 mb-5">
      <v-col cols="4"> </v-col>
      <v-col>
        <div class="mr-3 flex center">
          <VButton
            rounded
            outlined
            color="#213E9F"
            label-color="#ffffff"
            :label="$t('buttons.save')"
            :isLarge="true"
            class="ml-2"
            @click="submitForm"
          />
        </div>
      </v-col>
    </v-row>
    <v-snackbar
      :timeout="2000"
      v-model="state.snackbar"
      location="bottom right"
      :color="state.color"
    >
      {{ state.textAlert }}
    </v-snackbar>
  </div>
</template>

<script>
import { useI18n } from "vue-i18n";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import axios from "axios";
import VButton from "@/components/VButton.vue";
import { reactive, onMounted, computed, ref, inject } from "vue";
import ModalAddEditGateway from "@/components/modals/ModalAddEditGateway.vue";
import { v4 as uuidv4 } from "uuid";
import useValidate from "@vuelidate/core";
import { required, helpers, requiredIf } from "@vuelidate/validators";

export default {
  name: "ConfigurationComponent",
  components: {
    VButton,
    AgGridVue,
    ModalAddEditGateway,
  },

  setup() {
    const { t } = useI18n();
    const overlayTemplate = ref("");
    const emitter = inject("emitter");
    const state = reactive({
      timeZoneList: [],

      loading: false,
      isLoadingDialogue: false,
      //
      modalData: {},
      modalMode: "",
      isModalOpen: false,
      isOpen: null,
      editRow: {},
      //

      snackbar: false,
      color: "",
      textAlert: "",
      //General params
      timeZone: "",
      domain: "",
      hostName: "",
    });
    const gridApi = ref(null);

    const DNSServer = computed(() => {
      return t("settings.DNSServer");
    });
    const Usethegateway = computed(() => {
      return t("settings.Usethegateway");
    });

    const columnGateway = ref([
      {
        headerName: DNSServer,
        field: "dns_server",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: Usethegateway,
        field: "gateway",
        // cellRenderer:actionGateway,
        width: 90,
        minWidth: 50,
        flex: 1,
      },

      {
        headerName: "Actions",
        cellRenderer: actionCellRenderer,
      },
    ]);
    const rowDataGateway = reactive({});

    const getCookie = (name) => {
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
    };

    onMounted(() => {
      overlayTemplate.value = `
      <span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
     </svg></span>`;

      let generaleSettings =
        document.getElementById("app").attributes["generale_settings"].value;
      const parsedArray1 = JSON.parse(generaleSettings);
      let timeZone =
        document.getElementById("app").attributes["time_zone"].value;
      const parsedArray = JSON.parse(timeZone);

      let gatewaySettings =
        document.getElementById("app").attributes["network_info"].value;
      const parsedArray2 = JSON.parse(gatewaySettings);

      rowDataGateway.value = parsedArray2[0].map((i) => {
        return {
          uuid: uuidv4(),
          dns_server: i.dns_server,
          gateway: Object.keys(i.gateway).length === 0 ? "" : i.gateway,
          info:
            Object.keys(i.gateway).length === 0
              ? []
              : {
                  interface_id: i.interface_id,
                  metric: i.metric,
                  name_interface: i.name_interface,
                },
        };
      });

      if (!rowDataGateway.value) {
        rowDataGateway.value = [];
      }

      if (gridApi.value) {
        gridApi.value.setRowData(rowDataGateway.value);
      } else {
        console.error("Grid API.");
      }

      state.timeZoneList = parsedArray;
      let time = state.timeZoneList.filter(
        (i) => i.id === parsedArray1?.time_zone?.id
      );
      state.timeZone = time[0];
      state.domain = parsedArray1?.domaine;
      state.hostName = parsedArray1?.hostname;

      emitter.on("closeModalGateway", () => {
        state.isModalOpen = false;
        state.isOpen = false;
        state.modalMode = "";
        state.editRow = {};
      });
      emitter.on("add-gateway", (data) => {
        if (!rowDataGateway.value) {
          rowDataGateway.value = [];
        }

        let test = {
          uuid: data.uuid,
          dns_server: data.dns_server,
          gateway: data.gateway.address,
          info: data.gateway.info,
        };
        rowDataGateway.value.push(test);
        if (gridApi.value) {
          gridApi.value.setRowData(rowDataGateway.value);
        } else {
          console.error("Grid API.");
        }
      });

      function updateObjectById(uuid, updatedObject) {
        const index = rowDataGateway.value.findIndex(
          (obj) => obj.uuid === uuid
        );

        if (index !== -1) {
          rowDataGateway.value[index] = {
            ...rowDataGateway.value[index],
            ...updatedObject,
          };
        }
      }

      emitter.on("edit-gateway", (data) => {
        let test = {
          uuid: data.uuid,
          dns_server: data.dns_server,
          gateway: data.gateway.address,
          info: data.gateway.info,
        };

        updateObjectById(data.uuid, test);

        if (!rowDataGateway.value) {
          rowDataGateway.value = [];
        }
        // rowDataGateway.value.push(data);

        if (gridApi.value) {
          gridApi.value.setRowData(rowDataGateway.value);
        } else {
          console.error("Grid API.");
        }
      });
    });

    // function actionGateway(data) {
    //   let eGui = document.createElement("div");
    //   if(Object.keys(data.data.gateway).length === 0) {
    //     eGui.innerHTML = `--`;
    //   }
    //   else {
    //     eGui.innerHTML = `${data.data.gateway}`;
    //   }
    //   return eGui;
    // }

    const submitForm = async () => {
      const result = await v$.value.$validate();

      if (result) {
        const csrfToken = getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

        let dns_server = rowDataGateway.value.map((i) => {
          return {
            dns_server: i.dns_server,
            gateway: i.gateway ?? "",
            interface_id: i.info.interface_id ?? i.info.interface ?? null,
            name_interface:
              i.info.name_interface ?? i.info.name_interface ?? "",
            ...(i.gateway ? { metric: i.info.metric ?? "" } : {}),
          };
        });

        let payload = {
          hostname: state.hostName,
          domain: `${state.domain}`,
          timezone: state.timeZone.name,
          dns_servers: dns_server,
        };
        state.loading = true;
        state.isLoadingDialogue = true;
        axios
          .put(`/settings/generale_settings/1`, payload)
          .then((response) => {
            if (response.status == 200) {
              state.loading = false;
              state.isLoadingDialogue = false;
              state.snackbar = true;
              state.color = "success";
              state.textAlert = response.data.msg;
              setTimeout(() => {
                state.snackbar = false;
                location.reload();
              }, 1000);
            }
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
      } else {
        console.log("v$", v$.value);
      }
    };

    const onGridReady = (params) => {
      gridApi.value = params.api;

      if (gridApi.value) {
        gridApi.value.setRowData(rowDataGateway.value);
      } else {
        console.error("Grid API.");
      }
    };

    function actionCellRenderer(params) {
      let eGui = document.createElement("div");
      eGui.innerHTML = `
      
      <button
      class="action-button edit"
      data-action="edit">
         <i class="far fa-edit" style="color: #086eae;"></i>
      </button>
  
      <button
        class="action-button delete"
        data-action="delete">
          <i class="fas fa-times" style="color: #086eae;"></i>
      </button>
      `;

      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          handleAction(action, params.node.data, params.node.rowIndex);
        });
      });

      return eGui;
    }

    const handleAction = (action, rowData) => {
      switch (action) {
        case "edit":
          state.modalData = {};
          state.modalMode = "edit";
          state.isModalOpen = true;
          state.editRow = rowData;
          break;
        case "delete":
          const index = rowDataGateway.value.findIndex(
            (item) => item.id === rowData.id
          );

          if (index !== -1) {
            rowDataGateway.value.splice(index, 1);
            if (gridApi.value) {
              gridApi.value.setRowData(rowDataGateway.value);
            } else {
              console.error("Grid API.");
            }
          }
          break;
        default:
          break;
      }
    };
    const openModalAdd = () => {
      state.modalData = {};
      state.modalMode = "create";
      state.isModalOpen = true;
      emitter.emit("list-gateway", rowDataGateway.value);
    };
    const cancel = () => {};
    const Formatdomain = computed(() => {
      return t("errors.Formatdomain");
    });
    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const rules = computed(() => {
      return {
        domain: {
          required: helpers.withMessage(error, required),
          isValidDomain: helpers.withMessage(
            Formatdomain,
            helpers.regex(/\.com$/)
          ),
        },
      };
    });

    const v$ = useValidate(rules, state);

    return {
      v$,
      cancel,
      getCookie,
      submitForm,
      state,
      emitter,
      rowDataGateway,
      gridApi,
      columnGateway,
      onGridReady,
      openModalAdd,
      overlayTemplate,
    };
  },
};
</script>
<style lang="scss">
.error-feedback {
  color: orange;
  font-size: 0.85em;
}

.label-style {
  color: #020202;
  font-family: Nunito;
  font-size: 15px;
  font-style: normal;
  font-weight: 300;
  line-height: normal;
}
/* CSS to style the text */
.text-xs {
  font-size: 12px; /* Example font size for small text */
}
.container {
  height: 50px;
}
</style>
