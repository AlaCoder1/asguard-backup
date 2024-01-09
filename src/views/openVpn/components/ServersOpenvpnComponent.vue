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
              <label>Server name*</label>
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
              <label>Server mode*</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select
                label="Server mode"
                v-model="state.serverMode"
                item-title="name"
                item-value="slug"
                return-object
                :items="[
                  {
                    name: 'Remote Access (SSL/TLS)',
                    slug: 'remote_access',
                  },
                  { name: 'Peer to peer(SSL/TLS)', slug: 'peer-to-peer' },
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
              <label>Protocol*</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select
                label="Protocol"
                v-model="state.protocol"
                item-title="name"
                item-value="slug"
                return-object
                :items="protocolList"
              ></v-select>
              <p class="error-feedback mb-5" v-if="v$.protocol.$errors.length">
                {{ v$.protocol.$errors?.[0].$message }}
              </p>
            </v-col>

            <v-col cols="4" align-self="center">
              <label>Device Mode*</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select
                v-model="state.deviceMode"
                label="Device Mode"
                item-title="name"
                item-value="id"
                return-object
                :items="deviceModeList"
              ></v-select>
              <p
                class="error-feedback mb-5"
                v-if="v$.deviceMode.$errors.length"
              >
                {{ v$.deviceMode.$errors?.[0].$message }}
              </p>
            </v-col>

            <v-col cols="4" align-self="center">
              <label>Interface*</label>
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
              <label>Local port*</label>
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
              :addressPool="state.adressPool"
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
            :isBridge="state.isBridge"
            :deviceMode="state.deviceMode.slug"
            :errors="v$"
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
    <v-snackbar
      :timeout="1000"
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
import { inject, ref, toRefs } from "vue";
import axios from "axios";
import useValidate from "@vuelidate/core";
import VButton from "@/components/VButton.vue";
import { required, requiredIf, helpers } from "@vuelidate/validators";
import UsersList from "../../system/user/components/UsersList.vue";
import tunnelSettings from "./serveurComponents/tunnelSettings.vue";
import clientSettings from "./serveurComponents/clientSettings.vue";
import cryptoSettings from "./serveurComponents/cryptoSettings.vue";
import { reactive, onMounted, computed, watch } from "vue";

