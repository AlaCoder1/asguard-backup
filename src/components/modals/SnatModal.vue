<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm" class="scroller">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              Create New SNAT Rule</span
            >
            <span class="headline" v-if="modalMode === 'edit'">
              Update SNAT Rule</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <!-- <v-col cols="4" align-self="center">
                  <label>Activate</label>
                </v-col>
                <v-col cols="8" class="mb-n6">
                  <input type="checkbox" v-model="state.activateStatus" />
                  <label class="ml-2"> Activate rule</label>
                </v-col> -->
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.interface"
                    label="Interface"
                    item-title="name"
                    item-value="id"
                    :items="state.mapedInterface"
                    clearable
                    return-object
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.interface.$error">
                    {{ v$.interface.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.tcpIpVersion"
                    label="Select TCP/IP version"
                    item-title="name"
                    item-value="slug"
                    :items="state.versionList"
                    clearable
                    return-object
                  ></v-select>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.protocol"
                    label="Select Protocol"
                    item-title="name"
                    item-value="slug"
                    :items="state.protocolList"
                    clearable
                    return-object
                  ></v-select>
                </v-col>
                <!-- <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.source"
                    label="select source"
                    item-title="name"
                    item-value="id"
                    :items="state.mapedInterface"
                    clearable
                    return-object
                  ></v-select>
                </v-col> -->

                <v-col cols="7" class="mb-n6">
                  <v-text-field
                    label="Enter source address"
                    v-model="state.sourceAddress"
                  ></v-text-field>
                  <p class="error-feedback mb-5" v-if="v$.sourceAddress.$error">
                    {{ v$.sourceAddress.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="1" class="mb-n6">
                  <div class="ml-1 mt-5">/</div>
                </v-col>
                <v-col cols="4" class="mb-n6">
                  <v-select
                    label="Prefix"
                    v-model="state.sourcePrefix"
                    :items="numberList"
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.sourcePrefix.$error">
                    {{ v$.sourcePrefix.$errors[0].$message }}
                  </p>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.sourcePort"
                    label="select source port"
                    item-title="name"
                    item-value="slug"
                    :items="state.listPort"
                    clearable
                    return-object
                  ></v-select>
                </v-col>
                <v-col cols="12" class="mb-n6" v-if="isSourceOther">
                  <v-text-field
                    label="port"
                    v-model="state.port"
                  ></v-text-field>
                  <p class="error-feedback mb-5" v-if="v$.port.$error">
                    {{ v$.port.$errors[0].$message }}
                  </p>
                </v-col>
                <!-- <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.destination"
                    label="select destination"
                    item-title="name"
                    item-value="id"
                    :items="state.mapedInterface"
                    clearable
                    return-object
                  ></v-select>
                </v-col> -->
                <v-col cols="7" class="mb-n6">
                  <v-text-field
                    label="Enter destination address"
                    v-model="state.destinationAddress"
                  ></v-text-field>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.destinationAddress.$error"
                  >
                    {{ v$.destinationAddress.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="1" class="mb-n6">
                  <div class="ml-1 mt-5">/</div>
                </v-col>
                <v-col cols="4" class="mb-n6">
                  <v-select
                    label="Prefix"
                    v-model="state.destinationPrefix"
                    :items="numberList"
                  ></v-select>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.destinationPrefix.$error"
                  >
                    {{ v$.destinationPrefix.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.destinationPort"
                    label="select destination port"
                    item-title="name"
                    item-value="slug"
                    :items="state.listPort"
                    clearable
                    return-object
                  ></v-select>
                </v-col>
                <v-col cols="12" class="mb-n6" v-if="isDestinationOther">
                  <v-text-field
                    label="port"
                    v-model="state.specificPort"
                  ></v-text-field>
                  <p class="error-feedback mb-5" v-if="v$.specificPort.$error">
                    {{ v$.specificPort.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-radio-group v-model="state.checkInterface" inline>
                    <v-row>
                      <v-col cols="6" v-for="area in state.isCombo" :key="area">
                        <v-radio :label="area" :value="area"></v-radio>
                      </v-col>
                    </v-row>
                  </v-radio-group>
                </v-col>
                <!-- <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Translation  target"
                    v-model="state.translateTarget"
                  ></v-text-field>
                </v-col> -->
                <template v-if="state.checkInterface === 'Static'">
                  <v-col cols="12" class="mb-n6">
                    <v-text-field
                      label="Enter Translation address from"
                      v-model="state.translationAddressFrom"
                    ></v-text-field>
                    <p
                      class="error-feedback mb-5"
                      v-if="v$.translationAddressFrom.$error"
                    >
                      {{ v$.translationAddressFrom.$errors[0].$message }}
                    </p>
                  </v-col>
                  <v-col cols="12" class="mb-n6">
                    <v-text-field
                      label="Enter Translation address to"
                      v-model="state.translationAddressTo"
                    ></v-text-field>
                    <p
                      class="error-feedback mb-5"
                      v-if="v$.translationAddressTo.$error"
                    >
                      {{ v$.translationAddressTo.$errors[0].$message }}
                    </p>
                  </v-col>
                  <v-col cols="12" class="mb-n6">
                    <v-text-field
                      label="Translation port"
                      v-model="state.translationPort"
                    ></v-text-field>
                  </v-col>
                </template>

                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Description"
                    v-model="state.description"
                  ></v-text-field>
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
              <span class="pr-3 pl-3" style="color: #213e9f">Cancel</span>
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
import { toRefs, watch, reactive, computed, inject, onMounted, ref } from "vue";
import { required, helpers, requiredIf } from "@vuelidate/validators";
import { getCookie } from "@/mixins/csrftoken.js";

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
      required: true,
    },
  },

  setup(props) {
    const emitter = inject("emitter");
    const { isOpen, editRow, modalMode } = toRefs(props);
    const numberList = ref(Array.from({ length: 32 }, (_, i) => i + 1));

    const state = reactive({
      isCombo: ["MASQ", "Static"],
      versionList: [
        { name: "IPv4", slug: "ipv4" },
        { name: "IPv6", slug: "ipv6" },
      ],
      protocolList: [
        { name: "Udp", slug: "udp" },
        { name: "Tcp", slug: "tcp" },
      ],
      listPort: [
        { name: "HTTP", slug: "80" },
        { name: "HTTPS", slug: "443" },
        { name: "FTP", slug: "21" },
        { name: "SSH", slug: "22" },
        { name: "Telnet", slug: "23" },
        { name: "SMTP", slug: "25" },
        { name: "DNS", slug: "53" },
        { name: "DHCP", slug: "67" },
        { name: "TFTP", slug: "69" },
        { name: "HTTP(alternative)", slug: "8080" },
        { name: "MySQL", slug: "3306" },
        { name: "PostgreSQL", slug: "5432" },
        { name: "RDP (Remote Desktop Protocol)", slug: "3389" },
        { name: "NTP (Network Time Protocol)", slug: "123" },
        { name: "SNMP (Simple Network Management Protocol)", slug: "161" },
        { name: "LDAP (Lightweight Directory Access Protocol)", slug: "389" },
        { name: "HTTPS (alternative)", slug: "8443" },
        { name: "SMTPS", slug: "465" },
        { name: "OTHER", slug: "other" },
      ],
      //
      // activateStatus: "",
      interface: "",
      tcpIpVersion: "",
      protocol: "",
      // source: "",
      sourceAddress: "",
      sourcePrefix: "",
      sourcePort: "",
      port: "",
      // destination: "",
      destinationAddress: "",
      destinationPrefix: "",
      destinationPort: "",
      specificPort: "",
      checkInterface: "MASQ",
      // translateTarget: "",
      translationAddressFrom: "",
      translationAddressTo: "",
      translationPort: "",
      description: "",
    });

    const isSourceOther = computed(() => {
      return state.sourcePort?.slug === "other";
    });
    const isDestinationOther = computed(() => {
      return state.destinationPort?.slug === "other";
    });

    onMounted(() => {
      getInterface();
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
        // populate(val);
      }
    );
    watch(
      () => modalMode.value,
      () => {
        if (modalMode.value === "create") {
          state.areaName = "";
          state.interfaces = [];
        }
      }
    );
    //   const populate = (data) => {
    //     if (modalMode.value === "edit") {
    //       state.areaName = data.name;
    //       state.id = data.id;

    //       let filtredInterface = [];
    //       data?.members.forEach((e) => {
    //         filtredInterface = [
    //           ...filtredInterface,
    //           ...state.mapedInterface.filter((i) => i.name === e),
    //         ];
    //       });
    //       state.interfaces = filtredInterface;
    //     }
    //   };

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

          state.mapedInterface = interfaces;
        },
        (error) => {
          console.log(error);
        }
      );
    };

    const closeModal = () => {
      emitter.emit("closeSnatModal");
      if (modalMode.value === "create") {
      }
    };

    const submitForm = async () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      const result = await v$.value.$validate();
      if (result) {
        let payload = {
          interface: state.interface.id,
          tcp_ip: state.tcpIpVersion?.slug ?? "",
          protocol: state.protocol?.slug ?? "",
          source_address: state.sourceAddress
            ? `${state.sourceAddress}/${state.sourcePrefix}`
            : "",
          source_port:
            state.sourcePort?.slug === "other"
              ? state.port
              : state.sourcePort?.slug
              ? state.sourcePort?.slug
              : "",
          destination_address: state.destinationAddress
            ? `${state.destinationAddress}/${state.destinationPrefix}`
            : "",
          destination_port:
            state.destinationPort?.slug === "other"
              ? state.specificPort
              : state.destinationPort?.slug
              ? state.destinationPort?.slug
              : "",
          snat_type: state.checkInterface,
          description: state.description,
        };
        if (state.checkInterface === "Static") {
          payload = {
            ...payload,
            translation_address_from: state.translationAddressFrom,
            translation_address_to: state.translationAddressTo,
            translation_port: state.translationPort,
          };
        }
        console.log("pay", payload);
        axios
          .post(`/nat/createSNat`, payload)
          .then((response) => {
            if (response.status == "201") {
              state.snackbar = true;
              state.color = "success";
              state.textAlert = response.data.msg;
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
        console.log("v$", v$.value);
      }
    };

    const rules = computed(() => {
      return {
        interface: { required },
        translationAddressFrom: {
          requiredIfFuction: helpers.withMessage(
            "Value is required",
            requiredIf(() => state.checkInterface === "Static")
          ),
          isValidDestinationAddress: helpers.withMessage(
            `Format must be like adresse IP : X.X.X.X`,

            helpers.regex(/^(\d{1,3}\.){3}\d{1,3}$/)
          ),
        },
        port: {
          requiredIfFuction: helpers.withMessage(
            "Value is required",
            requiredIf(() => state.sourcePort?.slug === "other")
          ),
        },
        specificPort: {
          requiredIfFuction: helpers.withMessage(
            "Value is required",
            requiredIf(() => state.destinationPort?.slug === "other")
          ),
        },
        sourcePrefix: {
          requiredIfFuction: helpers.withMessage(
            "Value is required",
            requiredIf(() => state.sourceAddress)
          ),
        },
        destinationPrefix: {
          requiredIfFuction: helpers.withMessage(
            "Value is required",
            requiredIf(() => state.destinationAddress)
          ),
        },

        sourceAddress: {
          isValidSourceAddress: helpers.withMessage(
            `Format must be like adresse IP : X.X.X.X`,

            helpers.regex(/^(\d{1,3}\.){3}\d{1,3}$/)
          ),
        },
        destinationAddress: {
          isValidDestinationAddress: helpers.withMessage(
            `Format must be like adresse IP : X.X.X.X`,

            helpers.regex(/^(\d{1,3}\.){3}\d{1,3}$/)
          ),
        },

        translationAddressTo: {
          isValidDestinationAddress: helpers.withMessage(
            `Format must be like adresse IP : X.X.X.X`,

            helpers.regex(/^(\d{1,3}\.){3}\d{1,3}$/)
          ),
        },
      };
    });

    const v$ = useValidate(rules, state);

    return {
      state,
      isSourceOther,
      isDestinationOther,
      v$,
      numberList,
      emitter,
      submitForm,
      closeModal,
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
.scroller {
  overflow: auto;
}
</style>
