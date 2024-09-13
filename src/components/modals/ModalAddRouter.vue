<template>
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
            <!-- <v-btn
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
  </v-row>
</template>

<script>
import axios from "axios";
import { toRefs, ref, watch, reactive, inject } from "vue";
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
    const RouterName = ref("");
    const RouterAttribute = ref("");
    const Description = ref("");
    const Tunneler = ref(false);
    const Traversal = ref(false);
    const rules = [(value) => !!value || "You must enter a value."];
    const emitter = inject("emitter");

    const { isOpen, editRow, modalMode } = toRefs(props);

    const submitForm = async () => {
      try {
        if (Traversal.value === "Traversal") {
          Traversal.value = true;
        }

        if (Tunneler.value === "Tunneler") {
          Tunneler.value = true;
        }
        let token = document.getElementById("app").getAttribute("token");

        const proxyUrl = "https://asguard:3000";
        const apiUrl = "/edge/management/v1/edge-routers";
        const response = await axios.post(
          proxyUrl + apiUrl,
          {
            name: RouterName.value,
            noTraversal: Traversal.value,
            isTunnelerEnabled: Tunneler.value,
            roleAttributes: [RouterAttribute.value],
          },
          {
            headers: {
              "zt-session": token,
              "Content-Type": "application/json",
            },
          }
        );
        setTimeout(() => {
          location.reload();
        }, 1000);

        emitter.emit("closeRouterModal");
      } catch (error) {
        console.error(
          "Failed to submit form:",
          error.response ? error.response.data : error.message
        );
      }
    };

    const state = reactive({
      openModal: false,
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
          // ConfigName.value = "";
          // adress.value = "";
          // portLow.value = "";
          // portHigh.value = "";
          // Description.value = "";
          // selectedTitle.value = "tcp";
        }
      }
    );
    const populate = (data) => {
      if (modalMode.value === "edit") {
        console.log("dataService", data);
      }
    };

    const cancel = () => {
      console.log("test");
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
