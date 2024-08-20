<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm" class="scroller">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
             {{$t("nat.create_msg_one") }}</span
            >
            <span class="headline" v-if="modalMode === 'edit'">
              {{$t("nat.update_msg_one")}}</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.interface"
                    :label="$t('nat.interface')"
                    :no-data-text="$t('nat.msg_no_data')"
                    item-title="name"
                    item-value="id"
                    :items="state.mapedInterface"
                    clearable
                    return-object
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.interface.$error">
                    {{ v$.interface.$errors[0].$message }}
                  </p>
                </v-col>

                <v-col cols="7" class="mb-n6">
                  <v-text-field
                  :label="$t('nat.ent_saddr')"
                    v-model="state.sourceAddress"
                  ></v-text-field>
                  <p class="error-feedback mb-5" v-if="v$.sourceAddress.$error">
                    {{ v$.sourceAddress.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="1" class="mb-n6">
                  <div class="ml-1 mt-5">/</div>
                </v-col>
                <v-col cols="4" class="mb-n6">
                  <v-select
                  :label="$t('nat.prefix')"
                    v-model="state.sourcePrefix"
                    :no-data-text="$t('nat.msg_no_data')"
                    :items="numberList"
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.sourcePrefix.$error">
                    {{ v$.sourcePrefix.$errors[0].$message }}
                  </p>
                </v-col>

                <v-col cols="7" class="mb-n6">
                  <v-text-field
                    :label="$t('nat.ent_tran_add')"
                    v-model="state.translationAddress"
                  ></v-text-field>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.translationAddress.$error"
                  >
                    {{ v$.translationAddress.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="1" class="mb-n6">
                  <div class="ml-1 mt-5">/</div>
                </v-col>
                <v-col cols="4" class="mb-n6">
                  <v-select
                    :label="$t('nat.prefix')"
                    v-model="state.translationPrefix"
                    :no-data-text="$t('nat.msg_no_data')"
                    :items="numberList"
                  ></v-select>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.translationPrefix.$error"
                  >
                    {{ v$.translationPrefix.$errors[0].$message }}
                  </p>
                </v-col>

                <v-col cols="7" class="mb-n6">
                  <v-text-field
                  :label="$t('nat.ent_daddr')"
                    v-model="state.destinationAddress"
                  ></v-text-field>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.destinationAddress.$error"
                  >
                    {{ v$.destinationAddress.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="1" class="mb-n6">
                  <div class="ml-1 mt-5">/</div>
                </v-col>
                <v-col cols="4" class="mb-n6">
                  <v-select
                  :label="$t('nat.prefix')"
                    v-model="state.destinationAddressPrefix"
                    :no-data-text="$t('nat.msg_no_data')"
                    :items="numberList"
                    clearable
                  ></v-select>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.destinationAddressPrefix.$error"
                  >
                    {{ v$.destinationAddressPrefix.$errors[0].$message }}
                  </p>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-text-field
                  :label="$t('nat.description')"
                    v-model="state.description"
                  ></v-text-field>
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
              variant="outlined"
              @click="closeModal"
              class="mt-3 btn-add"
            >
            <span class="pr-3 pl-3" style="color: #213e9f">{{$t("firewall.cancel")}}</span>
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
import axios from "axios";
import useValidate from "@vuelidate/core";
import { toRefs, watch, reactive, computed, inject, onMounted, ref } from "vue";
import { required, helpers, requiredIf } from "@vuelidate/validators";
import { getCookie } from "@/mixins/csrftoken.js";
import { useI18n } from "vue-i18n";

export default {
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
    const { t } = useI18n();
    const emitter = inject("emitter");
    const { isOpen, editRow, modalMode } = toRefs(props);
    const numberList = ref(Array.from({ length: 32 }, (_, i) => i + 1));

    const state = reactive({
      //list
      isCombo: ["Lan", "Wan"],
      //
      id: null,
      interface: "",
      sourceAddress: "",
      sourcePrefix: "",
      destinationAddress: "",
      translationAddress: "",
      destinationAddressPrefix: "",
      translationPrefix: "",
      description: "",
    });

    onMounted(() => {
      getInterface();
    });

    watch(
      () => isOpen.value,
      (val) => {
        state.openModal = val;
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
      () => {
        if (modalMode.value === "create") {
          state.interface = "";
          state.sourceAddress = "";
          state.sourcePrefix = "";
          state.destinationAddress = "";
          state.translationAddress = "";
          state.destinationAddressPrefix = "";
          state.translationPrefix = "";
          state.description = "";
        }
      }
    );
    const populate = (data) => {
      if (modalMode.value === "edit") {
        state.id = data.id;

        let filtredInterface = state.mapedInterface.filter(
          (i) => i.id === data?.interface
        );

        state.interface = filtredInterface[0];

        let resultSource = data?.source_address
          ? data?.source_address?.split("/")
          : "";
        if (resultSource) {
          resultSource[1] = parseInt(resultSource[1], 10);
        }
        state.sourceAddress = resultSource ? resultSource[0] : "";
        state.sourcePrefix = resultSource ? resultSource[1] : "";
      }

      let resultDestination = data?.destination_address
        ? data?.destination_address?.split("/")
        : "";
      if (resultDestination) {
        resultDestination[1] = parseInt(resultDestination[1], 10);
      }
      state.destinationAddress = resultDestination ? resultDestination[0] : "";
      state.destinationAddressPrefix = resultDestination
        ? resultDestination[1]
        : "";

      let resultTranslation = data?.translation_address
        ? data?.translation_address?.split("/")
        : "";
      if (resultTranslation) {
        resultTranslation[1] = parseInt(resultTranslation[1], 10);
      }
      state.translationAddress = resultTranslation ? resultTranslation[0] : "";
      state.translationPrefix = resultTranslation ? resultTranslation[1] : "";
      state.description = data.description;
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

          state.mapedInterface = interfaces;
        },
        (error) => {
          console.log(error);
        }
      );
    };

    const closeModal = () => {
      emitter.emit("closeOneModal");
      if (modalMode.value === "create") {
        state.interface = "";
        state.sourceAddress = "";
        state.sourcePrefix = "";
        state.destinationAddress = "";
        state.translationAddress = "";
        state.destinationAddressPrefix = "";
        state.translationPrefix = "";
        state.description = "";
      }
    };

    const submitForm = async () => {
      const result = await v$.value.$validate();
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      if (result) {
        let payload = {
          interface: state.interface.id,
          source_address: `${state.sourceAddress}/${state.sourcePrefix}`,
          translation_address: `${state.translationAddress}/${state.translationPrefix}`,
          destination_address: state.destinationAddress
            ? `${state.destinationAddress}/${state.destinationAddressPrefix}`
            : "",
          description: state.description,
        };

        if (modalMode.value === "edit") {
          axios
            .put(`/nat/updateOneToOneNat/${state.id}`, payload)
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
              state.textAlert = i.response.data.response;
            });
        } else {
          axios
            .post("/nat/createOneToOneNat", payload)
            .then((response) => {
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
        }
      } else {
        console.log("v$", v$.value);
      }
    };
    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const formaaddress = computed(() => {
      return t("errors.formatMustBeLikeAdresseIP");
    });
    const onlynumbers = computed(() => {
      return t("errors.ChampIncludeOnlyNumbers");
    });

    const rules = computed(() => {
      return {
        interface: {required: helpers.withMessage(error, required) },
        sourceAddress: {
          required: helpers.withMessage(error, required),
          isValidSourceAddress: helpers.withMessage(
            formaaddress,

            helpers.regex(/^(\d{1,3}\.){3}\d{1,3}$/)
          ),
        },
        translationAddress: {
          required: helpers.withMessage(error, required),
          isValidSourceAddress: helpers.withMessage(
            formaaddress,

            helpers.regex(/^(\d{1,3}\.){3}\d{1,3}$/)
          ),
        },
        destinationAddress: {
          isValidSourceAddress: helpers.withMessage(
            formaaddress,

            helpers.regex(/^(\d{1,3}\.){3}\d{1,3}$/)
          ),
        },
        sourcePrefix: {
          required: helpers.withMessage(error, required),
        },
        translationPrefix: {
          required: helpers.withMessage(error, required),
        },

        destinationAddressPrefix: {
          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(() => state.destinationAddress)
          ),
        },
      };
    });

    const v$ = useValidate(rules, state);

    return {
      state,
      v$,
      numberList,
      emitter,
      submitForm,
      closeModal,
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
