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
      <!-- <div class="container" style="display: flex;"> -->
      <h4>General information</h4>
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
          <v-col cols="4" align-self="center">
            <label>Suricata</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <input type="checkbox" v-model="state.status_enabled" />
            <label class="ml-2"> Enable IDS system</label>
            <br />
            <small class="ml-5 error-feedback" v-show="switchValue"
              >Enable intrusion detection system.</small
            >
          </v-col>
          <!-- <v-col cols="4" align-self="center">
            <label>IPS Mode</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <input type="checkbox" v-model="state.copy_mode" />
            <label class="ml-2">Enable IPS </label>
            <br />
            <small class="ml-5 error-feedback" v-show="switchValue"
              >In IPS mode, Suricata actively blocks traffic according
            </small>
            <br />
            <small class="ml-5 error-feedback" v-show="switchValue">
              to intrusion detection rules.</small
            >
          </v-col> -->
          <v-col cols="4" align-self="center">
            <label>Promisuous Mode</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <input type="checkbox" v-model="state.promisc" />
            <label class="ml-2">Enable Promisuous Mode </label>
            <br />
            <small class="ml-5 error-feedback" v-show="switchValue"
              >Promiscuous mode allows Suricata to capture
            </small>
            <br />
            <small class="ml-5 error-feedback" v-show="switchValue">
              and analyze all traffic on the network interface.</small
            >
          </v-col>
          <v-col cols="4" align-self="center">
            <label>Enable syslog alerts</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <input type="checkbox" v-model="state.syslog" />
            <label class="ml-2">Enable syslog alerts</label>
            <br />
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
            >
          </v-col>
          <v-col cols="4">
            <label>Enable eve syslog output</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <input type="checkbox" v-model="state.eve_log" />
            <label class="ml-2">Enable syslog output</label>
            <br />
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
            >
          </v-col>
          <v-col cols="4" align-self="center">
            <label>Pattern matcher</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-select
              label="Pattern matcher"
              v-model="state.mpm_algo"
              item-title="name"
              item-value="slug"
              return-object
              :items="[
                {
                  id: '1',
                  name: 'Auto',
                  slug: 'auto',
                },
                {
                  id: '2',
                  name: 'Aho-Corasick, default implementation',
                  slug: 'ac',
                },
                {
                  id: '3',
                  name: 'Aho-Corasick, reduced memory implementation',
                  slug: 'ac-bs',
                },
                {
                  id: '4',
                  name: 'Aho-Corasick, Ken Steele variant',
                  slug: 'ac-ks',
                },
                {
                  id: '5',
                  name: 'Hyperscan',
                  slug: 'hs',
                },
              ]"
            ></v-select>
          </v-col>
          <v-col cols="4" align-self="center">
            <label>Detect Profile</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-select
              label="Detect Profile"
              v-model="state.profile"
              item-title="name"
              item-value="slug"
              return-object
              :items="[
                {
                  id: '1',
                  name: 'Medium',
                  slug: 'medium',
                },
                {
                  id: '2',
                  name: 'High',
                  slug: 'high',
                },
                {
                  id: '3',
                  name: 'Low',
                  slug: 'low',
                },
              ]"
            ></v-select>
          </v-col>

          <v-col cols="4" align-self="center">
            <label>Copy Mode</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <input type="checkbox" v-model="state.copyMode" />
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
            label="Add"
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
          />
        </div>
      </v-col>
    </v-row>
    <v-row class="flex py-8 mb-5">
      <v-col cols="4"> </v-col>
      <v-col>
        <div class="mr-3 flex center">
          <VButton
            rounded
            outlined
            color="#ffffff"
            label-color="#213E9F"
            label="cancel"
            :isLarge="true"
            @click="cancel"
          />
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
  </div>
  <ModalAddInterface :isOpen="state.isModalOpen" />
  <h4>Update suricata rules</h4>
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
          label="Make your updates"
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
  <!-- </div> -->
</template>

<script>
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import axios from "axios";
import useValidate from "@vuelidate/core";
import VButton from "@/components/VButton.vue";
import { required, requiredIf, helpers } from "@vuelidate/validators";
import UsersList from "../../system/user/components/UsersList.vue";
import { reactive, onMounted, computed, ref, inject } from "vue";
import ModalAddInterface from "@/components/modals/ModalAddInterface.vue";

