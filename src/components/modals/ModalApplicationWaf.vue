<template>
  <v-row justify="center">
    <v-overlay v-model="state.loading">
      <v-dialog
        v-model="state.isLoadingDialogue"
        :scrim="false"
        persistent
        width="auto"
      >
        <v-card color="#193286">
          <v-card-text>
            {{ $t("sdwan.pleaseWait") }}
            <v-progress-linear
              indeterminate
              color="white"
              class="mb-0"
            ></v-progress-linear>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-overlay>
    <v-dialog v-model="state.openModal" persistent width="800">
      <form ref="myForm" @submit.prevent="submitForm" class="scroller">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              {{ $t("Waf.createNewApplication") }}</span
            >
            <span class="headline" v-if="modalMode === 'edit'">
              {{ $t("Waf.updateApplication") }}</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n5 mb-1 mt-0">
                  <v-expansion-panels v-model="state.panel">
                    <v-expansion-panel>
                      <v-expansion-panel-title>{{
                        $t("Waf.parameters")
                      }}</v-expansion-panel-title>
                      <v-expansion-panel-text>
                        <v-col cols="12" class="mb-n6">
                          <v-text-field
                            :label="$t('Waf.applicationName')"
                            v-model="state.applicationName"
                          ></v-text-field>
                          <p
                            class="error-feedback mb-5"
                            v-if="v$.applicationName.$error"
                          >
                            {{ v$.applicationName.$errors[0].$message }}
                          </p>
                        </v-col>
                        <v-col cols="12" class="mb-n6">
                          <v-select
                            v-model="state.type"
                            label="Type"
                            item-title="name"
                            item-value="slug"
                            :items="state.listType"
                            return-object
                            :no-data-text="$t('certificat.certificatlist')"
                          ></v-select>
                          <p class="error-feedback mb-5" v-if="v$.type.$error">
                            {{ v$.type.$errors[0].$message }}
                          </p>
                        </v-col>
                        <v-col cols="12" class="mb-n6">
                          <v-select
                            v-model="state.protocol"
                            :label="$t('firewall.protocol')"
                            item-title="name"
                            item-value="slug"
                            :items="state.listProtocol"
                            return-object
                            :no-data-text="$t('certificat.certificatlist')"
                          ></v-select>
                          <p
                            class="error-feedback mb-5"
                            v-if="v$.protocol.$error"
                          >
                            {{ v$.protocol.$errors[0].$message }}
                          </p>
                        </v-col>
                        <v-col
                          cols="12"
                          class="mb-n6"
                          v-if="state.protocol.slug === 'https'"
                        >
                          <v-select
                            :label="$t('openvpn.ServeurCertificate')"
                            v-model="state.serverCertif"
                            item-title="name"
                            item-value="id"
                            :items="state.filtredMapCertif"
                            :no-data-text="$t('certificat.certificatlist')"
                            return-object
                          ></v-select>
                          <p
                            class="error-feedback mb-5"
                            v-if="v$.serverCertif.$errors.length"
                          >
                            {{ v$.serverCertif.$errors?.[0].$message }}
                          </p>
                        </v-col>

                        <v-col cols="12" class="mb-n6">
                          <v-text-field
                            :label="$t('squid.value')"
                            v-model="state.value"
                          ></v-text-field>
                          <p class="error-feedback mb-5" v-if="v$.value.$error">
                            {{ v$.value.$errors[0].$message }}
                          </p>
                        </v-col>
                        <v-col cols="12" class="mb-n6">
                          <v-text-field
                            label="Port"
                            v-model.number="state.port"
                          ></v-text-field>
                          <p class="error-feedback mb-5" v-if="v$.port.$error">
                            {{ v$.port.$errors[0].$message }}
                          </p>
                        </v-col>
                        <v-col cols="12" class="mb-n6">
                          <v-text-field
                            label="Description"
                            v-model="state.description"
                          ></v-text-field>
                        </v-col>
                        <v-col cols="12" class="mb-n6">
                          <v-autocomplete
                            multiple
                            v-model="state.country"
                            :label="$t('certificat.country')"
                            item-title="countryName"
                            item-value="countryCode"
                            return-object
                            :items="state.countriesList"
                          ></v-autocomplete>
                          <!-- <p class="error-feedback mb-5" v-if="v$.country.$error">
                    {{ v$.country.$errors[0].$message }}
                  </p> -->
                        </v-col>
                      </v-expansion-panel-text>
                    </v-expansion-panel>
                    <v-expansion-panel>
                      <v-expansion-panel-title>{{
                        $t("Waf.rulesList")
                      }}</v-expansion-panel-title>
                      <v-expansion-panel-text>
                        <ag-grid-vue
                          id="grid-wrapper"
                          domLayout="autoHeight"
                          class="ag-theme-alpine mt-3"
                          :columnDefs="columnWafApp"
                          :alwaysShowHorizontalScroll="false"
                          :alwaysShowVarticalScroll="false"
                          :rowData="rowDataWafApp.value"
                          style="width: 100%; height: 100%"
                          :overlayNoRowsTemplate="overlayTemplate"
                          @grid-ready="onGridReady"
                          :pagination="false"
                          :paginationPageSize="20"
                          :localeText="paginationLocalization"
                        />
                      </v-expansion-panel-text>
                    </v-expansion-panel>
                    <v-expansion-panel>
                      <v-expansion-panel-title
                        >Configuration</v-expansion-panel-title
                      >
                      <v-expansion-panel-text>
                        <v-row class="mt-2">
                          <v-col cols="12" class="mb-n6">
                            <v-select
                              v-model="state.rule_engine"
                              :label="$t('Waf.Ruleengine')"
                              item-title="name"
                              item-value="slug"
                              clearable
                              return-object
                              :items="state.engineList"
                            ></v-select>
                            <p
                              class="error-feedback mb-5"
                              v-if="v$.rule_engine.$error"
                            >
                              {{ v$.rule_engine.$errors[0].$message }}
                            </p>
                          </v-col>

                          <v-col cols="12" class="mb-n6">
                            <input
                              type="checkbox"
                              hide-details
                              v-model="state.access_request"
                            />
                            <label class="ml-2">
                              {{ $t("Waf.EnableAccessrequestbodies") }}</label
                            >
                          </v-col>

                          <v-col cols="12" class="mb-n6">
                            <input
                              type="checkbox"
                              hide-details
                              v-model="state.xml_request"
                            />
                            <label class="ml-2">{{
                              $t("Waf.EnableXMLrequestbodyparser")
                            }}</label>
                          </v-col>

                          <v-col cols="12">
                            <input
                              type="checkbox"
                              hide-details
                              v-model="state.json_request"
                            />
                            <label class="ml-2">{{
                              $t("Waf.EnableJSONrequestbodyparser")
                            }}</label>
                          </v-col>

                          <v-col cols="12" class="mb-n6">
                            <v-text-field
                              :label="$t('Waf.Maximumrequestbodysize')"
                              v-model="state.maximum_request"
                            ></v-text-field>
                            <p
                              class="error-feedback mb-5"
                              v-if="v$.maximum_request.$error"
                            >
                              {{ v$.maximum_request.$errors[0].$message }}
                            </p>
                          </v-col>

                          <v-col cols="12" class="mb-n6">
                            <v-text-field
                              :label="$t('Waf.Requestbodysizefiles')"
                              v-model="state.size_file"
                            ></v-text-field>
                            <p
                              class="error-feedback mb-5"
                              v-if="v$.size_file.$error"
                            >
                              {{ v$.size_file.$errors[0].$message }}
                            </p>
                          </v-col>

                          <v-col cols="12" class="mb-n6">
                            <v-select
                              v-model="state.limit_action"
                              :label="$t('Waf.RequestBodyLimitAction')"
                              item-title="name"
                              item-value="slug"
                              clearable
                              return-object
                              :items="state.requestBodyList"
                            ></v-select>
                            <p
                              class="error-feedback mb-5"
                              v-if="v$.limit_action.$error"
                            >
                              {{ v$.limit_action.$errors[0].$message }}
                            </p>
                          </v-col>

                          <v-col cols="12" class="mb-n6">
                            <v-text-field
                              :label="$t('Waf.Maximumparsingdepth')"
                              v-model="state.max_parsing"
                            ></v-text-field>
                            <p
                              class="error-feedback mb-5"
                              v-if="v$.max_parsing.$error"
                            >
                              {{ v$.max_parsing.$errors[0].$message }}
                            </p>
                          </v-col>

                          <v-col cols="12" class="mb-n6">
                            <v-text-field
                              :label="$t('Waf.Maximumnumberofargs/request')"
                              v-model="state.max_number"
                            ></v-text-field>
                            <p
                              class="error-feedback mb-5"
                              v-if="v$.max_number.$error"
                            >
                              {{ v$.max_number.$errors[0].$message }}
                            </p>
                          </v-col>

                          <v-col cols="12" class="mb-n6">
                            <v-text-field
                              :label="$t('Waf.PcreMatchLimit')"
                              v-model="state.pcre_match_limit"
                            ></v-text-field>
                            <p
                              class="error-feedback mb-5"
                              v-if="v$.pcre_match_limit.$error"
                            >
                              {{ v$.pcre_match_limit.$errors[0].$message }}
                            </p>
                          </v-col>

                          <v-col cols="12" class="mb-n6">
                            <v-text-field
                              :label="$t('Waf.PcreMatchLimitRecursion')"
                              v-model="state.pcre_limit_recursion"
                            ></v-text-field>
                            <p
                              class="error-feedback mb-5"
                              v-if="v$.pcre_limit_recursion.$error"
                            >
                              {{ v$.pcre_limit_recursion.$errors[0].$message }}
                            </p>
                          </v-col>

                          <v-col cols="12">
                            <input
                              type="checkbox"
                              hide-details
                              v-model="state.access_bodies"
                            />
                            <label class="ml-2">
                              {{ $t("Waf.Enableaccessresponsebodies") }}</label
                            >
                          </v-col>

                          <v-col cols="12" class="mb-n6">
                            <v-select
                              v-model="state.body_mimetype"
                              :label="$t('Waf.ResponseBodyMimeType')"
                              item-title="name"
                              item-value="slug"
                              clearable
                              return-object
                              :items="state.bodyMimeTypeList"
                            ></v-select>
                            <p
                              class="error-feedback mb-5"
                              v-if="v$.body_mimetype.$error"
                            >
                              {{ v$.body_mimetype.$errors[0].$message }}
                            </p>
                          </v-col>

                          <v-col cols="12" class="mb-n6">
                            <v-text-field
                              :label="$t('Waf.ResponseBodyLimit')"
                              v-model="state.response_body_limit"
                            ></v-text-field>
                            <p
                              class="error-feedback mb-5"
                              v-if="v$.response_body_limit.$error"
                            >
                              {{ v$.response_body_limit.$errors[0].$message }}
                            </p>
                          </v-col>

                          <v-col cols="12" class="mb-n6">
                            <v-select
                              v-model="state.response_limit_action"
                              :label="$t('Waf.ResponseBodyLimitAction')"
                              item-title="name"
                              item-value="slug"
                              clearable
                              return-object
                              :items="state.responseBodyList"
                            ></v-select>
                            <p
                              class="error-feedback mb-5"
                              v-if="v$.response_limit_action.$error"
                            >
                              {{ v$.response_limit_action.$errors[0].$message }}
                            </p>
                          </v-col>
                        </v-row>
                      </v-expansion-panel-text>
                    </v-expansion-panel>
                  </v-expansion-panels>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions class="mt-3 actionBtn">
            <v-btn
              color="indigo-darken-3"
              large
              rounded
              outlined
              label-color="#213E9F"
              variant="flat"
              @click="closeModal"
              class="mt-3 btn-add"
            >
              <span class="text-white pr-3 pl-3">{{
                $t("buttons.close")
              }}</span>
            </v-btn>

            <v-btn
              large
              rounded
              outlined
              label-color="#213E9F"
              type="submit"
              color="indigo-darken-3"
              variant="flat"
              class="mt-3 btn-add"
            >
              <span class="text-white pr-3 pl-3" v-if="modalMode === 'create'">
                {{ $t("buttons.create") }}</span
              >
              <span class="text-white pr-3 pl-3" v-if="modalMode === 'edit'">
                {{ $t("buttons.update") }}</span
              >
            </v-btn>
          </v-card-actions>
        </v-card>
      </form>
    </v-dialog>

    <v-snackbar
      :timeout="2000"
      v-model="state.snackbar"
      location="bottom right"
      :color="state.color"
    >
      {{ state.textAlert }}
    </v-snackbar>
  </v-row>
