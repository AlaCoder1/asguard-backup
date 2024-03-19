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
        <h4>General information</h4>
       
        <v-divider class="mb-2"></v-divider>
      </div>
      <v-row class="ml-3 mr-3">
        <v-col cols="6">
          <v-row class="mt-2">
            <v-col cols="4" align-self="center">
              <label>DHCPServer</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <input type="checkbox" v-model="state.enable_dhcpv4 " />
              <label class="ml-2"> Enable DHCP server on this interface</label>
            </v-col>
            <v-col cols="4" align-self="center">
              <label>Subnet Address</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                v-model="state.subnet_addr"
                required
                readonly
              ></v-text-field>
            </v-col>
            <v-col cols="4" align-self="center">
              <label>Subnet Mask</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <!-- <label class="ml-2"> {{state.subnet_mask}}</label> -->
              <v-text-field
                v-model="state.subnet_mask"
                required
                readonly

              ></v-text-field>
            </v-col>
            <v-col cols="4" align-self="center">
              <label>Available Range</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                v-model="state.available_range"
                required
                readonly
              ></v-text-field>
            </v-col>
            <v-col cols="4" align-self="center">
              <label>Range from</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                v-model="state.range_from"
                required
              ></v-text-field>
            </v-col>
            <v-col cols="4" align-self="center">
              <label>Range to</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                v-model="state.range_to"
                required
              ></v-text-field>
            </v-col>

            <v-col cols="4" align-self="center">
              <label>DNS server</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                v-model="state.dns_server"
                required
              ></v-text-field>
            </v-col>
          
            <v-col cols="4" align-self="center">
              <label>Gateway</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                v-model="state.gateway"
                required
              ></v-text-field>
            </v-col>
            
            <v-col cols="4" align-self="center">
              <label>Domain name</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                v-model="state.domain_name"
                required
              ></v-text-field>
            </v-col>
            
          </v-row>
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
  </template>
  
  <script>
  import { AgGridVue } from "ag-grid-vue3";
  import "ag-grid-community/styles/ag-grid.css";
  import "ag-grid-community/styles/ag-theme-alpine.css";
  import axios from "axios";
  import VButton from "@/components/VButton.vue";
  import UsersList from "../../system/user/components/UsersList.vue";
  import { reactive, onMounted, ref, inject } from "vue";
  import ModalAddInterface from "@/components/modals/ModalAddInterface.vue";
  
  export default {
    name: "ConfigServerDhcp4Component",
    components: {
      UsersList,
      VButton,
      AgGridVue,
      ModalAddInterface,
    },
    props: {
      configInfo: {},
  },
    setup(props) {
      // console.log(props.configInfo)
      const emitter = inject("emitter");
      const switchValue = ref(false);
      const state = reactive({
        
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
        enable_dhcpv4:false,
        subnet_addr: null,
        subnet_mask: null,
        available_range: null,
        range_from:[],
        range_to: [],
        dns_server:[],
        gateway: null,
        domain_name: null,
      
      });
  
      state.enable_dhcpv4 = props.configInfo.enable_dhcpv4;
      state.subnet_addr = props.configInfo.subnet_addr;
      state.subnet_mask = props.configInfo.subnet_mask;
      state.available_range = props.configInfo.available_range;
      state.range_from = props.configInfo.range_from;
      state.range_to = props.configInfo.range_to;
      state.dns_server = props.configInfo.dns_server;
      state.gateway = props.configInfo.gateway;
      state.domain_name = props.configInfo.domain_name;
      
      
    
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


      const submitForm = async () => {
        const csrfToken = getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
  
          let payload = {
            enable_dhcpv4: state.enable_dhcpv4,
            subnet_addr: state.subnet_addr,
            subnet_mask: state.subnet_mask,
            available_range: state.available_range,
            dns_server: Array.isArray(state.dns_server) ? state.dns_server : [state.dns_server],
            gateway: state.gateway,
            domain_name: state.domain_name,
            ranges_from: Array.isArray(state.range_from) ? state.range_from : [state.range_from],
            ranges_to: Array.isArray(state.range_to) ? state.range_to : [state.range_to],

          };
          state.loading = true;
          state.isLoadingDialogue = true;
        
          axios
            .put("/server_dhcp4/updateDhcp4Server/" + props.configInfo.id, payload)
            .then((response) => {
              if (response.status == 200) {
                state.loading = false;
                state.isLoadingDialogue = false;
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.msg;
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
                state.textAlert = response.data.msg;
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
              state.textAlert = i.response.data.msg;
              setTimeout(() => {
                state.snackbar = false;
                location.reload();
              }, 1000);
            });
        
      };
      const cancel = () => {};
  
      return {
        switchValue,
        cancel,
        getCookie,
        submitForm,
        state,
        emitter,
      
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
  