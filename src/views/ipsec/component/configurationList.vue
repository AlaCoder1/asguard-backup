<template>
  <div class="mt-3 ml-3 mr-3">
    <v-row>
      <v-col cols="12">
        <h4 class="mb-1">
          IPSEC PEERS
          <i class="mdi mdi-play-circle mr-1 ml-1" style="color: #4caf50; font-size: 20px"></i>
          <i class="mdi mdi-stop-circle" style="color: #b00020; font-size: 20px"></i>
        </h4>

        <v-divider></v-divider>
        <div style="display: flex; flex-direction: column">
          <v-card class="flex mt-3">
            <ag-grid-vue id="grid-wrapper" domLayout="autoHeight" class="ag-theme-alpine mt-3 mb-3 ml-3 mr-3"
              :columnDefs="columns" :rowData="rowData.value" :gridOptions="gridOptions" :defaultColDef="defaultColDef"
              :rowGroupPanelShow="rowGroupPanelShow" @grid-ready="onGridReady" style="width: 100%; height: 100%" />
            <div class="justify-end d-flex mr-3 mt-3 mb-3">
              <VButton rounded outlined color="#213E9F" label-color="#ffffff" label="Add New Peer" :isLarge="true"
                class="ml-2" @click="addServer" />
            </div>
          </v-card>
          <br />
          <br />
          <br />
        </div>
      </v-col>
    </v-row>
  </div>
  <!-- Dialog for delete confirmation -->
  <v-dialog v-model="dialogDelete" max-width="500">
    <v-card>
      <v-card-title>Delete Confirmation</v-card-title>
      <v-card-text>Are you sure you want to delete this server?</v-card-text>
      <v-card-actions>
        <v-btn color="error" text @click="deleteItem">Delete</v-btn>
        <v-btn text @click="dialogDelete = false">Cancel</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from "axios";
import VButton from "@/components/VButton.vue";
import { AgGridVue } from "ag-grid-vue3";
import { onMounted, reactive, ref } from "vue";
import { inject } from "vue";

import "ag-grid-community/styles/ag-grid.css"; // Core grid CSS, always needed
import "ag-grid-community/styles/ag-theme-alpine.css"; // Optional theme CSS

