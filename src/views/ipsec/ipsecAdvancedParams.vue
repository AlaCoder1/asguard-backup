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
          :keyExchange="state.keyExchange"
          :authMethodItem="state.authMethod"
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
          :isdeadPeer="state.deadPeer"
        />
      </v-col>
      <v-col cols="6">
        <generalInfoPhaseTwo
          v-model:mode="state.mode"
          v-model:remoteTunnelAddress="state.remoteTunnelAddress"
          v-model:type="state.type"
          v-model:remoteNetworkAddress="state.remoteNetworkAddress"
          v-model:selectAddressNetwork="state.selectAddressNetwork"
          v-model:description="state.descriptionPh2"
          v-model:localAddress="state.localAddress"
          v-model:localNetworkAddress="state.localNetworkAddress"
          v-model:selectRemoteAddressNetwork="state.selectRemoteAddressNetwork"
          v-model:typeRemoteNetwork="state.typeRemoteNetwork"
          :isMode="state.mode"
          :isTypeWAn="state.isTypeWAn"
          :defaultValue="state.defaultValue"
          :isDefault="state.isDefault"
          :isDefaultRemote="state.isDefaultRemote"
          :defaultValueRemote="state.defaultValueRemote"
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
          :isMode="state.mode"
          :isProtocol="state.protocol"
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
import { reactive, onMounted, computed, watch } from "vue";
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
      defaultValueRemote: "",
      isDefaultRemote: false,
      defaultValue: "",
      isDefault: false,
      isTypeWAn: false,
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
        slug: "256",
      },
      hashAlgo: {
        name: "SHA256",
        slug: "sha256",
      },
      dhKey: {
        name: "20 (NIST EC 384 bits)",
        slug: "20:384",
      },
      lifetime: "28800s",
      //advancedOptions
      policy: true,
      rekey: false,
      reauth: false,
      natTraversal: { name: "Unforce", slug: "Disable" },
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
      descriptionPh2: "",
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
        slug: "256",
      },
      hashAlgoExchange: {
        name: "SHA256",
        slug: "sha256",
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
        negotiationMode: {
          requiredIfFuction: helpers.withMessage(
            "This field must be indicated",
            requiredIf(() => state.keyExchange.slug === "v1")
          ),
        },

        sharedKey: {
          requiredIfFuction: helpers.withMessage(
            "This field must be indicated",
            requiredIf(() => state.authMethod.slug === "Mutual PSK")
          ),
          isValidKey: helpers.withMessage(
            `There must be at least 32 characters, including at least one uppercase,one lowercase, one number, and one special character.`,

            helpers.regex(
              /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~])[A-Za-z\d!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]{32,128}$/
            )
          ),
        },

        certificate: {
          requiredIfFuction: helpers.withMessage(
            "This field must be indicated",
            requiredIf(() => state.authMethod.slug === "Mutual RSA")
          ),
        },

        keyPair: {
          requiredIfFuction: helpers.withMessage(
            "This field must be indicated",
            requiredIf(() => state.authMethod.slug === "Mutual Public key")
          ),
        },

        localKey: {
          requiredIfFuction: helpers.withMessage(
            "This field must be indicated",
            requiredIf(() => state.authMethod.slug === "Mutual Public key")
          ),
        },

        peerIdentifier: {
          requiredIfFuction: helpers.withMessage(
            "This field must be indicated",
            requiredIf(() => state.authMethod.slug === "Mutual RSA")
          ),
        },

        // phase algo
        encryptAlgo: { required },
        hashAlgo: { required },
        dhKey: { required },
        // general info phase 2
        mode: { required },
        // remoteTunnelAddress: {
        //   required,
        //   isValidRemoteTunnelAddress: helpers.withMessage(
        //     `Format must be like adresse IP : X.X.X.X`,

        //     helpers.regex(/^[0-9.]+$/)
        //   ),
        // },
        type: { required },

        remoteNetworkAddress: {
          requiredIfFuction: helpers.withMessage(
            "This field must be indicated",
            requiredIf(() => state.mode.slug === "Tunnel IPv4")
          ),
          isValidremoteNetworkAddress: helpers.withMessage(
            `Format must be like adresse IP : X.X.X.X`,

            helpers.regex(/^[0-9.]+$/)
          ),
        },

        selectAddressNetwork: {
          requiredIfFuction: helpers.withMessage(
            "This field must be indicated",
            requiredIf(() => state.type.slug === "Network")
          ),
        },
        // description: { required },

        // localAddress: {
        //   required,
        //   isValidlocalAddress: helpers.withMessage(
        //     `Format must be like adresse IP : X.X.X.X`,

        //     helpers.regex(/^[0-9.]+$/)
        //   ),
        // },

        localNetworkAddress: {
          requiredIfFuction: helpers.withMessage(
            "This field must be indicated",
            requiredIf(
              () =>
                (state.type.slug === "Network" ||
                  state.type.slug === "Address") &&
                state.mode.slug === "Tunnel IPv4"
            )
          ),
          isValidlocalNetworkAddress: helpers.withMessage(
            `Format must be like adresse IP : X.X.X.X`,

            helpers.regex(/^[0-9.]+$/)
          ),
        },

        selectRemoteAddressNetwork: {
          requiredIfFuction: helpers.withMessage(
            "This field must be indicated",
            requiredIf(
              () =>
                state.typeRemoteNetwork.slug === "Network" &&
                state.mode.slug === "Tunnel IPv4"
            )
          ),
        },

        typeRemoteNetwork: { required },
        //exchange
        protocol: { required },
        encryptAlgoExchange: { required },
        hashAlgoExchange: { required },
        pfsKey: { required },
        // pingHost: { required },
        // spdEntries: { required },
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

    watch(
      state,
      () => {
        console.log("state", state);
        if (state.type.slug === "WAN" || state.type.slug === "LAN") {
          state.isTypeWAn = true;
        } else {
          state.isTypeWAn = false;
        }
        if (state.type.slug === "Address") {
          state.defaultValue = "32";
          state.selectAddressNetwork = "";
          state.isDefault = true;
        } else if (state.type.slug === "Network") {
          state.defaultValue = "mask";
          state.isDefault = false;
        } else {
          state.defaultValue = "32";
          state.isDefault = false;
        }
        if (state.typeRemoteNetwork.slug === "Address") {
          state.selectRemoteAddressNetwork = "";
          state.defaultValueRemote = "32";
          state.isDefaultRemote = true;
        } else {
          state.defaultValueRemote = "mask";
          state.isDefaultRemote = false;
        }
      },
      { immediate: true }
    );

    const save = async () => {
      console.log("save", state);
      const result = await v$.value.$validate();

      if (result) {
        let KeyExchange = null;

        if (state.keyExchange.slug === "v1") {
          KeyExchange = {
            key_exchange_version: state.keyExchange?.name,
            negotiation_mode: state.negotiationMode.name,
          };
        } else {
          KeyExchange = {
            key_exchange_version: state.keyExchange?.name,
          };
        }
        let authen = null;
        if (state.authMethod?.slug === "Mutual Public key") {
          authen = {
            authentication_method: state.authMethod?.slug,
            local_key_pair: state.localKey,
            peer_key_pair: state.keyPair,
          };
        } else if (state.authMethod?.slug === "Mutual PSK") {
          authen = {
            authentication_method: state.authMethod?.slug,
            pre_shared_key: state.sharedKey,
          };
        } else if (state.authMethod?.slug === "Mutual RSA") {
          authen = {
            authentication_method: state.authMethod?.slug,
            cert: state.certificate.name,
            remote_distingushed_name: state.peerIdentifier,
          };
        }

        let isdeadPeer = null;

        if (state.deadPeer) {
          isdeadPeer = {
            disable: state.deadPeer,
            deed_peer_delay: state.seconds,
            deed_peer_timeout: state.retries,
            deed_peer_action: state.selectDear.slug,
          };
        } else {
          isdeadPeer = {
            disable: state.deadPeer,
          };
        }
        if (Array.isArray(state.dhKey)) {
          var mappedDhKey = state.dhKey.map((e) => e.slug);
        } else {
          var mappedDhKey = [state.dhKey.slug];
        }
        if (Array.isArray(state.hashAlgo)) {
          var mappedhashAlgo = state.hashAlgo.map((e) => e.slug);
        } else {
          var mappedhashAlgo = [state.hashAlgo.slug];
        }
        if (Array.isArray(state.encryptAlgoExchange)) {
          var mappedencryptAlgoExchange = state.encryptAlgoExchange.map(
            (e) => e.slug
          );
        } else {
          var mappedencryptAlgoExchange = [state.encryptAlgoExchange.slug];
        }
        if (Array.isArray(state.hashAlgoExchange)) {
          var mappedhashAlgoExchange = state.hashAlgoExchange.map(
            (e) => e.slug
          );
        } else {
          var mappedhashAlgoExchange = [state.hashAlgoExchange.slug];
        }

        let isKeyExchange = null;

        if (state.protocol.slug === "ESP") {
          isKeyExchange = {
            protocol: state.protocol.slug,
            encryption_algorithm_ph2: mappedencryptAlgoExchange,
            hash_algorithm_ph2: mappedhashAlgoExchange,
            pfs_key_group: state.pfsKey.slug,
          };
        } else if (state.protocol.slug === "AH") {
          isKeyExchange = {
            protocol: state.protocol.slug,
            hash_algorithm_ph2: mappedhashAlgoExchange,
            pfs_key_group: state.pfsKey.slug,
          };
        }

        let isMode_ph2 = null;

        if (state.mode.slug === "Tunnel IPv4") {
          isMode_ph2 = {
            mode: state.mode?.slug,
            local_network: {
              type_local_network: state.type?.slug,
              address_local_network: state.localNetworkAddress,
              mask:
                state.type?.slug === "Address"
                  ? "32"
                  : state.selectAddressNetwork.toString(),
            },
            remote_network: {
              type_remote_network: state.typeRemoteNetwork.slug,
              address_local_network: state.remoteNetworkAddress,
              mask:
                state.typeRemoteNetwork.slug === "Address"
                  ? "32"
                  : state.selectRemoteAddressNetwork.toString(),
            },
          };
        } else if (state.mode.slug === "Transport") {
          isMode_ph2 = {
            mode: state.mode?.slug,
          };
        }

        let payload = {
          conn_name: state.tunnelSettings,
          connection_method: state.connectionMethod?.slug,
          key_exchange: KeyExchange,
          internet_protocol: state.internetProtocol.slug,
          interface_name: state.generalinterface?.name,
          remote_gateway: state.remoteGateway,
          dynamic_gateway: state.remoteConnect,
          description_ph1: state.description,
          authentication: authen,
          encryption_algorithm_ph1: state.encryptAlgo?.slug,
          hash_algorithm_ph1: mappedhashAlgo,
          dh_key_group: mappedDhKey,
          lifetime_ph1: state.lifetime,
          policy: state.policy,
          rekey: state.rekey,
          reauth: state.reauth,
          mobike: state.mobike,
          nat_traversal: state.natTraversal.slug,
          inactivity_timeout: state.interactivityTimout,
          margin_time: state.marginTime,
          rekey_fuzz: state.rekeyFuzz,
          deed_peer: isdeadPeer,
          description_ph2: state.descriptionPh2,
          lifetime_ph2: state.lifetimeExchange,
          sa_key_exchange: isKeyExchange,
          mode_ph2: isMode_ph2,
        };
        console.log("payload", payload);
        axios
          .post("/ipsec/createServerIPsec", payload)
          .then((response) => {
            if (response.status == "201") {
              state.snackbar = true;
              state.color = "success";
              state.textAlert = response.data.msg;
              setTimeout(() => {
                location.reload();
              }, 1000);
            }
          })
          .catch((i) => {
            state.snackbar = true;
            state.color = "red";
            state.textAlert = i.response.data.error;
          });
      } else {
        console.log("error", v$.value);
      }
    };

    return {
      getCookie,
      getInterface,
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
