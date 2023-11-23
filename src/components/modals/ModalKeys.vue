<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="text-h5"> Create new Key</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Enter Key Name"
                    v-model="state.keyName"
                  ></v-text-field>
                  <p class="error-feedback mb-5" v-if="v$.keyName.$error">
                    {{ v$.keyName.$errors[0].$message }}
                  </p>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.type"
                    label="Select Type"
                    item-title="name"
                    item-value="slug"
                    :items="listType"
                    return-object
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.type.$error">
                    {{ v$.type.$errors[0].$message }}
                  </p>
                </v-col>
                <template v-if="isPrivate">
                  <v-col cols="6" class="mb-n6">
                    <v-text-field
                      model-value="RSA algorithm"
                      readonly
                    ></v-text-field>
                  </v-col>
                  <v-col cols="6" class="mb-n6">
                    <v-select
                      v-model="state.key"
                      label="Key Length"
                      item-title="name"
                      item-value="slug"
                      :items="listKey"
                      return-object
                    ></v-select>
                    <p class="error-feedback mb-5" v-if="v$.key.$error">
                      {{ v$.key.$errors[0].$message }}
                    </p>
                  </v-col>
                </template>

                <v-col cols="12" class="mb-n6" v-if="isPublic">
                  <v-select
                    v-model="state.privateKey"
                    label="Select Private Key"
                    item-title="name"
                    item-value="id"
                    :items="state.mapedListKeyPrivate"
                    return-object
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.privateKey.$error">
                    {{ v$.privateKey.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6" v-if="isImport">
                  <v-textarea
                    v-model="state.externKey"
                    label="Enter Extern Key"
                    variant="outlined"
                  ></v-textarea>
                  <p class="error-feedback mb-5" v-if="v$.externKey.$error">
                    {{ v$.externKey.$errors[0].$message }}
                  </p>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions class="mt-3 actionBtn">
            <v-btn
              color="indigo-darken-3"
              :rounded="true"
              large
              rounded
              outlined
              label-color="#213E9F"
              variant="flat"
              @click="closeModal"
              class="mt-3 btn-add"
            >
              <span class="text-white pr-3 pl-3">Close</span>
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
              class="mt-3 btn-add"
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
import { toRefs, ref, watch, onMounted, reactive, computed } from "vue";
import { required, helpers, requiredIf } from "@vuelidate/validators";
export default {
  props: {
    isOpen: {
      type: Boolean,
      required: true,
    },
  },

  setup(props) {
    onMounted(() => {
      let privateKeyAttribute =
        document.getElementById("app").attributes["privateKey"].value;
      console.log("privateKeyAttribute", privateKeyAttribute);

      const validJsonString = privateKeyAttribute
        .replace(/'/g, '"')
        .replace(/True/g, "true")
        .replace(/False/g, "false")
        .replace(/None/g, "null");
      const parsedArray = JSON.parse(validJsonString);

      let mapedPrivateKey = parsedArray.map((i) => {
        return {
          id: i.id,
          name: i.name,
        };
      });
      state.mapedListKeyPrivate = mapedPrivateKey;
    });

    const { isOpen } = toRefs(props);
    const listType = ref([
      {
        name: "Create Private Key",
        slug: "Create Private Key",
      },
      {
        name: "Create Public Key",
        slug: "create",
      },
      {
        name: "Import Public Key",
        slug: "import",
      },
    ]);
    const listKey = ref([
      {
        name: "2048",
        slug: "2048",
      },
      {
        name: "4096",
        slug: "4096",
      },
      {
        name: " 8192",
        slug: " 8192",
      },
    ]);

    const state = reactive({
      snackbar: false,
      color: "",
      textAlert: "",
      mapedListKeyPrivate: [],
      openModal: false,
      type: {
        name: "Create Private Key",
        slug: "Create Private Key",
      },
      keyName: null,
      key: {
        name: "2048",
        slug: "2048",
      },
      privateKey: null,
      externKey: null,
    });

    watch(
      () => isOpen.value,
      () => {
        state.openModal = true;
      }
    );

    const isPrivate = computed(() => {
      return state.type.slug === "Create Private Key";
    });
    const isPublic = computed(() => {
      return state.type.slug === "create";
    });
    const isImport = computed(() => {
      return state.type.slug === "import";
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

    const submitForm = async () => {
      console.log("state", state);
      const result = await v$.value.$validate();
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      if (result) {
        let payload = {};
        if (state.type.slug === "Create Private Key") {
          payload = {
            name: state.keyName,
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
            name: state.keyName,
            method: {
              method_name: state.type?.slug,
              private_key: state.privateKey?.id,
              encryption_algorithm: "RSA",
            },
          };
        } else if (state.type.slug === "import") {
          payload = {
            name: state.keyName,
            method: {
              method_name: state.type?.slug,
              public_key_value: state.externKey,
            },
          };
        }
        axios
          .post("/key_pairs/createPublicKey", payload)
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
      } else {
        console.log("v$", v$.value);
      }
    };

    const closeModal = () => {
      state.openModal = false;
      location.reload();
    };

    const rules = computed(() => {
      return {
        type: { required },

        keyName: {
          required,
          isValidkeyName: helpers.withMessage(
            `Champs can include only letters & Numbers & underscores & hyphens without space.`,

            helpers.regex(/^[A-Za-z0-9_\-]+$/)
          ),
        },

        key: {
          requiredIfFuction: helpers.withMessage(
            "This field must be indicated",
            requiredIf(() => state.type.slug === "Create Private Key")
          ),
        },
        privateKey: {
          requiredIfFuction: helpers.withMessage(
            "This field must be indicated",
            requiredIf(() => state.type.slug === "create")
          ),
        },

        externKey: {
          requiredIfFuction: helpers.withMessage(
            "This field must be indicated",
            requiredIf(() => state.type.slug === "import")
          ),
        },
      };
    });

    const v$ = useValidate(rules, state);

    watch(isPrivate, () => {
      v$.value.$reset();
    });
    watch(isPublic, () => {
      v$.value.$reset();
    });
    watch(isImport, () => {
      v$.value.$reset();
    });

    return {
      state,
      listType,
      listKey,
      isPrivate,
      isPublic,
      isImport,
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
  justify-content: center;
}
</style>
