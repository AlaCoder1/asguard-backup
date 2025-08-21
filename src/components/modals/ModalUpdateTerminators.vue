<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="updateTerminators">
        <v-card>
          <v-card-title>
            <span class="text-h5">{{ $t("ztna.updateTerminator") }}</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="6">
                  <v-text-field
                    id="Address"
                    v-model="address"
                    :placeholder="$t('ztna.address')"
                    :rules="rules"
                    persistent-placeholder
                    outlined
                    dense
                    hide-details="auto"
                  />
                </v-col>
                <v-col cols="6" class="mb-n6">
                  <v-text-field
                    id="port"
                    v-model.number="port"
                    placeholder="Port"
                    :rules="rules"
                    persistent-placeholder
                    outlined
                    dense
                    hide-details="auto"
                  />
                </v-col>
                <v-col cols="12">
                  <div class="d-flex align-center">
                    <label class="ml-1" for="PROTOCOL">{{
                      $t("ztna.protocol")
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
                    id="Router"
                    v-model="router"
                    :placeholder="$t('ztna.router')"
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
              rounded
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
              {{ $t("buttons.update") }}
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
    const routers = ref([]);
    const svc = ref("");
    const address = ref("");
    const port = ref("");
    const selectedTitle = ref("tcp");
    const items = [{ title: "tcp" }, { title: "udp" }];
    const router = ref("");
    const Description = ref("");
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

    const fetchRouters = () => {
      let routersString = document
        .getElementById("app")
        .getAttribute("routers");
      let routersObject;
      try {
        routersObject = JSON.parse(routersString);
      } catch (error) {}
      routers.value = routersObject.data;
    };

    const updateTerminators = async () => {
      try {
        let token = document.getElementById("app").getAttribute("token");
        let requestBody = {};

        if (address.value.trim() !== "") {
          requestBody.address = address.value;
        }
        if (port.value !== "") {
          requestBody.port = Number(port.value);
        }
        if (selectedTitle.value.trim() !== "") {
          requestBody.protocol = selectedTitle.value;
        }
        if (router.value.trim() !== "") {
          const targetRouter = routers.value.find(
            (r) => r.name === router.value
          );
          if (targetRouter) {
            requestBody.router = targetRouter.id;
          } else {
          }
        }
        const proxyUrl = "https://asguard:3000";
        const apiUrl = `/edge/management/v1/terminators/${state.itemId}`;
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
      cancel,
      emitter,
      svc,
      address,
      port,
      router,
      updateTerminators,
      Description,
      rules,
      selectedId,
      selectItem,
      selectedTitle,
      items,
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
