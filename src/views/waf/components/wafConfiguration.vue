<template>
  <v-overlay v-model="state.viewModal">
    <v-dialog v-model="state.isviewModal" persistent :scrim="false" width="auto">
      <v-card color="#193286" class="alert-box">
        <v-card-title class="img-containter">
          <img src="@/assets/images/view.png" alt="logo" class="img-view" width="100" height="100" /></v-card-title>
          <v-card-text v-html="overlayMessage">
          </v-card-text>

        <div class="mr-3 mb-5 d-flex justify-end">
          <VButton rounded outlined color="#ffffff" label-color="#213E9F" :label="$t('buttons.close')" :isLarge="true"
            @click="close" />
        </div>
      </v-card>
    </v-dialog>
  </v-overlay>
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
            {{ $t("requiredfield.attente") }}
            <v-progress-linear
              indeterminate
              color="white"
              class="mb-0"
            ></v-progress-linear>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-overlay>
    <div class="ml-3 mr-3 mt-5">
      <h4>{{ $t("openvpn.Generalinformation") }}</h4>

      <v-divider class="mb-2"></v-divider>
    </div>
    <v-row class="ml-1 mr-3">
      <v-col cols="6">
        <v-row class="mt-2">
          <v-col cols="4" class="mt-5">
            <label> {{ $t("Waf.Ruleengineinitialization") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-select
              v-model="state.rule_engine"
              :label="$t('Waf.Ruleengine')"
              item-title="name"
              item-value="slug"
              clearable
              return-object
              :items="state.engineList"
            ></v-select>
            <p class="error-feedback mb-5" v-if="v$.rule_engine.$error">
              {{ v$.rule_engine.$errors[0].$message }}
            </p>
          </v-col>

          <v-col cols="4">
            <label> {{ $t("Waf.Accessrequestbodies") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <input
              type="checkbox"
              hide-details
              v-model="state.access_request"
            />
            <label class="ml-2">
              {{ $t("Waf.EnableAccessrequestbodies") }}</label
            >
          </v-col>

          <v-col cols="4">
            <label>{{ $t("Waf.XMLrequestbodyparser") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <input type="checkbox" hide-details v-model="state.xml_request" />
            <label class="ml-2">{{
              $t("Waf.EnableXMLrequestbodyparser")
            }}</label>
          </v-col>

          <v-col cols="4">
            <label>{{ $t("Waf.JSONrequestbodyparser") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <input type="checkbox" hide-details v-model="state.json_request" />
            <label class="ml-2">{{
              $t("Waf.EnableJSONrequestbodyparser")
            }}</label>
          </v-col>

          <v-col cols="4" class="mt-5">
            <label>{{ $t("Waf.Maximumrequestbodysize") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-text-field
              :label="$t('Waf.Maximumrequestbodysize')"
              v-model="state.maximum_request"
            ></v-text-field>
            <p class="error-feedback mb-5" v-if="v$.maximum_request.$error">
              {{ v$.maximum_request.$errors[0].$message }}
            </p>
          </v-col>

          <v-col cols="4" class="mt-5">
            <label>{{ $t("Waf.Requestbodysizefilesexcluded") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-text-field
              :label="$t('Waf.Requestbodysizefiles')"
              v-model="state.size_file"
            ></v-text-field>
            <p class="error-feedback mb-5" v-if="v$.size_file.$error">
              {{ v$.size_file.$errors[0].$message }}
            </p>
          </v-col>

          <v-col cols="4" class="mt-5">
            <label>{{ $t("Waf.RequestBodyLimitAction") }} </label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-select
              v-model="state.limit_action"
              :label="$t('Waf.RequestBodyLimitAction')"
              item-title="name"
              item-value="slug"
              clearable
              return-object
              :items="state.requestBodyList"
            ></v-select>
            <p class="error-feedback mb-5" v-if="v$.limit_action.$error">
              {{ v$.limit_action.$errors[0].$message }}
            </p>
          </v-col>

          <v-col cols="4" class="mt-5">
            <label>{{ $t("Waf.MaximumparsingdepthforJSON") }} </label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-text-field
              :label="$t('Waf.Maximumparsingdepth')"
              v-model="state.max_parsing"
            ></v-text-field>
            <p class="error-feedback mb-5" v-if="v$.max_parsing.$error">
              {{ v$.max_parsing.$errors[0].$message }}
            </p>
          </v-col>

          <v-col cols="4" class="mt-5">
            <label>{{ $t("Waf.Maximumnumberofargs/request") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-text-field
              :label="$t('Waf.Maximumnumberofargs/request')"
              v-model="state.max_number"
            ></v-text-field>
            <p class="error-feedback mb-5" v-if="v$.max_number.$error">
              {{ v$.max_number.$errors[0].$message }}
            </p>
          </v-col>

          <v-col cols="4" class="mt-5">
            <label>{{ $t("Waf.PcreMatchLimit") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-text-field
              :label="$t('Waf.PcreMatchLimit')"
              v-model="state.pcre_match_limit"
            ></v-text-field>
            <p class="error-feedback mb-5" v-if="v$.pcre_match_limit.$error">
              {{ v$.pcre_match_limit.$errors[0].$message }}
            </p>
          </v-col>

          <v-col cols="4" class="mt-5">
            <label>{{ $t("Waf.PcreMatchLimitRecursion") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
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

          <v-col cols="4">
            <label>{{ $t("Waf.ResponseBodyAccess") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <input type="checkbox" hide-details v-model="state.access_bodies" />
            <label class="ml-2">
              {{ $t("Waf.Enableaccessresponsebodies") }}</label
            >
          </v-col>

          <v-col cols="4" class="mt-5">
            <label>{{ $t("Waf.ResponseBodyMimeType") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-select
              v-model="state.body_mimetype"
              :label="$t('Waf.ResponseBodyMimeType')"
              item-title="name"
              item-value="slug"
              clearable
              return-object
              :items="state.bodyMimeTypeList"
            ></v-select>
            <p class="error-feedback mb-5" v-if="v$.body_mimetype.$error">
              {{ v$.body_mimetype.$errors[0].$message }}
            </p>
          </v-col>

          <v-col cols="4" class="mt-5">
            <label>{{ $t("Waf.ResponseBodyLimit") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-text-field
              :label="$t('Waf.ResponseBodyLimit')"
              v-model="state.response_body_limit"
            ></v-text-field>
            <p class="error-feedback mb-5" v-if="v$.response_body_limit.$error">
              {{ v$.response_body_limit.$errors[0].$message }}
            </p>
          </v-col>

          <v-col cols="4" class="mt-5">
            <label>{{ $t("Waf.ResponseBodyLimitAction") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
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
      </v-col>
    </v-row>

    <v-row class="flex py-8 mb-5">
      <v-col cols="4" class="mt-5"> </v-col>
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
            @click="submitForm"
          />
        </div>
      </v-col>
    </v-row>
  </div>

  <v-snackbar
    :timeout="2000"
    v-model="state.snackbar"
    location="bottom right"
    :color="state.color"
  >
    {{ state.textAlert }}
  </v-snackbar>
</template>

<script>
import { useI18n } from "vue-i18n";
import axios from "axios";
import VButton from "@/components/VButton.vue";
import { reactive, onMounted, ref, inject, computed } from "vue";
import useValidate from "@vuelidate/core";
import { required, helpers, requiredIf, email } from "@vuelidate/validators";
import { user_privilege } from "@/mixins/user_privilege.js";

export default {
  name: "ConfigServerDhcp4Component",
  components: {
    VButton,
  },
  setup() {
    const { t } = useI18n();
    const current_user = ref();
    const last_Subscription = ref([]);
    const emitter = inject("emitter");

    const state = reactive({
      isviewModal: false,
      viewModal: false,
      loading: false,
      isLoadingDialogue: false,
      id: null,
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

      snackbar: false,
      color: "",
      textAlert: "",
    });

    onMounted(() => {
      let wafConf = document.getElementById("app").attributes["waf_conf"].value;
      let configuration = JSON.parse(wafConf);

      state.id = configuration?.id;
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

    const close = () => {
      state.isviewModal = false;
      state.viewModal = false;
    };

    const lastSubscription =
        document.getElementById("app").attributes["last_subscription"].value;
      let parsedArraySubscription = JSON.parse(lastSubscription);
      last_Subscription.value = parsedArraySubscription;
      console.log("last_Subscription",last_Subscription.value)
    const cancel = () => {
      const user = user_privilege('Waf');
      if (user && user !== 'viewer' && user !=='default' && last_Subscription.value.includes("Nat") ) {
        state.id = null;
        state.rule_engine = null;
        state.access_request = false;
        state.xml_request = false;
        state.json_request = false;
        state.maximum_request = null;
        state.size_file = null;
        state.limit_action = null;
        state.max_parsing = null;
        state.max_number = null;
        state.pcre_match_limit = null;
        state.pcre_limit_recursion = null;
        state.access_bodies = false;
        state.body_mimetype = null;
        state.response_body_limit = "";
        state.response_limit_action = null;
      } else {
        state.isviewModal = true;
        state.viewModal = true;
      }
    };
    const champonlyNumber = computed(() => {
      return t("errors.ChampIncludeOnlyNumbers");
    });
    const overlayMessage = computed(() => {
  if (current_user.value === "viewer" || current_user.value === "default") {
    return `${t("profil.NoPermission")} <br /> ${t("profil.ContactAdmin")}`;
  } else if (!last_Subscription.value.includes("WAF")) {
    return `${t("firewall.msg_subscription")}<br /><a href="/asguard/subscription/" class="white-link"> ${t("firewall.sub_page")}</a>`;
  } else{
    return ` ${t("profil.NoPermission")} <br /> ${t("profil.ContactAdmin")}`;
  }
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

    const rules = computed(() => {
      return {
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
    const restartNginx = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      axios.post("/waf/restartNginx");
    };
    const submitForm = async () => {
      const user = user_privilege('Waf');
      current_user.value=user
      const result = await v$.value.$validate();
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      if (user && user !== 'viewer' && user !=='default' && last_Subscription.value.includes("WAF") ) {
        if (result) {
          let payload = {
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
          };
          state.loading = true;
          state.isLoadingDialogue = true;
          axios
            .put(`/waf/updateConfigWaf/${state.id}`, payload)
            .then((response) => {
              if (response.status == 200) {
                restartNginx();
                state.loading = true;
                state.isLoadingDialogue = true;
                setTimeout(() => {
                  state.loading = false;
                  state.isLoadingDialogue = false;
                  state.snackbar = true;
                  state.color = "success";
                  state.textAlert = response.data.msg;
                }, 4000);
                setTimeout(() => {
                  location.reload();
                }, 4000);
              }
            })
            .catch((i) => {
              state.loading = false;
              state.isLoadingDialogue = false;
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
          console.log("error", v$.value);
        }
      } else {
        state.isviewModal = true;
        state.viewModal = true;
      }
    };
    return {
      v$,
      getCookie,
      submitForm,
      cancel,
      state,
      emitter,
      overlayMessage,
      close,
    };
  },
};
</script>
<style lang="scss">
.error-feedback {
  color: rgb(255, 4, 0);
  font-size: 0.85em;
}

.label-style {
  color: #020202;
  font-family: Nunito;
  font-size: 15px;
  font-style: normal;
  font-weight: 300;
  line-height: normal;
}

/* CSS to style the text */
.text-xs {
  font-size: 12px;
  /* Example font size for small text */
}

.container {
  height: 50px;
}
.white-link {
  color: white;
  text-decoration: underline;
}
</style>
