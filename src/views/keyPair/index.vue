<template>
  <v-app id="inspire">
    <base-layout title="Key Pair" active-menu="Key_Pair">
      <template #content>
        <div class="mr-3">
          <div
            class="certificats-management mt-6 ml-5"
            style="display: flex; flex-direction: column"
          >
            <h4>List of Keys</h4>
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
                    :columnDefs="columnKeys"
                    :rowData="rowDataKeys.value"
                  />
                </div>
                <div class="d-flex justify-end mt-3">
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
            <ModalKeys :isOpen="state.isModalOpen" />
          </div>
          <v-dialog v-model="state.deleteDialog" max-width="500px">
            <v-card>
              <v-card-title class="headline">Delete Confirmation</v-card-title>
              <v-card-text
                >Are you sure you want to delete this Key ?</v-card-text
              >
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="blue darken-1" text @click="cancelDelete"
                  >Cancel</v-btn
                >
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
    </base-layout>
  </v-app>
</template>

<script>
import axios from "axios";
import { reactive, ref, onMounted } from "vue";
import VButton from "@/components/VButton.vue";
import BaseLayout from "@/layouts/layout.vue";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import ModalKeys from "@/components/modals/ModalKeys.vue";
export default {
  name: "KeyPair",
  components: {
    ModalKeys,
    BaseLayout,
    AgGridVue,
    VButton,
  },
  setup() {
    const state = reactive({
      deleteDialog: false,
      deletedRow: null,
      snackbar: false,
      color: null,
      textAlert: "",
      modalData: {},
      modalMode: "create",
      isModalOpen: false,
      isOpen: null,
    });

    onMounted(() => {
      let privateKeyAttribute =
        document.getElementById("app").attributes["privateKey"].value;
      console.log("privateKeyAttribute", privateKeyAttribute);

      const validJsonString = privateKeyAttribute
        .replace(/'/g, '"')
        .replace(/True/g, "true")
        .replace(/False/g, "false")
        .replace(/None/g, "null");
      const parsedArray = JSON.parse(validJsonString);

      let publicKeyAttribute =
        document.getElementById("app").attributes["publicKey"].value;
      console.log("publicKeyAttribute", publicKeyAttribute);

      const validJsonString2 = publicKeyAttribute
        .replace(/'/g, '"')
        .replace(/True/g, "true")
        .replace(/False/g, "false")
        .replace(/None/g, "null");
      const parsedArray2 = JSON.parse(validJsonString2);

      let mapedPrivateKey = parsedArray.map((i) => {
        return {
          id: i.id,
          name: i.name,
          utility: "Private",
          key_size: i.key_size,
          fingerPrint: i.finger_print ?? "--",
        };
      });
      let mapedPublicKey = parsedArray2.map((i) => {
        return {
          id: i.id,
          name: i.name,
          utility: "Public",
          key_size: i.key_size,
          fingerPrint: i.finger_print ?? "--",
        };
      });
      var combinedArray = [...mapedPrivateKey, ...mapedPublicKey];
      rowDataKeys.value = combinedArray;
    });

    const columnKeys = [
      {
        headerName: "Key Name",
        field: "name",
        sortable: true,
        autoHeight: true,
        filter: true,
      },
      {
        headerName: "Utility",
        field: "utility",
        sortable: true,
        filter: true,
      },
      {
        headerName: "Key Size",
        autoHeight: true,
        field: "key_size",
        sortable: true,
        filter: true,
      },
      {
        headerName: "Finger Print",
        field: "fingerPrint",
        sortable: true,
        filter: true,
      },
      {
        headerName: "Action",
        cellRenderer: actionCellRendererKeys,
        minWidth: 150,
        field: "action",
        sortable: true,
        filter: true,
      },
    ];

    const rowDataKeys = reactive({});

    const gridApi = ref(null);

    const onGridReady = (params) => {
      gridApi.value = params.api;

      gridApi.value.sizeColumnsToFit();
      window.addEventListener("resize", function () {
        setTimeout(function () {
          gridApi.value.sizeColumnsToFit();
        });
      });
    };

    const defaultColDef = {
      sortable: true,
      filter: true,
      flex: 1,
    };

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

    function actionCellRendererKeys(params) {
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
          class="action-button delete"
          data-action="delete" title="Delete Server">
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
        case "delete":
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

    const cancelDelete = () => {
      state.deleteDialog = false;
    };
    const confirmDelete = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      if (state.deletedRow?.utility === "Private") {
        axios
          .delete(`/key_pairs/deletePrivateKey/${state.deletedRow.id}`)
          .then((response) => {
            state.snackbar = true;
            state.color = "success";
            state.textAlert = response.data.msg;

            setTimeout(() => {
              location.reload();
            }, 1000);
          })
          .catch((i) => {
            console.log("i", i.response.data.error);
            state.snackbar = true;
            state.color = "red";
            state.textAlert = i.response.data.error;
          });
      } else if (state.deletedRow?.utility === "Public") {
        axios
          .delete(`/key_pairs/deletePublicKey/${state.deletedRow.id}`)
          .then((response) => {
            state.snackbar = true;
            state.color = "success";
            state.textAlert = response.data.msg;

            setTimeout(() => {
              location.reload();
            }, 1000);
          })
          .catch((i) => {
            console.log("i", i.response.data.error);
            state.snackbar = true;
            state.color = "red";
            state.textAlert = i.response.data.error;
          });
      }
    };
    return {
      state,
      columnKeys,
      rowDataKeys,
      defaultColDef,
      actionCellRendererKeys,
      openModalAdd,
      onGridReady,
      getCookie,
      cancelDelete,
      confirmDelete,
    };
  },
};
</script>
