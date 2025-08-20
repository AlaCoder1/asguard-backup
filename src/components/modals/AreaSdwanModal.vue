<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm" class="scroller">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              {{ $t("sdwan.createNewArea") }}</span
            >
            <span class="headline" v-if="modalMode === 'edit'">
              {{ $t("sdwan.updateArea") }}</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="`${$t('sdwan.enterAreaName')} *`"
                    v-model="state.areaName"
                  ></v-text-field>
                  <p class="error-feedback mb-5" v-if="v$.areaName.$error">
                    {{ v$.areaName.$errors[0].$message }}
                  </p>
                </v-col>
              </v-row>

              <v-row class="mt-3">
                <v-col>
                  <v-select
                    v-model="state.interfaces"
                    :label="$t('sdwan.listWAN')"
                    item-title="name"
                    item-value="id"
                    multiple
                    clearable
                    return-object
                    :items="state.mapedInterface"
                  ></v-select>

                  <p class="error-feedback mb-5" v-if="v$.interfaces.$error">
                    {{ v$.interfaces.$errors[0].$message }}
                  </p>
                  <p
                    class="error-feedback mb-5"
                    v-if="state.interfaces.length && !isMoreThanTwo"
                  >
                    {{ $t("sdwan.minimumTwoInterfaces") }}
                  </p>
                </v-col>
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
            <span></span>
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
              <span class="pr-3 pl-3" style="color: #213e9f">{{
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
import { useI18n } from "vue-i18n";
import axios from "axios";
import useValidate from "@vuelidate/core";
import { toRefs, watch, reactive, computed, inject, onMounted } from "vue";
import { required, helpers } from "@vuelidate/validators";
import { getCookie } from "@/mixins/csrftoken.js";

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
    const emitter = inject("emitter");
    const { t } = useI18n();
    const { isOpen, editRow, modalMode } = toRefs(props);

    const state = reactive({
      id: null,
      interfaces: [],
      openModal: false,
      snackbar: false,
      color: "",
      textAlert: "",
      mapedInterface: [],
      areaName: "",
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
          state.areaName = "";
          state.interfaces = [];
        }
      }
    );
    const populate = (data) => {
      if (modalMode.value === "edit") {
        state.areaName = data.name;
        state.id = data.id;

        let filtredInterface = [];
        data?.members.forEach((e) => {
          filtredInterface = [
            ...filtredInterface,
            ...state.mapedInterface.filter((i) => i.name === e),
          ];
        });
        state.interfaces = filtredInterface;
      }
    };

    const getInterface = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/network/AllInterfaces").then(
        (response) => {
          let filtredInterface = response.data.filter(
            (i) =>
              !i.ifname.startsWith("tun_") &&
              !i.ifname.startsWith("tap_") &&
              !i.name_interface.startsWith("VXLAN") &&
              !i.name_interface.startsWith("VLAN") &&
              !i.name_interface.startsWith("vlan") &&
              !i.name_interface.startsWith("vxlan")
          );

          let interfaces = filtredInterface.map((i) => {
            return {
              id: i.id,
              name: i.name_interface,
            };
          });

          state.mapedInterface = interfaces;
        },
      );
    };

    const closeModal = () => {
      emitter.emit("closeSdwanAreaModal");

      if (modalMode.value === "create") {
        state.areaName = "";
        state.interfaces = [];
      }
    };

    const submitForm = async () => {
      const result = await v$.value.$validate();
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      if (result && isMoreThanTwo.value) {
        let nameInterface = state.interfaces.map((e) => e.id);

        let payload = {
          name: state.areaName,
          members: nameInterface,
        };
        if (modalMode.value === "edit") {
          axios
            .put(`/sdwan/updateArea/${state.id}`, payload)
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
            .post("/sdwan/createArea", payload)
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
        console.log("error :", v$.value);
      }
    };

    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const indication = computed(() => {
      return t("champs.indication");
    });
    const rules = computed(() => {
      return {
        interfaces: {
          required: helpers.withMessage(error, required),
          isMoreThanTwo,
        },
        areaName: {
          required: helpers.withMessage(error, required),
          isValidkeyName: helpers.withMessage(
            indication,
            helpers.regex(/^[A-Za-z0-9_\-]+$/)
          ),
        },
      };
    });

    const isMoreThanTwo = computed(() => {
      return state.interfaces.length >= 2 ? true : false;
    });

    const v$ = useValidate(rules, state);

    return {
      isMoreThanTwo,
      state,
      v$,
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
