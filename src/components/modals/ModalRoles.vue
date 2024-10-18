<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm" class="scroller">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              {{ $t("addRole") }}</span
            >
            <span class="headline" v-if="modalMode === 'edit'">
              {{ $t("editRole") }}</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    v-model="state.roles"
                    :label="$t('agGrid.name')"
                  ></v-text-field>

                  <p class="error-feedback mb-5" v-if="v$.roles.$error">
                    {{ v$.roles.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.privileges"
                    :label="$t('priveleges')"
                    item-title="fonctionalities"
                    item-value="id"
                    :items="state.listPrivileges"
                    multiple
                    clearable
                    return-object
                  ></v-select>

                  <p class="error-feedback mb-5" v-if="v$.privileges.$error">
                    {{ v$.privileges.$errors[0].$message }}
                  </p>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>

          <v-card-actions class="mt-3 actionBtnServer">
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
              <span class="pr-3 pl-3 text-white" style="color: #213e9f">{{
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
              <span class="text-white pr-3 pl-3">{{
                modalMode === "create"
                  ? $t("buttons.create")
                  : $t("buttons.update")
              }}</span>
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
    const { t } = useI18n();
    const emitter = inject("emitter");
    const { isOpen, editRow, modalMode } = toRefs(props);

    const state = reactive({
      id: null,
      roles: "",
      privileges: "",
      listPrivileges: [],
    });

    onMounted(() => {
      let allRolesPr =
        document.getElementById("app").attributes["servers"].value;
      const parsedArr = JSON.parse(allRolesPr);
      state.listPrivileges = parsedArr;
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
          state.roles = "";
          state.privileges = "";
        }
      }
    );
    const populate = (data) => {
      if (modalMode.value === "edit") {
        console.log('daatta',data)
        state.id = data.id;
        state.roles = "";
        state.privileges = "";
      }
    };

    const closeModal = () => {
      v$.value.$reset();
      emitter.emit("closeModalRoles");
      if (modalMode.value === "create") {
        state.roles = "";
        state.privileges = "";
      }
    };

    const submitForm = async () => {
      const result = await v$.value.$validate();
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      if (result) {
        let payload = {
          name: state.roles,
          fonctionalities: state.privileges,
        };
        console.log("payload", payload);
        if (modalMode.value === "edit") {
          axios
            .put(`/users/modifyRole/${state.id}`, payload)
            .then((response) => {
              if (response.status == "200") {
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.msg;
                // setTimeout(() => {
                //   location.reload();
                // }, 1000);
              }
            })
            .catch((i) => {
              state.snackbar = true;
              state.color = "red";
              state.textAlert = i.response.data.msg;
            });
        } else {
          axios
            .post("/users/createRole", payload)
            .then((response) => {
              if (response.status == "200") {
                state.openModal = false;
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.msg;
                // setTimeout(() => {
                //   location.reload();
                // }, 1000);
              }
            })
            .catch((i) => {
              state.snackbar = true;
              state.color = "red";
              state.textAlert = i.response.data.msg;
            });
        }
      } else {
        console.log("v$", v$.value);
      }
    };

    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const rules = computed(() => {
      return {
        roles: { required: helpers.withMessage(error, required) },
        privileges: { required: helpers.withMessage(error, required) },
      };
    });

    const v$ = useValidate(rules, state);

    return {
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
.actionBtnServer {
  justify-content: end;
  display: flex;
}
.scroller {
  overflow: auto;
}
</style>
