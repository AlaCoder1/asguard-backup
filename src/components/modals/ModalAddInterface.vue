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
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.interface.$errors.length"
                  >
                    {{ v$.interface.$errors?.[0].$message }}
                  </p>

                  <p class="error-feedback mb-5" v-if="isExist">
                    Interface Name exist déja
                  </p>
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
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.thread.$errors.length"
                  >
                    {{ v$.thread.$errors?.[0].$message }}
                  </p>
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
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.defrag.$errors.length"
                  >
                    {{ v$.defrag.$errors?.[0].$message }}
                  </p>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Cluster Id"
                    v-model="state.clusterId"
                  ></v-text-field>
                  <p class="error-feedback mb-5" v-if="isExistClusterId">
                    Cluster-Id exist déja
                  </p>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.clusterId.$errors.length"
                  >
                    {{ v$.clusterId.$errors?.[0].$message }}
                  </p>
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
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.clusterType.$errors.length"
                  >
                    {{ v$.clusterType.$errors?.[0].$message }}
                  </p>
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
                    :items="state.copyIfaceList"
                    background-color="#fffffff"
                  >
                  </v-select>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Buffer Size"
                    v-model="state.bufferSize"
                  ></v-text-field>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.bufferSize.$errors.length"
                  >
                    {{ v$.bufferSize.$errors?.[0].$message }}
                  </p>
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
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.useNmp.$errors.length"
                  >
                    {{ v$.useNmp.$errors?.[0].$message }}
                  </p>
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
              :disabled="isExist || isExistClusterId"
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
import {
  toRefs,
  ref,
  watch,
  onMounted,
  reactive,
  computed,
  inject,
  watchEffect,
} from "vue";
import { required, helpers, requiredIf } from "@vuelidate/validators";
import { v4 as uuidv4 } from "uuid";

export default {
  props: {
    isOpen: {
      type: Boolean,
      required: true,
    },
    editRow: {
      type: Object,
      Array,
      required: true,
    },
    modalMode: {
      type: Object,
      Array,
      String,
      required: true,
    },
    // rowDataList: {
    //   type: Array,
    //   required: true,
    // },
  },

  setup(props) {
    const emitter = inject("emitter");
    onMounted(() => {
      getInterface();

      emitter.on("list-Interface", (data) => {
        state.rowList = data;
      });
    });

    const isExist = computed(() => {
      let mapedName = state.rowList.map((i) => i.name_interface);
      if (mapedName.includes(state.interface.name)) return true;
      else return false;
    });
    const isExistClusterId = computed(() => {
      let mapedCluster = state.rowList.map((i) => i.cluster_id);
      if (mapedCluster.includes(+state.clusterId)) return true;
      else return false;
    });

    const { isOpen, editRow, modalMode } = toRefs(props);

    const state = reactive({
      rowList: [],
      editValue: null,
      copyIfaceList: [],
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
      copyIface: null,
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
              ifname: i.ifname,
            };
          });

          state.mapedInterface = interfaces;
        },
        (error) => {
          console.log(error);
        }
      );
    };

    // watchEffect(() => {
    //   state.rowList = rowDataList.value;
    //   console.log("state.rowList ", state.rowList);
    // });

    // watch(
    //   () => rowDataList.value,
    //   (val) => {
    //     console.log("valList", val);
    //   },
    //   { immediate: true },
    //   { deep: true }
    // );
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
      () => state.interface,
      (val) => {
        if (val && state.copyIface) state.copyIface = null;
      }
    );

    const populate = (data) => {
      if (modalMode.value === "edit") {
        let filtredInterface = state.mapedInterface.filter(
          (i) => i.name === data.name_interface
        );
        let filtredDefrag = state.defragList.filter(
          (i) => i.slug === data.defrag
        );
        let filtredType = state.clusterTypeList.filter(
          (i) => i.slug === data.cluster_type
        );
        let filtredIface = state.mapedInterface.filter((i) =>
          i.id === data.copy_iface.id ? data.copy_iface.id : data.copy_iface
        );
        let filtredUseMmap = state.useNmpList.filter(
          (i) => i.slug === data.use_mmap
        );
        let filtredCopy = state.copyModeList.filter(
          (i) => i.slug === data.copy_mode
        );

        state.interface = filtredInterface[0];
        state.bufferSize = data.ring_size;
        state.copyIface = filtredIface[0];
        state.copyMode = filtredCopy[0];
        state.clusterId = data.cluster_id;
        state.clusterType = filtredType[0];
        state.defrag = filtredDefrag[0];
        state.thread = data.threads;
        state.useNmp = filtredUseMmap[0];
        state.editValue = data.uuid;
      }
    };

    watch(
      () => modalMode.value,
      (val) => {
        if (val === "create") {
          state.interface = "";
          state.bufferSize = "";
          state.copyIface = null;
          state.copyMode = "";
          state.clusterId = "";
          state.clusterType = { name: "cluster_flow", slug: "cluster_flow" };
          state.defrag = "";
          state.thread = "auto";
          state.useNmp = "";
        }
      }
    );

    watch(
      () => state.interface,
      (val) => {
        if (val) {
          let copyIfaceList = state.mapedInterface.filter(
            (item) => item.name !== val.name
          );
          state.copyIfaceList = copyIfaceList;
        }
      }
    );

    const submitForm = async () => {
      const result = await v$.value.$validate();
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      if (result) {
        let payload = {
          uuid: modalMode.value === "create" ? uuidv4() : state.editValue,
          id: +state.interface.id,
          interface: state.interface.name,
          threads: state.thread,
          cluster_id: +state.clusterId,
          cluster_type: state.clusterType.slug,
          defrag: state.defrag.slug,
          use_mmap: state.useNmp.slug,
          ring_size: +state.bufferSize,
          copy_mode: state.copyMode.slug ?? null,
          copy_iface: state.copyIface ?? null,
          ifname: state.interface.ifname,
        };
        if (modalMode.value === "create") {
          emitter.emit("add-Interface", payload);
        }

        if (modalMode.value === "edit") {
          emitter.emit("edit-Interface", payload);
        }

        closeModal();
        v$.value.$reset();
      } else {
        console.log("v$", v$.value);
      }
    };

    const closeModal = () => {
      emitter.emit("closeModalAddInterface");
      state.interface = "";
      state.bufferSize = "";
      state.copyIface = null;
      state.copyMode = "";
      state.clusterId = "";
      state.clusterType = "";
      state.defrag = "";
      state.thread = "";
      state.useNmp = "";
    };

    const rules = computed(() => {
      return {
        interface: { required },
        bufferSize: {
          required,
          isValidBufferSize: helpers.withMessage(
            `Champs can include only Numbers.`,

            helpers.regex(/^[0-9]+$/)
          ),
        },

        clusterId: {
          required,
          isValidClusterId: helpers.withMessage(
            `Champs can include only Numbers.`,

            helpers.regex(/^[0-9]+$/)
          ),
        },

        clusterType: { required },
        defrag: { required },
        thread: { required },
        useNmp: { required },
      };
    });

    const v$ = useValidate(rules, state);

    return {
      isExist,
      isExistClusterId,
      state,
      emitter,
      v$,
      closeModal,
      submitForm,
      getCookie,
    };
  },
};
</script>
<style>
.error-feedback {
  color: red !important;
  font-size: 0.85em;
}
.actionBtn {
  justify-content: center;
}
</style>
