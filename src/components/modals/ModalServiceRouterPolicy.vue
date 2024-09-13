<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              {{ $t("ztna.addService") }}</span
            >
            <span class="headline" v-if="modalMode === 'edit'">
              {{ $t("ztna.updateService") }}</span
            >
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
                            {{ selectedsemantic }}
                          </v-btn>
                        </template>

                        <v-list>
                          <v-list-item
                            v-for="(item, index) in semantic"
                            :key="index"
                            @click="selectsemantic(item)"
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
                    id="serviceRA"
                    v-model="serviceRA"
                    :placeholder="$t('ztna.serviceRoleAttribute')"
                    :rules="rules"
                    persistent-placeholder
                  />
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
    }
  },
  setup(props) {
    const name = ref("");
    const serviceRA = ref("");
    const routerR = ref("");
    const Description = ref("");
    const selectedsemantic = ref("AllOf");
    const semantic = ref([{ title: "AllOf" }, { title: "AnyOf" }]);
    const rules = [
      (value) => {
        if (value) return true;
        return "You must enter a value.";
      },
    ];
    const emitter = inject("emitter");

    const { isOpen, editRow, modalMode } = toRefs(props);

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
        console.log("dataHost", data);
      }
    };


    const submitForm = async () => {
      try {
        let token = document.getElementById("app").getAttribute("token");
        let routerAttribute = `#${routerR.value}`;
        let serviceAttribute = `#${serviceRA.value}`;
        const proxyUrl = "https://asguard:3000";
        const apiUrl = "/edge/management/v1/service-edge-router-policies";
        await axios.post(
          proxyUrl + apiUrl,
          {
            name: name.value,
            semantic: selectedsemantic.value,
            edgeRouterRoles: [routerAttribute],
            serviceRoles: [serviceAttribute],
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
        emitter.emit("closeServiceRouterPolicyModal");
      } catch (error) {
        console.error("Failed to submit form:", error);
      }
    };
    const resetForm = () => {
      name.value = "";
      serviceRA.value = "";
      routerR.value = "";
      Description.value = "";
      selectedsemantic.value = "AllOf";
    };

    const cancel = () => {
      console.log("tes");
      emitter.emit("closeServiceRouterPolicyModal");
    };
    const selectsemantic = (item) => {
      selectedsemantic.value = item.title;
    };

    return {
      state,
      name,
      serviceRA,
      routerR,
      Description,
      semantic,
      rules,
      submitForm,
      resetForm,
      cancel,
      selectedsemantic,
      selectsemantic,
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