</template>

<script>
import countryList from "country-list";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import { useI18n } from "vue-i18n";
import axios from "axios";
import useValidate from "@vuelidate/core";
import { toRefs, ref, watch, onMounted, reactive, computed, inject } from "vue";
import { required, helpers, requiredIf, email } from "@vuelidate/validators";
import { getCookie } from "@/mixins/csrftoken.js";
import { CheckboxCellEditor } from "ag-grid-community";

export default {
  components: {
    AgGridVue,
  },
  props: {
    isOpen: {
      type: Boolean,
      required: true,
    },
    editRow: {
      type: Object,
      Array,
      required: true,
    },
    modalMode: {
      required: true,
    },
  },

  setup(props) {
    const emitter = inject("emitter");
    onMounted(() => {
      let countries = countryList.getData();
      getAllcountryCode(countries);
      getCertif();
      overlayTemplate.value = `
        <span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
        <path
          d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
          style="fill: #E8EAF6"
          data-name="Unbox"
        />
       </svg></span>`;

      let wafList =
        document.getElementById("app").attributes["list_rules"].value;
      let list_rules = JSON.parse(wafList);
      let mapedRow = list_rules.map((e) => {
        return {
          rule_waf: e.id,
          name: e.name,
          rule_policy: false,
          rule_log: false,
        };
      });

      rowDataWafApp.value = mapedRow;
    });
    const { t } = useI18n();
    const ListofErrorsParams = [
      "applicationName",
      "type",
      "protocol",
      "serverCertif",
      "value",
      "port",
    ];
    const ListofErrorsConfigs = [
      "rule_engine",
      "maximum_request",
      "size_file",
      "limit_action",
      "max_parsing",
      "max_number",
      "pcre_match_limit",
      "pcre_limit_recursion",
      "body_mimetype",
      "response_body_limit",
      "response_limit_action",
    ];
    const { isOpen, editRow, modalMode } = toRefs(props);

    const rowDataWafApp = ref([]);
    const paginationLocalization = reactive({
      of: "/",
    });
    const overlayTemplate = ref("");
    const gridApi = ref(null);
    const gridColumnApi = ref(null);

    const state = reactive({
      panel: null,
      loading: false,
      isLoadingDialogue: false,
      listType: ["ip", "domain"],
      countriesList: [],
      listProtocol: [
        { name: "HTTP", slug: "http" },
        { name: "HTTPS", slug: "https" },
      ],
      protocol: "",
      filtredMapCertif: [],
      serverCertif: "",
      id: null,
      //
      snackbar: false,
      color: "",
      textAlert: "",
      openModal: false,

      type: "",
      value: "",
      description: "",
      applicationName: "",
      country: [],
      port: "",
      //config
      //
      engineList: ["On", "Off", "DetectionOnly"],
      requestBodyList: ["ProcessPartial", "Reject"],
      responseBodyList: ["ProcessPartial", "Reject"],
      bodyMimeTypeList: ["text/*", "text/html", "text/xml", "text/plain"],
      //

      rule_engine: null,
      response_body_limit: "",
      access_request: false,
      xml_request: false,
      json_request: false,
      body_mimetype: null,
      access_bodies: false,

      maximum_request: null,
      size_file: null,
      limit_action: null,
      response_limit_action: null,
      max_parsing: null,
      max_number: null,
      pcre_match_limit: null,
      pcre_limit_recursion: null,
      //
    });

    watch(
      () => isOpen.value,
      (val) => {
        state.openModal = val;
      }
    );
    watch(
      () => state.protocol,
      (val) => {
        if (val.slug === "http") state.serverCertif = "";
      }
    );
    watch(
      () => editRow.value,
      (val) => {
        populate(val);
      }
    );
    watch(
      () => modalMode.value,
      (val) => {
        if (modalMode.value === "create") {
          initialConfig();
          state.type = "";
          state.applicationName = "";
          state.value = "";
          state.description = "";
          state.country = [];
          state.port = "";
          state.serverCertif = "";
          state.protocol = "";
        }
      }
    );

    const initialConfig = () => {
      //config
      let wafConf = document.getElementById("app").attributes["waf_conf"].value;
      let configuration = JSON.parse(wafConf);
      state.rule_engine = configuration?.rule_engine_initialization;
      state.access_request = configuration?.access_request_bodies;
      state.xml_request = configuration?.xml_request_body_parser;
      state.json_request = configuration?.json_request_body_parser;
      state.maximum_request = configuration?.maximum_request_body_size;
      state.size_file = configuration?.request_body_size_files_excluded;
      state.limit_action = configuration?.request_body_limit_action;
      state.max_parsing = configuration?.maximum_parsing_depth_json;
      state.max_number = configuration?.maximum_number_args_request;
      state.pcre_match_limit = configuration?.pcre_match_limit;
      state.pcre_limit_recursion = configuration?.pcre_match_limit_recursion;
      state.access_bodies = configuration?.response_body_access;
      state.body_mimetype = configuration?.response_body_mimetype;
      state.response_body_limit = configuration?.response_body_limit;
      state.response_limit_action = configuration?.response_body_limit_action;
      state.panel = null;
    };
    const getCertif = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/certificates/getAllCertificates").then(
        (response) => {
          let mapedListCertif = response.data.filter(
            (i) => i.certificate_type === "server"
          );
          let mapedCertServer = mapedListCertif.map((i) => {
            return {
              id: i.id,
              name: i.name,
              is_private_key: i.is_private_key,
              certificate_authority: i.certificate_authority,
            };
          });
          state.filtredMapCertif = mapedCertServer.filter(
            (i) => i.is_private_key
          );
        },
        (error) => {
          console.log(error);
        }
      );
    };

    const block = computed(() => {
      return t("Waf.block");
    });
    const rule = computed(() => {
      return t("Waf.Rule");
    });
    const log = computed(() => {
      return t("Waf.log");
    });

    const columnWafApp = ref([
      {
        headerName: rule,
        field: "name",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: block,
        field: "rule_policy",

        width: 150,
        cellRenderer: CheckboxCell,
      },
    ]);

    function CheckboxCell(params) {
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.checked = params.value;
      if (
        params.data.name === "REQUEST-949-BLOCKING-EVALUATION" ||
        params.data.name === "REQUEST-901-INITIALIZATION"
      ) {
        params.data.rule_policy = true;
        checkbox.disabled = true;
        checkbox.checked = true;
      } else {
        checkbox.addEventListener("change", () => {
          params.node.setDataValue(params.colDef.field, checkbox.checked);
        });
      }
      return checkbox;
    }

    const populate = (data) => {
      if (modalMode.value === "edit") {
        state.id = data.id;

        let filtredCountry = [];
        data?.country.forEach((e) => {
          filtredCountry = [
            ...filtredCountry,
            ...state.countriesList.filter((i) => i.countryCode === e),
          ];
        });
        state.country = filtredCountry ?? [];

        state.type = data.application_type;
        state.applicationName = data.name;
        state.value = data.application_value;
        console.log("application_value***", data.application_value);
        state.description = data.description;
        state.port = data.application_port;

        let mapedRow = data.rules.map((e) => {
          return {
            rule_waf: e.rule_waf,
            name: e.rule_name,
            rule_policy: e.rule_policy,
            rule_log: e.rule_log,
          };
        });

        rowDataWafApp.value = mapedRow;

        let filtredProtocol = state.listProtocol.filter(
          (i) => i.slug === data?.application_protocol
        );
        state.protocol = filtredProtocol[0];

        if (data.certificate_name) {
          let filtredCertif = state.filtredMapCertif.filter(
            (i) => i.name === data?.certificate_name
          );
          state.serverCertif = filtredCertif[0];
        }
        //config
        state.rule_engine = data?.config?.rule_engine_initialization;
        state.access_request = data?.config?.access_request_bodies;
        state.xml_request = data?.config?.xml_request_body_parser;
        state.json_request = data?.config?.json_request_body_parser;
        state.maximum_request = data?.config?.maximum_request_body_size;
        state.size_file = data?.config?.request_body_size_files_excluded;
        state.limit_action = data?.config?.request_body_limit_action;
        state.max_parsing = data?.config?.maximum_parsing_depth_json;
        state.max_number = data?.config?.maximum_number_args_request;
        state.pcre_match_limit = data?.config?.pcre_match_limit;
        state.pcre_limit_recursion = data?.config?.pcre_match_limit_recursion;
        state.access_bodies = data?.config?.response_body_access;
        state.body_mimetype = data?.config?.response_body_mimetype;
        state.response_body_limit = data?.config?.response_body_limit;
        state.response_limit_action = data?.config?.response_body_limit_action;
      }
    };

    const restartNginx = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      axios.post("/waf/restartNginx");
    };

    const submitForm = async () => {
      const result = await v$.value.$validate();
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      if (result) {
        let mapedCountry = state.country.map((e) => e.countryCode);
        let mapedRuleApp = rowDataWafApp.value.map((e) => {
          return {
            rule_waf: e.rule_waf,
            rule_policy: e.rule_policy,
            rule_log: e.rule_log,
          };
        });

        let payload = {
          name: state.applicationName,
          application_protocol: state.protocol.slug,
          application_type: state.type,
          application_value: state.value,
          application_port: state.port,
          description: state.description,
          country: mapedCountry,
          rules: mapedRuleApp,
          config: {
            rule_engine_initialization: state.rule_engine,
            access_request_bodies: state.access_request,
            xml_request_body_parser: state.xml_request,
            json_request_body_parser: state.json_request,
            maximum_request_body_size: state.maximum_request,
            request_body_size_files_excluded: state.size_file,
            request_body_limit_action: state.limit_action,
            maximum_parsing_depth_json: state.max_parsing,
            maximum_number_args_request: state.max_number,
            pcre_match_limit: state.pcre_match_limit,
            pcre_match_limit_recursion: state.pcre_limit_recursion,
            response_body_access: state.access_bodies,
            response_body_mimetype: state.body_mimetype,
            response_body_limit: state.response_body_limit,
            response_body_limit_action: state.response_limit_action,
          },
        };
        if (state.protocol.slug === "https") {
          payload = { ...payload, certificate_name: state.serverCertif.name };
        }

        if (modalMode.value === "edit") {
          axios
            .put(`/waf/updateApplicationWaf/${state.id}`, payload)
            .then((response) => {
              if (response.status == "201") {
                restartNginx();
                state.loading = true;
                state.isLoadingDialogue = true;
                setTimeout(() => {
                  state.loading = false;
                  state.isLoadingDialogue = false;
                  state.snackbar = true;
                  state.color = "success";
                  state.textAlert = response.data.msg;
                  closeModal();
                }, 5000);
                setTimeout(() => {
                  location.reload();
                }, 5000);
              }
            })
            .catch((i) => {
              if (i.response.status === 500) {
                state.snackbar = true;
                state.color = "red";
                state.textAlert = t("errors.errorServer");
              } else {
                state.snackbar = true;
                state.color = "red";
                state.textAlert = i.response.data.error;
              }
            });
        } else {
          axios
            .post("/waf/createApplicationWaf", payload)
            .then((response) => {
              if (response.status == "201") {
                restartNginx();
                state.loading = true;
                state.isLoadingDialogue = true;
                setTimeout(() => {
                  state.loading = false;
                  state.isLoadingDialogue = false;
                  state.snackbar = true;
                  state.color = "success";
                  state.textAlert = response.data.msg;
                  closeModal();
                }, 5000);
                setTimeout(() => {
                  location.reload();
                }, 5000);
              }
            })
            .catch((i) => {
              if (i.response.status === 500) {
                state.snackbar = true;
                state.color = "red";
                state.textAlert = t("errors.errorServer");
              } else {
                state.snackbar = true;
                state.color = "red";
                state.textAlert = i.response.data.error;
              }
            });
        }
      } else {
        if (ListofErrorsParams.includes(v$.value.$errors[0].$property)) {
          state.panel = 0;
        } else if (
          ListofErrorsConfigs.includes(v$.value.$errors[0].$property)
        ) {
          state.panel = 2;
        }
      }
    };

    const closeModal = () => {
      emitter.emit("closeWafApplicationModal");
      if (modalMode.value === "create") {
        state.type = "";
        state.applicationName = "";
        state.value = "";
        state.description = "";
        state.country = [];
        state.port = "";
        state.serverCertif = "";
        state.protocol = "";
        initialConfig();
        v$.value.$reset();
      }
    };
    const getAllcountryCode = async (countries) => {
      // await axios.get("https://countriesnow.space/api/v0.1/countries/iso").then(
      //   (response) => {
      //     console.log("re", response);

      //     let countryList = response.data.data.map((element) => {
      //       return {
      //         countryName: element.name,
      //         countryCode: element.Iso2,
      //       };
      //     });
      //     countryList.sort((a, b) =>
      //       a.countryName.localeCompare(b.countryName)
      //     );
      //     state.countriesList = countryList;
      //   },
      //   (error) => {
      //     console.log(error);
      //   }
      // );

      let countryList = countries.map((element) => {
        return {
          countryName: element.name,
          countryCode: element.code,
        };
      });
      countryList.sort((a, b) => a.countryName.localeCompare(b.countryName));
      state.countriesList = countryList;
    };
    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const onlynumbers = computed(() => {
      return t("errors.ChampIncludeOnlyNumbers");
    });
    const indication = computed(() => {
      return t("champs.indication");
    });

    const champonlyNumber = computed(() => {
      return t("errors.ChampIncludeOnlyNumbers");
    });
    const champ = computed(() => {
      return t("errors.valueRequired");
    });
    const nbre = computed(() => {
      return t("Waf.nombreMustBe");
    });
    const and = computed(() => {
      return t("Waf.and");
    });
    const port = computed(() => {
      return t("errors.port");
    });
    const formaaddress = computed(() => {
      return t("errors.formatMustBeLikeAdresseIP");
    });

    const isValidRemoteGateway = helpers.regex(
      /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
    );
    const isValidDomaineName = helpers.regex(
      /^([a-zA-Z]+\d*|\d+[a-zA-Z]*|\d+|[a-zA-Z]+)\.[a-zA-Z]{2,}$/
    );
    const format = computed(() => {
      return t("errors.format_address");
    });

    const rules = computed(() => {
      return {
        applicationName: {
          required: helpers.withMessage(error, required),
          isValidName: helpers.withMessage(
            indication,
            helpers.regex(/^[A-Za-z0-9_\-]+$/)
          ),
        },
        value: {
          required: helpers.withMessage(error, required),
          isValidAddress: helpers.withMessage(
            (value) => {
              if (state.type === "ip") {
                return formaaddress;
              }
              if (state.type === "domain") {
                return format;
              }
            },
            (value) => {
              if (state.type === "ip") {
                return isValidRemoteGateway(value);
              }
              if (state.type === "domain") {
                return isValidDomaineName(value);
              }
              return true;
            }
          ),
        },

        // value: {
        //   required: helpers.withMessage(error, required),

        //   // isValidlRemoteGateway: helpers.withMessage(
        //   //   formaaddress,
        //   //   helpers.regex(/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/)
        //   // ),
        // },
        protocol: {
          required: helpers.withMessage(error, required),
        },
        serverCertif: {
          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(() => state.protocol.slug === "https")
          ),
        },

        type: {
          required: helpers.withMessage(error, required),
        },

        // country: {
        //   required: helpers.withMessage(error, required),
        // },
        port: {
          required: helpers.withMessage(error, required),
          isValidPort: helpers.withMessage(
            onlynumbers,
            helpers.regex(/^[0-9]+$/)
          ),
          endsWith443: helpers.withMessage(
            port,
            (value) => {
              if (state.protocol.slug === "https") {
                return value.toString().endsWith("443");
              }
              return true;
            }
          ),
        },
        //config
        limit_action: { required },
        size_file: {
          required: helpers.withMessage(champ, required),
          isValidSizeFile: helpers.withMessage(
            champonlyNumber,

            helpers.regex(/^[0-9]+$/)
          ),
          interval: helpers.withMessage(
            `${nbre.value} 1 ${and.value} 1073741824`,
            (value) => {
              const num = Number(value);
              return !isNaN(num) && num >= 1 && num <= 1073741824;
            }
          ),
        },
        rule_engine: { required },
        maximum_request: {
          required: helpers.withMessage(champ, required),
          isValidMaxRequest: helpers.withMessage(
            champonlyNumber,

            helpers.regex(/^[0-9]+$/)
          ),
          interval: helpers.withMessage(
            `${nbre.value} 1 ${and.value} 1073741824`,
            (value) => {
              const num = Number(value);
              return !isNaN(num) && num >= 1 && num <= 1073741824;
            }
          ),
        },
        max_parsing: {
          required: helpers.withMessage(champ, required),
          isValidMaxParsing: helpers.withMessage(
            champonlyNumber,

            helpers.regex(/^[0-9]+$/)
          ),
          interval: helpers.withMessage(
            `${nbre.value} 100 ${and.value} 10000`,
            (value) => {
              const num = Number(value);
              return !isNaN(num) && num >= 100 && num <= 10000;
            }
          ),
        },
        body_mimetype: { required },
        response_limit_action: { required },
        response_body_limit: {
          required: helpers.withMessage(champ, required),
          isValidResponseBodyLimit: helpers.withMessage(
            champonlyNumber,

            helpers.regex(/^[0-9]+$/)
          ),
          interval: helpers.withMessage(
            `${nbre.value} 1 ${and.value} 1073741824`,
            (value) => {
              const num = Number(value);
              return !isNaN(num) && num >= 1 && num <= 1073741824;
            }
          ),
        },
        max_number: {
          required: helpers.withMessage(champ, required),
          isValidMaxNumber: helpers.withMessage(
            champonlyNumber,

            helpers.regex(/^[0-9]+$/)
          ),
          interval: helpers.withMessage(
            `${nbre.value} 1 ${and.value} 1000`,
            (value) => {
              const num = Number(value);
              return !isNaN(num) && num >= 1 && num <= 1000;
            }
          ),
        },
        pcre_limit_recursion: {
          required: helpers.withMessage(champ, required),
          isValidPcreLimitRecursion: helpers.withMessage(
            champonlyNumber,

            helpers.regex(/^[0-9]+$/)
          ),
          interval: helpers.withMessage(
            `${nbre.value} 1000 ${and.value} 50000`,
            (value) => {
              const num = Number(value);
              return !isNaN(num) && num >= 1000 && num <= 50000;
            }
          ),
        },
        pcre_match_limit: {
          required: helpers.withMessage(champ, required),
          isValidPcreMatchLimit: helpers.withMessage(
            champonlyNumber,

            helpers.regex(/^[0-9]+$/)
          ),
          interval: helpers.withMessage(
            `${nbre.value} 1000 ${and.value} 50000`,
            (value) => {
              const num = Number(value);
              return !isNaN(num) && num >= 1000 && num <= 50000;
            }
          ),
        },
      };
    });

    const v$ = useValidate(rules, state);

    const onGridReady = (params) => {
      gridApi.value = params.api;
      gridColumnApi.value = params.columnApi;
      if (gridApi.value) {
        gridApi.value.setRowData(rowDataWafApp.value);
      }
    };

    return {
      state,
      columnWafApp,
      rowDataWafApp,
      paginationLocalization,
      overlayTemplate,
      gridColumnApi,
      gridApi,
      emitter,
      v$,
      closeModal,
      onGridReady,
      submitForm,
    };
  },
};
</script>
<style>
.error-feedback {
  color: red;
  font-size: 0.85em;
}
.actionBtn {
  justify-content: center;
}
.scroller {
  overflow: auto;
}
</style>
