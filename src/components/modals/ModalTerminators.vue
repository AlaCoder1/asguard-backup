<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              {{ $t("ztna.addTerminator") }}</span>
            <span class="headline" v-if="modalMode === 'edit'">
              {{ $t("ztna.updateTerminator") }}</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <!-- <v-text-field id="Service" v-model="svc" :placeholder="$t('ztna.services')" :rules="rules"
                    persistent-placeholder /> -->
                  <v-select v-model="svc" :label="$t('ztna.services')" density="compact" item-title="name"
                    item-value="id" return-object :rules="rules" :items="ServList" background-color="#fffffff"
                    :no-data-text="$t('certificat.certificatlist')">
                  </v-select>
                </v-col>

                <v-col cols="6">
                  <v-text-field id="Address" v-model="address" :placeholder="$t('ztna.address')" :rules="rules"
                    persistent-placeholder outlined dense hide-details="auto" />
                </v-col>
                <v-col cols="6" class="mb-n6">
                  <v-text-field id="port" v-model.number="port" placeholder="Port" :rules="rules" persistent-placeholder
                    outlined dense hide-details="auto" />
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
                          <v-list-item v-for="(item, index) in items" :key="index" @click="selectItem(item)">
                            <v-list-item-title>{{
                              item
                              }}</v-list-item-title>
                          </v-list-item>
                        </v-list>
                      </v-menu>
                    </div>
                  </div>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <!-- <v-text-field
                    id="Router"
                    v-model="router"
                    :placeholder="$t('ztna.router')"
                    :rules="rules"
                    persistent-placeholder
                  /> -->

                  <v-select v-model="router" :label="$t('ztna.router')" density="compact" item-title="name"
                    item-value="id" return-object :rules="rules" :items="RouteList" background-color="#fffffff"
                    :no-data-text="$t('certificat.certificatlist')">
                  </v-select>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-text-field id="Description" v-model="Description" placeholder="Description" :rules="rules"
                    persistent-placeholder />
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="indigo-darken-3" :rounded="true" large outlined label-color="#213E9F" variant="flat"
              class="mt-3 btn-add" text @click="cancel"><span class="text-white pr-3 pl-3">
                {{ $t("buttons.close") }}</span
              ></v-btn>
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
            <v-btn large rounded outlined label-color="#213E9F" color="indigo-darken-3" variant="flat"
              class="mt-3 ml-2 btn-add" type="submit">
              <span class="text-white pr-3 pl-3" v-if="modalMode === 'create'">
                {{ $t("buttons.create") }}</span>
              <span class="text-white pr-3 pl-3" v-if="modalMode === 'edit'">
                {{ $t("buttons.update") }}</span>
            </v-btn>
          </v-card-actions>
        </v-card>
      </form>
    </v-dialog>
    <v-snackbar :timeout="2000" v-model="state.snackbar" location="bottom right" :color="state.color">
      {{ state.textAlert }}
    </v-snackbar>
  </v-row>
</template>

