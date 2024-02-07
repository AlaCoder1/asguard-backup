<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="text-h5"> Create new Rule</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Rule Name"
                    v-model="state.ruleName"
                  ></v-text-field>
                  <p class="error-feedback mb-5" v-if="v$.ruleName.$error">
                    {{ v$.ruleName.$errors[0].$message }}
                  </p>
                </v-col>

                <v-col cols="7" class="mb-n6">
                  <v-text-field
                    label="Source"
                    v-model="state.source"
                  ></v-text-field>
                </v-col>
                <v-col cols="1" class="mb-n6">
                  <div class="ml-1 mt-5">/</div>
                </v-col>
                <v-col cols="4" class="mb-n6">
                  <v-select
                    label="Prefix"
                    v-model="state.sourcePrefix"
                    :items="numberList"
                  ></v-select>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.algo"
                    label="Algo"
                    item-title="name"
                    item-value="slug"
                    :items="listAlgo"
                    return-object
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.algo.$error">
                    {{ v$.algo.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.area"
                    label="Area"
                    item-title="name"
                    item-value="slug"
                    :items="listAlgo"
                    return-object
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.area.$error">
                    {{ v$.area.$errors[0].$message }}
                  </p>
                </v-col>

                <v-col cols="7" class="mb-n6">
                  <v-text-field
                    label="Destination"
                    v-model="state.destination"
                  ></v-text-field>
                </v-col>
                <v-col cols="1" class="mb-n6">
                  <div class="ml-1 mt-5">/</div>
                </v-col>
                <v-col cols="4" class="mb-n6">
                  <v-select
                    label="Prefix"
                    v-model="state.destinationPrefix"
                    :items="numberList"
                  ></v-select>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    v-model="state.checkMilliseconds"
                    label="Health check milliseconds"
                  ></v-text-field>

                  <p
                    class="error-feedback mb-5"
                    v-if="v$.checkMilliseconds.$error"
                  >
                    {{ v$.checkMilliseconds.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    v-model="state.checkTargetMilliseconds"
                    label="Health check target milliseconds"
                  ></v-text-field>

                  <p
                    class="error-feedback mb-5"
                    v-if="v$.checkTargetMilliseconds.$error"
                  >
                    {{ v$.checkTargetMilliseconds.$errors[0].$message }}
                  </p>
                </v-col>
                <v-container class="mx-0 pt-1">
                  <v-radio-group v-model="state.inline" inline>
                    <v-row>
                      <v-col cols="6">
                        <v-radio label="test1" value="radio-1"></v-radio
                      ></v-col>
                      <v-col cols="6">
                        <v-radio label="test2" value="radio-2"></v-radio
                      ></v-col>
                    </v-row>
                  </v-radio-group>
                </v-container>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions class="actionBtn pt-0">
            <v-btn
              color="indigo-darken-3"
              :rounded="true"
              large
              rounded
              outlined
              label-color="#213E9F"
              variant="outlined"
              @click="closeModal"
              class="btn-add"
            >
              <span class="pr-3 pl-3" style="color: #213e9f"> Cancel</span>
            </v-btn>

            <v-btn
              large
              rounded
              outlined
              label-color="#213E9F"
              type="submit"
              color="indigo-darken-3"
              :rounded="true"
              variant="flat"
              class="btn-add"
            >
              <span class="text-white pr-3 pl-3">Create</span>
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
import axios from "axios";
import useValidate from "@vuelidate/core";
import { toRefs, ref, watch, onMounted, reactive, computed, inject } from "vue";
import { required, helpers, requiredIf } from "@vuelidate/validators";
export default {
  props: {
    isOpen: {
      type: Boolean,
      required: true,
    },
  },

  setup(props) {
    const emitter = inject("emitter");
    onMounted(() => {});

    const { isOpen } = toRefs(props);
    const listAlgo = ref([
      {
        name: "Failover",
        slug: "Failover",
      },
      {
        name: "Round-Robin",
        slug: "Round-Robin",
      },
      {
        name: "Source IP",
        slug: "Source IP",
      },
      {
        name: "Source-Destination IP",
        slug: "Source-Destination IP",
      },
      {
        name: "Best Quality",
        slug: "Best Quality",
      },
    ]);

    const numberList = ref(Array.from({ length: 32 }, (_, i) => i + 1));

    const state = reactive({
      inline: "",
      source: "",
      sourcePrefix: "",
      destination: "",
      destinationPrefix: "",
      area: "",
      algo: "",
      checkMilliseconds: "",
      checkTargetMilliseconds: "",
      snackbar: false,
      color: "",
      textAlert: "",
      openModal: false,
    });

    watch(
      () => isOpen.value,
      (val) => {
        state.openModal = val;
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

    const submitForm = async () => {
      const result = await v$.value.$validate();
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      if (result) {
        let payload = {};
        if (state.type.slug === "Create Private Key") {
          payload = {
            name: state.ruleName,
            encryption_algorithm: "RSA",
            key_size: state.key.slug,
          };

          axios
            .post("/key_pairs/createPrivateKey", payload)
            .then((response) => {
              console.log("response", response);
              if (response.status == "201") {
                state.openModal = false;
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
        } else if (state.type.slug === "create") {
          payload = {
            name: state.ruleName,
            method: {
              method_name: state.type?.slug,
              private_key: state.privateKey?.id,
              encryption_algorithm: "RSA",
            },
          };

          addPublicKey(payload);
        } else if (state.type.slug === "import") {
          payload = {
            name: state.ruleName,
            method: {
              method_name: state.type?.slug,
              public_key_value: state.checkMilliseconds,
            },
          };
          addPublicKey(payload);
        }
      } else {
        console.log("v$", v$.value);
      }
    };

    const closeModal = () => {
      emitter.emit("closeSdwanModalRule");
    };

    const rules = computed(() => {
      return {
        area: { required },
        algo: { required },
        checkTargetMilliseconds: { required },

        ruleName: {
          required,
          isValidruleName: helpers.withMessage(
            `Champs can include only letters & Numbers & underscores & hyphens without space.`,

            helpers.regex(/^[A-Za-z0-9_\-]+$/)
          ),
        },

        checkMilliseconds: {
          required: helpers.withMessage("Value is required", required),
        },
      };
    });

    const v$ = useValidate(rules, state);

    return {
      numberList,
      state,
      listAlgo,
      emitter,
      v$,
      closeModal,
      submitForm,
      getCookie,
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
  justify-content: end;
}
</style>
