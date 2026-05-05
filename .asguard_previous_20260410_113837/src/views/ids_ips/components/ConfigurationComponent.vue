<template>
  <v-overlay v-model="state.viewModal">
    <v-dialog
      v-model="state.isviewModal"
      persistent
      :scrim="false"
      width="auto"
    >
      <v-card color="#193286" class="alert-box">
        <v-card-title class="img-containter">
          <img
            src="@/assets/images/view.png"
            alt="logo"
            class="img-view"
            width="100"
            height="100"
        /></v-card-title>
        <v-card-text v-html="overlayMessage"> </v-card-text>

        <div class="mr-3 mb-5 d-flex justify-end">
          <VButton
            rounded
            outlined
            color="#ffffff"
            label-color="#213E9F"
            :label="$t('buttons.close')"
            :isLarge="true"
            @click="close"
          />
        </div>
      </v-card>
    </v-dialog>
  </v-overlay>
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
    <div class="ml-3 mr-3">
      <!-- <div class="container" style="display: flex;"> -->
      <h4>{{ $t("dhcpV4.generalInformation") }}</h4>
      <br />
      <!-- <div style="margin-left: auto; color: orange; margin-top: -17px;text: bold">
                <v-switch id="mySwitch" 
                        color="warning" v-model="switchValue" label="Full help" />
              </div> -->
      <!-- </div> -->
      <v-divider class="mb-2"></v-divider>
    </div>
    <v-row class="ml-3 mr-3">
      <v-col cols="6">
        <v-row class="mt-2">
          <v-col cols="4">
            <label>{{ $t("suricata.suricata") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <input type="checkbox" v-model="state.status_enabled" />
            <label class="ml-2"> {{ $t("suricata.enableIDS") }}</label>
            <!-- <br />
            <small class="ml-5 error-feedback" v-show="switchValue"
              >Enable intrusion detection system.</small
            > -->
          </v-col>
          <v-col cols="4">
            <label>{{ $t("suricata.IPSMode") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <input type="checkbox" v-model="state.mode_inline" />
            <label class="ml-2">{{ $t("suricata.enableIPS") }} </label>
            <!-- <br />
            <small class="ml-5 error-feedback" v-show="switchValue"
              >In IPS mode, Suricata actively blocks traffic according
            </small>
            <br />
            <small class="ml-5 error-feedback" v-show="switchValue">
              to intrusion detection rules.</small
            > -->
          </v-col>
          <v-col cols="4">
            <label>{{ $t("suricata.promisuousMode") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <input type="checkbox" v-model="state.promisc" />
            <label class="ml-2"
              >{{ $t("suricata.enablePromisuousMode") }}
            </label>
            <!-- <br />
            <small class="ml-5 error-feedback" v-show="switchValue"
              >Promiscuous mode allows Suricata to capture
            </small>
            <br />
            <small class="ml-5 error-feedback" v-show="switchValue">
              and analyze all traffic on the network interface.</small
            > -->
          </v-col>
          <v-col cols="4">
            <label>{{ $t("suricata.enableSyslogAlerts") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <input type="checkbox" v-model="state.syslog" />
            <label class="ml-2">{{ $t("suricata.enableSyslogAlerts") }}</label>
            <!-- <br />
            <small class="ml-5 error-feedback" v-show="switchValue"
              >Send alerts to system log in fast log format.</small
            >
            <br />
            <small class="ml-5 error-feedback" v-show="switchValue"
              >This will not change the alert logging</small
            >
            <br />
            <small class="ml-5 error-feedback" v-show="switchValue">
              used by the product itself.</small
            > -->
          </v-col>
          <v-col cols="4" class="mb-n6">
            <label>{{ $t("suricata.enableEveSyslogOutput") }}</label>
          </v-col>
          <v-col cols="8">
            <input type="checkbox" v-model="state.eve_log" />
            <label class="ml-2">{{
              $t("suricata.enableEveSyslogOutput")
            }}</label>
            <!-- <br />
            <small class="ml-5 error-feedback" v-show="switchValue"
              >Enable Suricata to output events(logs) in EVE.</small
            >
            <br />
            <small class="ml-5 error-feedback" v-show="switchValue"
              >syslog format.EVE(Extensible Event Format)
            </small>
            <br />
            <small class="ml-5 error-feedback" v-show="switchValue">
              is a flexible logging format that can be used</small
            >
            <br />
            <small class="ml-5 error-feedback" v-show="switchValue">
              to analyze security events.</small
            > -->
          </v-col>

          <v-col cols="4" class="mt-5">
            <label>{{ $t("suricata.patternMatcher") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-select
              :label="`${$t('suricata.patternMatcher')} *`"
              v-model="state.mpm_algo"
              item-title="name"
              item-value="slug"
              return-object
              :items="state.algoLists"
            ></v-select>
            <p class="error-feedback mb-5" v-if="v$.mpm_algo.$error">
              {{ v$.mpm_algo.$errors[0].$message }}
            </p>
          </v-col>
          <v-col cols="4" class="mt-5">
            <label>{{ $t("suricata.detectProfile") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-select
              :label="`${$t('suricata.detectProfile')} *`"
              v-model="state.profile"
              item-title="name"
              item-value="slug"
              return-object
              :items="state.profileLists"
            ></v-select>
            <p class="error-feedback mb-5" v-if="v$.profile.$error">
              {{ v$.profile.$errors[0].$message }}
            </p>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
    <v-row class="ml-3 mr-3">
      <v-col cols="12">
        <div class="d-flex justify-end mt-3">
          <VButton
            rounded
            outlined
            color="#213E9F"
            label-color="#ffffff"
            :label="$t('buttons.Add')"
            :isLarge="true"
            type="submit"
            class="ml-2"
            @click="openModalAdd"
          />
        </div>
        <div style="overflow: hidden; flex-grow: 1">
          <ag-grid-vue
            id="grid-wrapper"
            domLayout="autoHeight"
            class="ag-theme-alpine mt-3"
            style="width: 100%"
            @grid-ready="onGridReady"
            :columnDefs="columnAF"
            :rowData="rowDataAF.value"
            :pagination="true"
            :paginationPageSize="4"
            :localeText="paginationLocalization"
            :overlayNoRowsTemplate="overlayTemplate"
          />
        </div>
      </v-col>
    </v-row>
    <v-row class="flex py-8 mb-5">
      <v-col cols="4">
        <div class="text-start ml-5 mt-4">
          <span class="text-sm">
            <span class="text-red text-lg">*</span>
            {{ $t("errors.oblig") }}</span
          >
        </div>
      </v-col>
      <v-col>
        <div class="mr-3 flex center">
          <VButton
            rounded
            outlined
            color="#ffffff"
            label-color="#213E9F"
            :label="$t('buttons.cancel')"
            :isLarge="true"
            @click="cancel"
          />
          <VButton
            rounded
            outlined
            color="#213E9F"
            label-color="#ffffff"
            :label="$t('buttons.save')"
            :isLarge="true"
            class="ml-2"
            @click="confirmSave"
          />
        </div>
      </v-col>
    </v-row>
  </div>
  <ModalAddInterface :isOpen="state.isModalOpen" :modalMode="state.modalMode" />
  <!-- <ModalAddInterface
    :isOpen="state.isModalOpen"
    :editRow="state.editRow"
    :modalMode="state.modalMode"
    :rowDataList="rowDataAF.value"
  /> -->
  <h4>{{ $t("suricata.updateSuricata") }}</h4>
  <v-divider class="mt-2"></v-divider>
  <v-row class="flex py-8 mb-5">
    <v-col cols="4"> </v-col>
    <v-col>
      <div class="mr-3 flex center">
        <VButton
          rounded
          outlined
          color="#213E9F"
          label-color="#ffffff"
          :label="$t('suricata.makeYourUpdates')"
          :isLarge="true"
          class="ml-2"
          @click="reloadData"
        />
      </div>
    </v-col>
  </v-row>
  <v-alert
    v-model="state.snackbar"
    :type="state.color"
    class="d-flex mt-3"
    style="position: fixed; top: 80px; right: 10px"
  >
    <span class="c-o ml-3">
      <strong>{{ state.color }} </strong> {{ state.textAlert }}
    </span>
    <span class="ml-16" style="margin-top: 20px !important">
      <i class="fas fa-times justify-end cursor" @click="handleRemove"></i>
    </span>
  </v-alert>

  <v-dialog v-model="state.SaveConfig" max-width="500px">
    <v-card>
      <v-card-title class="headline">
        {{ $t("firewall.Save_confirm") }}
      </v-card-title>
      <v-card-text>{{ $t("firewall.msg_confirm_save") }}</v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="cancelSave">{{
          $t("firewall.cancel")
        }}</v-btn>
        <v-btn color="blue darken-1" text @click="submitForm">{{
          $t("firewall.save")
        }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="state.deleteDialog" max-width="500px">
    <v-card>
      <v-card-title class="headline">{{
        $t("firewall.delete_confirm")
      }}</v-card-title>
      <v-card-text>{{ $t("nat.msg_confirm_delete") }}</v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="cancelDelete">{{
          $t("firewall.cancel")
        }}</v-btn>
        <v-btn color="blue darken-1" text @click="confirmDelete">{{
          $t("firewall.delete")
        }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- </div> -->
</template>

<script>
import { useI18n } from "vue-i18n";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import axios from "axios";
// import useValidate from "@vuelidate/core";
import VButton from "@/components/VButton.vue";
// import { required, requiredIf, helpers } from "@vuelidate/validators";
import UsersList from "../../system/user/components/UsersList.vue";
import { reactive, onMounted, computed, ref, inject } from "vue";
import ModalAddInterface from "@/components/modals/ModalAddInterface.vue";
import { v4 as uuidv4 } from "uuid";
import useValidate from "@vuelidate/core";
import { required, helpers } from "@vuelidate/validators";
import { user_privilege } from "@/mixins/user_privilege.js";

export default {
  name: "ConfigurationComponent",
  components: {
    UsersList,
    VButton,
    AgGridVue,
    ModalAddInterface,
  },

  setup() {
    const { t } = useI18n();
    const emitter = inject("emitter");
    const rowDataInterfaces = reactive({});
    const current_user = ref();
    const last_Subscription = ref([]);
    const overlayTemplate = ref("");
    const switchValue = ref(false);
    const paginationLocalization = reactive({
      of: "/",
    });
    const state = reactive({
      deleteDialog: false,
      deletedRow: false,
      interId: null,
      SaveConfig: false,
      profileLists: [
        {
          id: "1",
          name: "Medium",
          slug: "medium",
        },
        {
          id: "2",
          name: "High",
          slug: "high",
        },
        {
          id: "3",
          name: "Low",
          slug: "low",
        },
      ],
      algoLists: [
        {
          id: "1",
          name: "Auto",
          slug: "auto",
        },
        {
          id: "2",
          name: "Aho-Corasick, default implementation",
          slug: "ac",
        },
        {
          id: "3",
          name: "Aho-Corasick, reduced memory implementation",
          slug: "ac-bs",
        },
        {
          id: "4",
          name: "Aho-Corasick, Ken Steele variant",
          slug: "ac-ks",
        },
        {
          id: "5",
          name: "Hyperscan",
          slug: "hs",
        },
      ],
      //
      modalData: {},
      modalMode: "",
      isviewModal: false,
      viewModal: false,
      isModalOpen: false,
      isOpen: null,
      editRow: {},
      //
      loading: false,
      isLoadingDialogue: false,

      snackbar: false,
      color: "",
      textAlert: "",
      //General information
      copyMode: false,
      status_enabled: false,
      mode_inline: false,
      promisc: "",
      syslog: "",
      eve_log: "",
      mpm_algo: "",
      profile: "",
      mapedInterface: [],
      interface: "",
    });
    const gridApi = ref(null);
    const overlayMessage = computed(() => {
      current_user.value = user_privilege("Suricata");
      if (current_user.value === "viewer" || current_user.value === "default") {
        return ` ${t("profil.NoPermission")} <br /> ${t(
          "profil.ContactAdmin"
        )}`;
      } else if (!last_Subscription.value.includes("IDS/IPS")) {
        return `${t(
          "firewall.msg_subscription"
        )}<br /><a href="/asguard/license/" class="white-link"> ${t(
          "firewall.sub_page"
        )}</a>`;
      } else {
        return ` ${t("profil.NoPermission")} <br /> ${t(
          "profil.ContactAdmin"
        )}`;
      }
    });
    const thread = computed(() => {
      return t("suricata.thread");
    });
    const cludtedId = computed(() => {
      return t("suricata.clusterId");
    });
    const clusterType = computed(() => {
      return t("suricata.clusterType");
    });
    const copyMode = computed(() => {
      return t("suricata.copyMode");
    });
    const copyIface = computed(() => {
      return t("suricata.copyIface");
    });
    const bufferSize = computed(() => {
      return t("suricata.bufferSize");
    });
    const useMmap = computed(() => {
      return t("suricata.useMmap");
    });

    const columnAF = ref([
      {
        headerName: "Interface",
        field: "name_interface",
        // cellRenderer: actionCopyInterface,

        autoHeight: true,
        resizable: true,
        width: 100,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: thread,
        field: "threads",
        width: 100,
        minWidth: 150,
        flex: 1,
        resizable: true,
      },
      {
        headerName: "Defrag",
        autoHeight: true,
        field: "defrag",
        width: 90,
        minWidth: 150,
        flex: 1,
        resizable: true,
      },
      {
        headerName: cludtedId,
        field: "cluster_id",
        width: 90,
        minWidth: 150,
        flex: 1,
        resizable: true,
      },
      {
        headerName: clusterType,
        field: "cluster_type",
        width: 90,
        minWidth: 150,
        flex: 1,
        resizable: true,
      },
      {
        headerName: copyMode,
        field: "copy_mode",
        width: 90,
        minWidth: 150,
        flex: 1,
        resizable: true,
      },
      {
        headerName: copyIface,
        field: "copy_iface",
        // cellRenderer: actionCopyIface,
        width: 90,
        minWidth: 150,
        flex: 1,
        resizable: true,
      },
      {
        headerName: bufferSize,
        field: "ring_size",
        width: 90,
        minWidth: 150,
        flex: 1,
        resizable: true,
      },
      {
        headerName: useMmap,
        field: "use_mmap",
        width: 90,
        minWidth: 150,
        flex: 1,
        resizable: true,
      },
      {
        headerName: "Actions",
        cellRenderer: actionCellRenderer,
        width: 150,
        field: "action",
      },
    ]);
    const rowDataAF = reactive({});
    const clearInterface = (selectedInterface) => {
      // Remove the selected interface from the state
      const index = this.state.interface.indexOf(selectedInterface);
      if (index !== -1) {
        this.state.interface.splice(index, 1);
      }
    };
    const listeInterfaces = reactive([]);
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

    const close = () => {
      state.isviewModal = false;
      state.viewModal = false;
    };

    const getInterface = async () => {
      rowDataInterfaces.value =
        document.getElementById("app").attributes["all_interfaces"].value;
      let validJsonString = rowDataInterfaces.value
        .replace(/'/g, '"')
        .replace(/True/g, "true")
        .replace(/False/g, "false")
        .replace(/None/g, "null");
      let parsedArray = JSON.parse(validJsonString);
      rowDataInterfaces.value = parsedArray;
      let interfaces = rowDataInterfaces.value.map((i) => {
        return {
          id: i.id,
          name: i.name_interface,
          ifname: i.ifname,
        };
      });
      listeInterfaces.value = interfaces;
      state.mapedInterface = interfaces;
    };

    // function actionCopyIface(data) {
    //   let eGui = document.createElement("div");

    //   if (typeof data.data.copy_iface === "object") {
    //     var filtredInterface = listeInterfaces.value.filter(
    //       (i) => i.id === data.data.copy_iface.id
    //     );
    //   } else {
    //     var filtredInterface = listeInterfaces.value.filter(
    //       (i) => i.id === data.data.copy_iface
    //     );
    //   }


    //   eGui.innerHTML = `
    //     ${filtredInterface[0].name}
    //    `;
    //   return eGui;
    // }

    // function actionCopyInterface(data) {
    //   let eGui = document.createElement("div");

    //   let filtredInterface = listeInterfaces.value.filter(
    //     (i) => i.name === data.data.name_interface
    //   );

    //   eGui.innerHTML = `
    //     ${filtredInterface[0].name}
    //    `;
    //   return eGui;
    // }

    function actionCellRenderer(params) {
      let eGui = document.createElement("div");
      // <button
      // class="action-button edit"
      // data-action="edit">
      //    <i class="far fa-edit" style="color: #086eae;"></i>
      // </button>
      eGui.innerHTML = `


      <button
        class="action-button delete"
        data-action="delete">
          <i class="fas fa-times" style="color: #086eae; margin-left: 10px;"></i>
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
      const user = user_privilege("suricata");
      switch (action) {
        // case "edit":
        //   // state.modalData = {};
        //   // state.modalMode = "edit";
        //   // state.isModalOpen = true;
        //   // state.editRow = rowData;

        //   break;
        case "delete":
          if (
            user &&
            user !== "viewer" &&
            user !== "default" &&
            last_Subscription.value.includes("IDS/IPS")
          ) {
            state.deleteDialog = true;
            state.deletedRow = rowData;
          } else {
            state.isviewModal = true;
            state.viewModal = true;
          }
          break;
        default:
          break;
      }
    };

    const reloadData = async () => {
      const user = user_privilege("Suricata");
      if (
        user &&
        user !== "viewer" &&
        user !== "default" &&
        last_Subscription.value.includes("IDS/IPS")
      ) {
        const csrfToken = getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
        state.loading = true;
        state.isLoadingDialogue = true;
        try {
          const response = await axios.post(
            "activerSuricataUpdate/" + state.interId
          );
          if (response.status === 200) {
            // state.messages=response.data.message
            state.loading = false;
            state.isLoadingDialogue = false;
            state.snackbar = true;
            state.color = "success";
            state.textAlert = t("suricata.rulesSavedSuccessfully");
            // Automatically close the snackbar after 3000 milliseconds (3 seconds)
            setTimeout(() => {
              state.snackbar = false;
            }, 1000);
          } else {
            state.loading = false;
            state.isLoadingDialogue = false;
            state.snackbar = true;
            state.color = "error";
            state.textAlert = t("suricata.failed");
            setTimeout(() => {
              state.snackbar = false;
            }, 2000);
          }
        } catch (error) {
          state.loading = false;
          state.isLoadingDialogue = false;
          state.snackbar = true;
          state.color = "error";
          state.textAlert = error;
          setTimeout(() => {
            state.snackbar = false;
          }, 2000);
        }
      } else {
        state.isviewModal = true;
        state.viewModal = true;
      }
    };

    onMounted(async () => {
      const lastSubscription =
        document.getElementById("app").attributes["last_subscription"].value;
      let parsedArraySubscription = JSON.parse(lastSubscription);
      last_Subscription.value = parsedArraySubscription;
      overlayTemplate.value = `<span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
    </svg></span>`;
      await getInterface();
      emitter.on("closeModalAddInterface", () => {
        state.isModalOpen = false;
        state.isOpen = false;
        state.modalMode = "";
        state.editRow = {};
      });
      emitter.on("add-Interface", (data) => {
        if (!rowDataAF.value) {
          rowDataAF.value = [];
        }

        let test = {
          id: data.id,
          uuid: data.uuid,
          cluster_id: data.cluster_id,
          cluster_type: data.cluster_type,
          copy_iface: data.copy_iface?.name ? data.copy_iface?.name : null,
          copy_mode: data.copy_mode,
          defrag: data.defrag,
          id_interface: data.id_interface,
          name_interface: data.interface,
          ring_size: data.ring_size,
          threads: data.threads,
          use_mmap: data.use_mmap,
          ifname: data.ifname,
        };
        rowDataAF.value.push(test);
        if (gridApi.value) {
          gridApi.value.setRowData(rowDataAF.value);
        } else {
          
        }
      });

      function updateObjectById(uuid, updatedObject) {
        const index = rowDataAF.value.findIndex((obj) => obj.uuid === uuid);

        if (index !== -1) {
          rowDataAF.value[index] = {
            ...rowDataAF.value[index],
            ...updatedObject,
          };
        }
      }

      emitter.on("edit-Interface", (data) => {
        let test = {
          uuid: data.uuid,
          id: data.id,
          cluster_id: data.cluster_id,
          cluster_type: data.cluster_type,
          copy_iface: data.copy_iface.name,
          copy_mode: data.copy_mode,
          defrag: data.defrag,
          id_interface: data.id_interface,
          name_interface: data.interface,
          ring_size: data.ring_size,
          threads: data.threads,
          use_mmap: data.use_mmap,
        };

        updateObjectById(data.uuid, test);

        if (!rowDataAF.value) {
          rowDataAF.value = [];
        }
        // rowDataAF.value.push(data);

        if (gridApi.value) {
          gridApi.value.setRowData(rowDataAF.value);
        } else {
          
        }
      });

      let rowConfiguration =
        document.getElementById("app").attributes["general_config_suricata"]
          .value;
      let rowConfig = JSON.parse(rowConfiguration);

      state.status_enabled = rowConfig.configuration.status_enabled;
      state.mode_inline = rowConfig.configuration?.mode_inline;
      state.promisc = rowConfig.configuration.promisc;
      state.syslog = rowConfig.configuration.syslog
        ? rowConfig.configuration.syslog.toLowerCase() === "yes"
        : "";
      state.eve_log = rowConfig.configuration.eve_log
        ? rowConfig.configuration.eve_log.toLowerCase() === "yes"
        : "";

      state.interId = rowConfig.configuration.id;

      let filtredProfile = state.profileLists.filter(
        (i) => i.slug === rowConfig.configuration.profile
      );
      let filtredAlgo = state.algoLists.filter(
        (i) => i.slug === rowConfig.configuration.mpm_algo
      );

      state.mpm_algo = filtredAlgo[0];
      state.profile = filtredProfile[0];

      rowDataAF.value = rowConfig.configuration.liste_interfaces.map((i) => {
        var filtredIFace = listeInterfaces.value.filter(
          (e) => e.id === i.copy_iface
        );

        return {
          uuid: uuidv4(),
          cluster_id: i.cluster_id,
          cluster_type: i.cluster_type,
          copy_iface: filtredIFace.length ? filtredIFace[0].name : "--",
          copy_mode: i.copy_mode ?? "--",
          defrag: i.defrag,
          id_interface: i.id_interface,
          name_interface: i.name_interface,
          ring_size: i.ring_size,
          threads: i.threads,
          use_mmap: i.use_mmap,
          ifname: i.ifname,
        };
      });

      if (!rowDataAF.value) {
        rowDataAF.value = [];
      }
      // rowDataAF.value = rowConfig.configuration.liste_interfaces;

      if (gridApi.value) {
        gridApi.value.setRowData(rowDataAF.value);
      } else {
        
      }
    });
    const handleRemove = () => {
      state.snackbar = false;
    };

    const onGridReady = (params) => {
      gridApi.value = params.api;
      if (gridApi.value) {
        gridApi.value.setRowData(rowDataAF.value);
      } else {
        
      }
    };

    const openModalAdd = () => {
      const user = user_privilege("Suricata");
      if (
        user &&
        user !== "viewer" &&
        user !== "default" &&
        last_Subscription.value.includes("IDS/IPS")
      ) {
        state.modalData = {};
        state.modalMode = "create";
        state.isModalOpen = true;
        emitter.emit("list-Interface", rowDataAF.value);
      } else {
        state.isviewModal = true;
        state.viewModal = true;
      }
    };

    const submitForm = async () => {
      state.SaveConfig = false;
      const user = user_privilege("Suricata");
      if (
        user &&
        user !== "viewer" &&
        user !== "default" &&
        last_Subscription.value.includes("IDS/IPS")
      ) {
        const result = await v$.value.$validate();
        if (result) {
          const csrfToken = getCookie("csrftoken");
          axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

          if (!rowDataAF.value) {
            rowDataAF.value = [];
          }

          if (rowDataAF.value.length) {
            var mapedRow = rowDataAF.value.map((e) => {
              let filtredCopy = state.mapedInterface
                .filter((i) => i.name === e.copy_iface)
                .map((i) => {
                  return {
                    id: i.id,
                    name: i.ifname,
                  };
                });

              return {
                id: e.id ?? e.id_interface,
                interface: e.ifname,
                threads: e.threads,
                cluster_id: e.cluster_id,
                cluster_type: e.cluster_type,
                defrag: e.defrag,
                use_mmap: e.use_mmap,
                ring_size: e.ring_size,
                copy_iface: filtredCopy[0] ?? null,
                copy_mode: e.copy_mode === "--" ? null : e.copy_mode,
              };
            });

            let payload = {
              status_enabled: state.status_enabled,
              promisc: state.promisc,
              eve_log: state.eve_log,
              syslog: state.syslog,
              mpm_algo: state.mpm_algo.slug,
              profile: state.profile.slug,
              mode_inline: state.mode_inline,
              list_interfaces: mapedRow,
            };
            state.loading = true;
            state.isLoadingDialogue = true;
            axios
              .put("/ids-ips/UpdateGeneralConfig/" + state.interId, payload)
              .then((response) => {
                if (response.status == 200) {
                  state.SaveConfig = false;
                  state.loading = false;
                  state.isLoadingDialogue = false;
                  state.snackbar = true;
                  state.color = "success";
                  state.textAlert = t("suricata.configurationSuccess");
                  // Automatically close the snackbar after 3000 milliseconds (3 seconds)
                  setTimeout(() => {
                    state.snackbar = false;
                    location.reload();
                  }, 1000);
                }
                // else {
                //   state.loading = false;
                //   state.isLoadingDialogue = false;
                //   state.snackbar = true;
                //   state.color = "error";
                //   state.textAlert = t("suricata.failedToSaveConfiguration");
                //   // Automatically close the snackbar after 3000 milliseconds (3 seconds)
                //   setTimeout(() => {
                //     state.snackbar = false;
                //   }, 2000);
                // }
              })
              .catch((i) => {
                state.SaveConfig = false;
                state.loading = false;
                state.isLoadingDialogue = false;

                if (i.response.status === 500) {
                  state.snackbar = true;
                  state.color = "red";
                  state.textAlert = t("errors.errorServer");
                } else {
                  state.snackbar = true;
                  state.color = "red";
                  state.textAlert = t("suricata.failedToSaveConfiguration");
                }
              });
          } else {
            state.SaveConfig = false;
            state.snackbar = true;
            state.color = "error";
            state.textAlert = t("suricata.MinimumOneInter");
            setTimeout(() => {
              state.snackbar = false;
            }, 3000);
          }
        } else {
          state.SaveConfig = false;
          if (rowDataAF.value.length === 0) {
            state.snackbar = true;
            state.color = "error";
            state.textAlert = t("suricata.MinimumOneInter");
            setTimeout(() => {
              state.snackbar = false;
            }, 3000);
          }
        }
      } else {
        state.isviewModal = true;
        state.viewModal = true;
      }
    };

    const error = computed(() => {
      return t("errors.valueRequired");
    });

    const rules = computed(() => {
      return {
        mpm_algo: {
          required: helpers.withMessage(error, required),
        },
        profile: {
          required: helpers.withMessage(error, required),
        },
      };
    });

    const v$ = useValidate(rules, state);
    const cancel = () => {};

    const confirmSave = () => {
      state.SaveConfig = true;
    };

    const cancelSave = () => {
      state.SaveConfig = false;
    };

    const cancelDelete = () => {
      state.deleteDialog = false;
    };

    const confirmDelete = () => {
      const index = rowDataAF.value.findIndex(
        (item) => item.id === state.deletedRow.id
      );

      if (index !== -1) {
        rowDataAF.value.splice(index, 1);
        state.deleteDialog = false;
        if (gridApi.value) {
          gridApi.value.setRowData(rowDataAF.value);
        } else {
          
        }
      }
    };

    return {
      confirmDelete,
      cancelDelete,
      switchValue,
      cancelSave,
      confirmSave,
      cancel,
      close,
      overlayMessage,
      getCookie,
      getInterface,
      submitForm,
      clearInterface,
      handleRemove,
      state,
      reloadData,
      columnAF,
      onGridReady,
      rowDataAF,
      emitter,
      overlayTemplate,
      paginationLocalization,
      openModalAdd,
      v$,
    };
  },
};
</script>
<style lang="scss">
.error-feedback {
  color: orange;
  font-size: 0.85em;
}
.white-link {
  color: white;
  text-decoration: underline;
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
