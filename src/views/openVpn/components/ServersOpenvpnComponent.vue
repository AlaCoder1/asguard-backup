<template>
  <div class="mt-3">
    <v-row>
      <v-col cols="6">
        <div class="ml-3 mr-3">
          <h4>General information</h4>
          <v-divider class="mt-2"></v-divider>
          <v-row class="mt-2">
            <v-col cols="4" align-self="center">
              <label>Server name</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                label="Server name"
                v-model="state.clientName"
              ></v-text-field>

              <p
                class="error-feedback mb-5"
                v-if="v$.clientName.$errors.length"
              >
                {{ v$.clientName.$errors?.[0].$message }}
              </p>
            </v-col>
            <v-col cols="4" align-self="center">
              <label>Description</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                label="Description"
                v-model="state.description"
              ></v-text-field>
            </v-col>
            <v-col cols="4" align-self="center">
              <label>Server mode</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select
                label="Server mode"
                v-model="state.serverMode"
                item-title="name"
                item-value="id"
                return-object
                :items="[
                  {
                    id: '1',
                    name: 'Remote Access (SSL/TLS)',
                    slug: 'remote_access',
                  },
                  { id: '2', name: 'Peer to peer(SSL/TLS)', slug: 'peer' },
                  {
                    id: '3',
                    name: 'Remote Access (Shared key)',
                    slug: 'shared',
                  },
                ]"
              ></v-select>
              <p
                class="error-feedback mb-5"
                v-if="v$.serverMode.$errors.length"
              >
                {{ v$.serverMode.$errors?.[0].$message }}
              </p>
            </v-col>

            <v-col cols="4" align-self="center">
              <label>Protocol</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select
                label="Protocol"
                v-model="state.protocol"
                item-title="name"
                item-value="id"
                return-object
                :items="[
                  {
                    id: '1',
                    name: 'UDP',
                    slug: 'udp',
                  },
                  { id: '2', name: 'UDP4', slug: 'udp4' },
                  { id: '3', name: 'UDP6', slug: 'udp6' },
                  { id: '4', name: 'TCP', slug: 'tcp' },
                  { id: '5', name: 'TCP4', slug: 'tcp4' },
                  { id: '6', name: 'TCP6', slug: 'tcp6' },
                ]"
              ></v-select>
              <p class="error-feedback mb-5" v-if="v$.protocol.$errors.length">
                {{ v$.protocol.$errors?.[0].$message }}
              </p>
            </v-col>

            <v-col cols="4" align-self="center">
              <label>Device Mode</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select
                v-model="state.deviceMode"
                label="Device Mode"
                item-title="name"
                item-value="id"
                return-object
                :items="[
                  {
                    id: '1',
                    name: 'TUN',
                    slug: 'tun',
                  },
                  { id: '2', name: 'TAP', slug: 'tap' },
                ]"
              ></v-select>
              <p
                class="error-feedback mb-5"
                v-if="v$.deviceMode.$errors.length"
              >
                {{ v$.deviceMode.$errors?.[0].$message }}
              </p>
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
              ></v-select>
              <p class="error-feedback mb-5" v-if="v$.interface.$errors.length">
                {{ v$.interface.$errors?.[0].$message }}
              </p>
            </v-col>

            <v-col cols="4" align-self="center">
              <label>Local port</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                label="Local port"
                v-model="state.localPort"
              ></v-text-field>
              <p class="error-feedback mb-5" v-if="v$.localPort.$errors.length">
                {{ v$.localPort.$errors?.[0].$message }}
              </p>
            </v-col>
          </v-row>
          <v-row class="mt-2">
            <div class="ml-3 mr-3">
              <v-row class="mt-2">
                <cryptoSettings
                  v-model:isEnableAuth="state.isEnableAuth"
                  v-model:tlsGenerate="state.tlsGenerate"
                  v-model:peerCertif="state.peerCertif"
                  v-model:serverCertif="state.serverCertif"
                  v-model:dhParameters="state.dhParameters"
                  v-model:encryptAlgo="state.encryptAlgo"
                  v-model:authDigest="state.authDigest"
                  v-model:hardwareCrypto="state.hardwareCrypto"
                  :errors="v$"
                />
              </v-row>
            </div>
          </v-row>
          <v-spacer></v-spacer>
        </div>
      </v-col>
      <v-col cols="6">
        <div class="ml-3 mr-3">
          <v-row class="mt-0">
            <tunnelSettings
              v-model:ip4Tunnel="state.ip4Tunnel"
              v-model:ip6Tunnel="state.ip6Tunnel"
              v-model:isGateway="state.isGateway"
              v-model:isBridge="state.isBridge"
              v-model:interfaceBridge="state.interfaceBridge"
              v-model:startDHCPBridge="state.startDHCPBridge"
              v-model:endDHCPBridge="state.endDHCPBridge"
              v-model:iPv4Local="state.iPv4Local"
              v-model:iPv6Local="state.iPv6Local"
              v-model:iPv4Remote="state.iPv4Remote"
              v-model:iPv6Remote="state.iPv6Remote"
              v-model:concurrentConnections="state.concurrentConnections"
              v-model:compression="state.compression"
              v-model:typefService="state.typefService"
              v-model:Connections="state.Connections"
              v-model:IPv6="state.IPv6"
              v-model:interClients="state.interClients"
              :deviceMode="state.deviceMode.slug"
              :errors="v$"
            />
          </v-row>
          <clientSettings
            v-model:dynamicIP="state.dynamicIP"
            v-model:adressPool="state.adressPool"
            v-model:topology="state.topology"
            v-model:dnsDefaultDomain="state.dnsDefaultDomain"
            v-model:dnsServers="state.dnsServers"
            v-model:forceDNS="state.forceDNS"
            v-model:ntpServers="state.ntpServers"
            v-model:clientPort="state.clientPort"
            v-model:startAddressPool="state.startAddressPool"
            v-model:endAddressPool="state.endAddressPool"
            v-model:activeDnsDefault="state.activeDnsDefault"
            v-model:activeDnsServer1="state.activeDnsServer1"
            v-model:activeDnsServer2="state.activeDnsServer2"
            v-model:activeNtpServer1="state.activeNtpServer1"
            v-model:activeNtpServer2="state.activeNtpServer2"
            v-model:verbLevel="state.verbLevel"
            :errors="v$"
          />
        </div>
      </v-col>
    </v-row>
    <v-row class="flex py-8 mb-5">
      <v-col cols="4"> </v-col>
      <v-col>
        <div class="mr-3 flex center">
          <v-btn class="mr-5" large rounded color="#213E9F">
            <span class="text-white c-o">Cancel</span>
          </v-btn>
          <v-btn @click="submitForm" large rounded color="#213E9F">
            <span class="text-white c-o">Save</span>
          </v-btn>
        </div>
      </v-col>
    </v-row>
    <v-snackbar
      :timeout="2000"
      v-model="state.snackbar"
      location="bottom right"
      :color="state.color"
    >
      {{ state.textAlert }}

      <template v-slot:actions> </template>
    </v-snackbar>
  </div>
