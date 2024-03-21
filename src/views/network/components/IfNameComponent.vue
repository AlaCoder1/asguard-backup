<template>
  <v-card>
    <v-form @submit.prevent="handleSubmit(onSubmit)">
      <v-row class="fill-height ml-3">
        <v-col cols="12" sm="6">
          <v-card-title class="title-text">Basic Configuration</v-card-title>
          <v-divider class="ml-3"></v-divider>
          <v-row class="ml-3 mt-3">
            <div style="color: black">Interface</div>
            <input type="checkbox" class="ml-5" v-model="activate" />
            <label class="ml-2">Activate</label>
          </v-row>
          <div class="ml-3" style="background-color: #f6f6f6">
            <v-row class="ml-3 mt-5">
              <v-col class="device-style"
                >Device<span style="color: red">*</span></v-col
              >
            </v-row>
            <v-row class="ml-3 mr-3">
              <v-text-field :model-value="device" readonly></v-text-field>
            </v-row>
          </div>
          <div class="ml-3" style="background-color: #f6f6f6">
            <v-row class="ml-3 mt-5">
              <v-col class="device-style"
                >Description <span style="color: red">*</span>
              </v-col>
            </v-row>
            <v-row class="ml-3 mr-3">
              <v-text-field
                v-model="description"
                :rules="[(v) => !!v || 'Description is required']"
                required
              ></v-text-field>
            </v-row>
          </div>
          <v-card-title class="title-text mt-5"
            >Generic configuration</v-card-title
          >
          <v-divider class="ml-3 mb-5"></v-divider>
          <table class="ml-3">
            <tbody>
              <tr>
                <td>
                  <div>Block networks</div>
                </td>
                <td>
                  <input type="checkbox" v-model="private_aux" class="ml-5" />
                  <label>Private</label>
                </td>
              </tr>
              <tr>
                <td>
                  <div class="mt-5">Block Bogon addresses</div>
                </td>
                <td>
                  <input type="checkbox" v-model="bogon_aux" class="ml-5" />
                  <label>Not assigned by IANA</label>
                </td>
              </tr>
              <tr>
                <td>
                  <div>
                    IPV4 Setup Type
                    <span style="color: red">*</span>
                  </div>
                </td>
                <td class="new-style">
                  <v-select
                    background-color="#f6f6f6"
                    v-model="setuptypeip4"
                    :items="items.map((item) => item.value)"
                    class="ml-3"
                    :rules="[(v) => !!v || 'IPV4 Setup Type is required']"
                  ></v-select>
                </td>
              </tr>
              <tr>
                <td>
                  <div style="color: #020202">MAC address</div>
                </td>
                <td>
                  <v-text-field
                    label="Enter MAC address"
                    class="ml-3"
                    v-model="addmac"
                    :rules="[macAddressValidation]"
                  ></v-text-field>
                </td>
              </tr>
              <tr>
                <td>
                  <div>MTU (Maximum Transmission Unit)</div>
                </td>
                <td>
                  <v-text-field
                    label="Enter MTU"
                    class="ml-3"
                    v-model="mtuv"
                    :rules="[validateRange]"
                  ></v-text-field>
                </td>
              </tr>
              <tr>
                <td>
                  <div>MSS</div>
                </td>
                <td>
                  <v-text-field
                    label="Enter MSS"
                    class="ml-3"
                    v-model="mssv"
                  ></v-text-field>
                </td>
              </tr>
              <tr>
                <td>
                  <span style="color: #020202">Speed and Duplex</span>
                </td>
                <td>
                  <v-select
                    v-model="speed_duplex"
                    :items="speedDuplexItems.map((item) => item)"
                    class="ml-3 speed-duplex-style"
                  ></v-select>
                </td>
              </tr>
            </tbody>
          </table>
        </v-col>
        <v-col cols="12" sm="6">
          <div v-if="setuptypeip4 === 'static'">
            <v-card-title class="title-text"
              >Static IPV4 address configuration</v-card-title
            >
            <v-divider class="ml-3 mr-3"></v-divider>
            <div class="mr-2 ml-2">
              <v-row class="mt-2">
                <v-col align-self="center" cols="4">
                  <label>IPV4 address</label>
                  <small style="color: red">*</small>
                </v-col>
                <v-col cols="4" class="mb-n6">
                  <v-text-field
                    label="Enter IPV4 address"
                    v-model="value_setup_Ipv4.ip_address4"
                    class="ip-address-style"
                    :rules="[
                      (v) => !!v || 'IPV4 address is required',
                      () => ipAddressValidation(value_setup_Ipv4.ip_address4),
                    ]"
                  ></v-text-field>
                </v-col>
                <v-col cols="4" class="mb-n6">
                  <v-select
                    v-model="value_setup_Ipv4.netmask4"
                    :items="netmaskItems"
                    class="ml-3 netmask-select-style"
                    :rules="[(v) => !!v || 'Netmask is required']"
                  ></v-select>
                </v-col>
                <v-col align-self="center" cols="4">
                  <label>IPV4 gateway</label>
                  <small style="color: red">*</small>
                </v-col>
                <v-col cols="2" class="mb-n6" align-self="center">
                  <v-btn
                    color="#F6F6F6"
                    class="text-none"
                    variant="flat"
                    @click="openGatewayDialog"
                  >
                    <svg
                      width="17"
                      height="17"
                      viewBox="0 0 17 17"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <mask
                        id="mask0_50_190"
                        style="mask-type: luminance"
                        maskUnits="userSpaceOnUse"
                        x="0"
                        y="0"
                        width="17"
                        height="17"
                      >
                        <path d="M17 0H0V17H17V0Z" fill="white" />
                      </mask>
                      <g mask="url(#mask0_50_190)">
                        <path
                          d="M8.70871 0.219971C10.3463 0.219971 11.9472 0.705584 13.3088 1.6154C14.6705 2.52522 15.7317 3.81838 16.3584 5.33135C16.9851 6.84432 17.1491 8.50916 16.8296 10.1153C16.5101 11.7215 15.7215 13.1968 14.5636 14.3548C13.4056 15.5128 11.9302 16.3014 10.3241 16.6209C8.7179 16.9404 7.05306 16.7764 5.54009 16.1497C4.02712 15.523 2.73396 14.4617 1.82414 13.1001C0.914324 11.7385 0.428711 10.1376 0.428711 8.49997C0.428976 6.30406 1.30142 4.19816 2.85416 2.64542C4.4069 1.09268 6.5128 0.220236 8.70871 0.219971Z"
                          fill="#086EAE"
                        />
                        <path
                          d="M13.6689 8.03597C13.7332 8.09478 13.7842 8.16654 13.8187 8.24652C13.8531 8.32651 13.8703 8.41289 13.8689 8.49997C13.8703 8.58779 13.8542 8.675 13.8216 8.75654C13.789 8.83808 13.7405 8.91233 13.6789 8.97497C13.6167 9.04086 13.5412 9.09277 13.4574 9.12725C13.3736 9.16173 13.2835 9.178 13.1929 9.17497H9.36591V12.981C9.36918 13.0709 9.35391 13.1606 9.32105 13.2443C9.28819 13.3281 9.23845 13.4042 9.17491 13.468C9.11435 13.5295 9.04187 13.578 8.96191 13.6105C8.88195 13.643 8.7962 13.6588 8.70991 13.657C8.62268 13.6583 8.53614 13.6412 8.45599 13.6068C8.37585 13.5723 8.30391 13.5212 8.24491 13.457C8.18336 13.3943 8.13487 13.3201 8.10225 13.2385C8.06963 13.157 8.05354 13.0698 8.05491 12.982V9.17697H4.22791C4.04915 9.17414 3.87848 9.10194 3.75197 8.97562C3.62546 8.84929 3.553 8.67873 3.54991 8.49997C3.54829 8.41285 3.5653 8.32639 3.59979 8.24637C3.63428 8.16635 3.68546 8.09462 3.74991 8.03597C3.81266 7.97421 3.88704 7.92552 3.96876 7.89274C4.05047 7.85995 4.13788 7.84371 4.22591 7.84497H8.05491V4.03797C8.04956 3.85273 8.11789 3.67292 8.24491 3.53797C8.30487 3.47498 8.37701 3.42483 8.45694 3.39056C8.53688 3.35629 8.62294 3.33862 8.70991 3.33862C8.79688 3.33862 8.88294 3.35629 8.96288 3.39056C9.04281 3.42483 9.11495 3.47498 9.17491 3.53797C9.3023 3.67276 9.37099 3.85259 9.36591 4.03797V7.84497H13.1929C13.2809 7.84377 13.3683 7.86003 13.45 7.89281C13.5317 7.9256 13.6061 7.97426 13.6689 8.03597Z"
                          fill="white"
                        />
                      </g>
                    </svg>
                    <span class="ml-2" style="color: #086eae">Add</span>
                  </v-btn>
                </v-col>
                <v-col cols="6" class="mb-n6">
                  <v-select
                    v-model="value_setup_Ipv4.gateway4.value"
                    :items="allStaticGatewaysAddresses"
                    :rules="[(v) => !!v || 'IPV4 gateway is required']"
                  ></v-select>
                </v-col>
              </v-row>
            </div>
          </div>
          <div v-if="setuptypeip4 === 'dhcp'">
            <v-card-title class="title-text"
              >Configuring the DHCP Client</v-card-title
            >
            <v-divider class="ml-3"></v-divider>
            <ConfigDHCPv4
              :ipAddress="value_setup_Ipv4.ip_address4"
              v-model:alias_add="interface.alias_add"
              v-model:alias_mask="interface.alias_mask"
              v-model:rejectLeases="interface.rejectLeases"
              v-model:hostname="interface.hostname"
              v-model:overrideMTU="interface.overrideMTU"
            />
            <v-row class="advanced-parameters-style">
              <label class="ml-3">Advanced parameters</label>
              <input
                type="checkbox"
                id="advancedParameters"
                name="advancedParameters"
                value="true"
                v-model="advancedParameters"
                class="ml-3"
              />
            </v-row>
            <AdvancedConfigDHCPv4
              v-if="advancedParameters"
              v-model:typeDHCP4="typeDHCP4"
              v-model:timeout="AdvancedConfigDHCPv4.timeout"
              v-model:retry="AdvancedConfigDHCPv4.retry"
              v-model:select_timeout="AdvancedConfigDHCPv4.select_timeout"
              v-model:reboot="AdvancedConfigDHCPv4.reboot"
              v-model:backoff="AdvancedConfigDHCPv4.backoff"
              v-model:initial_interval="AdvancedConfigDHCPv4.initial_interval"
              v-model:dhcp_client="AdvancedConfigDHCPv4.dhcp_client"
              v-model:lease_time="AdvancedConfigDHCPv4.lease_time"
              v-model:request="AdvancedConfigDHCPv4.request"
              v-model:require="AdvancedConfigDHCPv4.require"
              v-model:domain_name="AdvancedConfigDHCPv4.domain_name"
              v-model:domain_server="AdvancedConfigDHCPv4.domain_server"
            />
          </div>
        </v-col>
      </v-row>
      <v-spacer></v-spacer><v-spacer></v-spacer>
      <div class="text-center">
        <VButton
          large
          rounded
          outlined
          color="#FFFF"
          label-color="#213E9F"
          label="cancel"
          :isLarge="true"
          @click="cancel"
        />
        <VButton
          large
          rounded
          outlined
          color="#213E9F"
          label-color="#ffff"
          label="save"
          :isLarge="true"
          type="submit"
          class="ml-2"
        />
      </div>
      <br /><br /><br />
      <v-alert
        type="success"
        class="d-flex mt-3"
        style="align-self: flex-end"
        elevation="2"
        icon="mdi-check-circle-outline"
        border="top"
        v-if="showAlertGateway"
        :style="alertStyle"
      >
        Gateway added successfully
      </v-alert>
      <v-alert
        type="success"
        class="d-flex mt-3"
        style="align-self: flex-end"
        elevation="2"
        icon="mdi-check-circle-outline"
        border="top"
        v-if="showAlert"
        :style="alertStyle"
      >
        Configuration saved successfully
      </v-alert>
      <v-dialog
        v-model="showGatewayDialog"
        max-width="600px"
        class="gateway-dialog"
      >
        <v-card class="ml-3 mr-3">
          <v-card-title class="title-text">
            <span class="headline font-weight-bold">Add IPv4 Gateway</span>
          </v-card-title>
          <v-card-text>
            <v-form>
              <v-container>
                <v-row>
                  <v-text-field
                    label="Enter Gateway Name"
                    v-model="gateway.gwname"
                  ></v-text-field>
                </v-row>
                <v-row>
                  <v-text-field
                    label="Enter Gateway IPV4"
                    clsas="w-100"
                    v-model="gateway.gwaddress"
                  ></v-text-field>
                </v-row>
                <v-row>
                  <v-text-field
                    label="Enter Description"
                    v-model="gateway.description"
                  ></v-text-field
                ></v-row>
                <v-row>
                  <input type="checkbox" v-model="gateway.default_aux" />
                  <label class="ml-3">Default Gateway</label>
                </v-row>
                <v-row>
                  <input type="checkbox" v-model="gateway.far_aux" />
                  <label class="ml-3">Far Gateway</label>
                </v-row>
                <v-row>
                  <input type="checkbox" v-model="gateway.multiwan_aux" />
                  <label class="ml-3">Multi-WAN Gateway</label>
                </v-row>
              </v-container>
            </v-form>
          </v-card-text>
          <div class="text-center">
            <VButton
              large
              rounded
              outlined
              color="#FFFF"
              label-color="#213E9F"
              label="cancel"
              :isLarge="true"
              @click="cancelGateway"
            />
            <VButton
              large
              rounded
              outlined
              color="#213E9F"
              label-color="#ffff"
              label="save"
              :isLarge="true"
              type="submit"
              class="ml-2"
              @click="addGateway"
            />
          </div>
          <br />
        </v-card>
      </v-dialog>
    </v-form>
  </v-card>
