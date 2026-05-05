<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="updateRouterP">
        <v-card>
          <v-card-title>
            <span class="text-h5">{{ $t("ztna.updateRelaysPolicy") }}</span>
          </v-card-title>

          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    id="PolicyName"
                    v-model="name"
                    :placeholder="$t('ztna.policyName')"
                    :rules="rules"
                    persistent-placeholder
                  />
                </v-col>
                <v-col cols="12">
                  <div class="d-flex align-center">
                    <label class="ml-1" for="PROTOCOL">{{
                      $t("ztna.semantic")
                    }}</label>
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
                    </div>
                  </div>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    id="routerR"
                    v-model="routerR"
                    :placeholder="$t('ztna.edgeRelaysRole')"
                    :rules="rules"
                    persistent-placeholder
                  />
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    id="identityatt"
                    v-model="identityatt"
                    :placeholder="$t('ztna.identityRoleAttribute')"
                    :rules="rules"
                    persistent-placeholder
                  />
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    id="Description"
                    v-model="Description"
                    placeholder="Description"
                    :rules="rules"
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
              outlined
              label-color="#213E9F"
              variant="flat"
              class="mt-3 btn-add"
              text
              @click="cancel"
              >{{ $t("buttons.close") }}</v-btn
            >

            <v-btn
              large
              rounded
              outlined
              label-color="#213E9F"
              color="indigo-darken-3"
              variant="flat"
              class="mt-3 ml-2 btn-add"
              type="submit"
            >
              {{ $t("buttons.create") }}
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
    selectedId: {
      type: [String, Number],
      required: true,
    },
  },
  setup(props) {
    const name = ref("");
    const routerR = ref("");
    const identityatt = ref("");
    const Description = ref("");
    const selectedTitle = ref("AllOf");
    const items = ref([{ title: "AllOf" }, { title: "AnyOf" }]);
    const rules = [
      (value) => {
        if (value) return true;
        return "You must enter a value.";
      },
    ];
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
        state.itemId = val;
      }
    );

    const updateRouterP = async () => {
      try {
        let token = document.getElementById("app").getAttribute("token");
        let requestBody = {};

        if (name.value.trim() !== "") {
          requestBody.name = name.value;
        }
        if (routerR.value.trim() !== "") {
          requestBody.routerR = routerR.value;
        }
        if (identityatt.value.trim() !== "") {
          requestBody.identityatt = identityatt.value;
        }
        if (selectedTitle.value.trim() !== "") {
          requestBody.protocol = selectedTitle.value;
        }
        const proxyUrl = "https://asguard:3000";
        const apiUrl = `/edge/management/v1/edge-router-policies/${state.itemId}`;
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
      name,
      routerR,
      identityatt,
      updateRouterP,
      Description,
      selectedTitle,
      items,
      rules,
      selectedId,
      selectItem,
      cancel,
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
