<template>
  <div class="mt-3">
    <v-row>
      <v-col cols="6">
        <generalInfoPhaseOne
          v-model:tunnelSettings="state.tunnelSettings"
          v-model:connectionMethod="state.connectionMethod"
          v-model:keyExchange="state.keyExchange"
          v-model:internetProtocol="state.internetProtocol"
          v-model:remoteGateway="state.remoteGateway"
          v-model:generalinterface="state.generalinterface"
          v-model:remoteConnect="state.remoteConnect"
          v-model:description="state.description"
          :mapedInterface="state.mapedInterface"
          :errors="v$"
        />
        <phaseAuth
          v-model:authMethod="state.authMethod"
          v-model:negotiationMode="state.negotiationMode"
          v-model:sharedKey="state.sharedKey"
          v-model:certificate="state.certificate"
          v-model:keyPair="state.keyPair"
          v-model:localKey="state.localKey"
          v-model:peerIdentifier="state.peerIdentifier"
          :errors="v$"
        />

        <phaseAlgo
          v-model:encryptAlgo="state.encryptAlgo"
          v-model:hashAlgo="state.hashAlgo"
          v-model:dhKey="state.dhKey"
          v-model:lifetime="state.lifetime"
          :errors="v$"
        />
        <advancedOption
          v-model:policy="state.policy"
          v-model:rekey="state.rekey"
          v-model:reauth="state.reauth"
          v-model:natTraversal="state.natTraversal"
          v-model:deadPeer="state.deadPeer"
          v-model:retries="state.retries"
          v-model:mobike="state.mobike"
          v-model:selectDear="state.selectDear"
          v-model:interactivityTimout="state.interactivityTimout"
          v-model:interactivityTimout2="state.interactivityTimout2"
          v-model:seconds="state.seconds"
          v-model:rekeyFuzz="state.rekeyFuzz"
          v-model:marginTime="state.marginTime"
        />
      </v-col>
      <v-col cols="6">
        <generalInfoPhaseTwo
          v-model:mode="state.mode"
          v-model:remoteTunnelAddress="state.remoteTunnelAddress"
          v-model:type="state.type"
          v-model:remoteNetworkAddress="state.remoteNetworkAddress"
          v-model:selectAddressNetwork="state.selectAddressNetwork"
          v-model:description="state.description"
          v-model:localAddress="state.localAddress"
          v-model:localNetworkAddress="state.localNetworkAddress"
          v-model:selectRemoteAddressNetwork="state.selectRemoteAddressNetwork"
          v-model:typeRemoteNetwork="state.typeRemoteNetwork"
          :errors="v$"
        />
        <phaseTwoExchange
          v-model:protocol="state.protocol"
          v-model:encryptAlgoExchange="state.encryptAlgoExchange"
          v-model:hashAlgoExchange="state.hashAlgoExchange"
          v-model:pfsKey="state.pfsKey"
          v-model:lifetimeExchange="state.lifetimeExchange"
          v-model:pingHost="state.pingHost"
          v-model:spdEntries="state.spdEntries"
          :errors="v$"
        />
        <div class="btnCreate mt-6 mr-3">
          <VButton
            rounded
            outlined
            color="#213E9F"
            label-color="#ffffff"
            label="Create"
            :isLarge="true"
            class="ml-2"
            @click="save"
          />
        </div>
      </v-col>
    </v-row>

    <div class="flex py-8 mb-5"></div>

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
import VButton from "@/components/VButton.vue";
import { required, requiredIf, helpers } from "@vuelidate/validators";
import { reactive, onMounted, computed } from "vue";
import generalInfoPhaseOne from "./component/general_info_phase_one.vue";
import phaseAuth from "./component/phase_authentification.vue";
import phaseAlgo from "./component/phase_algorithms.vue";
import advancedOption from "./component/advancedOptions.vue";
import generalInfoPhaseTwo from "./component/general_info_phase_two.vue";
import phaseTwoExchange from "./component/phase_two_exchange.vue";

