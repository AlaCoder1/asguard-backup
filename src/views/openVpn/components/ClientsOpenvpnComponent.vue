<template>
  <div class="mt-3">
    <v-row>
      <v-col align-self="center" cols="6">
        <div class="ml-3 mr-3">
          <h4>General information</h4>
          <v-divider class="mt-2"></v-divider>
          <v-row class="mt-2">
            <v-col align-self="center" cols="4">
              <label>Client name</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                label="Client name"
                v-model="state.clientName"
              ></v-text-field>
              <p
                class="error-feedback mb-5"
                v-if="v$.clientName.$errors.length"
              >
                {{ v$.clientName.$errors?.[0].$message }}
              </p>
            </v-col>
            <v-col align-self="center" cols="4">
              <label>Description</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                label="Description"
                v-model="state.description"
              ></v-text-field>
            </v-col>
            <v-col align-self="center" cols="4">
              <label>Server mode</label>
            </v-col>
            <v-col align-self="center" cols="8" class="mb-n6">
              <v-select
                label="Server mode"
                v-model="state.server_mode"
                :items="serverMode"
                item-title="name"
                item-value="slug"
                return-object
              ></v-select>
              <p
                class="error-feedback mb-5"
                v-if="v$.server_mode.$errors.length"
              >
                {{ v$.server_mode.$errors?.[0].$message }}
              </p>
            </v-col>
            <v-col align-self="center" cols="4">
              <label>Protocol</label>
            </v-col>
            <v-col align-self="center" cols="8" class="mb-n6">
              <v-select
                label="Protocol"
                v-model="state.protocol"
                :items="protocols"
                item-title="name"
                item-value="slug"
                return-object
              ></v-select>
              <p class="error-feedback mb-5" v-if="v$.protocol.$errors.length">
                {{ v$.protocol.$errors?.[0].$message }}
              </p>
            </v-col>
            <v-col align-self="center" cols="4">
              <label>Device Mode</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select
                label="Device Mode"
                v-model="state.device_mode"
                :items="deviceMode"
                item-title="name"
                item-value="slug"
                return-object
              ></v-select>
              <p
                class="error-feedback mb-5"
                v-if="v$.device_mode.$errors.length"
              >
                {{ v$.device_mode.$errors?.[0].$message }}
              </p>
            </v-col>
            <v-col align-self="center" cols="4">
              <label>Interface</label>
            </v-col>
            <v-col align-self="center" cols="8" class="mb-n6">
              <v-select
                label="Interface"
                v-model="state.interface"
                :items="state.mapedInterface"
                item-title="name"
                item-value="id"
                return-object
              ></v-select>
              <p class="error-feedback mb-5" v-if="v$.interface.$errors.length">
                {{ v$.interface.$errors?.[0].$message }}
              </p>
            </v-col>
            <v-col align-self="center" cols="4">
              <label>Retry DNS resolution</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <input type="checkbox" v-model="state.resolv_retry" />
              <label class="ml-2">Infinitely resolve remote server</label>
            </v-col>

            <v-col align-self="center" cols="4">
              <label>Proxy host or address</label>
            </v-col>
            <v-col align-self="center" cols="8" class="mb-n6">
              <v-text-field
                label="Proxy host or address"
                v-model="state.proxy_host"
              ></v-text-field>
            </v-col>
            <v-col align-self="center" cols="4">
              <label>Proxy port</label>
            </v-col>
            <v-col align-self="center" cols="8" class="mb-n6">
              <v-text-field
                label="Proxy port"
                v-model="state.proxy_port"
              ></v-text-field>
            </v-col>

            <v-col align-self="center" cols="4" class="mt-1">
              <label>Proxy authentication extra options</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select
                label="Proxy authentication extra options"
                v-model="state.proxyAuthenticationExtraOptions"
                :items="proxyAuthenticationExtraOptionsList"
                item-title="name"
                item-value="slug"
                return-object
              ></v-select>
            </v-col>
            <template
              v-if="state.proxyAuthenticationExtraOptions.slug != 'none'"
              class="ml-1 mt-3"
            >
              <v-col align-self="center" cols="4"> <label> </label></v-col>
              <v-col align-self="center" cols="8">
                <v-text-field
                  label="Username"
                  v-model="state.username"
                ></v-text-field>
                <p
                  class="error-feedback mb-5"
                  v-if="v$.username.$errors.length"
                >
                  {{ v$.username.$errors?.[0].$message }}
                </p>
              </v-col>

              <v-col align-self="center" cols="4"><label> </label> </v-col>
              <v-col align-self="center" cols="8">
                <v-text-field
                  label="Password"
                  v-model="state.password"
                ></v-text-field>
                <p
                  class="error-feedback mb-5"
                  v-if="v$.password.$errors.length"
                >
                  {{ v$.password.$errors?.[0].$message }}
                </p>
              </v-col>
            </template>
          </v-row>
          <v-row>
            <v-col align-self="center" cols="4">
              <label>Local port</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                label="Local port"
                v-model="state.local_port"
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row class="mt-2">
            <div class="ml-3 mr-3">
              <v-row class="mt-2">
                <userAuthSettings
                  v-model:username="state.usernameUser"
                  v-model:password="state.passwordUser"
                  v-model:renegotiate_time="state.renegotiate_time"
                />
                <cryptoSettings
                  v-model:tlsGenerate="state.tlsGenerate"
                  v-model:sharedKey="state.sharedKey"
                  v-model:peerCertificateAuthority="
                    state.peerCertificateAuthority
                  "
                  v-model:clientCertificate="state.clientCertificate"
                  v-model:encryptionAlgorithm="state.encryptionAlgorithm"
                  v-model:authDigestAlgorithm="state.authDigestAlgorithm"
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
              v-model:ipv4TunnelNetwork="state.ipv4TunnelNetwork"
              v-model:ipv6TunnelNetwork="state.ipv6TunnelNetwork"
              v-model:ipv4RemoteNetwork="state.ipv4RemoteNetwork"
              v-model:ipv6RemoteNetwork="state.ipv6RemoteNetwork"
              v-model:limitOutgoingBandwidth="state.limitOutgoingBandwidth"
              v-model:compression="state.compression"
              v-model:typeOfService="state.typeOfService"
              v-model:ipv6="state.ipv6"
              v-model:pullRoutes="state.pullRoutes"
              v-model:addRemoveRoutes="state.addRemoveRoutes"
              :errors="v$"
            />
          </v-row>
          <advancedConfig
            v-model:verbosityLevel="state.verbosityLevel"
            v-model:hostAddress="state.hostAddress"
            v-model:port="state.port"
            :errors="v$"
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
import useValidate from "@vuelidate/core";
import { required, requiredIf, helpers } from "@vuelidate/validators";
import tunnelSettings from "./clientComponents/tunnelSettings.vue";
import advancedConfig from "./clientComponents/advancedConfig.vue";
import userAuthSettings from "./clientComponents/userAuthSettings.vue";
import cryptoSettings from "./clientComponents/cryptoSettings.vue";
import VButton from "@/components/VButton.vue";
import { reactive, onMounted, ref, computed, watch } from "vue";
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

    const state = reactive({
      //general information
      clientName: "",
      description: "",
      server_mode: "",
      protocol: "",
      device_mode: "",
      interface: "",
      resolv_retry: false,
      proxy_host: "",
      proxy_port: "",
      proxyAuthenticationExtraOptions: {
        name: "None",
        slug: "none",
      },
      usernameUser: "",
      passwordUser: "",

      username: "",
      password: "",
      local_port: "",
      mapedInterface: [],
      //User Auth
      username: "",
      password: "",
      renegotiate_time: "",
      //cryp
      tlsGenerate: true,
      sharedKey: "",
      peerCertificateAuthority: "",
      clientCertificate: "",
      encryptionAlgorithm: "",
      authDigestAlgorithm: "",
      hardwareCrypto: "",
      //tunnelSettings
      ipv4TunnelNetwork: "",
      ipv6TunnelNetwork: "",
      ipv4RemoteNetwork: "",
      ipv6RemoteNetwork: "",
      limitOutgoingBandwidth: "",
      compression: { name: "No preference", slug: "no_preference" },
      typeOfService: "",
      ipv6: "",
      pullRoutes: "",
      addRemoveRoutes: "",
      //advancedConfig
      verbosityLevel: "",
      remoteServer: "",
      hostAddress: "",
      port: "",
    });

    const rules = computed(() => {
      return {
        clientName: { required },
        server_mode: { required },
        protocol: { required },
        device_mode: { required },
        interface: { required },

        sharedKey: {
          requiredIfFuction: requiredIf(() => !state.tlsGenerate),
        },
        username: {
          requiredIfFuction: requiredIf(
            () => state.proxyAuthenticationExtraOptions.slug === "basic"
          ),
        },
        password: {
          requiredIfFuction: requiredIf(
            () => state.proxyAuthenticationExtraOptions.slug === "basic"
          ),
        },
        peerCertificateAuthority: { required },
        clientCertificate: { required },
        authDigestAlgorithm: { required },
        hardwareCrypto: { required },
        encryptionAlgorithm: { required },

        ipv4TunnelNetwork: { required },
        ipv4RemoteNetwork: { required },
        verbosityLevel: { required },
        hostAddress: { required },

        port: {
          required,
          isValidlifeTime: helpers.withMessage(
            `champs local Port can include only Numbers.`,
            helpers.regex(/^[0-9]+$/)
          ),
        },
      };
    });

    const v$ = useValidate(rules, state);
    watch(
      state,
      () => {
        if (state.proxyAuthenticationExtraOptions) {
          v$.value.username.$reset();
          v$.value.password.$reset();
        }
      },
      { immediate: true }
    );

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

    const save = async () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      const result = await v$.value.$validate();

      if (result) {
        let proxy_authentication = null;
        if (state.proxyAuthenticationExtraOptions.slug === "none") {
          proxy_authentication = {
            option: "none",
          };
        } else {
          proxy_authentication = {
            option: state.proxyAuthenticationExtraOptions.slug,
            username: state.username,
            password: state.password,
          };
        }
        let tls_auth = null;
        if (state.tlsGenerate) {
          tls_auth = {
            generate: state.tlsGenerate,
          };
        } else {
          tls_auth = {
            generate: state.tlsGenerate,
            tls_key: state.sharedKey,
          };
        }
        let payload = {
          name: state.clientName,
          description: state.description,
          server_mode: {
            mode: state.server_mode.slug,
          },
          protocol: state.protocol.slug,
          device_mode: state.device_mode.slug,
          interface: state.interface.id,
          resolv_retry: state.resolv_retry,
          proxy_host: state.proxy_host ?? "",
          proxy_port: state.proxy_port ?? "",
          proxy_authentication: proxy_authentication,
          local_port: state.local_port,
          username: state.username,
          password: state.password,
          renegotiate_time: state.renegotiate_time,
          tls_auth: tls_auth,
          auth_digest_algorithm: state.authDigestAlgorithm.slug,
          ca_name: state.peerCertificateAuthority.name,
          client_cert: state.clientCertificate.name,
          encryption_algorithm: state.encryptionAlgorithm.slug,
          hardware_crypto: state.hardwareCrypto.slug,
          ipv4_tunnel_network: state.ipv4TunnelNetwork,
          ipv4_remote_network: state.ipv4RemoteNetwork,
          limit_outgoing_bandwidth: state.limitOutgoingBandwidth,
          compression: state.compression.slug,
          type_of_service: state.typeOfService,
          ipv6: state.ipv6,
          pull_routes: state.pullRoutes,
          add_remove_routes: state.addRemoveRoutes,
          verbosity_level: state.verbosityLevel.slug,
          server_host: state.hostAddress,
          server_port: state.port,
        };

        axios.post("/openvpn/createClientOpenvpn", payload).then(
          (response) => {
            console.log(response);
          },
          (error) => {
            console.log(error);
          }
        );
      } else {
        console.log("v$.value", v$.value);
      }
    };

    onMounted(() => {
      getInterface();
      protocolsList.value = protocols;
    });

    return {
      state,
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
      v$,
      save,
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
