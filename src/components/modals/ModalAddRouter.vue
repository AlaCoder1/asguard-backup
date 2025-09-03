<template>
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
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              {{ $t("ztna.addRelay") }}</span
            >
            <span class="headline" v-if="modalMode === 'edit'">
              {{ $t("ztna.updateRelay") }}</span
            >
          </v-card-title>

          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    id="RouterName"
                    v-model="RouterName"
                    :placeholder="$t('ztna.relayName')"
                    :rules="rulesName"
                    persistent-placeholder
                  />
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    id="RouterAttribute"
                    v-model="RouterAttribute"
                    :placeholder="$t('ztna.relayAttribute')"
                    :rules="rulesatt"
                    persistent-placeholder
                  />
                </v-col>
                <v-col cols="12">
                  <v-text-field
                    id="Description"
                    v-model="Description"
                    placeholder="Description"
                    persistent-placeholder
                  />
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="indigo-darken-3"
              :rounded="true"
              large
              rounded
              outlined
              label-color="#213E9F"
              variant="flat"
              class="mt-3 btn-add"
              text
              @click="cancel"
              ><span class="text-white pr-3 pl-3">
                {{ $t("buttons.close") }}</span
              ></v-btn
            >
            <v-btn
              large
              rounded
              outlined
              label-color="#213E9F"
              color="indigo-darken-3"
              :rounded="true"
              variant="flat"
              class="mt-3 ml-2 btn-add"
              type="submit"
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
import { getCookie } from "@/mixins/csrftoken.js";
import axios from "axios";
import { toRefs, ref, watch, reactive, inject, onMounted } from "vue";
import { useI18n } from "vue-i18n";

export default {
  props: {
    isOpen: {
      type: Boolean,
      required: true,
    },
    modalMode: {
      required: true,
    },
    editRow: {
      type: Object,
      Array,
      required: true,
    },
  },

  setup(props) {
    const { t } = useI18n();
    const RouterId = ref("");
    const RouterName = ref("");
    const RouterAttribute = ref("");
    const Description = ref("");
    const Relays = ref([]);
    const Tunneler = ref(true);
    const Traversal = ref(false);
    const rules = [(value) => !!value || "You must enter a value."];
    const emitter = inject("emitter");

    const { isOpen, editRow, modalMode } = toRefs(props);
    const rulesName = [
      (value) => {
        if (!value) return t("ztna.enterValue");
        if (existingName(value)) return t("ztna.nameExist");
        if (inValidRelay(value)) return t("ztna.namerelay");
        return true;
      },
    ];
    const rulesatt = [
      (value) => {
        if (!value) return t("ztna.enterValue");
        return ValidName(value) ? true : t("ztna.validName");
      },
    ];

    function existingName(value) {
      const existingIdentity = Relays.value.find(
        (identity) => identity.name === value
      );

      if (existingIdentity) {
        return true;
      }

      return false;
    }

    function ValidName(value) {
      const hostnamePattern =
        /^(?=.*[a-zA-Z])[a-zA-Z0-9-\s]{1,63}(\.[a-zA-Z0-9-\s]{1,63})*$/;

      if (hostnamePattern.test(value) && !/^\d+$/.test(value)) {
        return true;
      }

      return false;
    }
    function inValidRelay(value) {
      const hostnamePattern = /^[a-zA-Z0-9_]+\.relay$/;
      // Check if the value matches the hostname pattern and is not entirely numeric
      if (hostnamePattern.test(value) && !/^\d+$/.test(value)) {
        return false;
      }

      return true;
    }

    const state = reactive({
      loading: false,
      isLoadingDialogue: false,
      openModal: false,
      snackbar: false,
      color: null,
      textAlert: "",
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
          RouterName.value = "";
          RouterAttribute.value = "";
          Description.value = "";
          Traversal.value = false;
        }
      }
    );
    const populate = (data) => {
      if (modalMode.value === "edit") {
        RouterId.value = data.id;
        RouterName.value = data.name;
        RouterAttribute.value = data.attribute_relay;
        Traversal.value = data.traversal;
        Description.value = data.description;
      }
    };
    const fetchRelays = async () => {
      try {
        const RelaysString = await document
          .getElementById("app")
          .getAttribute("routers");
        const RelaysObject = JSON.parse(RelaysString);

        const RelaysArray = Array.isArray(RelaysObject) ? RelaysObject : [];

        Relays.value = RelaysArray.map((identity) => ({ name: identity.name }));
      } catch (error) {
        Relays.value = [];
      }
    };

    onMounted(() => {
      fetchRelays();
    });

    const submitForm = async () => {
      const isFieldValid = rulesName.every(
        (rule) => rule(RouterName.value) === true
      );
      const isattValid = rulesatt.every(
        (rule) => rule(RouterAttribute.value) === true
      );
      console.log('isFieldValid',isFieldValid)
      console.log('isattValid',isattValid)
      
      if ((isFieldValid && isattValid)) {
        const csrfToken = getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

        if (Traversal.value === "Traversal") {
          Traversal.value = true;
        }

        let payload = {
          name: RouterName.value,
          noTraversal: Traversal.value,
          isTunnelerEnabled: Tunneler.value,
          roleAttributes: [RouterAttribute.value],
          Description: Description.value,
        };

        let token = document.getElementById("app").getAttribute("token");

        state.loading = true;
        state.isLoadingDialogue = true;
        if (modalMode.value === "edit") {
          axios
            .put(`/ztna/update_routers/${RouterId.value}`, payload, {
              headers: {
                "zt-session": token,
                "Content-Type": "application/json",
              },
            })
            .then((response) => {
              if (response.status == "200") {
                state.snackbar = true;
                state.color = "success";
                state.textAlert = t("ztna.routerUpdated");
                setTimeout(() => {
                  location.reload();
                }, 1000);
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
                state.textAlert = t(i.response.data.error);
              }
            });
        } else {
          axios
            .post("/ztna/add_routers", payload, {
              headers: {
                "zt-session": token,
                "Content-Type": "application/json",
              },
            })
            .then((response) => {
              if (response.status == "200") {
                state.snackbar = true;
                state.color = "success";
                state.textAlert = t("ztna.routerCreated");
                setTimeout(() => {
                  location.reload();
                }, 1000);
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
                state.textAlert = t(i.response.data.error);
              }
            });
        }
      } else {
        state.snackbar = true;
        state.color = "red";
        state.textAlert = t("ztna.missingFields");
      }
    };

    const cancel = () => {
      RouterName.value = "";
      RouterAttribute.value = "";
      Description.value = "";
      Tunneler.value = false;
      Traversal.value = false;
      emitter.emit("closeRouterModal");
    };

    return {
      state,
      cancel,
      emitter,
      RouterName,
      RouterAttribute,
      Description,
      Tunneler,
      Traversal,
      rules,
      submitForm,
      rulesName,
      rulesatt,
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

.red-asterisk {
  color: rgb(147, 3, 3);
  font-size: 1.6em;
}
</style>
