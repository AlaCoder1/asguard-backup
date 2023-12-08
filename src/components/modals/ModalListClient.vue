<template>
  <v-row justify="center">
    <v-dialog v-model="openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="text-h5">Client List Connected</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row class="mb-5">
                <v-col cols="12" class="mb-n5">
                  <ag-grid-vue
                    id="grid-wrapper"
                    domLayout="autoHeight"
                    class="ag-theme-alpine mt-3"
                    :columnDefs="columnClient"
                    :alwaysShowHorizontalScroll="false"
                    :alwaysShowVarticalScroll="false"
                    :rowData="rowDataClient"
                    style="width: 100%; height: 100%"
                    @grid-ready="onGridReady"
                  />
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>

          <v-card-actions class="actionBtn">
            <v-btn
              :rounded="true"
              class="mt-3 btn-add"
              color="blue-darken-1"
              variant="text"
              @click="closeModal"
            >
              <span class="text-white pr-3 pl-3">Close</span>
            </v-btn>
          </v-card-actions>
        </v-card>
      </form>
    </v-dialog>
    <v-snackbar
      :timeout="2000"
      v-model="snackbar"
      location="bottom right"
      :color="color"
    >
      {{ textAlert }}

      <template v-slot:actions> </template>
    </v-snackbar>
  </v-row>
</template>

<script>
import axios from "axios";
import { AgGridVue } from "ag-grid-vue3";
export default {
  inject: ["emitter"],
  props: {
    isOpenListView: {
      type: Boolean,
      required: true,
    },
    editRow: {
      type: Object,
      required: true,
    },
  },
  components: {
    AgGridVue,
  },
  data() {
    return {
      textAlert: "",
      color: "",
      snackbar: false,
      nameCertif: null,
      modalMode: "",
      openModal: false,
      rowEdit: {},
      isModalOpenRevoce: false,
      modalData: {},
      isModalOpen: false,
      columnClient: [
        { headerName: "username", field: "username" },
        { headerName: "certificate", field: "certificate" },
        {
          headerName: "Actions",
          cellRenderer: this.actionCellRenderer,
          editable: false,
          sortable: false,
          filter: false,
        },
      ],
      rowDataClient: [],
    };
  },
  watch: {
    isOpenListView(val) {
      this.openModal = val;
    },
    editRow(val) {
      let newData = { username: "souhail", certificate: "certif" };
      this.rowDataClient.push(newData);
    },
  },
  methods: {
    onGridReady(params) {
      this.gridApi = params.api;
      this.gridColumnApi = params.columnApi;

      params.api.sizeColumnsToFit();
      window.addEventListener("resize", function () {
        setTimeout(function () {
          params.api.sizeColumnsToFit();
        });
      });

      params.api.sizeColumnsToFit();
    },
    closeModal() {
      this.emitter.emit("closeModalClient");
    },
    openModalRevoce() {
      this.modalData = {};
      this.modalMode = "revoce";
      this.isModalOpenRevoce = true;
    },

    actionCellRenderer(params) {
      let eGui = document.createElement("div");
      let editingCells = params.api.getEditingCells();
      let isCurrentRowEditing = editingCells.some((cell) => {
        return cell.rowIndex === params.node.rowIndex;
      });
      if (isCurrentRowEditing) {
        eGui.innerHTML = `
           <button
             class="action-button update"
             data-action="update">
                  update
           </button>
           <button
             class="action-button cancel"
             data-action="cancel">
                  cancel
           </button>
           `;
      } else {
        eGui.innerHTML = `
          <button
            class="action-button cloud"
            data-action="cloud">
            <i class="mdi mdi-cloud-off-outline" style="color: #086eae; font-size:24px; aria-hidden="true"></i>
            </button>
          <button
          `;
      }
      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          this.handleAction(action, params.node.data);
        });
      });

      return eGui;
    },
    getCookie(name) {
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
    },
    handleAction(action, rowData) {
      switch (action) {
        case "cloud":
          console.log("rowData", rowData);
          break;
        default:
          break;
      }
    },
  },
};
</script>
<style lang="scss">
@import "font-awesome/css/font-awesome.css";
@import "~@mdi/font/css/materialdesignicons.min.css";
</style>
