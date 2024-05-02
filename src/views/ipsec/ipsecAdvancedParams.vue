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
          :connectionMethodList="connectionMethodList"
          :exchangeList="exchangeList"
          :protocolList="protocolList"
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
          :authenticationMethodList="authenticationMethodList"
          :negotiationList="negotiationList"
          :CertificateList="CertificateList"
          :CertificateListRemote="CertificateListRemote"
          :mapedKeyPublic="mapedKeyPublic"
          :errors="v$"
        />

        <phaseAlgo
          v-model:encryptAlgo="state.encryptAlgo"
          v-model:hashAlgo="state.hashAlgo"
          v-model:dhKey="state.dhKey"
          v-model:lifetime="state.lifetime"
          v-model:encryptAlgoV1="state.encryptAlgoV1"
          :dhKeyList="dhKeyList"
          :encryptAlgoList="encryptAlgoList"
          :hashAlgoList="hashAlgoList"
          :keyExchange="state.keyExchange"
          :filteredEncryptAlgoListV1="filteredEncryptAlgoListV1"
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
          :traversalList="traversalList"
          :deadPeerList="deadPeerList"
          :errors="v$"
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
          :modeList="modeList"
          :mapedInterfaceType="mapedInterfaceType"
          :numberList="numberList"
          :remoteTypeList="remoteTypeList"
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
          v-model:encryptAlgoExch2="state.encryptAlgoExch2"
          :isMode="state.mode"
          :isProtocol="state.protocol"
          :hashAlgoList="hashAlgoList"
          :protocolListph2="protocolListph2"
          :pfsList="pfsList"
          :encryptAlgoListExchange="encryptAlgoListExchange"
          :filteredAlgoListExchangeV1="filteredAlgoListExchangeV1"
          :keyExchange="state.keyExchange"
          :errors="v$"
        />
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
            :label="$t('PageGeneral.form.Cancel')"
            :isLarge="true"
            @click="cancel"
          />
          <VButton
            rounded
            outlined
            color="#213E9F"
            label-color="#ffffff"
            :label="state.isEditState === 'edit' ? $t('PageGeneral.form.Edit') : $t('buttons.create')"
            :isLarge="true"
            class="ml-2"
            @click="save"
          />
        </div>
      </v-col>
    </v-row>
    <!-- return json.dumps(list_ipsec) -->

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
import { inject, ref, toRefs } from "vue";
import useValidate from "@vuelidate/core";
import VButton from "@/components/VButton.vue";
import { required, requiredIf, helpers } from "@vuelidate/validators";
import { reactive, onMounted, computed, watch} from "vue";
import generalInfoPhaseOne from "./component/general_info_phase_one.vue";
import phaseAuth from "./component/phase_authentification.vue";
import phaseAlgo from "./component/phase_algorithms.vue";
import advancedOption from "./component/advancedOptions.vue";
import generalInfoPhaseTwo from "./component/general_info_phase_two.vue";
import phaseTwoExchange from "./component/phase_two_exchange.vue";
import { useI18n } from "vue-i18n";

