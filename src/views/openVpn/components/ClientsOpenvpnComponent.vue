<template>
  <v-overlay v-model="state.viewModal">
    <v-dialog
      v-model="state.isviewModal"
      persistent
      :scrim="false"
      width="auto"
    >
      <v-card color="#193286" class="alert-box">
        <v-card-title class="img-containter">
          <img
            src="@/assets/images/view.png"
            alt="logo"
            class="img-view"
            width="100"
            height="100"
        /></v-card-title>
        <v-card-text v-html="overlayMessage"> </v-card-text>

        <div class="mr-3 mb-5 d-flex justify-end">
          <VButton
            rounded
            outlined
            color="#ffffff"
            label-color="#213E9F"
            :label="$t('buttons.close')"
            :isLarge="true"
            @click="close"
          />
        </div>
      </v-card>
    </v-dialog>
  </v-overlay>
  <div class="mt-3">
    <v-row>
      <v-col align-self="center" cols="6">
        <div class="ml-3 mr-3">
          <h4>{{ $t("openvpn.Generalinformation") }}</h4>
          <v-divider class="mt-2"></v-divider>
          <v-row class="mt-2">
            <v-col align-self="center" cols="4">
              <label>{{ $t("openvpn.Clientname") }}*</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                :label="$t('openvpn.Clientname')"
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
              <label>{{ $t("openvpn.Servermode") }}*</label>
            </v-col>
            <v-col align-self="center" cols="8" class="mb-n6">
              <v-select
                :label="$t('openvpn.Servermode')"
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
              <label>{{ $t("PageIpsec.Protocol") }}*</label>
            </v-col>
            <v-col align-self="center" cols="8" class="mb-n6">
              <v-select
                :label="$t('PageIpsec.Protocol')"
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
              <label>{{ $t("openvpn.DeviceMode") }}*</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select
                :label="$t('openvpn.DeviceMode')"
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
            <!-- <v-col align-self="center" cols="4">
              <label>Interface</label>
            </v-col>
            <v-col align-self="center" cols="8" class="mb-n6">
              <v-select
                label="Interface"
                clearable
                v-model="state.interface"
                :items="state.mapedInterface"
                item-title="name"
                item-value="id"
                return-object
              ></v-select>
            </v-col> -->
            <v-col align-self="center" cols="4">
              <label>{{ $t("openvpn.RetryDNSresolution") }}</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <input type="checkbox" v-model="state.resolv_retry" />
              <label class="ml-2">{{
                $t("openvpn.Infinitelyresolveremoteserver")
              }}</label>
            </v-col>

            <v-col align-self="center" cols="4">
              <label>{{ $t("openvpn.Proxyhostoraddress") }}</label>
            </v-col>
            <v-col align-self="center" cols="8" class="mb-n6">
              <v-text-field
                :label="$t('openvpn.Proxyhostoraddress')"
                v-model="state.proxy_host"
              ></v-text-field>
              <p
                class="error-feedback mb-5"
                v-if="v$.proxy_host.$errors.length"
              >
                {{ v$.proxy_host.$errors?.[0].$message }}
              </p>
            </v-col>
            <v-col align-self="center" cols="4">
              <label>{{ $t("openvpn.Proxyport") }}</label>
            </v-col>
            <v-col align-self="center" cols="8" class="mb-n6">
              <v-text-field
                :label="$t('openvpn.Proxyport')"
                v-model="state.proxy_port"
              ></v-text-field>
              <p
                class="error-feedback mb-5"
                v-if="v$.proxy_port.$errors.length"
              >
                {{ v$.proxy_port.$errors?.[0].$message }}
              </p>
            </v-col>

            <v-col align-self="center" cols="4" class="mt-1">
              <label>{{ $t("openvpn.Proxyauthenticationextraoptions") }}</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select
                :label="$t('openvpn.Proxyauthenticationextraoptions')"
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
              <v-col align-self="center" cols="8" class="mb-n6">
                <v-text-field
                  :label="$t('form.username')"
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
              <v-col :cols="state.modeState === 'create' ? 8 : 4" class="mb-n6">
                <v-text-field
                  :append-inner-icon="
                    state.showpassword ? 'mdi-eye' : 'mdi-eye-off'
                  "
                  @click:append-inner="state.showpassword = !state.showpassword"
                  :type="state.showpassword ? 'text' : 'password'"
                  type="password"
                  :label="$t('form.password')"
                  v-model="state.password"
                ></v-text-field>
                <p
                  class="error-feedback mb-5"
                  v-if="v$.password.$errors.length"
                >
                  {{ v$.password.$errors?.[0].$message }}
                </p>
              </v-col>
              <v-col cols="4" class="mb-n6" v-if="state.modeState === 'edit'">
                <v-text-field
                  :append-inner-icon="
                    state.showNewpassword ? 'mdi-eye' : 'mdi-eye-off'
                  "
                  @click:append-inner="
                    state.showNewpassword = !state.showNewpassword
                  "
                  :type="state.showNewpassword ? 'text' : 'password'"
                  type="password"
                  :label="$t('openvpn.newPassword')"
                  v-model="state.NewProxyPassword"
                ></v-text-field>
                <p
                  class="error-feedback mb-5"
                  v-if="v$.NewProxyPassword.$errors.length"
                >
                  {{ v$.NewProxyPassword.$errors?.[0].$message }}
                </p>
              </v-col>
            </template>
          </v-row>
          <v-row>
            <v-col align-self="center" cols="4">
              <label>{{ $t("openvpn.Localport") }}</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                :label="$t('openvpn.Localport')"
                v-model="state.local_port"
              ></v-text-field>
              <p
                class="error-feedback mb-5"
                v-if="v$.local_port.$errors.length"
              >
                {{ v$.local_port.$errors?.[0].$message }}
              </p>
            </v-col>
          </v-row>
          <v-row class="mt-2">
            <div class="ml-3 mr-3">
              <v-row class="mt-2">
                <userAuthSettings
                  v-model:username="state.usernameUser"
                  v-model:password="state.passwordUser"
                  v-model:NewUserPassword="state.NewUserPassword"
                  v-model:renegotiate_time="state.renegotiate_time"
                  :modeState="state.modeState"
                  :errors="v$"
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
                  :clientCertificateList="state.clientCertificateList"
                  :mapedCertifAuth="state.mapedCertifAuth"
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
          <div class="mt-3">
            <h4 class="mt-6">{{ $t("openvpn.AdvancedConfiguration") }}</h4>
            <v-divider class="mt-2"></v-divider>
            <v-row class="mt-2">
              <v-col align-self="center" cols="4">
                <label>{{ $t("openvpn.VerbosityLevel") }}</label>
              </v-col>
              <v-col align-self="center" cols="8" class="mb-n6">
                <v-select
                  :label="$t('openvpn.VerbosityLevel')"
                  v-model="state.verbosityLevel"
                  :items="verbosityLevelList"
                  item-title="name"
                  item-value="slug"
                  return-object
                ></v-select>
              </v-col>
            </v-row>
          </div>
          <div class="mt-2">
            <h4 class="mt-6">{{ $t("openvpn.Remoteserver") }}</h4>
            <v-divider class="mt-2"></v-divider>
            <v-row class="mt-2">
              <v-row class="mb-5 ml-1">
                <v-col cols="12" class="mb-n5">
                  <div
                    style="
                      display: flex;
                      justify-content: flex-end;
                      margin-bottom: 10px;
                    "
                  >
                    <v-btn
                      type="submit"
                      color="asguard_primary_light"
                      :rounded="true"
                      class="mt-3 btn-add"
                      @click="addNewRow"
                    >
                      <span class="text-white">{{ $t("buttons.Add") }}</span>
                    </v-btn>
                  </div>

                  <ag-grid-vue
                    id="grid-wrapper"
                    domLayout="autoHeight"
                    class="ag-theme-alpine mt-3"
                    :columnDefs="columnCertificats"
                    :alwaysShowHorizontalScroll="false"
                    :alwaysShowVarticalScroll="false"
                    :defaultColDef="defaultColDef"
                    :rowData="rowDataCertificats.value"
                    style="width: 100%"
                    :overlayNoRowsTemplate="overlayTemplate"
                    @grid-ready="onGridReady"
                    :pagination="true"
                    :paginationPageSize="4"
                    :localeText="paginationLocalization"
                  />

                  <p class="error-feedback mb-5 mt-5" v-if="textAlertArray">
                    {{ textAlertArray }}
                  </p>
                </v-col>
              </v-row>
            </v-row>
          </div>
        </div>
      </v-col>
    </v-row>
    <v-row class="flex py-8">
      <v-col cols="4">
        <div class="text-start ml-2 mt-4">
          <span class="text-sm">
            <span class="text-red text-lg">*</span>
            {{ $t("errors.oblig") }}</span
          >
        </div>
      </v-col>
      <v-col>
        <div class="mr-3 flex center">
          <VButton
            rounded
            outlined
            color="#ffffff"
            label-color="#213E9F"
            :label="$t('buttons.cancel')"
            :isLarge="true"
            @click="cancel"
          />
          <VButton
            rounded
            outlined
            color="#213E9F"
            label-color="#ffffff"
            :label="$t('buttons.save')"
            :isLarge="true"
            class="ml-2"
            @click="save"
          />
        </div>
      </v-col>
    </v-row>
    <br />
    <v-spacer></v-spacer>
    <v-snackbar
      :timeout="1000"
      v-model="snackbar"
      location="bottom right"
      :color="color"
    >
      {{ textAlert }}
    </v-snackbar>
  </div>
