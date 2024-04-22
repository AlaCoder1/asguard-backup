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
            Please Wait...
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
      <h4>General Parameters</h4>
      <br />

      <v-divider class="mb-2"></v-divider>
    </div>
    <v-row>
      <v-col cols="10">
        <v-col cols="8" class="mb-n6">
          <h4>System</h4>

          <v-divider class="mb-2"></v-divider>

          <v-text-field
            label="Host name"
            density="compact"
            v-model="state.hostName"
          ></v-text-field>

          <v-text-field
            label="Domain"
            density="compact"
            v-model="state.domain"
          ></v-text-field>
          <v-select
            label="Time zone"
            density="compact"
            v-model="state.timeZone"
            item-title="name"
            item-value="id"
            return-object
            :items="state.timeZoneList"
          ></v-select>
        </v-col>

        <v-col cols="8" class="mb-n6">
          <h4>Network</h4>

          <v-divider class="mb-2"></v-divider>
          <div class="d-flex justify-end mt-3">
            <v-btn
              type="submit"
              @click="openModalAdd"
              color="#213E9F"
              density="comfortable"
              rounded
              >Add</v-btn
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
            label="save"
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
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import axios from "axios";
import VButton from "@/components/VButton.vue";
import { reactive, onMounted, computed, ref, inject } from "vue";
import ModalAddEditGateway from "@/components/modals/ModalAddEditGateway.vue";
import { v4 as uuidv4 } from "uuid";

export default {
  name: "ConfigurationComponent",
  components: {
    VButton,
    AgGridVue,
    ModalAddEditGateway,
  },

  setup() {
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

    const columnGateway = [
      {
        headerName: "DNS Server",
        field: "dns_server",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Use the gateway",
        field: "gateway",
        width: 90,
        minWidth: 50,
        flex: 1,
      },

      {
        headerName: "Actions",
        cellRenderer: actionCellRenderer,
      },
    ];
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
      let generaleSettings =
        document.getElementById("app").attributes["generale_settings"].value;
      const parsedArray1 = JSON.parse(generaleSettings);
      let timeZone =
        document.getElementById("app").attributes["time_zone"].value;
      const parsedArray = JSON.parse(timeZone);
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
          gateway: data.gateway,
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
          gateway: data.gateway,
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

    const submitForm = async () => {
      console.log("gateway", rowDataGateway.value);
      // const csrfToken = getCookie("csrftoken");
      // axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      // let payload = {
      //   hostname: state.hostName,
      //   domain: `${state.domain}.com`,
      //   timezone: state.timeZone.name,
      // };
      // console.log("pay", payload);
      // state.loading = true;
      // state.isLoadingDialogue = true;
      // axios
      //   .put(`/settings/generale_settings/1`, payload)
      //   .then((response) => {
      //     console.log("response", response);
      //     if (response.status == 200) {
      //       state.loading = false;
      //       state.isLoadingDialogue = false;
      //       state.snackbar = true;
      //       state.color = "success";
      //       state.textAlert = "Configuration saved successfully!";
      //       setTimeout(() => {
      //         state.snackbar = false;
      //         location.reload();
      //       }, 1000);
      //     }
      //   })
      //   .catch((i) => {
      //     state.loading = false;
      //     state.isLoadingDialogue = false;

      //     state.snackbar = true;
      //     state.color = "red";
      //     state.textAlert = i.response.data.msg;
      //   });
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

    return {
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
