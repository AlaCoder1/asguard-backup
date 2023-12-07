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
  
      <v-row>
        <v-col cols="6">
          <div class="ml-3 mr-3">
            <h4>General information</h4>
            <v-divider class="mt-2"></v-divider>
            <v-row class="mt-2">
              <v-col cols="4" align-self="center">
                <label>Suricata</label>
              </v-col>
              <v-col cols="8" class="mb-n6">
                <input type="checkbox" v-model="state.status_enabled" />
                <label class="ml-2"> Enable IDS system</label>
              </v-col>
              <v-col cols="4" align-self="center">
                <label>IPS Mode</label>
              </v-col>
              <v-col cols="8" class="mb-n6">
                <input type="checkbox" v-model="state.copy_mode" />
                <label class="ml-2">Enable IPS </label>
              </v-col>
              <v-col cols="4" align-self="center">
                <label>Promisuous Mode</label>
              </v-col>
              <v-col cols="8" class="mb-n6">
                <input type="checkbox" v-model="state.promisc" />
                <label class="ml-2">Enable Promisuous Mode </label>
              </v-col>
              <v-col cols="4" align-self="center">
                <label>Enable syslog alerts</label>
              </v-col>
              <v-col cols="8" class="mb-n6">
                <input type="checkbox" v-model="state.syslog" />
                <label class="ml-2">Enable syslog alerts</label>
              </v-col>
              <v-col cols="4" align-self="center">
                <label>Enable eve syslog output</label>
              </v-col>
              <v-col cols="8" class="mb-n6">
                <input type="checkbox" v-model="state.eve_log" />
                <label class="ml-2">Enable syslog output</label>
              </v-col>
              <v-col cols="4" align-self="center">
                <label>Pattern matcher</label>
              </v-col>
              <v-col cols="8" class="mb-n6">
                <v-select
                  label="Pattern matcher"
                  v-model="state.mpm_algo"
                  item-title="name"
                  item-value="id"
                  return-object
                  :items="[
                    {
                      id: '1',
                      name: 'auto',
                      slug: 'auto',
                    },
                    {
                      id: '2',
                      name: 'ac',
                      slug: 'ac',
                    },
                    {
                      id: '3',
                      name: 'ac-ks',
                      slug: 'ac-ks',
                    },
                    {
                      id: '4',
                      name: 'hs',
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
                  item-value="id"
                  return-object
                  :items="[
                    {
                      id: '1',
                      name: 'medium',
                      slug: 'medium',
                    },
                    {
                      id: '2',
                      name: 'high',
                      slug: 'high',
                    },
                    {
                      id: '3',
                      name: 'low',
                      slug: 'low',
                    },
                  ]"
                ></v-select>
  
               
              </v-col>
              <v-col cols="4" align-self="center">
                <label>Interface</label>
              </v-col>
              <v-col cols="8" class="mb-n6">
                <v-select
                  v-model="state.interface"
                  label="Interface"
                  item-title="name"
                  item-value="id"
                  return-object
                  :items="state.mapedInterface"
                  multiple
                  background-color="#fffffff"
                >
                </v-select>
  
              
              </v-col>
            </v-row>
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
      <v-alert
        v-model="state.snackbar"
        :type="state.color"
        class="d-flex mt-3"
        style="position: fixed; top: 80px; right: 10px;"
      >
        <span class="c-o ml-3">
          <strong>{{ state.color }} </strong> {{ state.textAlert }}
        </span>
        <span class="ml-16" style="margin-top: 20px !important;">
          <i class="fas fa-times justify-end cursor" @click="handleRemove"></i>
        </span>
      </v-alert>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  import useValidate from "@vuelidate/core";
  import VButton from "@/components/VButton.vue";
  import { required, requiredIf, helpers } from "@vuelidate/validators";
  import UsersList from "../../system/user/components/UsersList.vue";
  import { reactive, onMounted, computed } from "vue";
  
  export default {
    name: "ConfigurationComponent",
    components: {
      UsersList,
      VButton,
    },
    setup() {
      const rowDataConfiguration = reactive({});
      const rowDataInterfaces = reactive({});
      const state = reactive({
        loading: false,
        isLoadingDialogue: false,
  
        snackbar: false,
        color: "",
        textAlert: "",
        //General information
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
        rowDataInterfaces.value = document.getElementById("app").attributes[
          "all_interfaces"
        ].value;
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
  
      onMounted(async () => {
        await getInterface();
        rowDataConfiguration.value = document.getElementById("app").attributes[
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
  
      const submitForm = async () => {
        const csrfToken = getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
        let payload = {
          status_enabled: state.status_enabled,
          copy_mode: state.copy_mode,
          promisc: state.promisc,
          eve_log: state.eve_log,
          syslog: state.syslog,
          mpm_algo: state.mpm_algo,
          profile: state.profile,
          interface: state.interface,
        };
        state.loading = true;
        state.isLoadingDialogue = true;
        axios
          .put(
            "/ids-ips/UpdateGeneralConfig/" +
              rowDataConfiguration.value.configuration.id,
            payload
          )
          .then((response) => {
            if (response.status == "200") {
              state.loading = false;
              state.isLoadingDialogue = false;
              state.snackbar = true;
              state.color = "success";
              state.textAlert = "Configuration saved successfully!";
              // Automatically close the snackbar after 3000 milliseconds (3 seconds)
              setTimeout(() => {
                state.snackbar = false;
              }, 2000);
            }
          })
          .catch((i) => {
            state.loading = false;
            state.isLoadingDialogue = false;
            state.snackbar = true;
            state.color = "red";
            state.textAlert = "Failed to save configuration!";
            setTimeout(() => {
              state.snackbar = false;
            }, 2000);
          });
       
      };
      const cancel = () => {
        console.log("cancel");
      };
  
      return {
        cancel,
        getCookie,
        getInterface,
        submitForm,
        clearInterface,
        handleRemove,
        state,
      };
    },
  };
  </script>
  
  <style lang="scss">
  .error-feedback {
    color: red;
    font-size: 0.85em;
  }
  </style>