export default {
  name: "ConfigurationComponent",
  components: {
    UsersList,
    VButton,
    AgGridVue,
    ModalAddInterface,
  },

  setup() {
    const emitter = inject("emitter");
    const rowDataConfiguration = reactive({});
    const rowDataInterfaces = reactive({});
    const switchValue = ref(false);
    const state = reactive({
      modalData: {},
      modalMode: "create",
      isModalOpen: false,
      isOpen: null,

      //

      loading: false,
      isLoadingDialogue: false,

      snackbar: false,
      color: "",
      textAlert: "",
      //General information
      copyMode: false,
      status_enabled: false,
      copy_mode: false,
      promisc: "",
      syslog: "",
      eve_log: "",
      mpm_algo: "",
      profile: "",
      mapedInterface: [],
      interface: "",
    });
    const gridApi = ref(null);

    const columnAF = [
      {
        headerName: "Interface",
        field: "interface",
        sortable: true,
        autoHeight: true,
        filter: true,
      },
      {
        headerName: "Thread",
        field: "threads",
        sortable: true,
        filter: true,
      },
      {
        headerName: "Defrag",
        autoHeight: true,
        field: "defrag",
        sortable: true,
        filter: true,
      },
      {
        headerName: "Cluster Id",
        field: "cluster_id",
        sortable: true,
        filter: true,
      },
      {
        headerName: "Cluster Type",
        field: "cluster_type",
        sortable: true,
        filter: true,
      },
      {
        headerName: "Copy Mode",
        field: "copy_mode",
        sortable: true,
        filter: true,
      },
      {
        headerName: "Copy Iface",
        field: "copy_ifaceName",
        sortable: true,
        filter: true,
      },
      {
        headerName: "Buffer Size",
        field: "ring_size",
        sortable: true,
        filter: true,
      },
      {
        headerName: "Use Mmap",
        field: "use_mmap",
        sortable: true,
        filter: true,
      },
      {
        headerName: "Actions",
        // cellRenderer: actionCellRendererKeys,
        minWidth: 150,
        field: "action",
        sortable: true,
        filter: true,
      },
    ];
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
        };
      });
      listeInterfaces.value = interfaces;
      state.mapedInterface = interfaces;
    };

    // const actionCopyIface = (data) => {
    //   console.log("data", data);
    //   let eGui = document.createElement("div");

    //   eGui.innerHTML = `
    //   ${data.data.copy_iface.id} / ${data.data.copy_iface.name}
    //  `;
    //   return eGui;
    // };

    const reloadData = async () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      state.loading = true;
      state.isLoadingDialogue = true;
      try {
        const response = await axios.post(
          "activerSuricataUpdate/" + rowDataConfiguration.value.configuration.id
        );
        if (response.status === 200) {
          // state.messages=response.data.message
          state.loading = false;
          state.isLoadingDialogue = false;
          state.snackbar = true;
          state.color = "success";
          state.textAlert = "Rules saved successfully!";
          // Automatically close the snackbar after 3000 milliseconds (3 seconds)
          setTimeout(() => {
            state.snackbar = false;
          }, 2000);
        } else {
          state.loading = false;
          state.isLoadingDialogue = false;
          state.snackbar = true;
          state.color = "error";
          state.textAlert = "Failed to save rule!";
          // Automatically close the snackbar after 3000 milliseconds (3 seconds)
          setTimeout(() => {
            state.snackbar = false;
            // location.reload();
          }, 2000);
        }
      } catch (error) {
        state.loading = false;
        state.isLoadingDialogue = false;
        state.snackbar = true;
        state.color = "error";
        state.textAlert = error;
        // Automatically close the snackbar after 3000 milliseconds (3 seconds)
        setTimeout(() => {
          state.snackbar = false;
          // location.reload();
        }, 2000);
      }
    };
    onMounted(async () => {
      emitter.on("closeModalAddInterface", () => {
        state.isModalOpen = false;
      });
      emitter.on("add-Interface", (data) => {
        console.log("add-Interface", data);

        if (!rowDataAF.value) {
          rowDataAF.value = [];
        }
        rowDataAF.value.push(data);

        if (gridApi.value) {
          gridApi.value.setRowData(rowDataAF.value);
        } else {
          console.error("Grid API.");
        }
      });

      await getInterface();
      rowDataConfiguration.value =
        document.getElementById("app").attributes[
          "general_config_suricata"
        ].value;
      let validJsonString = rowDataConfiguration.value
        .replace(/True/g, "true")
        .replace(/False/g, "false")
        .replace(/None/g, "null");
      let parsedArray = JSON.parse(validJsonString);
      rowDataConfiguration.value = parsedArray;
      state.status_enabled =
        rowDataConfiguration.value.configuration.status_enabled;
      state.promisc = rowDataConfiguration.value.configuration.promisc;
      state.syslog =
        rowDataConfiguration.value.configuration.syslog.toLowerCase() === "yes";
      state.eve_log =
        rowDataConfiguration.value.configuration.eve_log.toLowerCase() ===
        "yes";
      state.copy_mode =
        rowDataConfiguration.value.configuration.copy_mode.toLowerCase() ===
        "ips";
      state.mpm_algo = rowDataConfiguration.value.configuration.mpm_algo;
      state.profile = rowDataConfiguration.value.configuration.profile;
      const interfaces = listeInterfaces.value;
      const selectedInterfaces = rowDataConfiguration.value.interface_ids.map(
        (id) => {
          const matchingInterface = interfaces.find(
            (interfaces) => interfaces.id === id
          );
          return matchingInterface ? matchingInterface : null;
        }
      );

      // state.interface = selectedInterfaces.filter(Boolean).join(' ');
      state.interface = selectedInterfaces.filter(Boolean);
    });
    const handleRemove = () => {
      state.snackbar = false;
    };

    const onGridReady = (params) => {
      gridApi.value = params.api;

      gridApi.value.sizeColumnsToFit();
      window.addEventListener("resize", function () {
        setTimeout(function () {
          gridApi.value.sizeColumnsToFit();
        });
      });
      if (gridApi.value) {
        gridApi.value.setRowData(rowDataAF.value);
      } else {
        console.error("Grid API.");
      }
    };

    const openModalAdd = () => {
      state.modalData = {};
      state.modalMode = "create";
      state.isModalOpen = true;
    };

    const submitForm = async () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      if (!rowDataAF.value) {
        rowDataAF.value = [];
      }

      if (rowDataAF.value.length) {
        var mapedRow = rowDataAF.value.map((e) => {
          return {
            id: e.id,
            interface: e.interface,
            threads: e.threads,
            cluster_id: e.cluster_id,
            cluster_type: e.cluster_type,
            defrag: e.defrag,
            use_mmap: e.use_mmap,
            ring_size: e.ring_size,
            copy_mode: e.copy_mode,
            copy_iface: e.copy_iface,
          };
        });
      }

      let payload = {
        status_enabled: state.status_enabled,
        copy_mode: state.copy_mode,
        promisc: state.promisc,
        eve_log: state.eve_log,
        syslog: state.syslog,
        mpm_algo: state.mpm_algo.slug,
        profile: state.profile.slug,
        copy_mode: state.copyMode,
        list_interfaces: mapedRow,
      };
      state.loading = true;
      state.isLoadingDialogue = true;
      console.log("payload", payload);
      axios
        .put(
          "/ids-ips/UpdateGeneralConfig/" +
            rowDataConfiguration.value.configuration.id,
          payload
        )
        .then((response) => {
          if (response.status == 200) {
            state.loading = false;
            state.isLoadingDialogue = false;
            state.snackbar = true;
            state.color = "success";
            state.textAlert = "Configuration saved successfully!";
            // Automatically close the snackbar after 3000 milliseconds (3 seconds)
            setTimeout(() => {
              state.snackbar = false;
              location.reload();
            }, 3000);
          } else {
            state.loading = false;
            state.isLoadingDialogue = false;
            state.snackbar = true;
            state.color = "error";
            state.textAlert = "Failed to save configuration!";
            // Automatically close the snackbar after 3000 milliseconds (3 seconds)
            setTimeout(() => {
              state.snackbar = false;
              location.reload();
            }, 3000);
          }
        })
        .catch((i) => {
          state.loading = false;
          state.isLoadingDialogue = false;
          state.snackbar = true;
          state.color = "error";
          state.textAlert = error;
          setTimeout(() => {
            state.snackbar = false;
            location.reload();
          }, 3000);
        });
    };
    const cancel = () => {
      console.log("cancel");
    };

    return {
      switchValue,
      cancel,
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