</template>

<script>
import axios from "axios";
import ConfigDHCPv4 from "./configDHCP/ConfigDHCPv4.vue";
import AdvancedConfigDHCPv4 from "./configDHCP/AdvancedConfigDHCPv4.vue";
import VButton from "../../../components/VButton.vue";
import netmaskItems from "../../../constants/netmask.js";

export default {
  name: "IfNameComponent",
  components: {
    ConfigDHCPv4,
    VButton,
    AdvancedConfigDHCPv4,
  },
  props: {
    activeTab: String,
  },
  data() {
    return {
      typeDHCP4: "",
      advancedParameters: false,
      interface: {
        alias_add: "",
        alias_mask: "",
        rejectLeases: "",
        hostname: "",
        overrideMTU: false,
      },
      items: [],
      speedDuplexItems: [
        "100baseTx-FD",
        "100baseTx-HD",
        "10baseT-FD",
        "10baseT-HD",
        "100baseTX",
        "10BaseT/UTP full duplex",
        "10BaseT/UTP",
      ],
      netmaskItems: netmaskItems,
      activate: false,
      device: "",
      description: "",
      private_aux: false,
      bogon_aux: false,
      setuptypeip4: "static",
      addmac: "",
      mtuv: "",
      mssv: "",
      speed_duplex: "",
      dynamicGatewayPolicy: false,
      showAlert: false,
      name_interface: "",
      value_setup_Ipv4: {
        ip_address4: "",
        netmask4: "",
        gateway4: {
          id: "",
          value: "",
        },
      },
      IPV4Config: {},
      allStaticGateways: [],
      showGatewayDialog: false,
      gateway: {
        gwname: "",
        gwaddress: "",
        description: "",
        default_aux: false,
        far_aux: false,
        multiwan_aux: false,
      },
      showAlertGateway: false,
      AdvancedConfigDHCPv4: {
        timeout: "",
        retry: "",
        select_timeout: "",
        select_timeout: "",
        reboot: "",
        backoff: "",
        initial_interval: "",
        dhcp_client: "",
        lease_time: "",
        request: "",
        require: "",
        domain_name: "",
        domain_server: "",
      },
    };
  },
  computed: {
    alertStyle() {
      return {
        position: "fixed",
        top: "60px",
        right: "20px",
        width: "20%",
      };
    },
    allStaticGatewaysAddresses() {
      return this.allStaticGateways.map((gateway) => gateway.gwaddress);
    },
  },
  methods: {
    validateRange(value) {
      const num = parseFloat(value); // Parse the value to a number

      if (isNaN(num)) {
        return true; // Return true if the value is not a number
      }

      if (num < 1500 || num > 9000) {
        return "Number must be between 1500 and 9000";
      }

      return true; // Return true when the value is within the range
    },
    macAddressValidation(value) {
      // if value is empty, return true
      if (!value) {
        return true;
      }

      // Regular expression for MAC address validation
      const macRegex = /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/;

      // Validate the input value against the regex
      if (!macRegex.test(value)) {
        return "Please enter a valid MAC address"; // Error message for invalid MAC address
      }
      return true; // Return true when the input is valid
    },
    ipAddressValidation(value) {
      if (!value) {
        return true;
      }

      // Regular expression for IP address validation
      const ipRegex =
        /^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;

      // Validate the input value against the regex
      if (!ipRegex.test(value)) {
        return "Please enter a valid IP address"; // Error message for invalid IP address
      }
      return true; // Return true when the input is valid
    },
    addNetwork() {
      if (this.advancedParameters) {
        this.typeDHCP4 = "Advanced";
      } else {
        this.typeDHCP4 = "Base";
      }
      // todo: add network refactoring && optimization needed
      if (this.setuptypeip4 === "static") {
        const params = {
          name_interface: this.activeTab,
          device: this.device,
          description: this.description,
          private_aux: this.private_aux,
          bogon_aux: this.bogon_aux,
          addmac: this.addmac,
          mtuv: this.mtuv,
          mssv: this.mssv,
          speed_duplex: this.speed_duplex,
          setuptypeIP4: this.setuptypeip4,
          value_setup_Ipv4: {
            ip_address4: this.value_setup_Ipv4.ip_address4,
            netmask4: this.value_setup_Ipv4.netmask4,
            gateway4: {
              value: this.value_setup_Ipv4.gateway4.value,
            },
          },
        };

        function getCookie(name) {
          let cookieValue = null;
          if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
              const cookie = cookies[i].trim();
              // Does this cookie string begin with the name we want?
              if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(
                  cookie.substring(name.length + 1)
                );
                break;
              }
            }
          }
          return cookieValue;
        }
        const csrfToken = getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

        axios.put("/network/conf/" + this.activeTab, params).then(
          () => {
            this.showAlert = true;
            setTimeout(() => {
              this.showAlert = false;
            }, 3000);
          },
          (error) => {
            console.log(error);
          }
        );
      }
      if (this.setuptypeip4 === "dhcp") {
        const params = {
          name_interface: this.activeTab,
          device: this.device,
          description: this.description,
          private_aux: this.private_aux,
          bogon_aux: this.bogon_aux,
          addmac: this.addmac,
          mtuv: this.mtuv,
          mssv: this.mssv,
          speed_duplex: this.speed_duplex,
          setuptypeIP4: this.setuptypeip4,
          value_setup_Ipv4: {
            typeDHCP4: this.typeDHCP4,
            alias_add: this.interface.alias_add,
            alias_mask: this.interface.alias_mask,
            reject: this.interface.rejectLeases,
            hostname: this.interface.hostname,
            timeout: this.AdvancedConfigDHCPv4.timeout,
            retry: this.AdvancedConfigDHCPv4.retry,
            backoff: this.AdvancedConfigDHCPv4.backoff,
            reboot: this.AdvancedConfigDHCPv4.reboot,
            select_timeout: this.AdvancedConfigDHCPv4.select_timeout,
            initial_interval: this.AdvancedConfigDHCPv4.initial_interval,
            send_options_dhcp_client:
              this.AdvancedConfigDHCPv4.send_options_dhcp_client,
            request: this.AdvancedConfigDHCPv4.request,
            require: this.AdvancedConfigDHCPv4.require,
            supersede_domain_name:
              this.AdvancedConfigDHCPv4.supersede_domain_name,
            prepend_domain_server:
              this.AdvancedConfigDHCPv4.prepend_domain_server,
          },
        };
        function getCookie(name) {
          let cookieValue = null;
          if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
              const cookie = cookies[i].trim();
              // Does this cookie string begin with the name we want?
              if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(
                  cookie.substring(name.length + 1)
                );
                break;
              }
            }
          }
          return cookieValue;
        }
        const csrfToken = getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

        axios.put("/network/conf/" + this.activeTab, params).then(
          () => {
            this.showAlert = true;
            setTimeout(() => {
              this.showAlert = false;
            }, 3000);
          },
          (error) => {
            console.log(error);
          }
        );
      }
    },
    cancel() {
      // todo: reset form values to initial values
    },
    openGatewayDialog() {
      this.showGatewayDialog = true;
    },
    addGateway() {
      const params = {
        gwname: this.gateway.gwname,
        gwaddress: this.gateway.gwaddress,
        description: this.gateway.description,
        default_aux: this.gateway.default_aux,
        far_aux: this.gateway.far_aux,
        multiwan_aux: this.gateway.multiwan_aux,
      };
      function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
          const cookies = document.cookie.split(";");
          for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === name + "=") {
              cookieValue = decodeURIComponent(
                cookie.substring(name.length + 1)
              );
              break;
            }
          }
        }
        return cookieValue;
      }
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.post("/gateway/addStaticGateway", params).then(
        (response) => {
          if (response.status == "200") {
            this.showGatewayDialog = false;
            this.gateway = {
              gwname: "",
              gwaddress: "",
              description: "",
              default_aux: true,
              far_aux: false,
              multiwan_aux: false,
            };
            this.showAlertGateway = true;
            setTimeout(() => {
              this.showAlertGateway = false;
            }, 3000);
          } else {
            this.showGatewayDialog = true;
          }
        },
        (error) => {
          console.log(error);
        }
      );
    },
    cancelGateway() {
      this.showGatewayDialog = false;
      this.gateway = {
        gwname: "",
        gwaddress: "",
        description: "",
        default_aux: true,
        far_aux: false,
        multiwan_aux: false,
      };
    },
    updateGateway() {
      const params = {
        gwname: this.gateway.gwname,
        gwaddress: this.gateway.gwaddress,
        description: this.gateway.description,
        default_aux: this.gateway.default_aux,
        far_aux: this.gateway.far_aux,
        multiwan_aux: this.gateway.multiwan_aux,
      };
      function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
          const cookies = document.cookie.split(";");
          for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === name + "=") {
              cookieValue = decodeURIComponent(
                cookie.substring(name.length + 1)
              );
              break;
            }
          }
        }
        return cookieValue;
      }
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.put("/gateway/updateStaticGateway", params).then(
        (response) => {
          this.showAlert = true;
          setTimeout(() => {
            this.showAlert = false;
          }, 3000);
        },
        (error) => {
          console.log(error);
        }
      );
    },
    onSubmit() {
      this.addNetwork();
    },
    handleSubmit() {
      this.onSubmit();
    },
  },
  beforeMount: async function () {
    let interfaces =
      document.getElementById("app").attributes["interfaces"].value;

    let validJsonStringInterface = interfaces
      .replace(/'/g, '"')
      .replace(/True/g, "true")
      .replace(/False/g, "false")
      .replace(/None/g, "null");
    let parsedArrayInterface = JSON.parse(validJsonStringInterface);

    let tab = localStorage.getItem("network-tab");
    let filtredInterface = parsedArrayInterface.filter(
      (i) => i.name_interface === tab
    );
    if (filtredInterface[0].ifname.startsWith("vlan")) {
      this.items.push({ id: 1, value: "static" });
    } else {
      this.items.push({ id: 1, value: "static" }, { id: 2, value: "dhcp" });
    }

    this.IPV4Config =
      document.getElementById("app").attributes["ipv4config"].value;
    let validJsonString = this.IPV4Config.replace(/'/g, '"')
      .replace(/True/g, "true")
      .replace(/False/g, "false")
      .replace(/None/g, "null");
    let parsedArray = JSON.parse(validJsonString);
    this.IPV4Config = parsedArray[this.activeTab];

    this.allStaticGateways =
      document.getElementById("app").attributes["allStaticGateways"].value;
    validJsonString = this.allStaticGateways
      .replace(/'/g, '"')
      .replace(/True/g, "true")
      .replace(/False/g, "false")
      .replace(/None/g, "null");
    parsedArray = JSON.parse(validJsonString);
    this.allStaticGateways = parsedArray;

    this.activate = this.IPV4Config?.interface !== null ? true : false;
    this.device = this.IPV4Config.interface.ifname;
    this.description = this.IPV4Config.interface.description;

    this.private_aux = this.IPV4Config.interface.private_aux;
    this.bogon_aux = this.IPV4Config.interface.bogon_aux;

    this.addmac = this.IPV4Config.genericConfig.addmac;
    this.mtuv = this.IPV4Config.genericConfig.mtuv;
    this.mssv = this.IPV4Config.genericConfig.mssv;
    this.speed_duplex = this.IPV4Config.genericConfig.speed_duplex;

    this.setuptypeip4 = this.IPV4Config.IPV4Config.typeip4;
    this.value_setup_Ipv4.ip_address4 = this.IPV4Config.IPV4Config.ip_address;
    this.value_setup_Ipv4.netmask4 = this.IPV4Config.IPV4Config.netmask;

    this.name_interface = this.IPV4Config.interface.name_interface;
    this.value_setup_Ipv4.gateway4.value = this.IPV4Config.IPV4Config.addrgw;

    this.typeDHCP4 = this.IPV4Config.IPV4Config.typedhcp;
    this.interface.alias_add = this.IPV4Config.IPV4Config.alias_add;
    this.interface.alias_mask = this.IPV4Config.IPV4Config.alias_mask;
    this.interface.rejectLeases = this.IPV4Config.IPV4Config.reject;
    this.interface.hostname = this.IPV4Config.IPV4Config.hostname;
  },
  watch: {
    typeDHCP4: function (val) {
      if (val === "Advanced") {
        this.advancedParameters = true;
        this.AdvancedConfigDHCPv4.timeout = this.IPV4Config.IPV4Config.timeout;
        this.AdvancedConfigDHCPv4.retry = this.IPV4Config.IPV4Config.retry;
        this.AdvancedConfigDHCPv4.select_timeout =
          this.IPV4Config.IPV4Config.select_timeout;
        this.AdvancedConfigDHCPv4.reboot = this.IPV4Config.IPV4Config.reboot;
        this.AdvancedConfigDHCPv4.backoff = this.IPV4Config.IPV4Config.backoff;
        this.AdvancedConfigDHCPv4.initial_interval =
          this.IPV4Config.IPV4Config.initial_interval;
        this.AdvancedConfigDHCPv4.dhcp_client =
          this.IPV4Config.IPV4Config.dhcp_client;
        this.AdvancedConfigDHCPv4.lease_time =
          this.IPV4Config.IPV4Config.lease_time;
        this.AdvancedConfigDHCPv4.request = this.IPV4Config.IPV4Config.request;
        this.AdvancedConfigDHCPv4.require = this.IPV4Config.IPV4Config.require;
        this.AdvancedConfigDHCPv4.domain_name =
          this.IPV4Config.IPV4Config.domain_name;
        this.AdvancedConfigDHCPv4.domain_server =
          this.IPV4Config.IPV4Config.domain_server;
      } else {
        this.advancedParameters = false;
      }
    },
  },
};
</script>

<style scoped>
.ip-address-style {
  width: 100%;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  margin-left: 0.5rem;
  margin-right: 0.5rem;
}

.error-feedback {
  color: red;
  font-size: 0.85em;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  margin-left: 0.5rem;
  margin-right: 0.5rem;
  white-space: pre-wrap;
}

.netmask-select-style {
  width: 100%;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  margin-left: 0.5rem;
  margin-right: 0.5rem;
}

.IPV4Setup-type-style {
  /* remove underline  */

  border-bottom: none !important;
  border-top: none !important;
  border-left: none !important;
  border-right: none !important;
  border-radius: 0px !important;
  border-color: #f6f6f6 !important;
  border-width: 0px !important;
  width: 100%;
}

.advanced-parameters-style {
  display: flex;
  margin-top: 1rem;
  margin-bottom: 1rem;
  margin-left: 0.5rem;
  margin-right: 0.5rem;
}
.gateway-dialog {
  position: fixed;
  overflow-x: unset;
  overflow-y: unset;
}

.new-style {
  width: 70%;
}
</style>