export default {
  name: "ClientsOpenvpnComponent",
  components: {
    generalInfoPhaseOne,
    generalInfoPhaseTwo,
    phaseTwoExchange,
    phaseAuth,
    phaseAlgo,
    advancedOption,
    VButton,
  },
  setup() {
    const state = reactive({
      snackbar: false,
      color: "",
      textAlert: "",
      //General information Phase 1
      tunnelSettings: "",
      connectionMethod: {
        name: "Default",
        slug: "default",
      },
      keyExchange: {
        name: "V2",
        slug: "v2",
      },
      internetProtocol: {
        name: "IPv4",
        slug: "IPv4",
      },
      remoteGateway: "",
      generalinterface: "",
      remoteConnect: false,
      description: "",
      //phase auth
      authMethod: {
        name: "Mutual RSA",
        slug: "Mutual RSA",
      },
      negotiationMode: {
        name: "Main",
        slug: "Main",
      },
      sharedKey: "",
      certificate: "",
      keyPair: "",
      localKey: "",
      peerIdentifier: "",
      //phase algo
      encryptAlgo: {
        name: "256 bit AES-GCM with 128 bit ICV",
        slug: "256 bit AES-GCM with 128 bit ICV",
      },
      hashAlgo: {
        name: "SHA256",
        slug: "SHA256",
      },
      dhKey: {
        name: "20 (NIST EC 384 bits)",
        slug: "20 (NIST EC 384 bits)",
      },
      lifetime: "28800",
      //advancedOptions
      policy: true,
      rekey: false,
      reauth: false,
      natTraversal: { name: "Unforce", slug: "Unforce" },
      deadPeer: false,
      retries: "",
      mobike: false,
      selectDear: "",
      interactivityTimout: "",
      interactivityTimout2: "",
      seconds: "",
      rekeyFuzz: "",
      marginTime: "",
      //general info 2
      mode: {
        name: "Tunnel IPv4",
        slug: "Tunnel IPv4",
      },
      remoteTunnelAddress: "",
      type: {
        name: "Address",
        slug: "Address",
      },
      remoteNetworkAddress: "",
      selectAddressNetwork: "",
      description: "",
      localAddress: "",
      localNetworkAddress: "",
      selectRemoteAddressNetwork: "",
      typeRemoteNetwork: { name: "Network", slug: "Network" },
      //exchange
      protocol: {
        name: "ESP",
        slug: "ESP",
      },
      encryptAlgoExchange: {
        name: "aes256gcm16",
        slug: "aes256gcm16",
      },
      hashAlgoExchange: {
        name: "SHA256",
        slug: "SHA256",
      },
      pfsKey: {
        name: "off",
        slug: "off",
      },
      lifetimeExchange: "",
      pingHost: "",
      spdEntries: "",
    });

    const rules = computed(() => {
      return {
        //General information Phase 1
        tunnelSettings: { required },
        connectionMethod: { required },
        keyExchange: { required },
        internetProtocol: { required },

        remoteGateway: {
          required,
          isValidlRemoteGateway: helpers.withMessage(
            `Format must be like adresse IP : X.X.X.X`,

            helpers.regex(/^[0-9.]+$/)
          ),
        },

        generalinterface: { required },
        // phase Auth
        authMethod: { required },
        negotiationMode: { required },
        sharedKey: { required },
        certificate: { required },
        keyPair: { required },
        localKey: { required },
        peerIdentifier: { required },
        // phase algo
        encryptAlgo: { required },
        hashAlgo: { required },
        dhKey: { required },
        lifetime: { required },
        // general info phase 2
        mode: { required },
        remoteTunnelAddress: {
          required,
          isValidRemoteTunnelAddress: helpers.withMessage(
            `Format must be like adresse IP : X.X.X.X`,

            helpers.regex(/^[0-9.]+$/)
          ),
        },
        type: { required },

        remoteNetworkAddress: {
          required,
          isValidremoteNetworkAddress: helpers.withMessage(
            `Format must be like adresse IP : X.X.X.X`,

            helpers.regex(/^[0-9.]+$/)
          ),
        },

        selectAddressNetwork: { required },
        description: { required },

        localAddress: {
          required,
          isValidlocalAddress: helpers.withMessage(
            `Format must be like adresse IP : X.X.X.X`,

            helpers.regex(/^[0-9.]+$/)
          ),
        },
        localNetworkAddress: {
          required,
          isValidlocalNetworkAddress: helpers.withMessage(
            `Format must be like adresse IP : X.X.X.X`,

            helpers.regex(/^[0-9.]+$/)
          ),
        },

        selectRemoteAddressNetwork: { required },
        typeRemoteNetwork: { required },
        //exchange
        protocol: { required },
        encryptAlgoExchange: { required },
        hashAlgoExchange: { required },
        pfsKey: { required },
        lifetimeExchange: { required },
        pingHost: { required },
        spdEntries: { required },
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

          let resultObject = interfaces.filter((i) => i.name === "WAN");
          state.generalinterface = resultObject[0];
        },
        (error) => {
          console.log(error);
        }
      );
    };

    onMounted(() => {
      getInterface();
    });

    const save = async () => {
      console.log("save", state);
      const result = await v$.value.$validate();

      if (result) {
        console.log("ok");
      } else {
        console.log("error", v$.value);
      }
    };
    // const submitForm = async () => {
    //   const result = await v$.value.$validate();

    //   if (result) {
    //     let tls_auth = null;
    //     if (state.isEnableAuth) {
    //       tls_auth = {
    //         generate: state.isEnableAuth,
    //       };
    //     } else {
    //       tls_auth = {
    //         generate: state.isEnableAuth,
    //         tls_key: state.tlsGenerate,
    //       };
    //     }

    //     let bridgeSelect = null;
    //     if (!state.isBridge) {
    //       bridgeSelect = {
    //         bridge_select: state.isBridge,
    //       };
    //     } else {
    //       bridgeSelect = {
    //         bridge_select: state.isBridge,
    //         bridge_interface: state.interfaceBridge.id,
    //         bridge_start_dhcp: state.startDHCPBridge,
    //         bridge_end_dhcp: state.endDHCPBridge,
    //       };
    //     }
    //     let addressPoolElected = null;
    //     if (!state.adressPool) {
    //       addressPoolElected = {
    //         address_pool_select: state.adressPool,
    //       };
    //     } else {
    //       addressPoolElected = {
    //         address_pool_select: state.adressPool,
    //         address_pool_start: state.startAddressPool,
    //         address_pool_end: state.endAddressPool,
    //       };
    //     }
    //     let electedDefaultDns = null;
    //     if (!state.dnsDefaultDomain) {
    //       electedDefaultDns = {
    //         dns_default_domain_select: state.dnsDefaultDomain,
    //       };
    //     } else {
    //       electedDefaultDns = {
    //         dns_default_domain_select: state.dnsDefaultDomain,
    //         dns_default_domain_server: state.activeDnsDefault,
    //       };
    //     }
    //     let electedDnsServers = null;
    //     if (!state.dnsServers) {
    //       electedDnsServers = {
    //         dns_servers_select: state.dnsServers,
    //       };
    //     } else {
    //       electedDnsServers = {
    //         dns_servers_select: state.dnsServers,
    //         dns_server1: state.activeDnsServer1,
    //         dns_server2: state.activeDnsServer2,
    //       };
    //     }
    //     let electedNtpServers = null;
    //     if (!state.ntpServers) {
    //       electedNtpServers = {
    //         ntp_servers_select: state.ntpServers,
    //       };
    //     } else {
    //       electedNtpServers = {
    //         ntp_servers_select: state.ntpServers,
    //         ntp_server1: state.activeNtpServer1,
    //         ntp_server2: state.activeNtpServer2,
    //       };
    //     }

    //     let payload = {
    //       name: state.clientName,
    //       description: state.description,
    //       server_mode: {
    //         mode: state.serverMode.slug,
    //       },
    //       protocol: state.protocol.slug,
    //       device_mode: state.deviceMode.slug,
    //       interface: state.interface.name,
    //       local_port: state.localPort,
    //       tls_auth: tls_auth,
    //       ca_name: state.peerCertif.name,
    //       server_cert: state.serverCertif.name,
    //       dh_params_length: state.dhParameters,
    //       encryption_algorithm: state.encryptAlgo,
    //       auth_digest_algorithm: state.authDigest.name,
    //       hardware_crypto: state.hardwareCrypto.slug,

    //       ipv4_tunnel_network: state.ip4Tunnel,
    //       gateway: state.isGateway,
    //       bridge: bridgeSelect,
    //       ipv4_local_network: state.iPv4Local,
    //       ipv4_remote_network: state.iPv4Remote,
    //       concurrent_connections: state.concurrentConnections,
    //       compression: state.compression.slug,
    //       type_of_service: state.typefService,
    //       duplicate_connections: state.Connections,
    //       ipv6: state.IPv6,
    //       inter_clients: state.interClients,
    //       address_pool: addressPoolElected,
    //       dynamic_ip: state.dynamicIP,
    //       topology: state.topology,
    //       dns_default_domain: electedDefaultDns,
    //       dns_servers: electedDnsServers,
    //       force_dns_cache_update: state.forceDNS,
    //       ntp_servers: electedNtpServers,
    //       verbosity_level: state.verbLevel?.slug ?? "",
    //     };
    //     state.loading = true;
    //     state.isLoadingDialogue = true;

    //     axios
    //       .post("/openvpn/createServerOpenvpn", payload)
    //       .then((response) => {
    //         if (response.status == "201") {
    //           state.loading = false;
    //           state.isLoadingDialogue = false;
    //           state.snackbar = true;
    //           state.color = "success";
    //           state.textAlert = response.data.msg;

    //           setTimeout(() => {
    //             location.reload();
    //           }, 1000);
    //         }
    //       })
    //       .catch((i) => {
    //         state.loading = false;
    //         state.isLoadingDialogue = false;
    //         state.snackbar = true;
    //         state.color = "red";
    //         state.textAlert = i.response.data.error;
    //       });
    //   } else {
    //     console.log("res", v$.value);
    //   }
    // };

    return {
      getCookie,
      getInterface,
      //   submitForm,
      save,
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
.btnCreate {
  display: flex;
  justify-content: flex-end;
}
</style>
