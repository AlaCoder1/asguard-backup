<template>
  <div class="mt-3">
    <v-row>
      <v-col align-self="center" cols="6">
        <div class="ml-3 mr-3">
          <h4>General information</h4>
          <v-divider class="mt-2"></v-divider>
          <v-row class="mt-2">
            <v-col align-self="center" cols="4">
              <label>Client name*</label>
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
              <label>Server mode*</label>
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
              <label>Protocol*</label>
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
              <label>Device Mode*</label>
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
                  type="password"
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
          <div class="mt-3">
            <h4 class="mt-6">Advanced Configuration</h4>
            <v-divider class="mt-2"></v-divider>
            <v-row class="mt-2">
              <v-col align-self="center" cols="4">
                <label>Verbosity level</label>
              </v-col>
              <v-col align-self="center" cols="8" class="mb-n6">
                <v-select
                  label="Verbosity level"
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
            <h4 class="mt-6">Remote server</h4>
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
                      <span class="text-white">Add</span>
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
                    style="width: 100%; height: 100%"
                    @grid-ready="onGridReady"
                  />
                </v-col>
              </v-row>
            </v-row>
          </div>
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
            class="ml-2"
            @click="save"
          />
        </div>
      </v-col>
    </v-row>
    <br />
    <v-spacer></v-spacer>
    <v-snackbar
      :timeout="2000"
      v-model="snackbar"
      location="bottom right"
      :color="color"
    >
      {{ textAlert }}
    </v-snackbar>
  </div>
</template>

<script>
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
    const { dataClient } = toRefs(props);
    const emitter = inject("emitter");
    const color = ref(null);
    const snackbar = ref(false);
    const textAlert = ref(false);
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

      username: "",
      password: "",
      local_port: "",
      // mapedInterface: [],
      mapedCertifAuth: [],
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
      // getInterface();
      getAllCertAuth();
      getAllClientCertif();
      protocolsList.value = protocols;

      emitter.on("edit-client", (data) => {
        if (data) state.isEditState = "edit";
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
        state.username = data.password;
        state.password = data.username;
        state.renegotiate_time = data.renegotiate_time;
        state.tlsGenerate = data.tls_key ? false : true;
        state.sharedKey = data.tls_key;

        let filtredCert = state.mapedCertifAuth.filter(
          (i) => i.name === data.ca_name
        );
        state.peerCertificateAuthority = filtredCert[0];

        let filtredCertiClient = clientCertificateList.value.filter(
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

    const rules = computed(() => {
      return {
        clientName: {
          required,
          isValidClientName: helpers.withMessage(
            `champs can include only letters & Numbers & underscores & hyphens without space.`,
            helpers.regex(/^[A-Za-z0-9_\-]+$/)
          ),
        },
        server_mode: { required },
        protocol: { required },
        device_mode: { required },

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
        // hardwareCrypto: { required },
        encryptionAlgorithm: { required },
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

    watch(
      () => dataClient.value,
      (newValue) => {
        if (newValue != "CLIENTS") {
          cancel();
        }
      }
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
      flex: 1,
      editable: true,
      cellDataType: false,
    });

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
      switch (action) {
        case "edit":
          gridApi.value.setFocusedCell(index);
          gridApi.value.startEditingCell({
            rowIndex: index,
            colKey: "host",
          });
          break;
        case "delete":
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
          break;
        default:
          break;
      }
    };

    const columnCertificats = ref([
      {
        headerName: "Host or address",
        field: "host",
        minWidth: 150,
        editable: true,
      },
      {
        headerName: "Protocole / Port",
        field: "port",
        minWidth: 250,
        editable: true,
      },
      {
        headerName: "Actions",
        cellRenderer: actionCellRenderer,
        minWidth: 150,
        editable: false,
        sortable: false,
        filter: false,
        resizable: true,
      },
    ]);

    const rowDataCertificats = ref([]);

    const addNewRow = () => {
      const newRow = { host: "", port: "" };
      rowDataCertificats.value.push(newRow);
      if (gridApi.value) {
        gridApi.value.setRowData(rowDataCertificats.value);
      } else {
        console.error("Grid API.");
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
      var invalidHostChars = /[^0-9.]/.test(obj.host);
      var invalidPortChars = /[^0-9]/.test(obj.port);

      return (
        obj.host === "" ||
        obj.port === "" ||
        invalidHostChars ||
        invalidPortChars
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
    const clientCertificateList = ref([]);
    const getAllClientCertif = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/certificates/getAllCertificates").then(
        (response) => {
          let mapedListCertif = response.data.filter(
            (i) => i.certificate_type === "client"
          );

          clientCertificateList.value = mapedListCertif.map((i) => {
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
    const save = async () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      var isArrayEmpty = rowDataCertificats.value.length === 0;
      if (isArrayEmpty) {
        snackbar.value = true;
        color.value = "red";
        textAlert.value = "The array is empty. Please add at least one object.";
      } else {
        var hasEmptyElement = rowDataCertificats.value.some(hasEmptyProperty);

        if (hasEmptyElement) {
          snackbar.value = true;
          color.value = "red";
          textAlert.value =
            "At least one element has an empty host or port, or contains invalid characters.";
        }
      }

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
              snackbar.value = true;
              color.value = "red";
              textAlert.value = i.response.data.error;
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
                }, 1000);
                emitter.emit("open-listing");
              }
            })
            .catch((i) => {
              snackbar.value = true;
              color.value = "red";
              textAlert.value = i.response.data.error;
            });
        }
      } else {
        console.log("v$.value", v$.value);
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
        name: "SHA244",
        slug: "SHA244",
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
      state.id = "";
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
    };

    return {
      state,
      cancel,
      userAuthSettings,
      cryptoSettings,
      tunnelSettings,
      onGridReady,
      getAllClientCertif,
      getAllCertAuth,
      rowDataCertificats,
      clientCertificateList,
      Listprotocols,
      addNewRow,
      snackbar,
      textAlert,
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
.btn-add {
  background: #213e9f;
}
</style>
