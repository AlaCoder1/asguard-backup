<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm" style="overflow: auto">
        <v-card>
          <v-card-title>
            <span class="text-h5"> AF Pack</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.interface"
                    label="Interface"
                    item-title="name"
                    item-value="id"
                    return-object
                    :items="state.mapedInterface"
                    background-color="#fffffff"
                  >
                  </v-select>
                  <!-- <small class="ml-5 error-feedback" v-show="switchValue"
                    >Specify the network interfaces on which Suricata</small
                  >
                  <small class="ml-5 error-feedback" v-show="switchValue"
                    >should monitor traffic.</small
                  > -->
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Thread"
                    v-model="state.thread"
                  ></v-text-field>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.defrag"
                    label="Defrag"
                    item-title="name"
                    item-value="slug"
                    return-object
                    :items="state.defragList"
                    background-color="#fffffff"
                  >
                  </v-select>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Cluster Id"
                    v-model="state.clusterId"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.clusterType"
                    label="Cluster Type"
                    item-title="name"
                    item-value="slug"
                    return-object
                    :items="state.clusterTypeList"
                    background-color="#fffffff"
                  >
                  </v-select>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.copyMode"
                    label="Copy Mode"
                    item-title="name"
                    item-value="slug"
                    return-object
                    :items="state.copyModeList"
                    background-color="#fffffff"
                  >
                  </v-select>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.copyIface"
                    label="Copy Iface"
                    item-title="name"
                    item-value="id"
                    return-object
                    :items="state.mapedInterface"
                    background-color="#fffffff"
                  >
                  </v-select>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Buffer Size"
                    v-model="state.bufferSize"
                  ></v-text-field>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.useNmp"
                    label="Use Nmp"
                    item-title="name"
                    item-value="slug"
                    return-object
                    :items="state.useNmpList"
                    background-color="#fffffff"
                  >
                  </v-select>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions class="mt-3 actionBtn">
            <v-btn
              color="indigo-darken-3"
              :rounded="true"
              large
              rounded
              outlined
              label-color="#213E9F"
              variant="outlined"
              @click="closeModal"
              class="mt-3 btn-add"
            >
              <span class="pr-3 pl-3">Close</span>
            </v-btn>

            <v-btn
              large
              rounded
              outlined
              label-color="#213E9F"
              type="submit"
              color="indigo-darken-3"
              :rounded="true"
              variant="flat"
              class="mt-3 btn-add"
            >
              <span class="text-white pr-3 pl-3">Create</span>
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
export default {
  props: {
    isOpen: {
      type: Boolean,
      required: true,
    },
  },

  setup(props) {
    const emitter = inject("emitter");
    onMounted(() => {
      getInterface();
    });

    const { isOpen } = toRefs(props);

    const state = reactive({
      mapedInterface: [],
      defragList: [
        { name: "Yes", slug: "yes" },
        { name: "No", slug: "no" },
      ],
      clusterTypeList: [
        { name: "cluster_flow", slug: "cluster_flow" },
        { name: "cluster_cpu", slug: "cluster_cpu" },
        { name: "cluster_qm", slug: "cluster_qm" },
        { name: "cluster_ebpf", slug: "cluster_ebpf" },
      ],
      copyModeList: [
        { name: "IPS", slug: "ips" },
        { name: "TAP", slug: "tap" },
      ],
      useNmpList: [
        { name: "Yes", slug: "yes" },
        { name: "No", slug: "no" },
      ],
      //
      interface: "",
      bufferSize: "",
      copyIface: "",
      copyMode: "",
      clusterId: "",
      clusterType: { name: "cluster_flow", slug: "cluster_flow" },
      defrag: "",
      thread: "auto",
      useNmp: "",
    });

    const getCookie = (name) => {
      let cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === name + "=") {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    };

    const getInterface = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/network/AllInterfaces").then(
        (response) => {
          let filtredInterface = response.data.filter(
            (i) => !i.ifname.startsWith("tun_") && !i.ifname.startsWith("tap_")
          );

          let interfaces = filtredInterface.map((i) => {
            return {
              id: i.id,
              name: i.name_interface,
            };
          });

          var combinedArray = [...interfaces];
          state.mapedInterface = combinedArray;
        },
        (error) => {
          console.log(error);
        }
      );
    };

    watch(
      () => isOpen.value,
      (val) => {
        state.openModal = val;
      }
    );

    const submitForm = async () => {
      //   const result = await v$.value.$validate();
      //   const csrfToken = getCookie("csrftoken");
      //   axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      //   if (result) {
      //   } else {
      //     console.log("v$", v$.value);
      //   }
      console.log("state", state);
      let payload = {
        id: state.interface.id,
        interface: state.interface.name,
        threads: state.thread,
        cluster_id: state.clusterId,
        cluster_type: state.clusterType.slug,
        defrag: state.defrag.slug,
        use_mmap: state.useNmp.slug,
        ring_size: state.bufferSize,
        copy_mode: state.copyMode.slug,
        copy_iface: state.copyIface,
        copy_ifaceName: state.copyIface.name,
      };

      console.log("payload", payload);
      emitter.emit("add-Interface", payload);
      closeModal();
    };

    const closeModal = () => {
      emitter.emit("closeModalAddInterface");
      state.interface = "";
      state.bufferSize = "";
      state.copyIface = "";
      state.copyMode = "";
      state.clusterId = "";
      state.clusterType = "";
      state.defrag = "";
      state.thread = "";
      state.useNmp = "";
    };

    // const rules = computed(() => {
    //   return {
    //     type: { required },

    //     keyName: {
    //       required,
    //       isValidkeyName: helpers.withMessage(
    //         `Champs can include only letters & Numbers & underscores & hyphens without space.`,

    //         helpers.regex(/^[A-Za-z0-9_\-]+$/)
    //       ),
    //     },

    //     key: {
    //       requiredIfFuction: helpers.withMessage(
    //         "Value is required",
    //         requiredIf(() => state.type.slug === "Create Private Key")
    //       ),
    //     },
    //     privateKey: {
    //       requiredIfFuction: helpers.withMessage(
    //         "Value is required",
    //         requiredIf(() => state.type.slug === "create")
    //       ),
    //     },

    //     externKey: {
    //       requiredIfFuction: helpers.withMessage(
    //         "Value is required",
    //         requiredIf(() => state.type.slug === "import")
    //       ),
    //     },
    //   };
    // });

    // const v$ = useValidate(rules, state);

    return {
      state,
      emitter,
      //   v$,
      closeModal,
      submitForm,
      getCookie,
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
</style>
