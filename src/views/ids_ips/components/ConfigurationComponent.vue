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
          <v-col cols="4" align-self="center">
            <label>IPS Mode</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <input type="checkbox" v-model="state.mode_inline" />
            <label class="ml-2">Enable IPS </label>
            <br />
            <small class="ml-5 error-feedback" v-show="switchValue"
              >In IPS mode, Suricata actively blocks traffic according
            </small>
            <br />
            <small class="ml-5 error-feedback" v-show="switchValue">
              to intrusion detection rules.</small
            >
          </v-col>
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
              :items="state.algoLists"
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
              :items="state.profileLists"
            ></v-select>
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
  <ModalAddInterface :isOpen="state.isModalOpen" :modalMode="state.modalMode"  />
  <!-- <ModalAddInterface
    :isOpen="state.isModalOpen"
    :editRow="state.editRow"
    :modalMode="state.modalMode"
    :rowDataList="rowDataAF.value"
  /> -->
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
// import useValidate from "@vuelidate/core";
import VButton from "@/components/VButton.vue";
// import { required, requiredIf, helpers } from "@vuelidate/validators";
import UsersList from "../../system/user/components/UsersList.vue";
import { reactive, onMounted, computed, ref, inject } from "vue";
import ModalAddInterface from "@/components/modals/ModalAddInterface.vue";
import { v4 as uuidv4 } from "uuid";

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
    const rowDataInterfaces = reactive({});
    const switchValue = ref(false);
    const state = reactive({
      interId: null,
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

    const columnAF = [
      {
        headerName: "Interface",
        field: "name_interface",
        // cellRenderer: actionCopyInterface,
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
        field: "copy_iface",
        // cellRenderer: actionCopyIface,
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
        cellRenderer: actionCellRenderer,
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
          ifname: i.ifname,
        };
      });
      listeInterfaces.value = interfaces;
      state.mapedInterface = interfaces;
    };

    // function actionCopyIface(data) {
    //   console.log("data", data);
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

    //   console.log("filtredInterfaceIface", filtredInterface[0]);

    //   eGui.innerHTML = `
    //     ${filtredInterface[0].name}
    //    `;
    //   return eGui;
    // }

    // function actionCopyInterface(data) {
    //   console.log("data", data);
    //   let eGui = document.createElement("div");

    //   let filtredInterface = listeInterfaces.value.filter(
    //     (i) => i.name === data.data.name_interface
    //   );
    //   console.log("filtredInterface*****", filtredInterface[0]);

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
        // case "edit":
        //   // state.modalData = {};
        //   // state.modalMode = "edit";
        //   // state.isModalOpen = true;
        //   // state.editRow = rowData;

        //   break;
        case "delete":
          const index = rowDataAF.value.findIndex(
            (item) => item.id === rowData.id
          );

          if (index !== -1) {
            rowDataAF.value.splice(index, 1);
            if (gridApi.value) {
              gridApi.value.setRowData(rowDataAF.value);
            } else {
              console.error("Grid API.");
            }
          }
          break;
        default:
          break;
      }
    };

    const reloadData = async () => {
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
          state.textAlert = "Rules saved successfully!";
          // Automatically close the snackbar after 3000 milliseconds (3 seconds)
          setTimeout(() => {
            state.snackbar = false;
          }, 1000);
        } else {
          state.loading = false;
          state.isLoadingDialogue = false;
          state.snackbar = true;
          state.color = "error";
          state.textAlert = "Failed to save rule!";
          // Automatically close the snackbar after 3000 milliseconds (3 seconds)
          setTimeout(() => {
            state.snackbar = false;
            location.reload();
          }, 1000);
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
          location.reload();
        }, 1000);
      }
    };

    onMounted(async () => {
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
          console.error("Grid API.");
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
          console.error("Grid API.");
        }
      });

      let rowConfiguration =
        document.getElementById("app").attributes["general_config_suricata"]
          .value;
      let rowConfig = JSON.parse(rowConfiguration);

      state.status_enabled = rowConfig.configuration.status_enabled;
      state.mode_inline = rowConfig.configuration?.mode_inline;
      state.promisc = rowConfig.configuration.promisc;
      state.syslog = rowConfig.configuration.syslog.toLowerCase() === "yes";
      state.eve_log = rowConfig.configuration.eve_log.toLowerCase() === "yes";

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
        console.error("Grid API.");
      }
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
      emitter.emit("list-Interface", rowDataAF.value);
    };

    const submitForm = async () => {
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
              state.loading = false;
              state.isLoadingDialogue = false;
              state.snackbar = true;
              state.color = "success";
              state.textAlert = "Configuration saved successfully!";
              // Automatically close the snackbar after 3000 milliseconds (3 seconds)
              setTimeout(() => {
                state.snackbar = false;
                location.reload();
              }, 1000);
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
              }, 1000);
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
            }, 1000);
          });
      } else {
        state.snackbar = true;
        state.color = "error";
        state.textAlert = "Minimum One Interface In AF Packet";
        setTimeout(() => {
          state.snackbar = false;
        }, 2000);
      }
    };
    const cancel = () => {};

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
