<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm" style="overflow: auto">
        <v-card>
          <v-card-title>
            <span class="text-h5"> {{ $t("openvpn.Gateway") }}</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="`${$t('settings.DNSServer')} *`"
                    density="compact"
                    v-model="state.dns_server"
                  ></v-text-field>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.dns_server.$errors.length"
                  >
                    {{ v$.dns_server.$errors?.[0].$message }}
                  </p>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.gateway"
                    :label="`${$t('openvpn.Gateway')} *`"
                    density="compact"
                    item-title="address"
                    item-value="id"
                    return-object
                    :items="state.gatwayList"
                    background-color="#fffffff"
                    :no-data-text="$t('certificat.certificatlist')"
                  >
                  </v-select>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.gateway.$errors.length"
                  >
                    {{ v$.gateway.$errors?.[0].$message }}
                  </p>
                </v-col>
                <v-container class="mx-0 pt-1" v-if="state.gateway">
                  <v-radio-group
                    v-model="state.checkInterface"
                    inline
                    :return-object="true"
                  >
                    <v-row>
                      <v-col
                        cols="6"
                        v-for="inter in isCombo.info"
                        :key="isCombo.info.id"
                      >
                        <v-radio
                          :label="inter.name_interface"
                          :value="inter"
                        ></v-radio>
                      </v-col>
                      <p
                        class="error-feedback mb-5 ml-5"
                        v-if="v$.checkInterface.$error"
                      >
                        {{ v$.checkInterface.$errors[0].$message }}
                      </p>
                    </v-row>
                  </v-radio-group>
                </v-container>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions class="mt-3 actionBtn">
            <div class="text-start ml-6 mt-3">
              <span class="text-sm">
                <span class="text-red text-lg">*</span>
                {{ $t("errors.oblig") }}</span
              >
            </div>
            <v-spacer></v-spacer>
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
              <span class="pr-3 pl-3">{{ $t("buttons.close") }}</span>
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
              <span class="text-white pr-3 pl-3">{{ $t("buttons.Add") }}</span>
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
import { useI18n } from "vue-i18n";
import axios from "axios";
import useValidate from "@vuelidate/core";
import {
  toRefs,
  ref,
  watch,
  onMounted,
  reactive,
  computed,
  inject,
  watchEffect,
} from "vue";
import { required, helpers, requiredIf } from "@vuelidate/validators";
import { v4 as uuidv4 } from "uuid";

export default {
  props: {
    isOpen: {
      type: Boolean,
      required: true,
    },
    editRow: {
      type: Object,
      Array,
      required: false,
    },
    modalMode: {
      type: String,
      required: true,
    },
  },

  setup(props) {
    const { t } = useI18n();
    const emitter = inject("emitter");
    onMounted(() => {
      emitter.on("list-gateway", (data) => {
        state.rowList = data;
      });

      let gateway = document.getElementById("app").attributes["gateway"].value;
      const parsedArrayGateway = JSON.parse(gateway);

      let arr = parsedArrayGateway.map((e) => {
        return {
          address: e.gateway.address,
          id: e.gateway.id,
          info: e.info,
        };
      });
      state.gatwayList = arr;

      //  let array=[]
      //  parsedArrayGateway.forEach(element => {
      //   array.push(element.gateway)
      //  });
      //  state.gatwayList = array
    });

    const { isOpen, editRow, modalMode } = toRefs(props);

    const state = reactive({
      checkInterface: "",
      rowList: [],
      editValue: null,
      gatwayList: [],

      //
      dns_server: "",
      gateway: "",
    });

    const isCombo = computed(() => {
      return state.gateway;
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

    const populate = (data) => {
      if (modalMode.value === "edit") {
        let filtredGateway = state.gatwayList.filter(
          (i) => i.address === data.gateway
        );
        state.editValue = data.uuid;
        state.gateway = filtredGateway[0];
        state.dns_server = data.dns_server;
        state.checkInterface = state.gateway?.info[0];
      }
    };

    watch(
      () => modalMode.value,
      (val) => {
        if (val === "create") {
          state.dns_server = "";
          state.gateway = "";
        }
      }
    );

    const submitForm = async () => {
      const result = await v$.value.$validate();
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      if (result) {
        let payload = {
          uuid: modalMode.value === "create" ? uuidv4() : state.editValue,
          gateway: {
            address: state.gateway?.address,
            id: state.gateway?.id,
            info: state.checkInterface,
          },
          dns_server: state.dns_server,
        };

        if (modalMode.value === "create") {
          emitter.emit("add-gateway", payload);
        }

        if (modalMode.value === "edit") {
          emitter.emit("edit-gateway", payload);
        }

        closeModal();
        v$.value.$reset();
      } else {
        console.log("v$", v$.value);
      }
    };

    const closeModal = () => {
      emitter.emit("closeModalGateway");
      state.dns_server = "";
      state.gateway = "";
    };
    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const formaaddress = computed(() => {
      return t("errors.formatMustBeLikeAdresseIP");
    });
    const rules = computed(() => {
      return {
        dns_server: {
          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(
              () => modalMode.value === "edit" || modalMode.value === "create"
            )
          ),
          isValidDns_server: helpers.withMessage(
            formaaddress,

            helpers.regex(
              /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
            )
          ),
        },
        gateway: {
          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(
              () => modalMode.value === "edit" || modalMode.value === "create"
            )
          ),
        },
        checkInterface: {
          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(
              () =>
                state.gateway &&
                (modalMode.value === "edit" || modalMode.value === "create")
            )
          ),
        },
      };
    });

    const v$ = useValidate(rules, state);

    return {
      state,
      isCombo,
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
  color: red !important;
  font-size: 0.85em;
}
.actionBtn {
  justify-content: center;
}
</style>
