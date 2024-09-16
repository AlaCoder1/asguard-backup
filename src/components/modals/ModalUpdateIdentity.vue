<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="updateIdentities">
        <v-card>
          <v-card-title>
            <span class="text-h5"> {{ $t("ztna.updateIdentity") }}</span>
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
              >{{ $t("buttons.close") }}</v-btn
            >
            <!-- <VBtn
              color="red"
              :rounded="true"
              large
              rounded
              outlined
              label-color="#213E9F"
              variant="flat"
              class="mt-3 btn-add"
              type="reset"
              @click="onReset"
            >
              Reset
            </VBtn> -->
            <VBtn
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
              {{ $t("buttons.update") }}
            </VBtn>
          </v-card-actions>
        </v-card>
      </form>
    </v-dialog>
  </v-row>
</template>

<script>
import axios from "axios";
import { toRefs, ref, watch, onMounted, reactive, computed, inject } from "vue";
export default {
  props: {
    isOpen: {
      type: Boolean,
      required: true,
    },
    selectedId: {
      type: [String, Number],
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
    const IdentityAttribute = ref("");
    const Description = ref("");
    const identityId = ref("");
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

    const { isOpen, selectedId, editRow } = toRefs(props);

    const state = reactive({
      openModal: false,
      itemId: null,
    });

    watch(
      () => editRow.value,
      (val) => {
        populate(val);
      }
    );

    watch(
      () => isOpen.value,
      (val) => {
        state.openModal = val;
      }
    );

    watch(
      () => selectedId.value,
      (val) => {
        console.log(val);
        state.itemId = val;
      }
    );

    const populate = (data) => {
      console.log("dataIdentityUpdate", data);
      if (data) {
        identityId.value = data.id;
        IdentityName.value = data.name;
        Description.value = data.description;
        IdentityAttribute.value = data.roleAttributes;
        selectedTitle.value = data.type;
      }
    };

    const updateIdentities = async () => {
      try {
        let token = document.getElementById("app").getAttribute("token");
        let requestBody = {};
        if (IdentityName.value.trim() !== "") {
          requestBody.name = IdentityName.value;
        }

        if (selectedTitle.value.trim() !== "") {
          requestBody.type = selectedTitle.value;
        }

        if (isAdmin.value !== undefined && isAdmin.value !== null) {
          requestBody.isAdmin = isAdmin.value;
        }

        if (IdentityAttribute.value.length > 0) {
          if (!requestBody.roleAttributes) {
            requestBody.roleAttributes = [];
          }
          requestBody.roleAttributes.push(...IdentityAttribute.value);
        }
        console.log(requestBody);

        const proxyUrl = "https://asguard:3000";
        const apiUrl = `/edge/management/v1/identities/${state.itemId}`;
        const response = await axios.patch(proxyUrl + apiUrl, requestBody, {
          headers: {
            "zt-session": token,
            "Content-Type": "application/json",
          },
        });
        setTimeout(() => {
          location.reload();
        }, 1000);
      } catch (error) {
        console.error(
          "Failed to update item:",
          error.response ? error.response.data : error.message
        );
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
     
      emitter.emit("closeUpdateModal");
    };

    return {
      state,
      cancel,
      emitter,
      IdentityName,
      IdentityAttribute,
      Description,
      rules,
      updateIdentities,
      isAdmin,
      selectedTitle,
      selectItem,
      items,
      onReset,
      identityId,
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