export default {
  name: "ConfigurationList",
  components: {
    AgGridVue,
    VButton,
  },
  setup() {
    const emitter = inject("emitter");
    const color = ref(null);
    const snackbar = ref(false);
    const textAlert = ref(false);
    const dialogDelete = ref(false);
    const currentRowToDelete = ref(null);
    const columns = ref([
      {
        headerName: "Type",
        cellRenderer: TypePeers,
        minWidth: 100,
        suppressSizeToFit: true,
        sortable: true,
        filter: true,
      },
      {
        headerName: "Remote Gateway",
        cellRenderer: RemoteGateway,
        minWidth: 200,
        suppressSizeToFit: true,
        sortable: true,
        filter: true,
      },
      {
        headerName: "Mode",
        field: "negotiation_mode",
        minWidth: 100,
        suppressSizeToFit: true,
        sortable: true,
        filter: true,
      },
      {
        headerName: "Phase 1 Proposal",
        cellRenderer: FirstPhaseProposal,
        minWidth: 300,
        suppressSizeToFit: true,
        sortable: true,
        filter: true,
      },
      {
        headerName: "Authentication",
        field: "authentication_method",
        minWidth: 150,
        suppressSizeToFit: true,
        sortable: true,
        filter: true,
      },
      {
        headerName: "Local Subnet",
        field: "address_local_network",
        minWidth: 150,
        suppressSizeToFit: true,
        sortable: true,
        filter: true,
      },
      {
        headerName: "Remote subnet",
        field: "address_remote_network",
        minWidth: 150,
        suppressSizeToFit: true,
        sortable: true,
        filter: true,
      },
      {
        headerName: "Phase 2 Proposal",
        cellRenderer: SecondPhaseProposal,
        minWidth: 200,
        suppressSizeToFit: true,
        sortable: true,
        filter: true,
      },
      {
        headerName: "Enable",
        minWidth: 100,
        suppressSizeToFit: true,
        field: "enable",
        cellRenderer: checkboxRender,
      },
      {
        headerName: "Action",
        cellRenderer: actionCellRenderer,
        minWidth: 100,
        editable: false,
        sortable: false,
        filter: false,
      },
    ]);

    function checkboxRender(params) {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      // return `<input type="checkbox" ${params.value ? "checked" : ""} />`;
      var input = document.createElement("input");
      input.type = "checkbox";
      input.checked = params.value;

      input.style.margin = "10px";
      input.addEventListener("click", function (event) {
        console.log("params", params.data.id);
        console.log("evene", event);
        params.value = !params.value;
        console.log("params.value", params.value);
        params.node.data.fieldName = params.value;

        axios
          .put(`/ipsec/updateServerIPsec/${state.id}`, payload)
          .then((response) => {
            if (response.status == "201") {
              state.loading = false;
              state.isLoadingDialogue = false;
              state.snackbar = true;
              state.color = "success";
              state.textAlert = response.data.msg;
              state.isEditState = "";
              setTimeout(() => {
                location.reload();
                emitter.emit("open-listingIpsec");
              }, 1000);
            }
          })
          .catch((i) => {
            console.log("eroor");
          });
      });
      return input;
    }

    const rowData = reactive([]);
    function TypePeers(data) {
      let eGui = document.createElement("div");
      eGui.innerHTML = `
          ${data.data.internet_protocol}  ${data.data.key_exchange_version}
          `;
      eGui.style.lineHeight = "2";
      return eGui;
    }
    function RemoteGateway(data) {
      let eGui = document.createElement("div");
      eGui.innerHTML = `
          ${data.data.interface}  ${data.data.remote_gateway}
          `;
      eGui.style.lineHeight = "2";
      return eGui;
    }
    function extractDHKey(data) {
      let data_dh_key_group = String(data); // Ensure data is converted to a string
      let split_data_dh_key_group = data_dh_key_group.split(":")[0];
      return split_data_dh_key_group;
    }
    function extractPFSKey(data) {
      let data_dh_key_group = String(data); // Ensure data is converted to a string
      let split_data_dh_key_group = data_dh_key_group.split(":")[1];
      console.log(split_data_dh_key_group);
      return split_data_dh_key_group;
    }
    function uppercaseData(data) {
      let data_uppercase = String(data); // Ensure data is converted to a string
      let uppercase_data = data_uppercase.toUpperCase();
      return uppercase_data;
    }
    function FirstPhaseProposal(data) {
      let eGui = document.createElement("div");
      let encryptionText = "";

      switch (data.data.encryption_algorithm_ph1) {
        case "128":
          encryptionText = "128 bit AES-GCM with 128 bit ICV";
          break;
        case "192":
          encryptionText = "192 bit AES-GCM with 128 bit ICV";
          break;
        case "256":
          encryptionText = "256 bit AES-GCM with 128 bit ICV";
          break;
        default:
          encryptionText = "";
      }

      eGui.innerHTML = `
          ${encryptionText} <br/>
          ${uppercaseData(data.data.hash_algorithm_ph1)} <br/> DH Group 
          ${extractDHKey(data.data.dh_key_group)}
          `;
      eGui.style.lineHeight = "2";
      return eGui;
    }

    function SecondPhaseProposal(data) {
      let eGui = document.createElement("div");
      let encryptionText = "";

      switch (data.data.encryption_algorithm_ph2) {
        case "128":
          encryptionText = "aes128gcm16";
          break;
        case "192":
          encryptionText = "aes192gcm16";
          break;
        case "256":
          encryptionText = "aes256gcm16";
          break;
        default:
          encryptionText = null; // Set encryptionText as null instead of an empty string
      }

      // Conditionally add <br/> if encryptionText is not null
      let lineBreak = encryptionText !== null ? '<br/>' : '';
      if (data.data.pfs_key_group !== "off") {
        let pfsKey = data.data.pfs_key_group ? `(${extractPFSKey(data.data.pfs_key_group)}) bits` : '';
        eGui.innerHTML = `
    ${encryptionText ? `${encryptionText} ${lineBreak}` : ''} 
    ${uppercaseData(data.data.hash_algorithm_ph2)} <br/>
    ${extractDHKey(data.data.pfs_key_group)} ${pfsKey}
  `;
      } else {
        eGui.innerHTML = `
    ${encryptionText ? `${encryptionText} ${lineBreak}` : ''} 
    ${uppercaseData(data.data.hash_algorithm_ph2)} <br/>
    ${extractDHKey(data.data.pfs_key_group)}
  `;

      }




      eGui.style.lineHeight = "2";
      return eGui;
    }


    const gridApi = ref(null);
    const gridOptions = ref({
      pagination: true,
      paginationPageSize: 5,
      rowSelection: "single",
      domLayout: "autoHeight",
      rowHeight: 80,
    });

    // Obtain API from grid's onGridReady event
    const onGridReady = (params) => {
      gridApi.value = params.api;
    };
    // DefaultColDef sets props common to all Columns
    const defaultColDef = {
      sortable: true,
      filter: true,
      flex: 1,
    };
    const rowGroupPanelShow = ref("always");
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
    function actionCellRenderer(params) {
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
            class="action-button editClient"
            data-action="edit" title="Edit">
              <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
            </button>
            <button
            class="action-button delete"
            data-action="delete" title="Delete">
              <i class="mdi mdi-delete" style="color: #086EAE; font-size: 20px;"></i>
            </button>
        `;
      }
      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          handleAction(action, params.node.data);
        });
      });
      return eGui;
    }
    const handleAction = (action, rowData) => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      switch (action) {
        case "edit":
          console.log("edit :", rowData);
          emitter.emit("add-serverIpsec");
          emitter.emit("edit-serverIpsec", rowData);
          break;
        case "delete":
          currentRowToDelete.value = rowData;
          dialogDelete.value = true;
          break;
        default:
          break;
      }
    };
    const addServer = () => {
      emitter.emit("add-serverIpsec");
    };
    const deleteItem = () => {
      // Perform delete action when confirmed
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      if (currentRowToDelete.value) {
        axios
          .delete(`/ipsec/deleteServerIPsec/${currentRowToDelete.value.id}`)
          .then((response) => {
            snackbar.value = true;
            color.value = "success";
            textAlert.value = response.data.msg;
            setTimeout(() => {
              location.reload();
            }, 1000);
          })
          .catch((error) => {
            snackbar.value = true;
            color.value = "red";
            textAlert.value = error.response.data.error;
          })
          .finally(() => {
            // Reset the current row data and close the dialog
            currentRowToDelete.value = null;
            dialogDelete.value = false;
          });
      }
    };
    onMounted(async () => {
      try {
        const serversAttribute =
          document.getElementById("app").attributes["servers"].value;
        const validJsonString = serversAttribute;
        // .replace(/'/g, '"')
        // .replace(/True/g, "true")
        // .replace(/False/g, "false")
        // .replace(/None/g, "null");
        const parsedArray = JSON.parse(validJsonString);
        rowData.value = parsedArray;
      } catch (error) {
        console.log(error);
      }
    });

    return {
      emitter,
      color,
      snackbar,
      textAlert,
      dialogDelete,
      currentRowToDelete,
      columns,
      rowData,
      defaultColDef,
      rowGroupPanelShow,
      gridApi,
      gridOptions,
      TypePeers,
      checkboxRender,
      RemoteGateway,
      extractDHKey,
      extractPFSKey,
      uppercaseData,
      FirstPhaseProposal,
      SecondPhaseProposal,
      onGridReady,
      getCookie,
      actionCellRenderer,
      handleAction,
      addServer,
      deleteItem,
    };
  },
};
</script>

<style scoped>
/* Add your custom styles here */
</style>