</template>

<script>
import axios from "axios";
import useValidate from "@vuelidate/core";
import { required, requiredIf, helpers } from "@vuelidate/validators";
import UsersList from "../../system/user/components/UsersList.vue";
import tunnelSettings from "./serveurComponents/tunnelSettings.vue";
import clientSettings from "./serveurComponents/clientSettings.vue";
import cryptoSettings from "./serveurComponents/cryptoSettings.vue";
import { reactive, onMounted, computed } from "vue";

export default {
  name: "ClientsOpenvpnComponent",
  components: {
    UsersList,
    tunnelSettings,
    clientSettings,
    cryptoSettings,
  },
  setup() {
    const state = reactive({
      snackbar: false,
      color: "",
      textAlert: "",
      //General information
      clientName: "",
      description: "",
      serverMode: "",
      protocol: "",
      deviceMode: "",
      interface: "",
      localPort: "",
      mapedInterface: [],
      //Cryptographic Settings
      isEnableAuth: true,
      tlsGenerate: "",
      peerCertif: "",
      serverCertif: "",
      dhParameters: "",
      encryptAlgo: "",
      authDigest: "",
      hardwareCrypto: "",
      //tunnelSettings
      ip4Tunnel: "",
      ip6Tunnel: "",
      isGateway: false,
      isBridge: false,
      interfaceBridge: "",
      startDHCPBridge: "",
      endDHCPBridge: "",
      iPv4Local: "",
      iPv6Local: "",
      iPv4Remote: "",
      iPv6Remote: "",
      concurrentConnections: "",
      compression: { name: "No preference", slug: "no_preference" },
      typefService: false,
      Connections: false,
      IPv6: false,
      interClients: false,
      //clientSettings
      dynamicIP: false,
      adressPool: false,
      topology: false,
      dnsDefaultDomain: false,
      dnsServers: false,
      forceDNS: false,
      ntpServers: false,
      clientPort: false,
      startAddressPool: "",
      endAddressPool: "",
      activeDnsDefault: "",
      activeDnsServer1: "",
      activeDnsServer2: "",
      activeNtpServer1: "",
      activeNtpServer2: "",
      verbLevel: "",
    });

    const rules = computed(() => {
      return {
        clientName: { required },
        serverMode: { required },
        protocol: { required },
        deviceMode: { required },
        interface: { required },

        localPort: {
          required,
          isValidlifeTime: helpers.withMessage(
            `champs local Port can include only Numbers min 4 and max 5.`,

            helpers.regex(/^[0-9]{4,5}$/)
          ),
        },
        //Cryptographic Settings
        tlsGenerate: {
          requiredIfFuction: requiredIf(() => !state.isEnableAuth),
        },
        peerCertif: { required },
        serverCertif: { required },
        dhParameters: { required },
        encryptAlgo: { required },
        authDigest: { required },
        hardwareCrypto: { required },

        //Tunnel Settings
        ip4Tunnel: { required },
        iPv4Local: { required },

        //Client Settings
        verbLevel: { required },
        startAddressPool: {
          requiredIfFuction: requiredIf(() => state.adressPool),
        },
        endAddressPool: {
          requiredIfFuction: requiredIf(() => state.adressPool),
        },
        activeDnsDefault: {
          requiredIfFuction: requiredIf(() => state.dnsDefaultDomain),
        },
        activeDnsServer1: {
          requiredIfFuction: requiredIf(() => state.dnsServers),
        },
        activeNtpServer1: {
          requiredIfFuction: requiredIf(() => state.ntpServers),
        },
      };
    });

    const v$ = useValidate(rules, state);

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

    const getInterface = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/network/AllInterfaces").then(
        (response) => {
          let interfaces = response.data.map((i) => {
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

    onMounted(() => {
      getInterface();
    });

    const submitForm = async () => {
      const result = await v$.value.$validate();

      if (result) {
        let tls_auth = null;
        if (state.isEnableAuth) {
          tls_auth = {
            generate: state.isEnableAuth,
          };
        } else {
          tls_auth = {
            generate: state.isEnableAuth,
            tls_key: state.tlsGenerate,
          };
        }

        let bridgeSelect = null;
        if (!state.isBridge) {
          bridgeSelect = {
            bridge_select: state.isBridge,
          };
        } else {
          bridgeSelect = {
            bridge_select: state.isBridge,
            bridge_interface: state.interfaceBridge.id,
            bridge_start_dhcp: state.startDHCPBridge,
            bridge_end_dhcp: state.endDHCPBridge,
          };
        }
        let addressPoolElected = null;
        if (!state.adressPool) {
          addressPoolElected = {
            address_pool_select: state.adressPool,
          };
        } else {
          addressPoolElected = {
            address_pool_select: state.adressPool,
            address_pool_start: state.startAddressPool,
            address_pool_end: state.endAddressPool,
          };
        }
        let electedDefaultDns = null;
        if (!state.dnsDefaultDomain) {
          electedDefaultDns = {
            dns_default_domain_select: state.dnsDefaultDomain,
          };
        } else {
          electedDefaultDns = {
            dns_default_domain_select: state.dnsDefaultDomain,
            dns_default_domain_server: state.activeDnsDefault,
          };
        }
        let electedDnsServers = null;
        if (!state.dnsServers) {
          electedDnsServers = {
            dns_servers_select: state.dnsServers,
          };
        } else {
          electedDnsServers = {
            dns_servers_select: state.dnsServers,
            dns_server1: state.activeDnsServer1,
            dns_server2: state.activeDnsServer2,
          };
        }
        let electedNtpServers = null;
        if (!state.ntpServers) {
          electedNtpServers = {
            ntp_servers_select: state.ntpServers,
          };
        } else {
          electedNtpServers = {
            ntp_servers_select: state.ntpServers,
            ntp_server1: state.activeNtpServer1,
            ntp_server2: state.activeNtpServer2,
          };
        }

        let payload = {
          name: state.clientName,
          description: state.description,
          server_mode: {
            mode: state.serverMode.slug,
          },
          protocol: state.protocol.slug,
          device_mode: state.deviceMode.slug,
          interface: state.interface.name,
          local_port: state.localPort,
          tls_auth: tls_auth,
          ca_name: state.peerCertif.name,
          server_cert: state.serverCertif.name,
          dh_params_length: state.dhParameters,
          encryption_algorithm: state.encryptAlgo,
          auth_digest_algorithm: state.authDigest.name,
          hardware_crypto: state.hardwareCrypto.slug,

          ipv4_tunnel_network: state.ip4Tunnel,
          gateway: state.isGateway,
          bridge: bridgeSelect,
          ipv4_local_network: state.iPv4Local,
          ipv4_remote_network: state.iPv4Remote,
          concurrent_connections: state.concurrentConnections,
          compression: state.compression.slug,
          type_of_service: state.typefService,
          duplicate_connections: state.Connections,
          ipv6: state.IPv6,
          inter_clients: state.interClients,
          address_pool: addressPoolElected,
          dynamic_ip: state.dynamicIP,
          topology: state.topology,
          dns_default_domain: electedDefaultDns,
          dns_servers: electedDnsServers,
          force_dns: state.forceDNS,
          ntp_servers: electedNtpServers,
          verbosity_level: state.verbLevel,
        };

        console.log("payload", payload);

        axios
          .post("/openvpn/createServerOpenvpn", payload)
          .then((response) => {
            if (response.status == "201") {
              console.log("response", response);
              state.snackbar = true;
              state.color = "success";
              state.textAlert = response.data.msg;

              setTimeout(() => {
                location.reload();
              }, 1000);
            }
          })
          .catch((i) => {
            console.log("i", i.response);
            // this.snackbar = true;
            // this.color = "red";
            // this.textAlert = i.response.data.error;
          });
      } else {
        console.log("res", v$.value);
      }
    };

    return {
      getCookie,
      getInterface,
      submitForm,
      state,
      v$,
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
