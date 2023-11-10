<template>
  <div class="mt-3">
    <v-row>
      <v-col cols="6">
        <div class="ml-3 mr-3">
          <h4>General information</h4>
          <v-divider class="mt-2"></v-divider>
          <v-row class="mt-2">
            <v-col cols="4">
              <label>Client name</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                label="Client name"
                v-model="genericInformation.clientName"
              ></v-text-field>
            </v-col>
            <v-col cols="4">
              <label>Description</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                label="Description"
                v-model="genericInformation.description"
              ></v-text-field>
            </v-col>
            <v-col cols="4">
              <label>Server mode</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select
                label="Server mode"
                v-model="genericInformation.server_mode"
                :items="serverMode"
                item-title="name"
                item-value="slug"
                return-object
              ></v-select>
            </v-col>
            <v-col cols="4">
              <label>Protocol</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select
                label="Protocol"
                v-model="genericInformation.protocol"
                :items="protocols"
                item-title="name"
                item-value="slug"
                return-object
              ></v-select>
            </v-col>
            <v-col cols="4">
              <label>Device Mode</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select
                label="Device Mode"
                v-model="genericInformation.device_mode"
                :items="deviceMode"
                item-title="name"
                item-value="slug"
                return-object
              ></v-select>
            </v-col>
            <v-col cols="4">
              <label>Interface</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select
                label="Interface"
                v-model="genericInformation.interface"
                :items="genericInformation.mapedInterface"
                item-title="name"
                item-value="id"
                return-object
              ></v-select>
            </v-col>
            <v-col cols="4">
              <label>Retry DNS resolution</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <input
                type="checkbox"
                v-model="genericInformation.resolv_retry"
              />
              <label class="ml-2">Infinitely resolve remote server</label>
            </v-col>
            <template v-if="!genericInformation.resolv_retry" class="ml-1 mt-3">
              <v-col cols="4">
                <label>Proxy host or address</label>
              </v-col>
              <v-col cols="8" class="mb-n6">
                <v-text-field
                  label="Proxy host or address"
                  v-model="genericInformation.proxy_host"
                ></v-text-field>
              </v-col>
              <v-col cols="4">
                <label>Proxy port</label>
              </v-col>
              <v-col cols="8" class="mb-n6">
                <v-text-field
                  label="Proxy port"
                  v-model="genericInformation.proxy_port"
                ></v-text-field>
              </v-col>
            </template>
            <v-col cols="4" class="mt-1">
              <label>Proxy authentication extra options</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select
                label="Proxy authentication extra options"
                v-model="genericInformation.proxyAuthenticationExtraOptions"
                :items="proxyAuthenticationExtraOptionsList"
                item-title="name"
                item-value="slug"
                return-object
              ></v-select>
            </v-col>
            <template
              v-if="
                genericInformation.proxyAuthenticationExtraOptions.slug !=
                'none'
              "
              class="ml-1 mt-3"
            >
              <v-col cols="4"> <label> </label></v-col>
              <v-col cols="8">
                <v-text-field
                  label="Username"
                  v-model="genericInformation.username"
                ></v-text-field>
              </v-col>

              <v-col cols="4"><label> </label> </v-col>
              <v-col cols="8">
                <v-text-field
                  label="Password"
                  v-model="genericInformation.password"
                ></v-text-field>
              </v-col>
              <v-col cols="4">
                <label>Local port</label>
              </v-col>
              <v-col cols="8" class="mb-n6">
                <v-text-field
                  label="Local port"
                  v-model="genericInformation.local_port"
                ></v-text-field>
              </v-col>
            </template>
          </v-row>
          <v-row class="mt-2">
            <div class="ml-3 mr-3">
              <v-row class="mt-2">
                <userAuthSettings
                  v-model:username="userAuthSettings.username"
                  v-model:password="userAuthSettings.password"
                  v-model:renegotiate_time="userAuthSettings.renegotiate_time"
                />
                <cryptoSettings
                  v-model:tlsGenerate="cryptoSettings.tlsGenerate"
                  v-model:sharedKey="cryptoSettings.sharedKey"
                  v-model:peerCertificateAuthority="
                    cryptoSettings.peerCertificateAuthority
                  "
                  v-model:clientCertificate="cryptoSettings.clientCertificate"
                  v-model:encryptionAlgorithm="
                    cryptoSettings.encryptionAlgorithm
                  "
                  v-model:authDigestAlgorithm="
                    cryptoSettings.authDigestAlgorithm
                  "
                  v-model:hardwareCrypto="cryptoSettings.hardwareCrypto"
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
              v-model:ipv4TunnelNetwork="tunnelSettings.ipv4TunnelNetwork"
              v-model:ipv6TunnelNetwork="tunnelSettings.ipv6TunnelNetwork"
              v-model:ipv4RemoteNetwork="tunnelSettings.ipv4RemoteNetwork"
              v-model:ipv6RemoteNetwork="tunnelSettings.ipv6RemoteNetwork"
              v-model:limitOutgoingBandwidth="
                tunnelSettings.limitOutgoingBandwidth
              "
              v-model:compression="tunnelSettings.compression"
              v-model:typeOfService="tunnelSettings.typeOfService"
              v-model:ipv6="tunnelSettings.ipv6"
              v-model:pullRoutes="tunnelSettings.pullRoutes"
              v-model:addRemoveRoutes="tunnelSettings.addRemoveRoutes"
            />
          </v-row>
          <advancedConfig
            v-model:verbosityLevel="advancedConfig.verbosityLevel"
            v-model:remoteServer="advancedConfig.remoteServer"
          />
        </div>
      </v-col>
    </v-row>
    <v-row class="flex py-8">
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
            type="submit"
            class="ml-2"
            @click="save"
          />
        </div>
      </v-col>
    </v-row>
    <br />
    <v-spacer></v-spacer>
  </div>
