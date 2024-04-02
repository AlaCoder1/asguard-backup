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
    <div class="ml-3 mr-3 mt-5">
      <h4>General information</h4>

      <v-divider class="mb-2"></v-divider>
    </div>
    <v-row class="ml-1 mr-3">
      <v-col cols="6">
        <v-row class="mt-2">
          <v-col cols="4" class="mt-5">
            <label>Rule engine initialization</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-select
              v-model="state.rule_engine"
              label="Rule engine"
              item-title="name"
              item-value="slug"
              clearable
              return-object
              :items="[]"
            ></v-select>
            <p class="error-feedback mb-5" v-if="v$.rule_engine.$error">
              {{ v$.rule_engine.$errors[0].$message }}
            </p>
          </v-col>

          <v-col cols="4">
            <label>Access request bodies</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <input
              type="checkbox"
              hide-details
              v-model="state.access_request"
            />
            <label class="ml-2"> Enable Access request bodies</label>
          </v-col>

          <v-col cols="4">
            <label>XML request body parser</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <input type="checkbox" hide-details v-model="state.xml_request" />
            <label class="ml-2"> Enable XML request body parser</label>
          </v-col>

          <v-col cols="4">
            <label>JSON request body parser</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <input type="checkbox" hide-details v-model="state.json_request" />
            <label class="ml-2">Enable JSON request body parser</label>
          </v-col>

          <v-col cols="4" class="mt-5">
            <label>Maximum request body size</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-text-field
              label="Maximum request body size"
              v-model="state.maximum_request"
            ></v-text-field>
            <p class="error-feedback mb-5" v-if="v$.maximum_request.$error">
              {{ v$.maximum_request.$errors[0].$message }}
            </p>
          </v-col>

          <v-col cols="4" class="mt-5">
            <label>Request body size files excluded</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-text-field
              label="Request body size files"
              v-model="state.size_file"
            ></v-text-field>
            <p class="error-feedback mb-5" v-if="v$.size_file.$error">
              {{ v$.size_file.$errors[0].$message }}
            </p>
          </v-col>

          <v-col cols="4" class="mt-5">
            <label>Request Body Limit Action </label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-select
              v-model="state.limit_action"
              label="Request Body Limit Action"
              item-title="name"
              item-value="slug"
              clearable
              return-object
              :items="[]"
            ></v-select>
            <p class="error-feedback mb-5" v-if="v$.limit_action.$error">
              {{ v$.limit_action.$errors[0].$message }}
            </p>
          </v-col>

          <v-col cols="4" class="mt-5">
            <label>Maximum parsing depth for JSON </label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-text-field
              label="Maximum parsing depth"
              v-model="state.max_parsing"
            ></v-text-field>
            <p class="error-feedback mb-5" v-if="v$.max_parsing.$error">
              {{ v$.max_parsing.$errors[0].$message }}
            </p>
          </v-col>

          <v-col cols="4" class="mt-5">
            <label>Maximum number of args/request</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-text-field
              label="Maximum number of args/request"
              v-model="state.max_number"
            ></v-text-field>
            <p class="error-feedback mb-5" v-if="v$.max_number.$error">
              {{ v$.max_number.$errors[0].$message }}
            </p>
          </v-col>

          <v-col cols="4" class="mt-5">
            <label>Pcre Match Limit</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-text-field
              label="Pcre Match Limit"
              v-model="state.pcre_match_limit"
            ></v-text-field>
            <p class="error-feedback mb-5" v-if="v$.pcre_match_limit.$error">
              {{ v$.pcre_match_limit.$errors[0].$message }}
            </p>
          </v-col>

          <v-col cols="4" class="mt-5">
            <label>Pcre Match Limit Recursion</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-text-field
              label="Pcre Match Limit Recursion"
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
            <label>Response Body Access</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <input type="checkbox" hide-details v-model="state.access_bodies" />
            <label class="ml-2"> Enable access response bodies</label>
          </v-col>

          <v-col cols="4" class="mt-5">
            <label>Response Body MimeType</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-select
              v-model="state.body_mimetype"
              label="Response Body MimeType"
              item-title="name"
              item-value="slug"
              clearable
              return-object
              :items="[]"
            ></v-select>
            <p class="error-feedback mb-5" v-if="v$.body_mimetype.$error">
              {{ v$.body_mimetype.$errors[0].$message }}
            </p>
          </v-col>

          <v-col cols="4" class="mt-5">
            <label>Response Body Limit</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-text-field
              label="Response Body Limit"
              v-model="state.response_body_limit"
            ></v-text-field>
            <p class="error-feedback mb-5" v-if="v$.response_body_limit.$error">
              {{ v$.response_body_limit.$errors[0].$message }}
            </p>
          </v-col>

          <v-col cols="4" class="mt-5">
            <label>Response Body Limit Action</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-select
              v-model="state.response_limit_action"
              label="Response Body Limit Action"
              item-title="name"
              item-value="slug"
              clearable
              return-object
              :items="[]"
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
import axios from "axios";
import VButton from "@/components/VButton.vue";
import { reactive, onMounted, ref, inject, computed } from "vue";
import useValidate from "@vuelidate/core";
import { required, helpers, requiredIf, email } from "@vuelidate/validators";

export default {
  name: "ConfigServerDhcp4Component",
  components: {
    VButton,
  },
  setup() {
    const emitter = inject("emitter");
    const state = reactive({
      loading: false,
      isLoadingDialogue: false,
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

    const rules = computed(() => {
      return {
        limit_action: { required },
        size_file: { required },
        rule_engine: { required },
        maximum_request: { required },
        max_parsing: { required },
        body_mimetype: { required },
        response_limit_action: { required },
        response_body_limit: { required },
        max_number: { required },
        pcre_limit_recursion: { required },
        pcre_match_limit: { required },
      };
    });

    const v$ = useValidate(rules, state);

    const submitForm = async () => {
      const result = await v$.value.$validate();
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      if (result) {
        // let payload = {
        //   access_request: state.access_request,
        //   maximum_request: state.maximum_request,
        //   size_file: state.size_file,
        //   limit_action: state.limit_action,
        //   dns_server: mapredServer,
        //   max_parsing: state.max_parsing,
        //   max_number: state.max_number,
        //   ranges_address: mapredRow,
        // };
        // state.loading = true;
        // state.isLoadingDialogue = true;
        // axios
        //   .put(
        //     `/server_dhcp4/updateDhcp4Server/${props.configInfo.id}`,
        //     payload
        //   )
        //   .then((response) => {
        //     if (response.status == 200) {
        //       state.loading = false;
        //       state.isLoadingDialogue = false;
        //       state.snackbar = true;
        //       state.color = "success";
        //       state.textAlert = response.data.msg;
        //       setTimeout(() => {
        //         state.snackbar = false;
        //         location.reload();
        //       }, 3000);
        //     }
        //   })
        //   .catch((i) => {
        //     state.loading = false;
        //     state.isLoadingDialogue = false;
        //     state.snackbar = true;
        //     state.color = "error";
        //     state.textAlert = i.response.data.msg;
        //     setTimeout(() => {
        //       state.snackbar = false;
        //       location.reload();
        //     }, 1000);
        //   });
      } else {
        console.log("error", v$.value);
      }
    };
    return {
      v$,
      getCookie,
      submitForm,
      state,
      emitter,
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
  font-size: 12px; /* Example font size for small text */
}
.container {
  height: 50px;
}
</style>