export default {
  name: "IpsecComponent",
  components: {
    generalInfoPhaseOne,
    generalInfoPhaseTwo,
    phaseTwoExchange,
    phaseAuth,
    phaseAlgo,
    advancedOption,
    VButton,
  },
  props: ["dataServer"],
  setup(props) {
    const { t } = useI18n();
    const emitter = inject("emitter");

    const { dataServer } = toRefs(props);
    const state = reactive({
      loading: false,
      isLoadingDialogue: false,
      id: null,
      isEditState: "Create",
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
        slug: "V2",
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
      encryptAlgoV1: {
        name: "AES256",
        slug: "aes256",
      },
      hashAlgo: {
        name: "SHA256",
        slug: "sha256",
      },
      dhKey: {
        name: "20 (NIST EC 384 bits)",
        slug: "20:384",
      },
      lifetime: "28800",
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
      encryptAlgoExch2: {
        name: "AES256",
        slug: "aes256",
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
    

    const connectionMethodList = ref([
      {
        name: "Default",
        slug: "default",
      },
      { name: "Respond only", slug: "Respond Only" },
      {
        name: "Start on traffic",
        slug: "Start on traffic",
      },
      {
        name: "Start immediate",
        slug: "Start immediate",
      },
    ]);
    const exchangeList = ref([
      {
        name: "auto",
        slug: "auto",
      },
      { name: "V1", slug: "V1" },
      {
        name: "V2",
        slug: "V2",
      },
    ]);
    const authenticationMethodList = ref([
      {
        name: "Mutual PSK",
        slug: "Mutual PSK",
      },
      { name: "Mutual Public key", slug: "Mutual Public key" },
      {
        name: "Mutual RSA",
        slug: "Mutual RSA",
      },
    ]);
    const negotiationList = ref([
      {
        name: "Main",
        slug: "Main",
      },
      { name: "Aggressive", slug: "Aggressive" },
    ]);
    const protocolList = ref([
      {
        name: "IPv4",
        slug: "IPv4",
      },
      { name: "IPv6", slug: "IPv6" },
    ]);
    const dhKeyList = ref([
      {
        name: "15 (3072 bits)",
        slug: "15:3072",
      },
      { name: "16 (4096 bits)", slug: "16:4096" },
      {
        name: "17 (6144 bits)",
        slug: "17:6144",
      },
      {
        name: "18 (8192 bits)",
        slug: "18:8192",
      },
      {
        name: "19 (NIST EC 256 bits)",
        slug: "19:256",
      },
      {
        name: "20 (NIST EC 384 bits)",
        slug: "20:384",
      },
      {
        name: "21 (NIST EC 521 bits)",
        slug: "21:521",
      },
      {
        name: "28 (Brainpool EC 256 bits)",
        slug: "28:256",
      },
      {
        name: "29 (Brainpool EC 384 bits)",
        slug: "29:384",
      },
      {
        name: "30 (Brainpool EC 512 bits)",
        slug: "30:512",
      },
      {
        name: "31 (Elliptic Curve 25519)",
        slug: "31:25519",
      },
    ]);

    const encryptAlgoList = ref([
      {
        name: "AES128",
        slug: "aes128",
      },
      {
        name: "AES192",
        slug: "aes192",
      },
      {
        name: "AES256",
        slug: "aes256",
      },
      {
        name: "128 bit AES-GCM with 128 bit ICV",
        slug: "128",
      },
      {
        name: "192 bit AES-GCM with 128 bit ICV",
        slug: "192",
      },
      {
        name: "256 bit AES-GCM with 128 bit ICV",
        slug: "256",
      },
    ]);

    const hashAlgoList = ref([
      {
        name: "SHA256",
        slug: "sha256",
      },
      { name: "SHA384", slug: "sha384" },
      {
        name: "SHA512",
        slug: "sha512",
      },
    ]);
    const traversalList = ref([
      {
        name: "Force",
        slug: "Enable",
      },
      { name: "Unforce", slug: "Disable" },
    ]);

    const deadPeerList = ref([
      {
        name: "Default",
        slug: "default",
      },
      { name: "Restart the tunnel", slug: "Restart the tunnel" },
      {
        name: "Stop the tunnel",
        slug: "Stop the tunnel",
      },
    ]);
    const modeList = ref([
      {
        name: "Tunnel IPv4",
        slug: "Tunnel IPv4",
      },
      { name: "Tunnel IPv6", slug: "Tunnel IPv6" },
      { name: "Transport", slug: "Transport" },
    ]);
    const remoteTypeList = ref([
      {
        name: "Address",
        slug: "Address",
      },
      { name: "Network", slug: "Network" },
    ]);

    watch(
      () => dataServer.value,
      (newValue) => {
        if (newValue != "TUNNEL CONFIGURATION") {
          state.isEditState = "";
          cancel();
        }
      }
    );

    const cancel = () => {
      //General information Phase 1
      state.tunnelSettings = "";
      state.connectionMethod = {
        name: "Default",
        slug: "default",
      };
      state.keyExchange = {
        name: "V2",
        slug: "V2",
      };
      state.internetProtocol = {
        name: "IPv4",
        slug: "IPv4",
      };
      state.remoteGateway = "";
      state.generalinterface = "";
      state.remoteConnect = false;
      state.description = "";
      //phase auth
      state.authMethod = {
        name: "Mutual RSA",
        slug: "Mutual RSA",
      };
      state.negotiationMode = {
        name: "Main",
        slug: "Main",
      };
      state.sharedKey = "";
      state.certificate = "";
      state.keyPair = "";
      state.localKey = "";
      state.peerIdentifier = "";
      //phase algo
      state.encryptAlgo = {
        name: "256 bit AES-GCM with 128 bit ICV",
        slug: "256",
      };
      state.hashAlgo = {
        name: "SHA256",
        slug: "sha256",
      };
      state.dhKey = {
        name: "20 (NIST EC 384 bits)",
        slug: "20:384",
      };
      state.lifetime = "28800";
      //advancedOptions
      state.policy = true;
      state.rekey = false;
      state.reauth = false;
      state.natTraversal = { name: "Unforce", slug: "Disable" };
      state.deadPeer = false;
      state.retries = "";
      state.mobike = false;
      state.selectDear = "";
      state.interactivityTimout = "";
      state.interactivityTimout2 = "";
      state.seconds = "";
      state.rekeyFuzz = "";
      state.marginTime = "";
      //general info 2
      state.mode = {
        name: "Tunnel IPv4",
        slug: "Tunnel IPv4",
      };
      state.remoteTunnelAddress = "";
      state.type = {
        name: "Address",
        slug: "Address",
      };
      state.remoteNetworkAddress = "";
      state.selectAddressNetwork = "";
      state.descriptionPh2 = "";
      state.localAddress = "";
      state.localNetworkAddress = "";
      state.selectRemoteAddressNetwork = "";
      state.typeRemoteNetwork = { name: "Network", slug: "Network" };
      //exchange
      state.protocol = {
        name: "ESP",
        slug: "ESP",
      };
      state.encryptAlgoExchange = {
        name: "aes256gcm16",
        slug: "256",
      };
      state.hashAlgoExchange = {
        name: "SHA256",
        slug: "sha256",
      };
      state.pfsKey = {
        name: "off",
        slug: "off",
      };
      state.lifetimeExchange = "";

      v$.value.$reset();
    };

    const numberList = ref(Array.from({ length: 32 }, (_, i) => i + 1));
    const CertificateList = ref([]);
    const CertificateListRemote = ref([]);
    const mapedInterfaceType = ref([]);
    const mapedKeyPublic = ref([]);

    const rules = computed(() => {
      return {
        //General information Phase 1

        tunnelSettings: {
          required,
          isValidTunnelSettings: helpers.withMessage(
            `champs can include only letters & Numbers & underscores & hyphens without space.`,
            helpers.regex(/^[A-Za-z0-9_\-]+$/)
          ),
        },
        connectionMethod: { required },
        keyExchange: { required },
        internetProtocol: { required },

        remoteGateway: {
          required,
          isValidlRemoteGateway: helpers.withMessage(
            `Format must be like adresse IP : X.X.X.X`,

            helpers.regex(/^(\d{1,3}\.){3}\d{1,3}$/)
          ),
        },

        lifetime: {
          isValidlifeTime: helpers.withMessage(
            `Champs can include only Numbers.`,

            helpers.regex(/^[0-9]+$/)
          ),
        },
        lifetimeExchange: {
          isValidlifetimeExchange: helpers.withMessage(
            `Champs can include only Numbers.`,

            helpers.regex(/^[0-9]+$/)
          ),
        },
        interactivityTimout: {
          isValidInteractivityTimout: helpers.withMessage(
            `Champs can include only Numbers.`,

            helpers.regex(/^[0-9]+$/)
          ),
        },
        marginTime: {
          isValidMarginTime: helpers.withMessage(
            `Champs can include only Numbers.`,

            helpers.regex(/^[0-9]+$/)
          ),
        },
        rekeyFuzz: {
          isValidRekeyFuzz: helpers.withMessage(
            `Champs can include only Numbers.`,

            helpers.regex(/^[0-9]+$/)
          ),
        },

        generalinterface: { required },
        // phase Auth
        authMethod: { required },
        negotiationMode: {
          requiredIfFuction: helpers.withMessage(
            "Value is required",
            requiredIf(() => state.keyExchange.slug === "V1")
          ),
        },

        sharedKey: {
          requiredIfFuction: helpers.withMessage(
            "Value is required",
            requiredIf(() => state.authMethod.slug === "Mutual PSK")
          ),
          isValidKey: helpers.withMessage(
            `There must be at least 32 characters, including at least one uppercase,one lowercase, one number, and one special character.`,

            helpers.regex(
              /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~])[A-Za-z\d!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~\\]{32,128}$/
            )
          ),
        },

        certificate: {
          requiredIfFuction: helpers.withMessage(
            "Value is required",
            requiredIf(() => state.authMethod.slug === "Mutual RSA")
          ),
        },

        keyPair: {
          requiredIfFuction: helpers.withMessage(
            "Value is required",
            requiredIf(() => state.authMethod.slug === "Mutual Public key")
          ),
        },

        localKey: {
          requiredIfFuction: helpers.withMessage(
            "Value is required",
            requiredIf(() => state.authMethod.slug === "Mutual Public key")
          ),
        },

        peerIdentifier: {
          requiredIfFuction: helpers.withMessage(
            "Value is required",
            requiredIf(() => state.authMethod.slug === "Mutual RSA")
          ),
        },

        // phase algo

        encryptAlgo: {
          requiredIfFuction: helpers.withMessage(
            "Value is required",
            requiredIf(() => state.keyExchange.slug === "V2")
          ),
        },

        encryptAlgoV1: {
          requiredIfFuction: helpers.withMessage(
            "Value is required",
            requiredIf(() => state.keyExchange.slug === "V1")
          ),
        },
        encryptAlgoExch2: {
          requiredIfFuction: helpers.withMessage(
            "Value is required",
            requiredIf(() => state.keyExchange.slug === "V1")
          ),
        },

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

        type: {
          requiredIfFuction: helpers.withMessage(
            "Value is required",
            requiredIf(() => state.mode.slug === "Tunnel IPv4")
          ),
        },

        remoteNetworkAddress: {
          requiredIfFuction: helpers.withMessage(
            "Value is required",
            requiredIf(() => state.mode.slug === "Tunnel IPv4")
          ),
          isValidremoteNetworkAddress: helpers.withMessage(
            `Format must be like adresse IP : X.X.X.X`,

            helpers.regex(/^(\d{1,3}\.){3}\d{1,3}$/)
          ),
        },

        selectAddressNetwork: {
          requiredIfFuction: helpers.withMessage(
            "Value is required",
            requiredIf(() => state.type.slug === "Network")
          ),
        },
        // localAddress: {
        //   required,
        //   isValidlocalAddress: helpers.withMessage(
        //     `Format must be like adresse IP : X.X.X.X`,

        //     helpers.regex(/^[0-9.]+$/)
        //   ),
        // },

        localNetworkAddress: {
          requiredIfFuction: helpers.withMessage(
            "Value is required",
            requiredIf(
              () =>
                (state.type.slug === "Network" ||
                  state.type.slug === "Address") &&
                state.mode.slug === "Tunnel IPv4"
            )
          ),
          isValidlocalNetworkAddress: helpers.withMessage(
            `Format must be like adresse IP : X.X.X.X`,

            helpers.regex(/^(\d{1,3}\.){3}\d{1,3}$/)
          ),
        },

        selectRemoteAddressNetwork: {
          requiredIfFuction: helpers.withMessage(
            "Value is required",
            requiredIf(
              () =>
                state.typeRemoteNetwork.slug === "Network" &&
                state.mode.slug === "Tunnel IPv4"
            )
          ),
        },

        typeRemoteNetwork: {
          requiredIfFuction: helpers.withMessage(
            "Value is required",
            requiredIf(() => state.mode.slug === "Tunnel IPv4")
          ),
        },
        //exchange
        protocol: { required },

        encryptAlgoExchange: {
          requiredIfFuction: helpers.withMessage(
            "Value is required",
            requiredIf(() => state.protocol.slug === "ESP")
          ),
        },

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

          let resultObject = interfaces.filter((i) => i.name === "WAN");
          state.generalinterface = resultObject[0];
        },
        (error) => {
          console.log(error);
        }
      );
    };
    const getPublickKey = () => {
      let publicKeyAttribute =
        document.getElementById("app").attributes["publicKey"].value;

      const validJsonString = publicKeyAttribute
        .replace(/'/g, '"')
        .replace(/True/g, "true")
        .replace(/False/g, "false")
        .replace(/None/g, "null");
      const parsedArray = JSON.parse(validJsonString);

      let mapedPublicKey = parsedArray.map((i) => {
        return {
          id: i.id,
          name: i.name,
        };
      });
      mapedKeyPublic.value = mapedPublicKey;
    };

    const getAllCertif = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/certificates/getAllCertificates").then(
        (response) => {
          let mapedListCertif = response.data.filter(
            (i) => i.certificate_type === "server"
          );

          let certif = mapedListCertif.map((i) => {
            return {
              id: i.id,
              name: i.name,
              is_private_key: i.is_private_key,
            };
          });
          CertificateListRemote.value = certif;

          CertificateList.value = certif.filter((i) => i.is_private_key);
        },
        (error) => {
          console.log(error);
        }
      );
    };

    const getInterfaceType = () => {
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
              slug: i.name_interface,
            };
          });

          let listInter = [
            {
              name: "Address",
              slug: "Address",
            },
            { name: "Network", slug: "Network" },
          ]

          var combinedArray = [...listInter, ...interfaces];
          mapedInterfaceType.value = combinedArray;
        },
        (error) => {
          console.log(error);
        }
      );
    };

    onMounted(() => {
      getInterface();
      getPublickKey();
      getAllCertif();
      getInterfaceType();

      emitter.on("edit-serverIpsec", (data) => {
        console.log("data", data);
        if (data) state.isEditState = "edit";
        state.id = data.id;
        //General information Phase 1
        state.tunnelSettings = data.conn_name;

        let filtredconnectionMethod = connectionMethodList.value.filter(
          (i) => i.slug === data?.connection_method
        );

        state.connectionMethod = filtredconnectionMethod[0];
        let filtredexchangeList = exchangeList.value.filter(
          (i) => i.slug === data?.key_exchange_version
        );
        let filtredprotocolList = protocolList.value.filter(
          (i) => i.slug === data?.internet_protocol
        );

        let filtredInterfaces = state.mapedInterface.filter(
          (i) => i.id === +data.interface
        );

        let filtredInterfaceList = state.mapedInterface.filter(
          (i) => i.name === data?.interface
        );
        state.keyExchange = filtredexchangeList[0];
        state.internetProtocol = filtredprotocolList[0];
        state.remoteGateway = data.remote_gateway;
        state.generalinterface =
          filtredInterfaces[0] ?? filtredInterfaceList[0];
        state.remoteConnect = data.dynamic_gateway;
        state.description = data.description_ph1;

        // Phase 1 proposal (Authentication)

        let filtredAuthMethodList = authenticationMethodList.value.filter(
          (i) => i.slug === data?.authentication_method
        );
        let filtredNegotiationModeList = negotiationList.value.filter(
          (i) => i.name === data?.negotiation_mode
        );
        let filtredCertList = CertificateList.value.filter(
          (i) => i.name === data?.cert
        );
        let filtredPublicLocalList = mapedKeyPublic.value.filter(
          (i) => i.name === data?.local_key_pair
        );
        let filtredKeyPairList = mapedKeyPublic.value.filter(
          (i) => i.name === data?.peer_key_pair
        );
        state.authMethod = filtredAuthMethodList[0];
        state.negotiationMode = filtredNegotiationModeList[0];
        state.sharedKey = data?.pre_shared_key;
        state.certificate = filtredCertList[0];
        state.keyPair = filtredKeyPairList[0];
        state.localKey = filtredPublicLocalList[0];

        let filtredRemoteCertificate = CertificateListRemote.value.filter(
          (i) => i.name === data?.remote_cert
        );

        state.peerIdentifier = filtredRemoteCertificate[0];

        // Phase 1 proposal (Algorithms)

        let filtredEncryptAlgoList = encryptAlgoList.value.filter(
          (i) => i.slug === data?.encryption_algorithm_ph1
        );

        let filtredHashAlgoList = [];
        data?.hash_algorithm_ph1.forEach((e) => {
          filtredHashAlgoList = [
            ...filtredHashAlgoList,
            ...hashAlgoList.value.filter((i) => i.slug === e),
          ];
        });

        let filtredDhKeyList = [];
        data?.dh_key_group.forEach((e) => {
          filtredDhKeyList = [
            ...filtredDhKeyList,
            ...dhKeyList.value.filter((i) => i.slug === e),
          ];
        });

        state.encryptAlgo = filtredEncryptAlgoList[0] ?? "";
        state.encryptAlgoV1 = filtredEncryptAlgoList[0] ?? "";
        state.hashAlgo = filtredHashAlgoList;
        state.dhKey = filtredDhKeyList;
        state.lifetime = data?.lifetime_ph1;

        // Advanced Options

        state.policy = data?.policy;
        state.rekey = data?.rekey;
        state.reauth = data?.reauth;

        let filtredtraversalList = traversalList.value.filter(
          (i) => i.slug === data?.nat_traversal
        );
        state.natTraversal = filtredtraversalList[0];
        state.deadPeer = data?.deed_peer_detection;
        state.retries = data?.deed_peer_timeout;
        state.mobike = data?.mobike;

        let filtredDeadPeerList = deadPeerList.value.filter(
          (i) => i.slug === data?.deed_peer_action
        );

        state.selectDear = filtredDeadPeerList[0];

        state.interactivityTimout = data?.inactivity_timeout;

        state.seconds = data?.deed_peer_delay;
        state.rekeyFuzz = data?.rekey_fuzz;
        state.marginTime = data?.margin_time;

        //general info 2

        let filtredDModeList = modeList.value.filter(
          (i) => i.slug === data?.mode
        );
        let filtredtypeLocalNetworkList = mapedInterfaceType.value.filter(
          (i) => i.slug === data?.type_local_network
        );

        let filtredtypeRemoteNetworkList = remoteTypeList.value.filter(
          (i) => i.slug === data?.type_remote_network
        );

        let result = data?.address_local_network?.split("/");
        if (result) {
          result[1] = parseInt(result[1], 10);
        }

        let resultRemote = data?.address_remote_network?.split("/");
        if (resultRemote) {
          resultRemote[1] = parseInt(resultRemote[1], 10);
        }

        state.mode = filtredDModeList[0];
        state.descriptionPh2 = data.description_ph2;
        state.type = filtredtypeLocalNetworkList[0];
        state.remoteNetworkAddress = resultRemote ? resultRemote[0] : "";
        state.selectAddressNetwork = result ? result[1] : "";
        state.localNetworkAddress = result ? result[0] : "";
        state.selectRemoteAddressNetwork = resultRemote ? resultRemote[1] : "";
        state.typeRemoteNetwork = filtredtypeRemoteNetworkList[0];

        // exchage

        let filtredProtocolph2List = protocolListph2.value.filter(
          (i) => i.slug === data?.protocol
        );

        let filtredHashAlgoListExchange = [];
        data?.hash_algorithm_ph2.forEach((e) => {
          filtredHashAlgoListExchange = [
            ...filtredHashAlgoListExchange,
            ...hashAlgoList.value.filter((i) => i.slug === e),
          ];
        });

        state.protocol = filtredProtocolph2List[0];
        state.hashAlgoExchange = filtredHashAlgoListExchange ?? [];

        let filtredencryptAlgoExchange = [];

        if (data.encryption_algorithm_ph2) {
          data?.encryption_algorithm_ph2?.forEach((e) => {
            filtredencryptAlgoExchange = [
              ...filtredencryptAlgoExchange,
              ...encryptAlgoListExchange.value.filter((i) => i.slug === e),
            ];
          });
        }

        if (data.key_exchange_version === "V1") {
          state.encryptAlgoExch2 = filtredencryptAlgoExchange;
        } else {
          state.encryptAlgoExchange = filtredencryptAlgoExchange;
        }

        let filtredPfsKeyList = pfsList.value.filter(
          (i) => i.slug === data?.pfs_key_group
        );

        state.pfsKey = filtredPfsKeyList[0];

        state.lifetimeExchange = data.lifetime_ph2;

        console.log("state", state);
      });
    });

    const protocolListph2 = ref([
      {
        name: "ESP",
        slug: "ESP",
      },
      { name: "AH", slug: "AH" },
    ]);

    const pfsList = ref([
      {
        name: "off",
        slug: "off",
      },
      { name: "15 (3072 bits)", slug: "15:3072" },
      { name: "16 (4096 bits)", slug: "16:4096" },
      { name: "17 (6144 bits)", slug: "17:6144" },
      { name: "18 (8192 bits)", slug: "18:8192" },
      { name: "19 (NIST EC 256 bits)", slug: "19:256" },
      { name: "20 (NIST EC 384 bits)", slug: "20:384" },
      { name: "21 (NIST EC 521 bits)", slug: "21:521" },
      { name: "28 (Brainpool EC 256 bits)", slug: "28:256" },
      { name: "29 (Brainpool EC 384 bits)", slug: "29:384" },
      { name: "30 (Brainpool EC 512 bits)", slug: "30:512" },
      { name: "31 (Elliptic Curve 25519)", slug: "31:25519" },
    ]);

    const encryptAlgoListExchange = ref([
      {
        name: "AES128",
        slug: "aes128",
      },
      {
        name: "AES192",
        slug: "aes192",
      },
      {
        name: "AES256",
        slug: "aes256",
      },
      {
        name: "aes128gcm16",
        slug: "128",
      },
      {
        name: "aes192gcm16",
        slug: "192",
      },
      {
        name: "aes256gcm16",
        slug: "256",
      },
    ]);

    watch(
      state,
      () => {
        if (
          (state.type?.slug === "WAN" || state.type?.slug === "LAN") &&
          state.mode?.slug === "Tunnel IPv4"
        ) {
          state.isTypeWAn = true;
        } else {
          state.isTypeWAn = false;
        }
        if (
          state.type?.slug === "Address" &&
          state.mode?.slug === "Tunnel IPv4"
        ) {
          state.defaultValue = "32";
          state.selectAddressNetwork = "";
          state.isDefault = true;
        } else if (
          state.type?.slug === "Network" &&
          state.mode?.slug === "Tunnel IPv4"
        ) {
          state.defaultValue = "mask";
          state.isDefault = false;
        } else {
          state.defaultValue = "32";
          state.isDefault = false;
          state.localNetworkAddress = "";
          state.selectAddressNetwork = "";
        }
        if (
          state.typeRemoteNetwork?.slug === "Address" &&
          state.mode?.slug === "Tunnel IPv4"
        ) {
          state.selectRemoteAddressNetwork = "";
          state.defaultValueRemote = "32";
          state.isDefaultRemote = true;
        } else {
          state.defaultValueRemote = "mask";
          state.isDefaultRemote = false;
        }
        if (state.mode?.slug === "Transport") {
          console.log("Transport oui0");

          state.typeRemoteNetwork = "";
          state.type = "";
        } else if (state.mode?.slug === "Tunnel IPv4") {
          if (!state.type) {
            state.type = {
              name: "Address",
              slug: "Address",
            };
          }
          if (!state.typeRemoteNetwork) {
            state.typeRemoteNetwork = { name: "Network", slug: "Network" };
          }
        }
      },
      { immediate: true }
    );

    const save = async () => {
      const result = await v$.value.$validate();

      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      if (result) {
        let KeyExchange = null;

        if (state.keyExchange.slug === "V1") {
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
            local_key_pair: state.localKey?.name,
            peer_key_pair: state.keyPair?.name,
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
            remote_cert: state.peerIdentifier.name,
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
        if (Array.isArray(state.encryptAlgoExch2)) {
          var mappedencryptAlgoExch2 = state.encryptAlgoExch2.map(
            (e) => e.slug
          );
        } else {
          var mappedencryptAlgoExch2 = [state.encryptAlgoExch2.slug];
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
            encryption_algorithm_ph2:
              state.keyExchange.slug === "V1"
                ? mappedencryptAlgoExch2
                : mappedencryptAlgoExchange,
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
              address_remote_network: state.remoteNetworkAddress,
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
          encryption_algorithm_ph1:
            state.keyExchange.slug === "V1"
              ? state.encryptAlgoV1.slug
              : state.encryptAlgo?.slug,
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
        state.loading = true;
        state.isLoadingDialogue = true;
        if (state.isEditState === "edit") {
          console.log("payload", payload);
          axios
            .put(`/ipsec/updateServerIPsec/${state.id}`, payload)
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
                  emitter.emit("open-listingIpsec");
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
            .post("/ipsec/createServerIPsec", payload)
            .then((response) => {
              if (response.status == "201") {
                state.loading = false;
                state.isLoadingDialogue = false;
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.msg;
                setTimeout(() => {
                  location.reload();
                  emitter.emit("open-listingIpsec");
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
        console.log("error", v$.value);
      }
    };
    const filteredAlgoListExchangeV1 = computed(() => {
      if (state.keyExchange.slug === "V1") {
        return encryptAlgoListExchange.value.slice(0, 3);
      } else {
        return encryptAlgoListExchange.value;
      }
    });
    const filteredEncryptAlgoListV1 = computed(() => {
      if (state.keyExchange.slug === "V1") {
        return encryptAlgoList.value.slice(0, 3);
      } else {
        return encryptAlgoList.value;
      }
    });

    return {
      getCookie,
      getInterface,
      getPublickKey,
      getAllCertif,
      connectionMethodList,
      exchangeList,
      protocolList,
      protocolListph2,
      filteredAlgoListExchangeV1,
      filteredEncryptAlgoListV1,
      authenticationMethodList,
      encryptAlgoListExchange,
      pfsList,
      negotiationList,
      CertificateList,
      CertificateListRemote,
      mapedKeyPublic,
      dhKeyList,
      hashAlgoList,
      encryptAlgoList,
      traversalList,
      deadPeerList,
      modeList,
      mapedInterfaceType,
      numberList,
      remoteTypeList,
      save,
      cancel,
      state,
      emitter,
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