export default {
  name: "ClientsOpenvpnComponent",
  components: {
    UsersList,
    tunnelSettings,
    clientSettings,
    cryptoSettings,
    VButton,
  },
  props: ["dataServer"],
  setup(props) {
    const { dataServer } = toRefs(props);
    const emitter = inject("emitter");

    const state = reactive({
      id: "",
      loading: false,
      isLoadingDialogue: false,

      mapedCertifServer: [],
      snackbar: false,
      color: "",
      textAlert: "",
      isEditState: "",
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
      // hardwareCrypto: {
      //   name: "No Hardware Crypto acceleration",
      //   slug: "No Hardware Crypto",
      // },
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
      verbLevel: {
        name: "1 (default)",
        slug: "1",
      },
    });

    const rules = computed(() => {
      return {
        clientName: {
          required,
          isValidClientName: helpers.withMessage(
            `champs can include only letters & Numbers & underscores & hyphens without space.`,

            helpers.regex(/^[A-Za-z0-9_\-]+$/)
          ),
        },

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

        //Tunnel Settings

        ip4Tunnel: {
          requiredIfFuction: requiredIf(
            () => !state.isBridge && !state.adressPool
          ),
        },
        iPv4Local: {
          requiredIfFuction: requiredIf(
            () => !state.isBridge && !state.adressPool
          ),
        },
        interfaceBridge: {
          requiredIfFuction: requiredIf(() => state.isBridge),
        },

        //Client Settings
        startAddressPool: {
          requiredIfFuction: requiredIf(() => state.adressPool),
        },
        endAddressPool: {
          requiredIfFuction: requiredIf(() => state.adressPool),
        },
        startDHCPBridge: {
          requiredIfFuction: requiredIf(() => state.isBridge),
        },
        endDHCPBridge: {
          requiredIfFuction: requiredIf(() => state.isBridge),
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

    const authDigestList = ref([
      {
        name: "SHA224",
        slug: "sha224",
      },
      {
        name: "SHA256",
        slug: "SHA256",
      },
      {
        name: "SHA384",
        slug: "SHA384",
      },

      {
        name: "SHA512",
        slug: "SHA512",
      },
      {
        name: "SHA3-224",
        slug: "SHA3-224",
      },
      {
        name: "SHA3-256",
        slug: "SHA3-256",
      },
      {
        name: "SHA3-384",
        slug: "SHA3-384",
      },
      {
        name: "SHA3-512",
        slug: "SHA3-512",
      },
    ]);

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
          let filtredInterface = response.data.filter(
            (i) => !i.ifname.startsWith("tun_") && !i.ifname.startsWith("tap_")
          );

          let interfaces = filtredInterface.map((i) => {
            return {
              id: i.id,
              name: i.name_interface,
            };
          });

          let listInter = [{ id: 0, name: "Any" }];
          var combinedArray = [...listInter, ...interfaces];
          state.mapedInterface = combinedArray;
        },
        (error) => {
          console.log(error);
        }
      );
    };

    const getCertif = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/certificates/getAllCertificates").then(
        (response) => {
          let mapedListCertif = response.data.filter(
            (i) => i.certificate_type === "server"
          );
          state.mapedCertifServer = mapedListCertif.map((i) => {
            return {
              id: i.id,
              name: i.name,
            };
          });
        },
        (error) => {
          console.log(error);
        }
      );
    };
    const getAllCertAuth = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/certificates/getAllCertAuth").then(
        (response) => {
          let mapedList = response.data.map((i) => {
            return {
              id: i.id,
              name: i.name,
            };
          });
          state.mapedCertifAuth = mapedList;
        },
        (error) => {
          console.log(error);
        }
      );
    };

    const deviceModeList = ref([
      {
        id: "1",
        name: "TUN",
        slug: "tun",
      },
      { id: "2", name: "TAP", slug: "tap" },
    ]);
    const protocolList = ref([
      { name: "UDP4", slug: "udp4" },
      { name: "UDP6", slug: "udp6" },

      { name: "TCP4", slug: "tcp4" },
      { name: "TCP6", slug: "tcp6" },
    ]);
    const compressionList = ref([
      { name: "No preference", slug: "no_preference" },
      { name: "Disable-No Compression", slug: "disabled" },
      { name: "Enabled with Adaptive Compression", slug: "adaptive" },
      { name: "Enabled without Adaptive Compression", slug: "enabled" },
    ]);

    watch(
      () => dataServer.value,
      (newValue) => {
        if (newValue != "SERVERS") {
          cancel();
        }
      }
    );
    watch(
      () => state.isEnableAuth,
      (newValue) => {
        if (newValue) {
          state.tlsGenerate = "";
        }
      }
    );
    watch(
      () => state.adressPool,
      (newValue) => {
        if (!newValue) {
          state.startAddressPool = "";
          state.endAddressPool = "";
        }
      }
    );
    watch(
      () => state.dnsDefaultDomain,
      (newValue) => {
        if (!newValue) {
          state.activeDnsDefault = "";
        }
      }
    );
    watch(
      () => state.dnsServers,
      (newValue) => {
        if (!newValue) {
          (state.activeDnsServer1 = ""), (state.activeDnsServer2 = "");
        }
      }
    );
    watch(
      () => state.ntpServers,
      (newValue) => {
        if (!newValue) {
          (state.activeNtpServer1 = ""), (state.activeNtpServer2 = "");
        }
      }
    );
    watch(
      () => state.isBridge,
      (newValue) => {
        if (!newValue) {
          state.interfaceBridge = "";
          state.startDHCPBridge = "";
          state.endDHCPBridge = "";
        }
      }
    );

    onMounted(() => {
      getInterface();
      getAllCertAuth();
      getCertif();

      emitter.on("edit-server", (data) => {
        if (data) state.isEditState = "edit";

        state.id = data.id;

        //General information
        state.clientName = data.name;
        state.description = data.description;
        state.serverMode = data.server_mode;

        let filtredProtocol = protocolList.value.filter(
          (i) => i.slug === data.proto
        );

        let filtredCertifAuth = state.mapedCertifAuth.filter(
          (i) => i.name === data.ca_name
        );
        let filtredCertiServer = state.mapedCertifServer.filter(
          (i) => i.name === data.cert_name
        );
        state.protocol = filtredProtocol[0];

        let filtredDevice = deviceModeList.value.filter(
          (i) => i.slug === data.dev
        );

        state.deviceMode = filtredDevice[0];

        let filtredInterfaces = state.mapedInterface.filter(
          (i) => i.id === +data.interface
        );
        let filtredInter = state.mapedInterface.filter(
          (i) => i.name === data.interface
        );

        state.interface = filtredInterfaces[0] ?? filtredInter[0];
        state.localPort = data.port;
        //Cryptographic Settings
        state.isEnableAuth = data.tls_key ? false : true;
        state.tlsGenerate = data.tls_key;
        state.peerCertif = filtredCertifAuth[0];
        state.serverCertif = filtredCertiServer[0];
        state.dhParameters = data.dh;
        state.encryptAlgo = data.cipher;

        let filtredAuth = authDigestList.value.filter(
          (i) => i.slug === data.auth
        );

        state.authDigest = filtredAuth[0];
        // state.hardwareCrypto = data.hardware_crypto;
        //tunnelSettings
        state.ip4Tunnel = data.ipv4_tunnel_network;
        // state.ip6Tunnel= "";
        state.isGateway = data.gateway;
        state.isBridge = data.bridge_interface ? true : false;

        let filtredInterfacesBridge = state.mapedInterface.filter(
          (i) => i.id === +data.bridge_interface
        );
        let filtredInterBridge = state.mapedInterface.filter(
          (i) => i.name === data.bridge_interface
        );

        state.interfaceBridge =
          filtredInterfacesBridge[0] ?? filtredInterBridge[0];

        state.startDHCPBridge = data.bridge_start_dhcp;
        state.endDHCPBridge = data.bridge_end_dhcp;
        state.iPv4Local = data.ipv4_local_network;
        // state.iPv6Local= "";
        state.iPv4Remote = data.ipv4_remote_network;
        // state.iPv6Remote= "";
        state.concurrentConnections = data.concurrent_connections;

        let filtredCompression = compressionList.value.filter(
          (i) => i.slug === data.compression
        );

        state.compression = filtredCompression[0];
        state.typefService = data.type_of_service;
        state.Connections = data.duplicate_connections;
        state.IPv6 = data.ipv6;
        state.interClients = data.inter_clients;
        //clientSettings
        state.dynamicIP = data.dynamic_ip;
        state.adressPool = data.address_pool_start ? true : false;
        state.topology = data.topology;
        state.dnsDefaultDomain = data.dns_default_domain_server ? true : false;
        state.dnsServers = data.dns_server1 ? true : false;
        state.forceDNS = data.force_dns_cache_update;
        state.ntpServers = data.ntp_server1 ? true : false;
        state.clientPort = false; //*
        state.startAddressPool = data.address_pool_start;
        state.endAddressPool = data.address_pool_end;
        state.activeDnsDefault = data.dns_default_domain_server;
        state.activeDnsServer1 = data.dns_server1;
        state.activeDnsServer2 = data.dns_server2;
        state.activeNtpServer1 = data.ntp_server1;
        state.activeNtpServer2 = data.ntp_server2;
        state.verbLevel = data.verb;
      });
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
            mode: state.serverMode.slug ?? state.serverMode,
          },
          protocol: state.protocol.slug,
          device_mode: state.deviceMode.slug ?? state.deviceMode,
          interface: state.interface.name ?? state.interface,
          local_port: state.localPort,
          tls_auth: tls_auth,
          ca_name: state.peerCertif.name ?? state.peerCertif,
          server_cert: state.serverCertif.name ?? state.serverCertif,
          dh_params_length: state.dhParameters,
          encryption_algorithm: state.encryptAlgo,
          auth_digest_algorithm: state.authDigest.slug ?? state.authDigest,
          // hardware_crypto: state.hardwareCrypto.slug ?? state.hardwareCrypto,

          ipv4_tunnel_network: state.ip4Tunnel,
          gateway: state.isGateway,
          bridge: bridgeSelect,
          ipv4_local_network: state.iPv4Local,
          ipv4_remote_network: state.iPv4Remote,
          concurrent_connections: state.concurrentConnections,
          compression: state.compression.slug ?? state.compression,
          type_of_service: state.typefService,
          duplicate_connections: state.Connections,
          ipv6: state.IPv6,
          inter_clients: state.interClients,
          address_pool: addressPoolElected,
          dynamic_ip: state.dynamicIP,
          topology: state.topology,
          dns_default_domain: electedDefaultDns,
          dns_servers: electedDnsServers,
          force_dns_cache_update: state.forceDNS,
          ntp_servers: electedNtpServers,
          verbosity_level: state.verbLevel?.slug ?? state.verbLevel ?? "",
        };
        state.loading = true;
        state.isLoadingDialogue = true;

        if (state.isEditState === "edit") {
          axios
            .put(`/openvpn/updateServerOpenVPN/${state.id}`, payload)
            .then((response) => {
              if (response.status == "201") {
                state.loading = false;
                state.isLoadingDialogue = false;
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.msg;
                state.isEditState = "";

                setTimeout(() => {
                  location.reload();
                  emitter.emit("open-listing");
                }, 1000);
              }
            })
            .catch((i) => {
              state.loading = false;
              state.isLoadingDialogue = false;
              state.snackbar = true;
              state.color = "red";
              state.textAlert = i.response.data.error;
            });
        } else {
          axios
            .post("/openvpn/createServerOpenvpn", payload)
            .then((response) => {
              if (response.status == "201") {
                state.loading = false;
                state.isLoadingDialogue = false;
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.msg;

                setTimeout(() => {
                  location.reload();
                  emitter.emit("open-listing");
                }, 1000);
              }
            })
            .catch((i) => {
              state.loading = false;
              state.isLoadingDialogue = false;
              state.snackbar = true;
              state.color = "red";
              state.textAlert = i.response.data.error;
            });
        }
      } else {
        console.log("res", v$.value);
      }
    };

    const cancel = () => {
      state.id = "";
      state.isEditState = "";
      //General information
      state.clientName = "";
      state.description = "";
      state.serverMode = "";
      state.protocol = "";
      state.deviceMode = "";
      state.interface = "";
      state.localPort = "";
      //Cryptographic Settings
      state.isEnableAuth = true;
      state.tlsGenerate = "";
      state.peerCertif = "";
      state.serverCertif = "";
      state.dhParameters = "";
      state.encryptAlgo = "";
      state.authDigest = "";
      // state.hardwareCrypto = {
      //   name: "No Hardware Crypto acceleration",
      //   slug: "No Hardware Crypto acceleration",
      // };
      //tunnelSettings
      state.ip4Tunnel = "";
      state.ip6Tunnel = "";
      state.isGateway = false;
      state.isBridge = false;
      state.interfaceBridge = "";
      state.startDHCPBridge = "";
      state.endDHCPBridge = "";
      state.iPv4Local = "";
      state.iPv6Local = "";
      state.iPv4Remote = "";
      state.iPv6Remote = "";
      state.concurrentConnections = "";
      state.compression = { name: "No preference", slug: "no_preference" };
      state.typefService = false;
      state.Connections = false;
      state.IPv6 = false;
      state.interClients = false;
      //clientSettings
      state.dynamicIP = false;
      state.adressPool = false;
      state.topology = false;
      state.dnsDefaultDomain = false;
      state.dnsServers = false;
      state.forceDNS = false;
      state.ntpServers = false;
      state.clientPort = false;
      state.startAddressPool = "";
      state.endAddressPool = "";
      state.activeDnsDefault = "";
      state.activeDnsServer1 = "";
      state.activeDnsServer2 = "";
      state.activeNtpServer1 = "";
      state.activeNtpServer2 = "";
      state.verbLevel = {
        name: "1 (default)",
        slug: "1",
      };
      v$.value.$reset();
    };

    return {
      getCookie,
      cancel,
      getCertif,
      getInterface,
      authDigestList,
      submitForm,
      compressionList,
      getAllCertAuth,
      deviceModeList,
      protocolList,
      state,
      v$,
      emitter,
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
