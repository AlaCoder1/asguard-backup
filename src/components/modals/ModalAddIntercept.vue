<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="text-h5"> {{ $t("ztna.addInterceptConfig") }}</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    id="ConfigName"
                    v-model="ConfigName"
                    :placeholder="$t('ztna.configName')"
                    :rules="rules"
                    persistent-placeholder
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
                    id="adress"
                    v-model="adress"
                    :placeholder="$t('ztna.address')"
                    :rules="rules"
                    persistent-placeholder
                  />
                </v-col>

                <v-col cols="6">
                  <v-text-field
                    id="portLow"
                    v-model.number="portLow"
                    :placeholder="$t('ztna.lowPorts')"
                    :rules="rules"
                    persistent-placeholder
                    outlined
                    dense
                    hide-details="auto"
                  />
                </v-col>
                <v-col cols="6" class="mb-n6">
                  <v-text-field
                    id="portHigh"
                    v-model.number="portHigh"
                    :placeholder="$t('ztna.highPorts')"
                    :rules="rules"
                    persistent-placeholder
                    outlined
                    dense
                    hide-details="auto"
                  />
                </v-col>

                <v-col cols="12" class="mb-n6">
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
  },

  setup(props) {
    const ConfigName = ref("");
    const adress = ref("");
    const portLow = ref("");
    const portHigh = ref("");
    const Description = ref("");
    const selectedTitle = ref("tcp");
    const items = [{ title: "tcp" }, { title: "udp" }];
    const rules = [
      (value) => {
        if (value) return true;

        return "You must enter a value.";
      },
    ];
    const emitter = inject("emitter");

    const { isOpen } = toRefs(props);

    const state = reactive({
      openModal: false,
    });

    watch(
      () => isOpen.value,
      (val) => {
        state.openModal = val;
      }
    );

    const submitForm = async () => {
      try {
        let token = document.getElementById("app").getAttribute("token");

        const proxyUrl = "https://asguard:3000";
        const apiUrl = "/edge/management/v1/configs";
        const response = await axios.post(
          proxyUrl + apiUrl,
          {
            name: ConfigName.value,
            configTypeId: "g7cIWbcGg",
            data: {
              addresses: [adress.value],
              portRanges: [
                {
                  high: Number(portHigh.value),
                  low: Number(portLow.value),
                },
              ],
              protocols: [selectedTitle.value],
            },
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
        emitter.emit("closeInterceptModal");
      } catch (error) {
        console.error("Failed to submit form !!:", error);
      }
    };
    const selectItem = (item) => {
      selectedTitle.value = item.title;
    };
    const cancel = () => {
      console.log("test");
      emitter.emit("closeInterceptModal");
    };

    return {
      state,
      cancel,
      emitter,
      ConfigName,
      adress,
      portLow,
      portHigh,
      Description,
      selectedTitle,
      items,
      selectItem,
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
