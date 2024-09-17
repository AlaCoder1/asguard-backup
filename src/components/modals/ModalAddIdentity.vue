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
                    :rules="rules"
                    persistent-placeholder
                  />
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    id="IdentityAttribute"
                    v-model="IdentityAttribute"
                    :placeholder="$t('ztna.identityAttribute')"
                    :rules="rules"
                    persistent-placeholder
                  />
                </v-col>

                <v-col cols="12">
                  <div class="d-flex align-center">
                    <label class="ml-1" for="Type">Type</label>
                    <div class="ml-5 mt-1">
                      <v-menu open-on-hover>
                        <template v-slot:activator="{ props }">
                          <v-btn color="#FAFAFA" v-bind="props">
                            {{ selectedTitle }}
                          </v-btn>
                        </template>

                        <v-list>
                          <v-list-item
                            v-for="(item, index) in items"
                            :key="index"
                            @click="selectItem(item)"
                          >
                            <v-list-item-title>{{
                              item.title
                            }}</v-list-item-title>
                          </v-list-item>
                        </v-list>
                      </v-menu>

                      <label for="IsAdmin" class="mr-3 ml-5">{{
                        $t("ztna.isAdmin")
                      }}</label>
                      <input type="checkbox" id="IsAdmin" v-model="isAdmin" />
                    </div>
                  </div>
                </v-col>

                <!-- <v-col cols="12" class="ml-2">
                  <label for="IsAdmin" class="mr-3">Is Admin</label>
                  <input type="checkbox" id="IsAdmin" v-model="isAdmin" />
                </v-col> -->

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
              > <span class="text-white pr-3 pl-3">
                {{ $t("buttons.close") }}</span
              ></v-btn
            >
            <!-- <v-btn
                  color="red"
                  :rounded="true"
                  large
                  rounded
                  outlined
                  label-color="#213E9F"
                  variant="flat"F
                  class="mt-3 btn-add"
                  type="reset"
                  @click="onReset"
                >
                  Reset
                </v-btn> -->
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
    const IdentityName = ref("");
    const identityId = ref(null);
    const IdentityAttribute = ref("");
    const Description = ref("");
    const isAdmin = ref(false);
    const selectedTitle = ref("User");
    const items = [
      { title: "User" },
      { title: "Device" },
      { title: "Service" },
      { title: "Router" },
      { title: "Default" },
    ];
    const rules = [(value) => !!value || "You must enter a value."];

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
        IdentityAttribute.value = data.roleAttributes;
        selectedTitle.value = data.typeId;
        isAdmin.value = data.isAdmin;
      }
    };

    // const submitForm = async () => {
    //   try {
    //     let token = document.getElementById("app").getAttribute("token");
    //     console.log("token", token);

    //     const proxyUrl = "https://asguard:3000"; // Adjust this to your proxy server's URL
    //     const apiUrl = "/edge/management/v1/identities"; // This part remains the same

    //     const response = await axios.post(
    //       proxyUrl + apiUrl,
    //       {
    //         name: IdentityName.value,
    //         type: selectedTitle.value,
    //         isAdmin: isAdmin.value,
    //         roleAttributes: [IdentityAttribute.value],
    //       },
    //       {
    //         headers: {
    //           "zt-session": token,
    //           "Content-Type": "application/json",
    //         },
    //       }
    //     );

    //     setTimeout(() => {
    //       location.reload();
    //     }, 1000);

    //     emitter.emit("closeidentityModal");
    //   } catch (error) {
    //     console.error(
    //       "Failed to submit form:",
    //       error.response ? error.response.data : error.message
    //     );
    //   }
    // };

    const submitForm = async () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      let payload = {
        name: IdentityName.value,
        type: selectedTitle.value,
        isAdmin: isAdmin.value,
        roleAttributes: [IdentityAttribute.value],
      };

      let token = document.getElementById("app").getAttribute("token");

      if (modalMode.value === "edit") {
        axios
          .put(`/ztna/update_identities/${identityId.value}`, payload, {
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
            console.log("response", i.response);
            state.snackbar = true;
            state.color = "red";
            state.textAlert = i.response.data.response;
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
            console.log("response", i.response);
            state.snackbar = true;
            state.color = "red";
            state.textAlert = i.response.data.error;
          });
      }
    };

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
