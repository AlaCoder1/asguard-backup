<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="updateRouters">
        <v-card>
          <v-card-title>
            <span class="text-h5"> {{ $t("ztna.updateRelay") }}</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    id="RouterName"
                    v-model="RouterName"
                    :placeholder="$t('ztna.relayName')"
                    :rules="rules"
                    persistent-placeholder
                  />
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    id="RouterAttribute"
                    v-model="RouterAttribute"
                    :placeholder="$t('ztna.relayAttribute')"
                    :rules="rules"
                    persistent-placeholder
                  />
                </v-col>

                <v-col cols="12" class="mb-n3">
                  <label for="Tunneler" class="mr-3">{{
                    $t("ztna.tunneler")
                  }}</label>
                  <input
                    type="checkbox"
                    id="Tunneler"
                    value="Tunneler"
                    v-model="Tunneler"
                  />
                </v-col>
                <v-col cols="12" class="mb-n3">
                  <label for="Traversal" class="mr-3">{{
                    $t("ztna.traversal")
                  }}</label>
                  <input
                    type="checkbox"
                    id="Traversal"
                    value="Traversal"
                    v-model="Traversal"
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
  },

  setup(props) {
    const RouterName = ref("");
    const RouterAttribute = ref("");
    const Description = ref("");
    const routerId = ref("");
    const Tunneler = ref(false);
    const Traversal = ref(false);
    const rules = [(value) => !!value || "You must enter a value."];

    const emitter = inject("emitter");

    const { isOpen, selectedId } = toRefs(props);

    const state = reactive({
      openModal: false,
      itemId: null,
    });

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

    const updateRouters = async () => {
      try {
        let token = document.getElementById("app").getAttribute("token");
        let requestBody = {};
        if (RouterName.value.trim() !== "") {
          requestBody.name = RouterName.value;
        }

        if (Traversal.value === "Traversal" && Traversal.value !== null) {
          requestBody.noTraversal = true;
        }

        if (Tunneler.value === "Tunneler") {
          requestBody.isTunnelerEnabled = true;
        }

        if (RouterAttribute.value.length > 0) {
          if (!requestBody.roleAttributes) {
            requestBody.roleAttributes = [];
          }
          requestBody.roleAttributes.push(...RouterAttribute.value); // Spread operator to add all elements of the array
        }

        console.log(requestBody);
        const proxyUrl = "https://asguard:3000";
        const apiUrl = `/edge/management/v1/edge-routers/${state.itemId}`;
        const response = await axios.patch(proxyUrl + apiUrl, requestBody, {
          headers: {
            "zt-session": token,
            "Content-Type": "application/json",
          },
        });
        console.log("here");
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
      RouterName,
      RouterAttribute,
      Description,
      Tunneler,
      Traversal,
      rules,
      routerId,
      updateRouters,
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