</template>

<script>
import tunnelSettings from "./clientComponents/tunnelSettings.vue";
import advancedConfig from "./clientComponents/advancedConfig.vue";
import userAuthSettings from "./clientComponents/userAuthSettings.vue";
import cryptoSettings from "./clientComponents/cryptoSettings.vue";
import VButton from "@/components/VButton.vue";
import { reactive, onMounted, ref } from "vue";
import axios from "axios";
import protocols from "@/constants/protocols.js";

export default {
  name: "ClientsOpenvpnComponent",
  components: {
    tunnelSettings,
    advancedConfig,
    userAuthSettings,
    cryptoSettings,
    VButton,
  },
  setup() {
    const protocolsList = ref([]);
    const deviceMode = ref([
      {
        name: "TUN",
        slug: "tun",
      },
      {
        name: "TAP",
        slug: "tap",
      },
    ]);

    const proxyAuthenticationExtraOptionsList = ref([
      {
        name: "None",
        slug: "none",
      },
      {
        name: "Basic",
        slug: "basic",
      },
      {
        name: "NTLM",
        slug: "ntlm",
      },
    ]);

    const serverMode = ref([
      {
        name: "Peer to Peer (SSL/TLS)",
        slug: "peer_to_peer",
      },
      {
        name: "Peer to Peer (SSL/TLS) + User Auth",
        slug: "peer_to_peer_user_auth",
      },
      {
        name: "Server (SSL/TLS)",
        slug: "server",
      },
      {
        name: "Server (SSL/TLS) + User Auth",
        slug: "server_user_auth",
      },
    ]);

    const genericInformation = reactive({
      clientName: "",
      description: "",
      server_mode: "",
      protocol: "",
      device_mode: "",
      interface: "",
      resolv_retry: "",
      proxy_host: "",
      proxy_port: "",
      proxyAuthenticationExtraOptions: "",
      username: "",
      password: "",
      local_port: "",
      mapedInterface: [],
    });

    const userAuthSettings = reactive({
      username: "",
      password: "",
      renegotiate_time: "",
    });

    const cryptoSettings = reactive({
      tlsGenerate: "",
      sharedKey: "",
      peerCertificateAuthority: "",
      clientCertificate: "",
      encryptionAlgorithm: "",
      authDigestAlgorithm: "",
      hardwareCrypto: "",
    });

    const tunnelSettings = reactive({
      ipv4TunnelNetwork: "",
      ipv6TunnelNetwork: "",
      ipv4RemoteNetwork: "",
      ipv6RemoteNetwork: "",
      limitOutgoingBandwidth: "",
      compression: "",
      typeOfService: "",
      ipv6: "",
      pullRoutes: "",
      addRemoveRoutes: "",
    });

    const advancedConfig = reactive({
      verbosityLevel: "",
      remoteServer: "",
    });

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
          genericInformation.mapedInterface = interfaces;
        },
        (error) => {
          console.log(error);
        }
      );
    };

    const cancel = () => {
      genericInformation = { ...genericInformation };
      userAuthSettings = { ...userAuthSettings };
      cryptoSettings = { ...cryptoSettings };
      tunnelSettings = { ...tunnelSettings };
      advancedConfig = { ...advancedConfig };
    };

    const save = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      const params = {
        name: genericInformation.clientName,
        description: genericInformation.description,
        server_mode: {
          mode: genericInformation.server_mode.slug,
        },
        protocol: genericInformation.protocol.slug,
        device_mode: genericInformation.device_mode.slug,
        interface: genericInformation.interface.id,
        resolv_retry: genericInformation.resolv_retry,
        proxy_host: genericInformation.proxy_host,
        proxy_port: genericInformation.proxy_port,
        proxy_authentication: {
          option: genericInformation.proxyAuthenticationExtraOptions.slug,
          username: genericInformation.username,
          password: genericInformation.password,
        },
        local_port: genericInformation.local_port,
        username: userAuthSettings.username,
        password: userAuthSettings.password,
        renegotiate_time: userAuthSettings.renegotiate_time,
        tls_auth: {
          generate: cryptoSettings.tlsGenerate,
          tls_key: cryptoSettings.sharedKey,
        },
        ca_name: cryptoSettings.peerCertificateAuthority.name,
        client_cert: cryptoSettings.clientCertificate.name,
        encryption_algorithm: cryptoSettings.encryptionAlgorithm.slug,
        auth_digest_algorithm: cryptoSettings.authDigestAlgorithm.slug,
        hardware_crypto: cryptoSettings.hardwareCrypto.slug,
        ipv4_tunnel_network: tunnelSettings.ipv4TunnelNetwork,
        ipv4_remote_network: tunnelSettings.ipv4RemoteNetwork,
        limit_outgoing_bandwidth: tunnelSettings.limitOutgoingBandwidth,
        compression: tunnelSettings.compression.slug,
        type_of_service: tunnelSettings.typeOfService,
        ipv6: tunnelSettings.ipv6,
        pull_routes: tunnelSettings.pullRoutes,
        add_remove_routes: tunnelSettings.addRemoveRoutes,
        verbosity_level: advancedConfig.verbosityLevel.slug,
        server_name: advancedConfig.remoteServer.name,
      };

      axios.post("/openvpn/createClientOpenvpn", params).then(
        (response) => {
          console.log(response);
        },
        (error) => {
          console.log(error);
        }
      );
    };

    onMounted(() => {
      getInterface();
      protocolsList.value = protocols;
    });

    return {
      genericInformation,
      userAuthSettings,
      cryptoSettings,
      tunnelSettings,
      advancedConfig,
      protocols: protocolsList,
      deviceMode,
      proxyAuthenticationExtraOptionsList,
      serverMode,
      getCookie,
      getInterface,
      cancel,
      save,
    };
  },
};
</script>

<style lang="scss"></style>
