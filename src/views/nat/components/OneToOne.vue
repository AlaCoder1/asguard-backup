<template>
  <div class="mr-3">
    <div class="mt-6 ml-5" style="display: flex; flex-direction: column">
      <h4>One To One</h4>
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
              :columnDefs="columnOneTowOne"
              :rowData="rowDataOneTowOne.value"
              :gridOptions="gridOptions"
              :rowDragManaged="true"
              :rowDragEntireRow="true"
              @row-drag-end="onRowDragEnd"
            />
          </div>
          <div class="d-flex justify-end mt-3">
            <VButton
              rounded
              outlined
              color="#213E9F"
              label-color="#ffffff"
              label="Add"
              :isLarge="true"
              type="submit"
              class="ml-2"
              @click="openModalAdd"
            />
          </div>
        </v-col>
      </v-row>
      <OneToOneModal
        :isOpen="state.isModalAreaOpen"
        :editRow="state.editRow"
        :modalMode="state.modalMode"
      />
    </div>
    <v-dialog v-model="state.deleteDialog" max-width="500px">
      <v-card>
        <v-card-title class="headline">Delete Confirmation</v-card-title>
        <v-card-text>Are you sure you want to delete this Row ?</v-card-text>
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
import OneToOneModal from "@/components/modals/OneToOneModal.vue";
import { getCookie } from "@/mixins/csrftoken.js";
export default {
  name: "Sdwan",
  components: {
    OneToOneModal,
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
      isModalAreaOpen: false,
      isOpen: null,
      editRow: {},
    });

    const gridOptions = ref({
      pagination: true,
      paginationPageSize: 5,
      rowSelection: "single",
    });

    const columnOneTowOne = [
      {
        headerName: "Interface",
        field: "interface_name",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Source IP",
        field: "source_address",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },

      {
        headerName: "Translation IP",
        field: "translation_address",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "D.Address",
        field: "destination_address",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Description",
        field: "description",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Status",
        cellRenderer: checkboxRender,
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },

      {
        headerName: "Actions",
        cellRenderer: actionCellRendererArea,
        field: "action",
      },
    ];

    function checkboxRender(params) {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      var input = document.createElement("input");
      input.type = "checkbox";
      params.value = params.data.rule_status;
      input.checked = params.value;

      input.style.margin = "10px";
      input.style.width = "20px";
      input.style.height = "18px";
      input.style.cursor = "pointer";

      input.addEventListener("click", function (event) {
        params.value = !params.value;
        params.data.rule_status = params.value;

        if (params.value) {
          axios
            .put(`/nat/startOneToOneNat/${params.data.id}`)
            .then((response) => {
              if (response.status == "201") {
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.msg;
                setTimeout(() => {
                  location.reload();
                }, 1000);
              }
            })
            .catch((i) => {
              state.snackbar = true;
              state.color = "red";
              state.textAlert = i.response.data.error;
            });
        } else {
          axios
            .put(`/nat/stopOneToOneNat/${params.data.id}`)
            .then((response) => {
              if (response.status == "201") {
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.msg;
                setTimeout(() => {
                  location.reload();
                }, 1000);
              }
            })
            .catch((i) => {
              state.snackbar = true;
              state.color = "red";
              state.textAlert = i.response.data.error;
            });
        }
      });
      return input;
    }

    const onRowDragEnd = (event) => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      const id = event.node.data.id;
      let payload = {
        new_position: event.overIndex + 1,
      };

      axios
        .put(`/nat/changeOneToOneNatPosition/${id}`, payload)
        .then((response) => {
          if (response.status == "201") {
            state.snackbar = true;
            state.color = "success";
            state.textAlert = response.data.msg;
            setTimeout(() => {
              location.reload();
            }, 1000);
          }
        })
        .catch((i) => {
          state.snackbar = true;
          state.color = "red";
          state.textAlert = i.response.data.msg;
        });
    };
    const rowDataOneTowOne = reactive({});

    const gridApi = ref(null);

    const onGridReady = (params) => {
      gridApi.value = params.api;
      // gridApi.value.sizeColumnsToFit();
      // window.addEventListener("resize", function () {
      //   setTimeout(function () {
      //     gridApi.value.sizeColumnsToFit();
      //   });
      // });

      if (gridApi.value) {
        gridApi.value.setRowData(rowDataOneTowOne.value);
      } else {
        console.error("Grid API.");
      }
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
        eGui.innerHTML = `
              <button 
                class="action-button show "  
                data-action="show">
                <i class="mdi mdi-eye" style="color: #086eae;font-size: 20px;"></i>
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
        case "show":
          console.log("show", rowData);

          break;
        case "edit":
          console.log("edit", rowData);
          state.modalMode = "edit";
          state.isModalAreaOpen = true;
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
      state.isModalAreaOpen = true;
    };

    onMounted(() => {
      emitter.on("closeOneModal", () => {
        state.isModalAreaOpen = false;
        state.isOpen = false;
        state.modalMode = "";
        state.editRow = {};
      });

      let listOneToOne =
        document.getElementById("app").attributes["listOneToOne"].value;

      const validJsonString = listOneToOne
        .replace(/'/g, '"')
        .replace(/True/g, "true")
        .replace(/False/g, "false")
        .replace(/None/g, "null");
      const parsedArray = JSON.parse(validJsonString);
      console.log("parsedArrayOne", parsedArray);

      rowDataOneTowOne.value = parsedArray;
    });

    const cancelDelete = () => {
      state.deleteDialog = false;
    };

    const confirmDelete = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios
        .delete(`/nat/deleteOneToOneNat/${state.deletedRow.id}`)
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
      gridOptions,
      columnOneTowOne,
      emitter,
      rowDataOneTowOne,
      defaultColDef,
      actionCellRendererArea,
      openModalAdd,
      onGridReady,
      cancelDelete,
      confirmDelete,
      onRowDragEnd,
    };
  },
};
</script>

<style></style>
