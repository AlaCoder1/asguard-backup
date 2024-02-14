<template>
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
    <div class="mt-6 ml-5" style="display: flex; flex-direction: column">
      <h4>SDWAN Rules</h4>
      <v-divider></v-divider>
      <v-row>
        <v-col cols="12">
          <div style="overflow: hidden; flex-grow: 1">
            <ag-grid-vue
              id="grid-wrapper"
              domLayout="autoHeight"
              class="ag-theme-alpine mt-3"
              style="width: 100%"
              @grid-ready="onGridReady"
              :columnDefs="columnRules"
              :rowData="rowDataRule.value"
            />
          </div>
          <div class="d-flex justify-end mt-3 mb-15">
            <VButton
              rounded
              outlined
              color="#213E9F"
              label-color="#ffffff"
              label="Add Key"
              :isLarge="true"
              type="submit"
              class="ml-2"
              @click="openModalAdd"
            />
          </div>
        </v-col>
      </v-row>
      <ModalSdwanRule
        :isOpen="state.isModalOpen"
        :editRow="state.editRow"
        :modalMode="state.modalMode"
      />
    </div>
    <v-dialog v-model="state.deleteDialog" max-width="500px">
      <v-card>
        <v-card-title class="headline">Delete Confirmation</v-card-title>
        <v-card-text>Are you sure you want to delete this Rule ?</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="cancelDelete">Cancel</v-btn>
          <v-btn color="blue darken-1" text @click="confirmDelete"
            >Delete</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
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
import axios from "axios";
import { reactive, ref, onMounted, inject } from "vue";
import VButton from "@/components/VButton.vue";
import BaseLayout from "@/layouts/layout.vue";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import ModalSdwanRule from "@/components/modals/ModalSdwanRule.vue";
import { getCookie } from "@/mixins/csrftoken.js";
export default {
  name: "Sdwan",
  components: {
    ModalSdwanRule,
    BaseLayout,
    AgGridVue,
    VButton,
  },
  setup() {
    const emitter = inject("emitter");
    const state = reactive({
      deleteDialog: false,
      deletedRow: null,
      snackbar: false,
      color: null,
      textAlert: "",
      modalData: {},
      modalMode: "create",
      editRow: {},
      isModalOpen: false,
      isOpen: null,
      isLoadingDialogue: false,
      loading: false,
    });

    const columnRules = [
      {
        headerName: "Rule Name",
        field: "name",
        sortable: true,
        autoHeight: true,
        filter: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Source address",
        field: "source_address",
        sortable: true,
        filter: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Area",
        autoHeight: true,
        field: "area_name",
        sortable: true,
        filter: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Algorythm type",
        autoHeight: true,
        field: "algorythme_type",
        sortable: true,
        filter: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      // {
      //   headerName: "Destination address",
      //   autoHeight: true,
      //   field: "destination_address",
      //   sortable: true,
      //   filter: true,
      // },
      {
        headerName: "Actions",
        cellRenderer: actionCellRendererArea,
        field: "action",
        sortable: true,
        filter: true,
      },
    ];

    const rowDataRule = reactive({});

    const gridApi = ref(null);

    const onGridReady = (params) => {
      // gridApi.value = params.api;

      // gridApi.value.sizeColumnsToFit();
      // window.addEventListener("resize", function () {
      //   setTimeout(function () {
      //     gridApi.value.sizeColumnsToFit();
      //   });
      // });
    };

    const defaultColDef = {
      sortable: true,
      filter: true,
      flex: 1,
    };

    function actionCellRendererArea(params) {
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
        console.log("params", params.data.rule_status);

        if (!params.data.rule_status) {
          eGui.innerHTML = `

      <button
        id="play"
        class="action-button play"
        data-action="play" title="Start Server">
            <i class="mdi mdi-play-circle" style="color: #4CAF50; font-size: 20px;"></i>
        </button>
        <button
        class="action-button edit"
        data-action="edit" title="Edit Server">
            <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
        </button>
        <button
        class="action-button delete"
        data-action="delete" title="Delete ">
          <i class="mdi mdi-delete-circle" style="color: #086EAE; font-size: 20px;"></i>
        </button>


    `;
        } else if (params.data.rule_status) {
          eGui.innerHTML = `
        <button
        id="stop"
        class="action-button stop"
        data-action="stop" title="Stop Server">
            <i class="mdi mdi-stop-circle" style="color: #B00020; font-size: 20px;"></i>
        </button>
        <button
        class="action-button edit"
        data-action="edit" title="Edit Server">
            <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
        </button>
        <button
        class="action-button delete"
        data-action="delete" title="Delete ">
          <i class="mdi mdi-delete-circle" style="color: #086EAE; font-size: 20px;"></i>
        </button>


    `;
        }
      }
      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          handleActionClient(action, params.node.data);
        });
      });
      return eGui;
    }

    const handleActionClient = (action, rowData, index) => {
      switch (action) {
        case "play":
          console.log("play", rowData);

          state.loading = true;
          state.isLoadingDialogue = true;
          axios
            .put(`/sdwan/startSdwanRule/${rowData.id}`)
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
              state.snackbar = true;
              state.color = "red";
              state.textAlert = i.response.data.error;
              state.loading = false;
              state.isLoadingDialogue = false;
            });

          break;
        case "stop":
          console.log("stop", rowData);

          state.loading = true;
          state.isLoadingDialogue = true;
          axios
            .put(`/sdwan/stopSdwanRule/${rowData.id}`)
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
              state.snackbar = true;
              state.color = "red";
              state.textAlert = i.response.data.error;
              state.loading = false;
              state.isLoadingDialogue = false;
            });
          break;
        case "edit":
          console.log("edit", rowData);
          state.modalMode = "edit";
          state.isModalOpen = true;
          state.editRow = rowData;

          break;
        case "delete":
          console.log("delete", rowData);
          state.deleteDialog = true;
          state.deletedRow = rowData;

          break;
        default:
          break;
      }
    };

    const openModalAdd = () => {
      state.modalData = {};
      state.modalMode = "create";
      state.isModalOpen = true;
    };

    onMounted(() => {
      console.log("**********", getCookie("csrftoken"));
      emitter.on("closeSdwanModalRule", () => {
        state.isModalOpen = false;
        state.isOpen = false;
        state.modalMode = "";
        state.editRow = {};
      });
      let allRule = document.getElementById("app").attributes["allRule"].value;
      let parsedArray = JSON.parse(allRule);
      console.log("parsedArray", parsedArray);

      if (!rowDataRule.value) rowDataRule.value = [];
      rowDataRule.value = parsedArray;
    });

    const cancelDelete = () => {
      state.deleteDialog = false;
    };
    const confirmDelete = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios
        .delete(`/sdwan/deleteSdwanRule/${state.deletedRow.id}`)
        .then((response) => {
          state.snackbar = true;
          state.color = "success";
          state.textAlert = response.data.msg;

          setTimeout(() => {
            location.reload();
          }, 1000);
        })
        .catch((i) => {
          state.snackbar = true;
          state.color = "red";
          state.textAlert = i.response.data.error;
        });
    };
    return {
      state,
      columnRules,
      rowDataRule,
      defaultColDef,
      actionCellRendererArea,
      openModalAdd,
      onGridReady,
      cancelDelete,
      confirmDelete,
    };
  },
};
</script>
