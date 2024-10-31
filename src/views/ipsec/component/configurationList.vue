<template>
  <v-overlay v-model="state.viewModal">
    <v-dialog v-model="state.isviewModal" persistent :scrim="false" width="auto">
      <v-card color="#193286" class="alert-box">
        <v-card-title class="img-containter">
          <img src="@/assets/images/view.png" alt="logo" class="img-view" width="100" height="100" /></v-card-title>
          <v-card-text v-html="overlayMessage">
          </v-card-text>

        <div class="mr-3 mb-5 d-flex justify-end">
          <VButton rounded outlined color="#ffffff" label-color="#213E9F" :label="$t('buttons.close')" :isLarge="true"
            @click="close" />
        </div>
      </v-card>
    </v-dialog>
  </v-overlay>
  <div class="mt-3 ml-3 mr-3">
    <v-row>
      <v-overlay v-model="loading">
        <v-dialog v-model="isLoadingDialogue" :scrim="false" persistent width="auto">
          <v-card color="#193286">
            <v-card-text>
              {{ $t("requiredfield.attente") }}
              <v-progress-linear indeterminate color="white" class="mb-0"></v-progress-linear>
            </v-card-text>
          </v-card>
        </v-dialog>
      </v-overlay>

      <v-col cols="12">
        <h4 class="mb-1">
          IPSEC PEERS
          <i class="mdi mdi-play-circle mr-1 ml-1" style="color: #4caf50; font-size: 20px; cursor: pointer"
            @click="startStopServer('start')"></i>
          <i v-if="status" class="mdi mdi-stop-circle" style="color: #b00020; font-size: 20px; cursor: pointer"
            @click="startStopServer('stop')"></i>
        </h4>

        <v-divider></v-divider>
        <div class="mt-3" style="display: flex; flex-direction: column">
          <ag-grid-vue id="grid-wrapper" domLayout="autoHeight" class="ag-theme-alpine mt-3 mb-3" :columnDefs="columns"
            :rowData="rowData.value" :gridOptions="gridOptions" :defaultColDef="defaultColDef"
            :overlayNoRowsTemplate="overlayTemplate" :rowGroupPanelShow="rowGroupPanelShow" @grid-ready="onGridReady"
            style="width: 100%; height: 100%" :localeText="paginationLocalization" />
          <div class="justify-end d-flex mr-3 mt-3 mb-3">
            <VButton rounded outlined color="#213E9F" label-color="#ffffff" :label="$t('PageIpsec.addnewpeer')"
              :isLarge="true" class="ml-2" @click="addServer" />
          </div>
          <br />
          <br />
          <br />
        </div>
      </v-col>
    </v-row>
    <v-snackbar :timeout="2000" v-model="snackbar" location="bottom right" :color="color">
      {{ textAlert }}

      <template v-slot:actions> </template>
    </v-snackbar>
  </div>
  <!-- Dialog for delete confirmation -->
  <v-dialog v-model="dialogDelete" max-width="500">
    <v-card>
      <v-card-title>{{ $t("delete.DeleteConfirmation") }}</v-card-title>
      <v-card-text>{{ $t("delete.deleteRow") }} ?</v-card-text>
      <v-card-actions>
        <v-btn color="error" text @click="deleteItem">{{
          $t("buttons.delete")
        }}</v-btn>
        <v-btn text @click="dialogDelete = false">{{
          $t("buttons.cancel")
        }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { useI18n } from "vue-i18n";
import axios from "axios";
import VButton from "@/components/VButton.vue";
import { AgGridVue } from "ag-grid-vue3";
import { onMounted, reactive, computed, ref } from "vue";
import { inject } from "vue";
import { user_privilege } from "@/mixins/user_privilege.js";

import "ag-grid-community/styles/ag-grid.css"; // Core grid CSS, always needed
import "ag-grid-community/styles/ag-theme-alpine.css"; // Optional theme CSS

export default {
  name: "ConfigurationList",
  components: {
    AgGridVue,
    VButton,
  },
  setup() {
    const { t } = useI18n();
    const current_user = ref();
    const last_Subscription = ref([]);
    const paginationLocalization = reactive({
      of: "/",
    });
    const emitter = inject("emitter");
    const state = reactive({
      isviewModal: false,
      viewModal: false,
    })
    const color = ref(null);
    const snackbar = ref(false);
    const textAlert = ref(false);
    const dialogDelete = ref(false);
    const overlayTemplate = ref("");
    const currentRowToDelete = ref(null);
    const loading = ref(false);
    const isLoadingDialogue = ref(false);
    const status = ref(false);
    const remoteGateway = computed(() => {
      return t("PageIpsec.remotegateway");
    });
    const overlayMessage = computed(() => {
current_user.value= user_privilege('Ipscec') 
  if (current_user.value === "viewer" || current_user.value === "default") {
    return ` ${t("profil.NoPermission")} <br /> ${t("profil.ContactAdmin")}`;
  } else if (!last_Subscription.value.includes("VPN IPSEC")) {
    return `${t("firewall.msg_subscription")}<br /><a href="/asguard/subscription/" class="white-link"> ${t("firewall.sub_page")}</a>`;
  } else{
    return ` ${t("profil.NoPermission")} <br /> ${t("profil.ContactAdmin")}`;
  }
});
    const Phase1Proposal = computed(() => {
      return t("PageIpsec.Phase1Proposal");
    });
    const auth = computed(() => {
      return t("PageNetwork.Authentication");
    });
    const localsubnet = computed(() => {
      return t("PageIpsec.LocalSubnet");
    });
    const Remotesubnet = computed(() => {
      return t("PageIpsec.Remotesubnet");
    });
    const Phase2Proposal = computed(() => {
      return t("PageIpsec.Phase2Proposal");
    });
    const Enable = computed(() => {
      return t("PageIpsec.Enable");
    });
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
        headerName: remoteGateway,
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
        headerName: Phase1Proposal,
        cellRenderer: FirstPhaseProposal,
        minWidth: 300,
        suppressSizeToFit: true,
        sortable: true,
        filter: true,
      },
      {
        headerName: auth,
        field: "authentication_method",
        minWidth: 150,
        suppressSizeToFit: true,
        sortable: true,
        filter: true,
      },
      {
        headerName: localsubnet,
        field: "address_local_network",
        minWidth: 150,
        suppressSizeToFit: true,
        sortable: true,
        filter: true,
      },
      {
        headerName: Remotesubnet,
        field: "address_remote_network",
        minWidth: 150,
        suppressSizeToFit: true,
        sortable: true,
        filter: true,
      },
      {
        headerName: Phase2Proposal,
        cellRenderer: SecondPhaseProposal,
        minWidth: 200,
        suppressSizeToFit: true,
        autoHeight: true,
        sortable: true,
        filter: true,
      },
      {
        headerName: Enable,
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
      params.value = params.data.server_status;
      input.checked = params.value;

      input.style.margin = "10px";
      input.style.width = "20px";
      input.style.height = "18px";
      input.style.cursor = "pointer";

      input.addEventListener("click", function (event) {
        params.value = !params.value;
        params.data.server_status = params.value;
        let payload = {
          enable: params.value,
        };

        axios
          .put(`/ipsec/statusServerIPsec/${params.data.id}`, payload)
          .then((response) => {
            if (response.status == "200") {
              snackbar.value = true;
              color.value = "success";
              textAlert.value = response.data.msg;
              setTimeout(() => {
                location.reload();
              }, 1000);
            }
          })
          .catch((i) => {
            if (i.response.status === 500) {
              state.snackbar = true;
              state.color = "red";
              state.textAlert = t("errors.errorServer");
            } else {
              state.snackbar = true;
              state.color = "red";
              state.textAlert = i.response.data.error;
            }
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
      // let encryptionText = "";

      // switch (data.data.encryption_algorithm_ph1) {
      //   case "128":
      //     encryptionText = "128 bit AES-GCM with 128 bit ICV";
      //     break;
      //   case "192":
      //     encryptionText = "192 bit AES-GCM with 128 bit ICV";
      //     break;
      //   case "256":
      //     encryptionText = "256 bit AES-GCM with 128 bit ICV";
      //     break;
      //   default:
      //     encryptionText = "";
      // }

      eGui.innerHTML = `
          ${data.data.encryption_algorithm_ph1} <br/>
          ${uppercaseData(data.data.hash_algorithm_ph1)} <br/> DH Group 
          ${extractDHKey(data.data.dh_key_group)}
          `;
      eGui.style.lineHeight = "2";
      return eGui;
    }

    function SecondPhaseProposal(data) {
      let eGui = document.createElement("div");
      let encryptionText = "";

      // Assuming data.data.encryption_algorithm_ph2 is an array
      // if (
      //   Array.isArray(data.data.encryption_algorithm_ph2) &&
      //   data.data.encryption_algorithm_ph2.length > 0
      // ) {
      //   encryptionText = data.data.encryption_algorithm_ph2
      //     .map((algorithm) => {
      //       switch (algorithm) {
      //         case "128":
      //           return "aes128gcm16";
      //         case "192":
      //           return "aes192gcm16";
      //         case "256":
      //           return "aes256gcm16";
      //         default:
      //           return ""; // For unknown cases, add an empty string or handle accordingly
      //       }
      //     })
      //     .join(" "); // Join the algorithms with space
      // } else {
      //   encryptionText = null; // Set encryptionText as null if encryption algorithms array is empty or undefined
      // }

      // // Conditionally add <br/> if encryptionText is not null
      // let lineBreak = encryptionText !== null ? "<br/>" : "";

      const resultMessage = data.data.encryption_algorithm_ph2
        .map((e) => e + "<br>")
        .join("");

      if (data.data.pfs_key_group !== "off") {
        let pfsKey = data.data.pfs_key_group
          ? `(${extractPFSKey(data.data.pfs_key_group)}) bits`
          : "";
        eGui.innerHTML = `
      ${resultMessage ? `${resultMessage}` : ""}
      ${uppercaseData(data.data.hash_algorithm_ph2)} <br/>
      ${extractDHKey(data.data.pfs_key_group)} ${pfsKey}
    `;
      } else {
        eGui.innerHTML = `
      ${resultMessage ? `${resultMessage}` : ""}
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
            class="action-button up"
            data-action="up">
              <i class="mdi mdi-arrow-up-bold-circle" style="color: #086EAE; font-size: 20px;" ></i>
            </button>
            <button
            class="action-button editClient"
            data-action="edit">
              <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
            </button>
            <button
            class="action-button delete"
            data-action="delete">
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
      const user = user_privilege('Ipsec');

      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      switch (action) {
        case "edit":
        if (user && user !== 'viewer' && user!=='default' && last_Subscription.value.includes("VPN IPSEC")) {

          console.log("edit :", rowData);
          emitter.emit("add-serverIpsec");

          setTimeout(() => {
            emitter.emit("edit-serverIpsec", rowData);
          }, 1000);
        } else {
            state.isviewModal = true;
            state.viewModal = true;
          };
          break;
        case "delete":
        if (user && user !== 'viewer' && user!=='default' && last_Subscription.value.includes("VPN IPSEC")) {

          currentRowToDelete.value = rowData;
          dialogDelete.value = true;
        } else {
            state.isviewModal = true;
            state.viewModal = true;
          };
          break;
        case "up":
        if (user && user !== 'viewer' && user!=='default' && last_Subscription.value.includes("VPN IPSEC")) {

          console.log("up", rowData);
          let id = rowData.id;
          upServer(id);
        } else {
            state.isviewModal = true;
            state.viewModal = true;
          };
          break;
        default:
          break;
      }
    };
    const upServer = async (id) => {
      let timeoutPromise = new Promise((resolve, reject) => {
        setTimeout(() => {
          reject(new Error("Request is taking longer than expected."));
        }, 3000);
      });
      console.log("up", id);
      try {
        loading.value = true;
        isLoadingDialogue.value = true;
        // loading.value = true;
        // isLoadingDialogue.value = true;
        // let response = await axios.post(`/ipsec/upServerIPsec/${id}`);
        // console.log("response", response);
        // if (response) {
        //   snackbar.value = true;
        //   color.value = "success";
        //   textAlert.value = response.data.msg;
        //   loading.value = false;
        //   isLoadingDialogue.value = false;
        //   setTimeout(() => {
        //     location.reload();
        //   }, 1000);
        // }
        let response = await Promise.race([
          axios.post(`/ipsec/upServerIPsec/${id}`),
          timeoutPromise,
        ]);

        console.log("response", response);

        if (response) {
          snackbar.value = true;
          color.value = "success";
          textAlert.value = response.data.msg;
          loading.value = false;
          isLoadingDialogue.value = false;

          setTimeout(() => {
            location.reload();
          }, 1000);
        }
      } catch (error) {
        // snackbar.value = true;
        // color.value = "red";
        // textAlert.value = i.response.data.error;
        // loading.value = false;
        // isLoadingDialogue.value = false;

        if (error.response.status === 500) {
          loading.value = false;
          isLoadingDialogue.value = false;
          state.snackbar = true;
          state.color = "red";
          state.textAlert = t("errors.errorServer");
        }

        if (error.message === "Request is taking longer than expected.") {
          // snackbar.value = true;
          // color.value = "warning";
          // textAlert.value = "The request is taking longer than expected...";
          loading.value = false;
          isLoadingDialogue.value = false;
        } else {
          // console.error(error);
          // snackbar.value = true;
          // color.value = "error";
          // textAlert.value = "An error occurred while processing your request.";
          loading.value = false;
          isLoadingDialogue.value = false;
        }
      }
    };
    const addServer = () => {
      const user = user_privilege('Ipsec');
      if (user && user !== 'viewer' && user!=='default' && last_Subscription.value.includes("VPN IPSEC")) {
        emitter.emit("add-serverIpsec");
      } else {
        state.isviewModal = true;
        state.viewModal = true;
      };
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
          .catch((i) => {
            if (i.response.status === 500) {
              state.snackbar = true;
              state.color = "red";
              state.textAlert = t("errors.errorServer");
            } else {
              state.snackbar = true;
              state.color = "red";
              state.textAlert = i.response.data.error;
            }
          })
          .finally(() => {
            // Reset the current row data and close the dialog
            currentRowToDelete.value = null;
            dialogDelete.value = false;
          });
      }
    };
    onMounted(async () => {
      
    const lastSubscription =
        document.getElementById("app").attributes["last_subscription"].value;
      let parsedArraySubscription = JSON.parse(lastSubscription);
      last_Subscription.value = parsedArraySubscription;
      console.log("last_Subscription",last_Subscription.value)
      overlayTemplate.value = `
      <span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
     </svg></span>`;

      try {
        const serversAttribute =
          document.getElementById("app").attributes["servers"].value;
        const validJsonString = serversAttribute;
        const parsedArray = JSON.parse(validJsonString);
        rowData.value = parsedArray;
        console.log("rowData.value", rowData.value);

        const statusAttribute =
          document.getElementById("app").attributes["status"].value;
        console.log("statusAttribute", statusAttribute);

        status.value = statusAttribute === "False" ? false : true;
      } catch (error) {
        console.log(error);
      }
    });

    const startStopServer = (data) => {
      const user = user_privilege('Ipsec');
      if (user && user !== 'viewer' && user!=='default' && last_Subscription.value.includes("VPN IPSEC")) {

        const csrfToken = getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

        let payload = {
          status: data,
        };

        axios
          .post("/ipsec/statusIPsec", payload)
          .then((response) => {
            snackbar.value = true;
            color.value = "success";
            textAlert.value = response.data.msg;

            setTimeout(() => {
              location.reload();
            }, 1000);
          })
          .catch((i) => {
            if (i.response.status === 500) {
              state.snackbar = true;
              state.color = "red";
              state.textAlert = t("errors.errorServer");
            } else {
              state.snackbar = true;
              state.color = "red";
              state.textAlert = i.response.data.error;
            }
          });
      } else {
        state.isviewModal = true;
        state.viewModal = true;
      };

    };
    const close = () => {
      state.isviewModal = false;
      state.viewModal = false;
    };

    return {
      close,
      loading,
      state,
      isLoadingDialogue,
      status,
      emitter,
      overlayTemplate,
      color,
      snackbar,
      textAlert,
      dialogDelete,
      currentRowToDelete,
      columns,
      paginationLocalization,
      rowData,
      defaultColDef,
      rowGroupPanelShow,
      gridApi,
      gridOptions,
      TypePeers,
      checkboxRender,
      RemoteGateway,
      overlayMessage,
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
      startStopServer,
    };
  },
};
</script>

<style scoped>
.white-link {
  color: white;
  text-decoration: underline;
}
</style>
