<template>
  <div class="mr-3">
    <div class="mt-6 ml-5" style="display: flex; flex-direction: column">
      <h4>SNAt</h4>
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
              :columnDefs="columnSnat"
              :rowData="rowDataSnat.value"
              :gridOptions="gridOptions"
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
      <SnatModal
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
import { reactive, ref, onMounted, inject, onBeforeMount } from "vue";
import VButton from "@/components/VButton.vue";
import BaseLayout from "@/layouts/layout.vue";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import SnatModal from "@/components/modals/SnatModal.vue";
import { getCookie } from "@/mixins/csrftoken.js";
export default {
  name: "SNAT",
  components: {
    SnatModal,
    BaseLayout,
    AgGridVue,
    VButton,
  },
  setup() {
    const emitter = inject("emitter");
    const state = reactive({
      mapedInterface: [],
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

    const columnSnat = [
      {
        headerName: "Interface",
        field: "interface_name",
        autoHeight: true,
        resizable: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Protocol",
        field: "protocol",
        autoHeight: true,
        resizable: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "S.address",
        field: "source_address",
        autoHeight: true,
        resizable: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Ports",
        field: "source_port",
        autoHeight: true,
        resizable: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "D.Address",
        field: "destination_address",
        autoHeight: true,
        resizable: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Ports",
        field: "destination_port",
        autoHeight: true,
        resizable: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Transalation IP",
        field: "tcp_ip",
        autoHeight: true,
        resizable: true,
        width: 100,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: "Ports",
        field: "translation_port",
        autoHeight: true,
        resizable: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Description",
        field: "description",
        autoHeight: true,
        resizable: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Status",
        // field: "rule_status",
        cellRenderer: checkboxRender,
        autoHeight: true,
        resizable: true,
        // editable: true,
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

    const rowDataSnat = reactive({});

    const gridApi = ref(null);

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
            .put(`/nat/startSNat/${params.data.id}`)
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
            .put(`/nat/stopSNat/${params.data.id}`)
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

    const onGridReady = (params) => {
      gridApi.value = params.api;
      //   gridApi.value.sizeColumnsToFit();
      //   window.addEventListener("resize", function () {
      //     setTimeout(function () {
      //       gridApi.value.sizeColumnsToFit();
      //     });
      //   });

      if (gridApi.value) {
        gridApi.value.setRowData(rowDataSnat.value);
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

    const getInterface = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/network/AllInterfaces").then(
        (response) => {
          let filtredInterface = response.data.filter(
            (i) => !i.ifname.startsWith("tun_") && !i.ifname.startsWith("tap_")
          );

          let interfaces = filtredInterface.map((i) => {
            return {
              id: i.id,
              name: i.name_interface,
            };
          });

          state.mapedInterface = interfaces;
        },
        (error) => {
          console.log(error);
        }
      );
    };

    const openModalAdd = () => {
      state.modalData = {};
      state.modalMode = "create";
      state.isModalAreaOpen = true;
    };
    onBeforeMount(() => {
      getInterface();
    }),
      onMounted(() => {
        emitter.on("closeSnatModal", () => {
          state.isModalAreaOpen = false;
          state.isOpen = false;
          state.modalMode = "";
          state.editRow = {};
        });

        let allListNat =
          document.getElementById("app").attributes["listNat"].value;

        const validJsonString = allListNat
          .replace(/'/g, '"')
          .replace(/True/g, "true")
          .replace(/False/g, "false")
          .replace(/None/g, "null");
        const parsedArray = JSON.parse(validJsonString);

        let mapedNatRow = parsedArray.map((i) => {
          return {
            id: i.id,
            description: i.description,
            destination_address: i.destination_address,
            destination_port: i.destination_port,
            interface: i.interface,
            interface_name: i.interface_name,
            protocol: i.protocol,
            rule_number: i.rule_number,
            rule_status: i.rule_status,
            snat_type: i.snat_type,
            source_address: i.source_address,
            source_port: i.source_port,
            tcp_ip: i.tcp_ip,
            translation_address_from: i.translation_address_from,
            translation_address_to: i.translation_address_to,
            translation_port: i.translation_port,
          };
        });
        rowDataSnat.value = mapedNatRow;
      });

    const cancelDelete = () => {
      state.deleteDialog = false;
    };

    const confirmDelete = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios
        .delete(`/nat/deleteSNat/${state.deletedRow.id}`)
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
      columnSnat,
      emitter,
      rowDataSnat,
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

<style></style>
