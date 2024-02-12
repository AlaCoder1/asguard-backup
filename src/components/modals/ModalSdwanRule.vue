<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm" class="scroller">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              Create New Rule</span
            >
            <span class="headline" v-if="modalMode === 'edit'">
              Update Rule</span
            >
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
                  <p class="error-feedback mb-5" v-if="v$.source.$error">
                    {{ v$.source.$errors[0].$message }}
                  </p>
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
                  <p class="error-feedback mb-5" v-if="v$.sourcePrefix.$error">
                    {{ v$.sourcePrefix.$errors[0].$message }}
                  </p>
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
                <template v-if="state.algo.slug != 'failover'">
                  <v-col cols="12" class="mb-n6">
                    <v-select
                      v-model="state.area"
                      label="Area"
                      item-title="name"
                      item-value="slug"
                      :items="state.mapeArea"
                      return-object
                    ></v-select>
                    <p class="error-feedback mb-5" v-if="v$.area.$error">
                      {{ v$.area.$errors[0].$message }}
                    </p>
                  </v-col>
                </template>
                <template v-else>
                  <v-col cols="12" class="mb-n6">
                    <v-select
                      v-model="state.area"
                      label="Area"
                      item-title="name"
                      item-value="slug"
                      :items="state.KlonaArea"
                      return-object
                    ></v-select>
                    <p class="error-feedback mb-5" v-if="v$.area.$error">
                      {{ v$.area.$errors[0].$message }}
                    </p>
                  </v-col>
                </template>

                <template v-if="false">
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
                </template>

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
                <v-container
                  class="mx-0 pt-1"
                  v-if="state.algo.slug === 'failover'"
                >
                  <v-radio-group v-model="state.checkInterface" inline>
                    <v-row>
                      <v-col
                        cols="6"
                        v-for="area in isCombo.members"
                        :key="isCombo.id"
                      >
                        <v-radio :label="area" :value="area"></v-radio>
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
    onMounted(() => {
      let allArea = document.getElementById("app").attributes["allArea"].value;
      let parsedArray = JSON.parse(allArea);

      let mapedArea = parsedArray.map((element) => {
        return {
          id: element.id,
          name: element.name,
          members: element.members.map((i) => {
            return i;
          }),
        };
      });
      state.mapeArea = mapedArea;
      state.KlonaArea = mapedArea.filter((i) => i.members.length == 2);
    });

    const { isOpen, editRow, modalMode } = toRefs(props);
    const listAlgo = ref([
      {
        name: "Failover",
        slug: "failover",
      },
      {
        name: "Round-Robin",
        slug: "round_robin",
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
      id: null,
      mapeArea: [],
      KlonaArea: [],

      snackbar: false,
      color: "",
      textAlert: "",
      openModal: false,

      ruleName: "",
      checkInterface: "",
      source: "",
      sourcePrefix: 32,
      destination: "",
      destinationPrefix: "",
      area: "",
      algo: "",
      checkMilliseconds: "",
      checkTargetMilliseconds: "8.8.8.8",
    });

    watch(
      () => isOpen.value,
      (val) => {
        state.openModal = val;
      }
    );

    watch(
      state,
      () => {
        if (state.algo.slug === "failover") {
          if (state.area && state.area.members.length > 2) state.area = "";
        }
      },
      { immediate: true }
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
          state.ruleName = "";
          state.checkInterface = "";
          state.source = "";
          state.sourcePrefix = 32;
          state.destination = "";
          state.destinationPrefix = "";
          state.area = "";
          state.algo = "";
          state.checkMilliseconds = "";
          state.checkTargetMilliseconds = "8.8.8.8";
        }
      }
    );
    const populate = (data) => {
      if (modalMode.value === "edit") {
        state.id = data.id;
        let resultSource = data?.source_address?.split("/");
        if (resultSource) {
          resultSource[1] = parseInt(resultSource[1], 10);
        }

        let filtredArea = state.mapeArea.filter((i) => i.id === data?.area);
        let filtredAlgo = listAlgo.value.filter(
          (i) => i.slug === data?.algorythme_type
        );

        state.ruleName = data.name;
        state.checkInterface = data?.primary_interface
          ? data?.primary_interface
          : "";
        state.source = resultSource ? resultSource[0] : "";
        state.sourcePrefix = resultSource ? resultSource[1] : "";
        state.area = filtredArea[0];
        state.algo = filtredAlgo[0];
        state.checkMilliseconds = data.health_check;
        state.checkTargetMilliseconds = data.health_check_target;
      }
    };

    const isCombo = computed(() => {
      return state.algo.slug === "failover" && state.area;
    });

    const submitForm = async () => {
      const result = await v$.value.$validate();
      if (result) {
        const csrfToken = getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

        let payload = {
          name: state.ruleName,
          source_address: `${state.source}/${state.sourcePrefix}`,
          area: state.area.id,
          algorythme_type: state.algo.slug,
          health_check: state.checkMilliseconds,
          health_check_target: state.checkTargetMilliseconds,
        };

        if (state.algo.slug === "failover") {
          payload = { ...payload, primary_interface: state.checkInterface };
        }

        if (modalMode.value === "edit") {
          axios
            .put(`/sdwan/updateSdwanRule/${state.id}`, payload)
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
            .post("/sdwan/createSdwanRule", payload)
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

    const closeModal = () => {
      emitter.emit("closeSdwanModalRule");

      if (modalMode.value === "create") {
        state.ruleName = "";
        state.checkInterface = "";
        state.source = "";
        state.sourcePrefix = 32;
        state.destination = "";
        state.destinationPrefix = "";
        state.area = "";
        state.algo = "";
        state.checkMilliseconds = "";
        state.checkTargetMilliseconds = "8.8.8.8";
      }
    };

    const rules = computed(() => {
      return {
        area: { required },
        algo: { required },

        checkInterface: {
          requiredIfFuction: helpers.withMessage(
            "Value is required",
            requiredIf(() => state.algo.slug === "failover")
          ),
        },

        checkTargetMilliseconds: {
          required,
          isValidCheckTargetMilliseconds: helpers.withMessage(
            `Format must be like adresse IP : X.X.X.X`,

            helpers.regex(/^(\d{1,3}\.){3}\d{1,3}$/)
          ),
        },

        ruleName: {
          required,
          isValidruleName: helpers.withMessage(
            `Champs can include only letters & Numbers & underscores & hyphens without space.`,

            helpers.regex(/^[A-Za-z0-9_\-]+$/)
          ),
        },

        source: {
          required,
          isValidSource: helpers.withMessage(
            `Format must be like adresse IP : X.X.X.X`,

            helpers.regex(/^(\d{1,3}\.){3}\d{1,3}$/)
          ),
        },

        sourcePrefix: { required },

        checkMilliseconds: {
          required,
          isValidlifeTime: helpers.withMessage(
            `champs can include only Numbers.`,

            helpers.regex(/^[0-9]+$/)
          ),
        },
      };
    });

    const v$ = useValidate(rules, state);

    return {
      isCombo,
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
.scroller {
  overflow: auto;
}
</style>
