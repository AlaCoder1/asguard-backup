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
            <div class="container" style="display: flex;">
              <h4>General information</h4>
              <div style="margin-left: auto; color: orange; margin-top: -17px;text: bold">
                  <v-switch id="mySwitch" 
                          color="warning" v-model="switchValue" label="Full help" />
                </div>
            
            </div>
            <v-divider class="mb-2"></v-divider>
         
          <v-row class="mt-2">
            <v-col cols="4" align-self="center">
              <label>Suricata</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <input type="checkbox" v-model="state.status_enabled" />
              <label class="ml-2"> Enable IDS system</label>
              <br />
              <small class="ml-5 error-feedback" v-show="switchValue">Enable intrusion detection system.</small>
            </v-col>
            <v-col cols="4" align-self="center">
              <label>IPS Mode</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <input type="checkbox" v-model="state.copy_mode" />
              <label class="ml-2">Enable IPS </label>
              <br /> 
              <small class="ml-5 error-feedback" v-show="switchValue">In IPS mode, Suricata actively blocks traffic according </small> <br/>
              <small class="ml-5 error-feedback" v-show="switchValue"> to intrusion detection rules.</small>
            </v-col>
            <v-col cols="4" align-self="center">
              <label>Promisuous Mode</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <input type="checkbox" v-model="state.promisc" />
              <label class="ml-2">Enable Promisuous Mode </label>
              <br/>
              <small class="ml-5 error-feedback" v-show="switchValue">Promiscuous mode allows Suricata to capture </small>
              <br /> 
              <small class="ml-5 error-feedback" v-show="switchValue"> and analyze all traffic on the network interface.</small>
            </v-col>
            <v-col cols="4" align-self="center">
              <label>Enable syslog alerts</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <input type="checkbox" v-model="state.syslog" />
              <label class="ml-2">Enable syslog alerts</label>
              <br/>
              <small class="ml-5 error-feedback" v-show="switchValue">Send alerts to system log in fast log format.</small>
              <br /> 
              <small class="ml-5 error-feedback" v-show="switchValue">This will not change the alert logging</small> <br/>
              <small class="ml-5 error-feedback" v-show="switchValue"> used by the product itself.</small>
            </v-col>
            <v-col cols="4" align-self="center">
              <label>Enable eve syslog output</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <input type="checkbox" v-model="state.eve_log" />
              <label class="ml-2">Enable syslog output</label>
              <br/>
              <small class="ml-5 error-feedback" v-show="switchValue">Enable Suricata to output events(logs) in EVE.</small> 
              <br /> 
              <small class="ml-5 error-feedback" v-show="switchValue">syslog format.EVE(Extensible Event Format) </small>
              <br/>
              <small class="ml-5 error-feedback" v-show="switchValue"> is a flexible logging format that can be used</small>
              <br/>
              <small class="ml-5 error-feedback" v-show="switchValue"> to analyze security events.</small>
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
                item-value="id"
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
              <small class="ml-5 error-feedback" v-show="switchValue">Specify the network interfaces on which Suricata</small> 
              <br/>
              <small class="ml-5 error-feedback" v-show="switchValue">should monitor traffic.</small>
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
  </div>

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
      style="position: fixed; top: 80px; right: 10px;"
    >
      <span class="c-o ml-3">
        <strong>{{ state.color }} </strong> {{ state.textAlert }}
      </span>
      <span class="ml-16" style="margin-top: 20px !important;">
        <i class="fas fa-times justify-end cursor" @click="handleRemove"></i>
      </span>
    </v-alert>
  <!-- </div> -->
</template>

<script>
import axios from "axios";
import useValidate from "@vuelidate/core";
import VButton from "@/components/VButton.vue";
import { required, requiredIf, helpers } from "@vuelidate/validators";
import UsersList from "../../system/user/components/UsersList.vue";
import { reactive, onMounted, computed,ref } from "vue";

export default {
  name: "ConfigurationComponent",
  components: {
    UsersList,
    VButton,
  },
  setup() {
    const rowDataConfiguration = reactive({});
    const rowDataInterfaces = reactive({});
    const switchValue = ref(false)
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
      const reloadData = async() => {
        const csrfToken = getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken; 
        state.loading = true;
        state.isLoadingDialogue = true;
        try {
        const response = await axios.post(
          "activerSuricataUpdate/" +  rowDataConfiguration.value.configuration.id
        );
        if (response.status === 200 ) {
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
                location.reload();
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
                location.reload();

              }, 2000);
       
      }
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
          if (response.status == 200) {
            state.loading = false;
            state.isLoadingDialogue = false;
            state.snackbar = true;
            state.color = "success";
            state.textAlert = "Configuration saved successfully!";
            // Automatically close the snackbar after 3000 milliseconds (3 seconds)
            setTimeout(() => {
              state.snackbar = false;
              location.reload()
            }, 3000);
          }
          else{
            state.loading = false;
            state.isLoadingDialogue = false;
            state.snackbar = true;
            state.color = "error";
            state.textAlert = "Failed to save configuration!";
            // Automatically close the snackbar after 3000 milliseconds (3 seconds)
            setTimeout(() => {
              state.snackbar = false;
              location.reload()
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
            location.reload()
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
      reloadData
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