<script>
import { getCookie } from "@/mixins/csrftoken.js";
import axios from "axios";
import { toRefs, ref, watch, reactive, inject, onMounted } from "vue";

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
    const services = ref([]);
    const ServList = ref([]);
    const RouteList = ref([]);
    const routers = ref([]);
    const svc = ref("");
    const serviceId = ref("");
    const address = ref("");
    const port = ref("");
    const selectedTitle = ref("tcp");
    const items = [ "tcp" ,   "udp" ];
    const router = ref("");
    const Description = ref("");
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
      snackbar: false,
      color: null,
      textAlert: "",
    });

    onMounted(() => {
      fetchServices();
      fetchRouters();
    })
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
          services.value = [];
          routers.value = [];
          svc.value = "";
          address.value = "";
          port.value = "";
          router.value = "";
          Description.value = "";
          selectedTitle.value = "tcp";
        }
      }
    );
    const populate = (data) => {
      if (modalMode.value === "edit") {
        console.log("dataService", data);

  serviceId.value = data.id
        let filtredServ = ServList.value.filter(
          (i) => i.id === data.serviceId
        );

        let filtredRouter = RouteList.value.filter(
          (i) => i.id === data.routerId
        );

        svc.value = filtredServ[0];
        router.value = filtredRouter[0];
        Description.value = "";
        let spl = data.address.split(':')

        address.value = spl[1];
        port.value = spl[2];
        selectedTitle.value = spl[0];
      }
    };

    const fetchServices = () => {
      let servicesString = document
        .getElementById("app")
        .getAttribute("services");
      let servicesObject;
      try {
        servicesObject = JSON.parse(servicesString);
      } catch (error) {
        console.error("Failed to parse services string:", error);
      }

      ServList.value = servicesObject
    };

    const fetchRouters = () => {
      let routersString = document
        .getElementById("app")
        .getAttribute("routers");
      let routersObject;
      try {
        routersObject = JSON.parse(routersString);
        console.log(routersObject);
      } catch (error) {
        console.error("Failed to parse routers string:", error);
      }
      RouteList.value = routersObject
    };

    const submitForm = async () => {

      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      // let selectedService = services.value.find(
      //   (service) => service.name === svc.value
      // );
      // if (!selectedService) {
      //   throw new Error(`Service '${svc.value}' not found`);
      // }
      // let serviceId = selectedService.id;

      // let selectedRouter = routers.value.find(
      //   (rtr) => rtr.name === router.value
      // );
      // if (!selectedRouter) {
      //   throw new Error(`Router '${router.value}' not found`);
      // }
      // let routerId = selectedRouter.id;

      let fullAddress = `${selectedTitle.value}:${address.value}:${port.value}`;

      let payload = {
        address: fullAddress,
        binding: "edge_transport",
        router: router.value.id,
        service: svc.value.id,
      };

      let token = document.getElementById("app").getAttribute("token");

      if (modalMode.value === "edit") {
        axios
          .put(`/ztna/update_terminators/${serviceId.value}`, payload, {
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
            state.snackbar = true;
            state.color = "red";
            state.textAlert = i.response.data.response;
          });
      } else {
        axios
          .post("/ztna/add_terminators", payload, {
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
            state.snackbar = true;
            state.color = "red";
            state.textAlert = i.response.data.response;
          });

        // try {
        //   fetchServices();
        //   fetchRouters();

        //   let token = document.getElementById("app").getAttribute("token");

        //   let selectedService = services.value.find(
        //     (service) => service.name === svc.value
        //   );
        //   if (!selectedService) {
        //     throw new Error(`Service '${svc.value}' not found`);
        //   }
        //   let serviceId = selectedService.id;

        //   let selectedRouter = routers.value.find(
        //     (rtr) => rtr.name === router.value
        //   );
        //   if (!selectedRouter) {
        //     throw new Error(`Router '${router.value}' not found`);
        //   }
        //   let routerId = selectedRouter.id;

        //   let fullAddress = `${selectedTitle.value}:${address.value}:${port.value}`;
        //   console.log(serviceId, fullAddress);
        //   const proxyUrl = "https://asguard:3000";
        //   const apiUrl = "/edge/management/v1/terminators";
        //   const response = await axios.post(
        //     proxyUrl + apiUrl,
        //     {
        //       address: fullAddress,
        //       binding: "edge_transport",
        //       router: routerId,
        //       service: serviceId,
        //     },
        //     {
        //       headers: {
        //         "zt-session": token,
        //         "Content-Type": "application/json",
        //       },
        //     }
        //   );

        //   setTimeout(() => {
        //     location.reload();
        //   }, 1000);
        //   emitter.emit("closeTerminatorsModal");
        // } catch (error) {
        //   console.error("Failed to submit form !!:", error);
        // }
      }
    };

    const resetForm = () => {
      svc.value = "";
      address.value = "";
      port.value = "";
      router.value = "";
      Description.value = "";
    };

    const cancel = () => {
      services.value = [];
      routers.value = [];
      svc.value = "";
      address.value = "";
      port.value = "";
      router.value = "";
      Description.value = "";
      selectedTitle.value = "tcp";

      emitter.emit("closeTerminatorsModal");
    };

    const selectItem = (item) => {
      selectedTitle.value = item;
    };

    return {
      state,
      ServList,
      RouteList,
      cancel,
      emitter,
      svc,
      address,
      port,
      router,
      Description,
      rules,
      submitForm,
      resetForm,
      selectItem,
      selectedTitle,
      items,
      services,
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

.reduced-margin {
  margin-right: 3px !important;
  /* Adjust as needed */
}
</style>