</template>

<script>
import { useI18n } from "vue-i18n";
import { inject, toRefs } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import useValidate from "@vuelidate/core";
import { required, requiredIf, helpers } from "@vuelidate/validators";
import tunnelSettings from "./clientComponents/tunnelSettings.vue";
import userAuthSettings from "./clientComponents/userAuthSettings.vue";
import cryptoSettings from "./clientComponents/cryptoSettings.vue";
import VButton from "@/components/VButton.vue";
import { reactive, onMounted, ref, computed, watch } from "vue";
import axios from "axios";
import protocols from "@/constants/protocols.js";
import { user_privilege } from "@/mixins/user_privilege.js";

export default {
  name: "ClientsOpenvpnComponent",
  components: {
    tunnelSettings,
    userAuthSettings,
    cryptoSettings,
    VButton,
    AgGridVue,
  },
  props: ["dataClient"],
  setup(props) {
    const { t } = useI18n();
    const current_user = ref();
    const last_Subscription = ref([]);
    const paginationLocalization = reactive({
      of: "/",
    });
    const { dataClient } = toRefs(props);
    const emitter = inject("emitter");
    const overlayTemplate = ref("");
    const color = ref(null);
    const snackbar = ref(false);
    const textAlert = ref(false);
    const textAlertArray = ref(false);
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

    const gridApi = ref(null);
    const gridColumnApi = ref(null);

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
        name: "Remote Access (SSL/TLS)",
        slug: "remote_access",
      },
    ]);

    const state = reactive({
      isviewModal: false,
      viewModal: false,
      modeState: "create",
      showpassword: false,
      showNewpassword: false,
      clientCertificateList: [],
      mapedCertifAuth: [],
      filtredMapCertif: [],
      id: "",
      isEditState: "",
      //general information
      clientName: "",
      description: "",
      server_mode: "",
      protocol: "",
      device_mode: "",
      // interface: "",
      resolv_retry: false,
      proxy_host: "",
      proxy_port: "",
      proxyAuthenticationExtraOptions: {
        name: "None",
        slug: "none",
      },
      usernameUser: "",
      passwordUser: "",
      NewUserPassword: "",

      // username: "",
      // password: "",
      local_port: "",
      // mapedInterface: [],
      mapedCertifAuth: [],
      //User Auth
      username: "",
      password: "",
      NewProxyPassword: "",
      renegotiate_time: "",
      //cryp
      tlsGenerate: true,
      sharedKey: "",
      peerCertificateAuthority: "",
      clientCertificate: "",
      encryptionAlgorithm: "",
      authDigestAlgorithm: "",
      // hardwareCrypto: {
      //   name: "No Hardware Crypto acceleration",
      //   slug: "No Hardware Crypto",
      // },

      //tunnelSettings
      ipv4TunnelNetwork: "",
      ipv6TunnelNetwork: "",
      ipv4RemoteNetwork: "",
      ipv6RemoteNetwork: "",
      limitOutgoingBandwidth: "",
      compression: { name: "No preference", slug: "no_preference" },
      typeOfService: false,
      ipv6: false,
      pullRoutes: false,
      addRemoveRoutes: false,
      //advancedConfig
      verbosityLevel: {
        name: "1 (default)",
        slug: "1",
      },
      remoteServer: "",
      hostAddress: "",
      port: "",
    });

    onMounted(() => {
      const lastSubscription =
        document.getElementById("app").attributes["last_subscription"].value;
      let parsedArraySubscription = JSON.parse(lastSubscription);
      last_Subscription.value = parsedArraySubscription;
      console.log("last_Subscription", last_Subscription.value);
      // getInterface();
      getAllCertAuth();
      getAllClientCertif();
      protocolsList.value = protocols;
      overlayTemplate.value = `
      <span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
     </svg></span>`;

      emitter.on("edit-client", (data) => {
        console.log("clinet-edit", data);
        if (data) state.isEditState = "edit";
        state.modeState = "edit";
        state.id = data.id;
        state.clientName = data.name;
        state.description = data.description;

        let filtredMode = serverMode.value.filter(
          (i) => i.slug === data.server_mode
        );

        state.server_mode = filtredMode[0];

        let filtredProtocol = Listprotocols.value.filter(
          (i) => i.slug === data.proto
        );

        state.protocol = filtredProtocol[0];

        let filtredDevice = deviceMode.value.filter((i) => i.slug === data.dev);

        state.device_mode = filtredDevice[0];

        // let filtredInterfaces = state.mapedInterface.filter(
        //   (i) => i.id === +data.interface
        // );
        // let filtredInter = state.mapedInterface.filter(
        //   (i) => i.name === data.interface
        // );

        // state.interface = filtredInterfaces[0] ?? filtredInter[0] ?? "";
        state.resolv_retry = data.resolv_retry;
        state.proxy_host = data.proxy_host;
        state.proxy_port = data.proxy_port;

        let filtredProxy = proxyAuthenticationExtraOptionsList.value.filter(
          (i) => i.slug === data.proxy_authentication_option
        );

        state.proxyAuthenticationExtraOptions = filtredProxy[0];
        state.usernameUser = data.username;
        state.passwordUser = data.password;
        state.username = data.proxy_auth_username;
        state.password = data.proxy_auth_password;
        state.local_port = data.port;
        // state.username = data.password;
        // state.password = data.username;
        state.renegotiate_time = data.renegotiate_time;
        state.tlsGenerate = data.tls_key ? false : true;
        state.sharedKey = data.tls_key;

        let filtredCert = state.mapedCertifAuth.filter(
          (i) => i.name === data.ca_name
        );
        state.peerCertificateAuthority = filtredCert[0];

        let filtredCertiClient = state.filtredMapCertif.filter(
          (i) => i.name === data.cert_name
        );
        state.clientCertificate = filtredCertiClient[0];

        let filtredEncrypt = encryptionAlgorithmList.value.filter(
          (i) => i.slug === data.cipher
        );
        state.encryptionAlgorithm = filtredEncrypt[0];

        let filtredAuth = authDigestAlgorithmList.value.filter(
          (i) => i.slug === data.auth
        );

        state.authDigestAlgorithm = filtredAuth[0];

        // let filtredHardware = hardwareCryptoList.value.filter(
        //   (i) => i.slug === data.hardware_crypto
        // );
        // state.hardwareCrypto = filtredHardware[0] ?? "";

        state.ipv4TunnelNetwork = data.ipv4_tunnel_network;
        // state.ipv6TunnelNetwork= data.,
        state.ipv4RemoteNetwork = data.ipv4_remote_network;
        // state.ipv6RemoteNetwork= data.,
        state.limitOutgoingBandwidth = data.limit_outgoing_bandwidth;

        let filtredCompression = compression.value.filter(
          (i) => i.slug === data.compression
        );

        state.compression = filtredCompression[0];
        state.typeOfService = data.type_of_service;
        state.ipv6 = data.ipv6;
        state.pullRoutes = data.pull_routes;
        state.addRemoveRoutes = data.add_remove_routes;

        let filtredVerb = verbosityLevelList.value.filter(
          (i) => i.slug === data.verb
        );

        state.verbosityLevel = filtredVerb[0];

        rowDataCertificats.value = data.server_remote;
        if (gridApi.value) {
          gridApi.value.setRowData(rowDataCertificats.value);
        } else {
          console.error("Grid API.");
        }
      });
    });
    const champ = computed(() => {
      return t("champs.indication");
    });
    const overlayMessage = computed(() => {
      current_user.value = user_privilege("Openvpn");
      console.log("current_user", current_user.value);
      if (current_user.value === "viewer" || current_user.value === "default") {
        return ` ${t("profil.NoPermission")} <br /> ${t(
          "profil.ContactAdmin"
        )}`;
      } else if (!last_Subscription.value.includes("VPN SSL")) {
        return `${t(
          "firewall.msg_subscription"
        )}<br /><a href="/asguard/license/" class="white-link"> ${t(
          "firewall.sub_page"
        )}</a>`;
      } else {
        return ` ${t("profil.NoPermission")} <br /> ${t(
          "profil.ContactAdmin"
        )}`;
      }
      su;
    });
    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const formatMustBeLikeAdresseIP = computed(() => {
      return t("errors.formatMustBeLikeAdresseIP");
    });
    const formatMustBeLikeAdresse = computed(() => {
      return t("errors.formatMustBeLikeAdresse");
    });
    const onlynumbers = computed(() => {
      return t("errors.ChampIncludeOnlyNumbers");
    });

    const specificform = computed(() => {
      return t("errors.formsepcificpassword");
    });
    const rules = computed(() => {
      return {
        clientName: {
          required: helpers.withMessage(error, required),
          isValidClientName: helpers.withMessage(
            champ,
            helpers.regex(/^[A-Za-z0-9_\-]+$/)
          ),
        },

        ipv4TunnelNetwork: {
          isValidIpv4TunnelNetwork: helpers.withMessage(
            formatMustBeLikeAdresse,
            // helpers.regex(/^(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b\/\d{1,2})$/)
            helpers.regex(
              /^((?!0\.0\.0\.0)(\b(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\/([1-9]|[12][0-9]|3[0-2]))$/
            )
          ),
        },
        ipv4RemoteNetwork: {
          isValidIpv4RemoteNetwork: helpers.withMessage(
            formatMustBeLikeAdresse,
            // helpers.regex(/^(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b\/\d{1,2})$/)
            helpers.regex(
              /^((?!0\.0\.0\.0)(\b(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\/([1-9]|[12][0-9]|3[0-2]))$/
            )
          ),
        },

        server_mode: { required: helpers.withMessage(error, required) },
        protocol: { required: helpers.withMessage(error, required) },
        device_mode: { required: helpers.withMessage(error, required) },

        proxy_host: {
          isValidProxy_host: helpers.withMessage(
            formatMustBeLikeAdresseIP,
            helpers.regex(
              /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
            )
          ),
        },
        proxy_port: {
          isValidProxy_port: helpers.withMessage(
            onlynumbers,
            helpers.regex(/^[0-9]+$/)
          ),
        },
        local_port: {
          isValidLocal_port: helpers.withMessage(
            onlynumbers,
            helpers.regex(/^[0-9]+$/)
          ),
        },

        sharedKey: {
          // requiredIfFuction: requiredIf(() => !state.tlsGenerate),

          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(() => !state.tlsGenerate)
          ),
        },
        username: {
          // requiredIfFuction: requiredIf(
          //   () => state.proxyAuthenticationExtraOptions.slug === "basic"
          // ),

          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(
              () => state.proxyAuthenticationExtraOptions.slug === "basic"
            )
          ),
        },
        passwordUser: {
          isValidPassword: helpers.withMessage(
            specificform,
            helpers.regex(
              /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~])[A-Za-z\d!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]{20,}$/
            )
          ),
          // requiredIfFuction: requiredIf(
          //   () => state.modeState === "edit" && state.NewUserPassword
          // ),

          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(
              () => state.modeState === "edit" && state.NewUserPassword
            )
          ),
        },
        NewUserPassword: {
          isValidNewUserPassword: helpers.withMessage(
            specificform,

            helpers.regex(
              /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~])[A-Za-z\d!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]{20,}$/
            )
          ),
          // requiredIfFuction: requiredIf(
          //   () => state.modeState === "edit" && state.passwordUser
          // ),
          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(() => state.modeState === "edit" && state.passwordUser)
          ),
        },

        password: {
          isValidPassword: helpers.withMessage(
            specificform,

            helpers.regex(
              /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~])[A-Za-z\d!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]{20,}$/
            )
          ),

          // requiredIfFuction: requiredIf(
          //   () =>
          //     (state.proxyAuthenticationExtraOptions.slug === "basic" &&
          //       state.modeState === "create") ||
          //     (state.modeState === "edit" && state.NewProxyPassword)
          // ),

          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(
              () =>
                (state.proxyAuthenticationExtraOptions.slug === "basic" &&
                  state.modeState === "create") ||
                (state.modeState === "edit" && state.NewProxyPassword)
            )
          ),
        },
        NewProxyPassword: {
          isValidNewProxyPassword: helpers.withMessage(
            specificform,

            helpers.regex(
              /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~])[A-Za-z\d!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]{20,}$/
            )
          ),

          // requiredIfFuction: requiredIf(
          //   () => state.modeState === "edit" && state.password
          // ),

          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(() => state.modeState === "edit" && state.password)
          ),
        },
        peerCertificateAuthority: {
          required: helpers.withMessage(error, required),
        },
        clientCertificate: { required: helpers.withMessage(error, required) },
        authDigestAlgorithm: { required: helpers.withMessage(error, required) },
        // hardwareCrypto: { required },
        encryptionAlgorithm: { required: helpers.withMessage(error, required) },
      };
    });

    const v$ = useValidate(rules, state);
    watch(
      state,
      () => {
        if (state.proxyAuthenticationExtraOptions.slug === "none") {
          state.username = "";
          state.password = "";
          v$.value.username.$reset();
          v$.value.password.$reset();
        }
      },
      { immediate: true }
    );

    watch(
      () => dataClient.value,
      (newValue) => {
        if (newValue != "tabs.clients") {
          // cancel();
        }
      }
    );

    watch(
      () => state.peerCertificateAuthority,
      (newValue) => {
        let clientCert = state.filtredMapCertif.filter(
          (e) => e.certificate_authority === newValue.id
        );
        if (clientCert.length == 0) {
          state.clientCertificate = "";
          state.clientCertificateList = clientCert;
        } else state.clientCertificateList = clientCert;
      },
      { deep: true }
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
    const defaultColDef = ref({
      // flex: 1,
      editable: true,
      cellDataType: false,
    });

    const close = () => {
      state.isviewModal = false;
      state.viewModal = false;
    };

    const actionCellRenderer = (params) => {
      let eGui = document.createElement("div");

      {
        eGui.innerHTML = `
          <button
          class="action-button delete"
          data-action="delete">
            <i class="fas fa-times" style="color: #086eae; font-size: 20px;"></i>
        </button>

            `;
      }
      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          handleAction(action, params.node.data, params.node.rowIndex);
        });
      });

      return eGui;
    };
    const handleAction = (action, rowData, index) => {
      const user = user_privilege("Openvpn");
      switch (action) {
        case "edit":
          if (
            user &&
            user !== "viewer" &&
            user !== "default" &&
            last_Subscription.value.includes("VPN SSL")
          ) {
            gridApi.value.setFocusedCell(index);
            gridApi.value.startEditingCell({
              rowIndex: index,
              colKey: "host",
            });
          } else {
            state.isviewModal = true;
            state.viewModal = true;
          }
          break;
        case "delete":
          if (
            user &&
            user !== "viewer" &&
            user !== "default" &&
            last_Subscription.value.includes("VPN SSL")
          ) {
            const index = rowDataCertificats.value.findIndex(
              (item) => item.host === rowData.host
            );

            if (index !== -1) {
              rowDataCertificats.value.splice(index, 1);
              if (gridApi.value) {
                gridApi.value.setRowData(rowDataCertificats.value);
              } else {
                console.error("Grid API.");
              }
            }
          } else {
            state.isviewModal = true;
            state.viewModal = true;
          }
          break;
        default:
          break;
      }
    };
    const Hostoraddress = computed(() => {
      return t("Clientsopenvpn.Hostoraddress");
    });
    const Protocole = computed(() => {
      return t("Clientsopenvpn.Protocol/Port");
    });

    const columnCertificats = ref([
      {
        headerName: Hostoraddress,
        field: "host",
        width: 90,
        minWidth: 50,
        flex: 1,
        editable: true,
      },
      {
        headerName: Protocole,
        field: "port",
        width: 90,
        minWidth: 50,
        flex: 1,
        editable: true,
      },
      {
        headerName: "Actions",
        cellRenderer: actionCellRenderer,
        width: 150,
        editable: false,
      },
    ]);

    const rowDataCertificats = ref([]);

    const addNewRow = () => {
      const user = user_privilege("Openvpn");
      if (
        user &&
        user !== "viewer" &&
        user !== "default" &&
        last_Subscription.value.includes("VPN SSL")
      ) {
        const newRow = { host: "", port: "" };
        rowDataCertificats.value.push(newRow);
        if (gridApi.value) {
          gridApi.value.setRowData(rowDataCertificats.value);
        } else {
          console.error("Grid API.");
        }
      } else {
        state.isviewModal = true;
        state.viewModal = true;
      }
    };
    const onGridReady = (params) => {
      gridApi.value = params.api;
      gridColumnApi.value = params.columnApi;
      if (gridApi.value) {
        gridApi.value.setRowData(rowDataCertificats.value);
      } else {
        console.error("Grid API.");
      }
    };

    const verbosityLevelList = ref([
      {
        name: "0 (none)",
        slug: "0",
      },
      {
        name: "1 (default)",
        slug: "1",
      },
      {
        name: "2",
        slug: "2",
      },
      {
        name: "3",
        slug: "3",
      },
      {
        name: "4",
        slug: "4",
      },
      {
        name: "5",
        slug: "5",
      },
      {
        name: "6",
        slug: "6",
      },
      {
        name: "7",
        slug: "7",
      },
      {
        name: "8",
        slug: "8",
      },
      {
        name: "9",
        slug: "9",
      },
      {
        name: "10",
        slug: "10",
      },
      {
        name: "11",
        slug: "11",
      },
    ]);
    const hasEmptyProperty = (obj) => {
      // var invalidHostChars = /[^0-9.]/.test(obj.host);
      var invalidHostChars =
        !/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(
          obj.host
        );
      var invalidPortChars = /[^0-9]/.test(obj.port);

      return (
        obj.host === "" ||
        obj.port === "" ||
        invalidHostChars ||
        invalidPortChars
      );
    };

    // const clientCertificateList = ref([]);
    const getAllCertAuth = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/certificates/getAllCertAuth").then(
        (response) => {
          let mapedList = response.data.map((i) => {
            return {
              id: i.id,
              name: i.name,
              is_private_key: i.is_private_key,
            };
          });

          state.mapedCertifAuth = mapedList.filter((i) => i.is_private_key);
        },
        (error) => {
          console.log(error);
        }
      );
    };

    const getAllClientCertif = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/certificates/getAllCertificates").then(
        (response) => {
          let mapedListCertif = response.data.filter(
            (i) => i.certificate_type === "client"
          );

          let clientCerticateList = mapedListCertif.map((i) => {
            return {
              id: i.id,
              name: i.name,
              is_private_key: i.is_private_key,
              certificate_authority: i.certificate_authority,
            };
          });

          state.filtredMapCertif = clientCerticateList.filter(
            (i) => i.is_private_key
          );
        },
        (error) => {
          console.log(error);
        }
      );
    };
    const save = async () => {
      const user = user_privilege("Openvpn");
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      if (
        user &&
        user !== "viewer" &&
        user !== "default" &&
        last_Subscription.value.includes("VPN SSL")
      ) {
        const result = await v$.value.$validate();

        if (result) {
          var isArrayEmpty = rowDataCertificats.value.length === 0;
          if (isArrayEmpty) {
            textAlertArray.value = t("errors.emptyArray");
            setTimeout(() => {
              textAlertArray.value = "";
            }, 2000);
            return;
          } else {
            var hasEmptyElement =
              rowDataCertificats.value.some(hasEmptyProperty);

            if (hasEmptyElement) {
              textAlertArray.value = t("errors.invalidChar");
              setTimeout(() => {
                textAlertArray.value = "";
              }, 2000);
              return;
            }
          }

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
              new_password: state.NewProxyPassword,
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
            protocol: state.protocol.slug ?? state.protocol,
            device_mode: state.device_mode.slug,
            interface: state.interface?.id ?? "",
            resolv_retry: state.resolv_retry,
            proxy_host: state.proxy_host ?? "",
            proxy_port: state.proxy_port ?? "",
            proxy_authentication: proxy_authentication,
            local_port: state.local_port,
            username: state.usernameUser,
            password: state.passwordUser,
            new_password: state.NewUserPassword,
            renegotiate_time: state.renegotiate_time,
            tls_auth: tls_auth,
            auth_digest_algorithm: state.authDigestAlgorithm.slug,
            ca_name: state.peerCertificateAuthority.name,
            client_cert: state.clientCertificate.name,
            encryption_algorithm: state.encryptionAlgorithm.slug,
            // hardware_crypto: state.hardwareCrypto.slug,
            ipv4_tunnel_network: state.ipv4TunnelNetwork,
            ipv4_remote_network: state.ipv4RemoteNetwork,
            limit_outgoing_bandwidth: state.limitOutgoingBandwidth,
            compression: state.compression.slug,
            type_of_service: state.typeOfService,
            ipv6: state.ipv6,
            pull_routes: state.pullRoutes,
            add_remove_routes: state.addRemoveRoutes,
            verbosity_level: state.verbosityLevel.slug ?? "",
            server_remote: rowDataCertificats.value,
          };

          if (state.isEditState === "edit") {
            axios
              .put(`/openvpn/updateClientOpenvpn/${state.id}`, payload)
              .then((response) => {
                if (response.status == "201") {
                  snackbar.value = true;
                  color.value = "success";
                  textAlert.value = response.data.msg;
                  state.isEditState = "";

                  setTimeout(() => {
                    location.reload();
                    emitter.emit("open-listing");
                  }, 1000);
                }
              })
              .catch((i) => {
                if (i.response.status === 500) {
                  snackbar.value = true;
                  color.value = "red";
                  textAlert.value = t("errors.errorServer");
                } else {
                  snackbar.value = true;
                  color.value = "red";
                  textAlert.value = i.response.data.error;
                }
              });
          } else {
            axios
              .post("/openvpn/createClientOpenvpn", payload)
              .then((response) => {
                if (response.status == "201") {
                  snackbar.value = true;
                  color.value = "success";
                  textAlert.value = response.data.msg;

                  setTimeout(() => {
                    location.reload();
                    emitter.emit("open-listing");
                  }, 1000);
                }
              })
              .catch((i) => {
                if (i.response.status === 500) {
                  snackbar.value = true;
                  color.value = "red";
                  textAlert.value = t("errors.errorServer");
                } else {
                  snackbar.value = true;
                  color.value = "red";
                  textAlert.value = i.response.data.error;
                }
              });
          }
        } else {
          console.log("v$.value", v$.value);

          var isArrayEmpty = rowDataCertificats.value.length === 0;
          if (isArrayEmpty) {
            textAlertArray.value = t("errors.emptyArray");
            setTimeout(() => {
              textAlertArray.value = "";
            }, 2000);
          } else {
            var hasEmptyElement =
              rowDataCertificats.value.some(hasEmptyProperty);

            if (hasEmptyElement) {
              textAlertArray.value = t("errors.invalidChar");
              setTimeout(() => {
                textAlertArray.value = "";
              }, 2000);
            }
          }
        }
      } else {
        state.isviewModal = true;
        state.viewModal = true;
      }
    };

    const encryptionAlgorithmList = ref([
      {
        name: "AES-256-GCM",
        slug: "AES-256-GCM",
      },
      {
        name: "AES-128-GCM",
        slug: "AES-128-GCM",
      },
      {
        name: "CHACHA20-POLY1305",
        slug: "CHACHA20-POLY1305",
      },
    ]);
    const authDigestAlgorithmList = ref([
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

    const hardwareCryptoList = ref([
      {
        name: "No Hardware Crypto acceleration",
        slug: "No Hardware Crypto",
      },
      {
        name: "Intel RDRAND engine -RAND",
        slug: "Intel RDRAND engine -RAND",
      },
    ]);

    const compression = ref([
      { name: "No preference", slug: "no_preference" },
      { name: "Disable-No Compression", slug: "disabled" },
      { name: "Enabled with Adaptive Compression", slug: "adaptive" },
      { name: "Enabled without Adaptive Compression", slug: "enabled" },
    ]);

    const Listprotocols = ref([
      {
        name: "UDP4",
        slug: "udp4",
      },
      {
        name: "UDP6",
        slug: "udp6",
      },
      {
        name: "TCP4",
        slug: "tcp4",
      },
      {
        name: "TCP6",
        slug: "tcp6",
      },
    ]);

    const cancel = () => {
      const user = user_privilege("Openvpn");
      if (
        user &&
        user !== "viewer" &&
        user !== "default" &&
        last_Subscription.value.includes("VPN SSL")
      ) {
        state.id = "";
        state.modeState = "create";
        state.isEditState = "";
        //general information
        state.clientName = "";
        state.description = "";
        state.server_mode = "";
        state.protocol = "";
        state.device_mode = "";
        state.interface = "";
        state.resolv_retry = false;
        state.proxy_host = "";
        state.proxy_port = "";
        state.proxyAuthenticationExtraOptions = {
          name: "None",
          slug: "none",
        };
        state.usernameUser = "";
        state.passwordUser = "";

        state.username = "";
        state.password = "";
        state.local_port = "";
        //User Auth
        state.username = "";
        state.password = "";
        state.renegotiate_time = "";
        //cryp
        state.tlsGenerate = true;
        state.sharedKey = "";
        state.peerCertificateAuthority = "";
        state.clientCertificate = "";
        state.encryptionAlgorithm = "";
        state.authDigestAlgorithm = "";
        // state.hardwareCrypto = {
        //   name: "No Hardware Crypto acceleration",
        //   slug: "No Hardware Crypto acceleration",
        // };
        //tunnelSettings
        state.ipv4TunnelNetwork = "";
        state.ipv6TunnelNetwork = "";
        state.ipv4RemoteNetwork = "";
        state.ipv6RemoteNetwork = "";
        state.limitOutgoingBandwidth = "";
        state.compression = { name: "No preference", slug: "no_preference" };
        state.typeOfService = false;
        state.ipv6 = false;
        state.pullRoutes = false;
        state.addRemoveRoutes = false;
        //advancedConfig
        state.verbosityLevel = {
          name: "1 (default)",
          slug: "1",
        };
        state.remoteServer = "";
        state.hostAddress = "";
        state.port = "";
        rowDataCertificats.value = [];
        if (gridApi.value) {
          gridApi.value.setRowData(rowDataCertificats.value);
        } else {
          console.error("Grid API.");
        }
        v$.value.$reset();
      } else {
        state.isviewModal = true;
        state.viewModal = true;
      }
    };

    return {
      state,
      close,
      cancel,
      userAuthSettings,
      cryptoSettings,
      tunnelSettings,
      onGridReady,
      overlayTemplate,
      getAllClientCertif,
      getAllCertAuth,
      rowDataCertificats,
      // clientCertificateList,
      Listprotocols,
      addNewRow,
      snackbar,
      textAlert,
      textAlertArray,
      columnCertificats,
      protocols: protocolsList,
      deviceMode,
      proxyAuthenticationExtraOptionsList,
      serverMode,
      encryptionAlgorithmList,
      verbosityLevelList,
      getCookie,
      color,
      authDigestAlgorithmList,
      compression,
      defaultColDef,
      gridApi,
      hardwareCryptoList,
      v$,
      save,
      overlayMessage,
      emitter,
      paginationLocalization,
    };
  },
};
</script>

<style lang="scss">
.error-feedback {
  color: red;
  font-size: 0.85em;
}
.white-link {
  color: white;
  text-decoration: underline;
}
.btn-add {
  background: #213e9f;
}
</style>
