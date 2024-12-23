<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              {{ $t("ztna.createNewIdentity") }}</span
            >
            <span class="headline" v-if="modalMode === 'edit'">
              {{ $t("ztna.updateIdentity") }}</span
            >
          </v-card-title>

          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    id="IdentityName"
                    v-model="IdentityName"
                    :placeholder="$t('ztna.identityName')"
                    :rules="rulesName"
                    persistent-placeholder
                  />
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    id="IdentityAttribute"
                    v-model="IdentityAttribute"
                    :placeholder="$t('ztna.identityAttribute')"
                    :rules="rulesName"
                    persistent-placeholder
                  />
                </v-col>
                <v-col cols="12">
                  <div class="d-flex align-center">
                    <label class="ml-1" for="Type">{{$t('ztna.osType')}}</label>
                    <div class="ml-5 mt-1">
                      <v-menu open-on-hover>
                        <template v-slot:activator="{ props }">
                          <v-btn color="#FAFAFA" v-bind="props">
                            {{ selectedOs }}
                          </v-btn>
                        </template>
                        <v-list>
                          <v-list-item
                            v-for="(item, index) in OS"
                            :key="index"
                            @click="selectOs(item)"
                          >
                            <v-list-item-title>{{
                              item.title
                            }}</v-list-item-title>
                          </v-list-item>
                        </v-list>
                      </v-menu>
                    </div>
                  </div>
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
            >
              <span class="text-white pr-3 pl-3">
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
import axios from "axios";
import { toRefs, ref, watch, onMounted, reactive, computed, inject } from "vue";
import { getCookie } from "@/mixins/csrftoken.js";
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
    const IdentityName = ref("");
    const identityId = ref(null);
    const IdentityAttribute = ref("");
    const Identities = ref([]);
    const Description = ref("");
    const isAdmin = ref(false);
    const selectedTitle = ref("User");
    const selectedOs = ref("windows");
    const items = [
      { title: "User" },
      { title: "Device" },
      { title: "Service" },
      { title: "Router" },
      { title: "Default" },
    ];
    const OS = [{ title: "windows" }, { title: "linux" }];
    const rules = [(value) => !!value || "You must enter a value."];
    const rulesName = [
      (value) => {
        if (!value) return true;
        if (existingName(value)) return "The name already exists";
        return ValidName(value) ? true : "Please enter a valid name.";
      },
    ];

    const emitter = inject("emitter");

    const { isOpen, editRow, modalMode } = toRefs(props);

    const state = reactive({
      openModal: false,
      snackbar: false,
      color: "",
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
          IdentityName.value = "";
          identityId.value = null;
          IdentityAttribute.value = "";
          Description.value = "";
          isAdmin.value = false;
          selectedTitle.value = "User";
        }
      }
    );
    const populate = (data) => {
      if (modalMode.value === "edit") {
        identityId.value = data.id;
        IdentityName.value = data.name;
        Description.value = data.description;
        IdentityAttribute.value = data.attribute_identitie;
        selectedTitle.value = "User";
        selectedOs.value = data.os;
        isAdmin.value = data.is_admin;
      }
    };

    const submitForm = async () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      let payload = {
        name: IdentityName.value,
        type: selectedTitle.value,
        isAdmin: isAdmin.value,
        roleAttributes: [IdentityAttribute.value],
        Description: Description.value,
        os: selectedOs.value,
      };

      let token = document.getElementById("app").getAttribute("token");

      if (modalMode.value === "edit") {
        axios
          .patch(`/ztna/update_identities/${identityId.value}`, payload, {
            headers: {
              "zt-session": token,
              "Content-Type": "application/json",
            },
          })
          .then((response) => {
            if (response.status == "200") {
              state.snackbar = true;
              state.color = "success";
              state.textAlert = response.data.message;
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
          .post("/ztna/add_identities", payload, {
            headers: {
              "zt-session": token,
              "Content-Type": "application/json",
            },
          })
          .then((response) => {
            if (response.status == "200") {
              state.openModal = false;
              state.snackbar = true;
              state.color = "success";
              state.textAlert = response.data.message;
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
    };

    const fetchIdentities = async () => {
      try {
        const IdentitiesString = await document
          .getElementById("app")
          .getAttribute("Identities");
        const IdentitiesObject = JSON.parse(IdentitiesString);

        const identitiesArray = Array.isArray(IdentitiesObject)
          ? IdentitiesObject
          : [];

        Identities.value = identitiesArray.map((identity) => ({
          name: identity.name,
        }));

        console.log("Identities.value", Identities.value);
      } catch (error) {
        console.error("Failed to fetch identities:", error);
        Identities.value = [];
      }
    };

    onMounted(() => {
      fetchIdentities();
    });

    const onReset = () => {
      IdentityName.value = "";
      IdentityAttribute.value = "";
      Description.value = "";
      isAdmin.value = false;
      selectedTitle.value = "User";
    };
    const selectItem = (item) => {
      selectedTitle.value = item.title;
    };

    const selectOs = (item) => {
      selectedOs.value = item.title;
    };

    function ValidName(value) {
      const hostnamePattern = /^(?=.*[a-zA-Z])[a-zA-Z0-9-\s]{1,63}(\.[a-zA-Z0-9-\s]{1,63})*$/;

      console.log("Identities.value", Identities.value);

      if (!Array.isArray(Identities.value)) {
        console.error("Identities.value is not an array:", Identities.value);
        return false;
      }

      const existingIdentity = Identities.value.find(
        (identity) => identity.name === value
      );

      if (
        existingIdentity ||
        !hostnamePattern.test(value) ||
        /^\d+$/.test(value)
      ) {
        return false;
      }

      return true;
    }

    function existingName(value) {
      const existingIdentity = Identities.value.find(
        (identity) => identity.name === value
      );

      if (existingIdentity) {
        return true;
      }

      return false;
    }
    const cancel = () => {
      onReset();
      emitter.emit("closeidentityModal");
    };

    return {
      state,
      cancel,
      emitter,
      IdentityName,
      IdentityAttribute,
      Description,
      rules,
      submitForm,
      isAdmin,
      selectedTitle,
      selectItem,
      selectedOs,
      selectOs,
      OS,
      rulesName,
      items,
      onReset,
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
