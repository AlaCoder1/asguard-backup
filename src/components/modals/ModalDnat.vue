<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm" class="scroller">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              {{ $t("nat.create_msg_dnat") }}</span
            >
            <span class="headline" v-if="modalMode === 'edit'">
              {{ $t("nat.update_msg_dnat") }}</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.interface"
                    :label="$t('nat.interface')"
                    :no-data-text="$t('nat.msg_no_data')"
                    item-title="name"
                    item-value="id"
                    :items="state.mapedInterface"
                    return-object
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.interface.$error">
                    {{ v$.interface.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.tcpIpVersion"
                    :label="$t('nat.select_protocol')"
                    :no-data-text="$t('nat.msg_no_data')"
                    item-title="name"
                    item-value="id"
                    :items="state.versionList"
                    clearable
                    return-object
                  ></v-select>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.protocol"
                    :label="$t('nat.select_protocol')"
                    :no-data-text="$t('nat.msg_no_data')"
                    item-title="name"
                    item-value="id"
                    :items="state.protocolList"
                    clearable
                    return-object
                  ></v-select>
                </v-col>

                <v-col cols="7" class="mb-n6">
                  <v-text-field
                    :label="$t('nat.ent_saddr')"
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
                    :label="$t('nat.prefix')"
                    v-model="state.sourcePrefix"
                    :items="numberList"
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.sourcePrefix.$error">
                    {{ v$.sourcePrefix.$errors[0].$message }}
                  </p>
                </v-col>

                <v-col cols="6" class="mb-n6 mt-3">
                  <span>{{ $t("nat.sport_range") }} </span>
                </v-col>
                <v-col cols="3" class="mb-n6">
                  <v-select
                    :label="$t('nat.from')"
                    v-model="state.sourceRangeFrom"
                    :no-data-text="$t('nat.msg_no_data')"
                    :items="state.listPort"
                    item-title="name"
                    item-value="slug"
                    return-object
                  ></v-select>
                  <v-text-field
                    v-if="state.sourceRangeFrom.slug === 'other'"
                    :label="$t('nat.from')"
                    v-model="state.specificSourceFrom"
                  ></v-text-field>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.specificSourceFrom.$error"
                  >
                    {{ v$.specificSourceFrom.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="3" class="mb-n6">
                  <v-select
                    :label="$t('nat.to')"
                    v-model="state.sourceRangeTo"
                    :items="state.listPortSourceTo"
                    :no-data-text="$t('nat.msg_no_data')"
                    item-title="name"
                    item-value="slug"
                    return-object
                  ></v-select>
                  <v-text-field
                    v-if="state.sourceRangeTo.slug === 'other'"
                    label="To"
                    v-model="state.specificSourceTo"
                  ></v-text-field>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.specificSourceTo.$error"
                  >
                    {{ v$.specificSourceTo.$errors[0].$message }}
                  </p>
                </v-col>
                <p
                  class="error-feedback mb-5 ml-5"
                  v-if="
                    state.specificSourceFrom &&
                    state.specificSourceTo &&
                    !isHightSpecificSource
                  "
                >
                  {{ $t("nat.msg_validation_port") }}
                </p>

                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="$t('nat.ent_ext_add')"
                    v-model="state.externalAddress"
                  ></v-text-field>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.externalAddress.$error"
                  >
                    {{ v$.externalAddress.$errors[0].$message }}
                  </p>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="$t('nat.ent_int_add')"
                    v-model="state.internalAddress"
                  ></v-text-field>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.internalAddress.$error"
                  >
                    {{ v$.internalAddress.$errors[0].$message }}
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
                <template v-if="state.checkInterface === 'Port Forwarding'">
                  <v-col cols="6" class="mb-n6 mt-3">
                    <span>{{ $t("nat.dport_range") }}</span>
                  </v-col>
                  <v-col cols="3" class="mb-n6">
                    <v-select
                      :label="$t('nat.from')"
                      :no-data-text="$t('nat.msg_no_data')"
                      v-model="state.destinationRangeFrom"
                      :items="state.listPort"
                      item-title="name"
                      item-value="slug"
                      return-object
                    ></v-select>
                    <v-text-field
                      v-if="state.destinationRangeFrom.slug === 'other'"
                      :label="$t('nat.from')"
                      v-model="state.specificDestinationFrom"
                    ></v-text-field>
                    <p
                      class="error-feedback mb-5"
                      v-if="v$.specificDestinationFrom.$error"
                    >
                      {{ v$.specificDestinationFrom.$errors[0].$message }}
                    </p>

                    <p
                      class="error-feedback mb-5"
                      v-if="v$.destinationRangeFrom.$error"
                    >
                      {{ v$.destinationRangeFrom.$errors[0].$message }}
                    </p>
                  </v-col>
                  <v-col cols="3" class="mb-n6">
                    <v-select
                      :label="$t('nat.to')"
                      v-model="state.destinationRangeTo"
                      :items="state.listPortDestinationTo"
                      :no-data-text="$t('nat.msg_no_data')"
                      item-title="name"
                      item-value="slug"
                      return-object
                    ></v-select>
                    <v-text-field
                      v-if="state.destinationRangeTo.slug === 'other'"
                      :label="$t('nat.to')"
                      v-model="state.specificDestinationTo"
                    ></v-text-field>
                    <p
                      class="error-feedback mb-5"
                      v-if="v$.specificDestinationTo.$error"
                    >
                      {{ v$.specificDestinationTo.$errors[0].$message }}
                    </p>

                    <p
                      class="error-feedback mb-5"
                      v-if="v$.destinationRangeTo.$error"
                    >
                      {{ v$.destinationRangeTo.$errors[0].$message }}
                    </p>
                  </v-col>

                  <p
                    class="error-feedback mb-5 ml-5"
                    v-if="
                      state.specificDestinationFrom &&
                      state.specificDestinationTo &&
                      !isHightSpecificDestination
                    "
                  >
                    {{ $t("nat.msg_validation_port") }}
                  </p>

                  <v-col cols="12" class="mb-n6">
                    <v-select
                      :label="$t('nat.port')"
                      v-model.number="state.port"
                      :no-data-text="$t('nat.msg_no_data')"
                      :items="state.listPort"
                      item-title="name"
                      item-value="slug"
                      return-object
                    ></v-select>

                    <v-text-field
                      v-if="state.port.slug === 'other'"
                      :label="$t('nat.port')"
                      v-model="state.specificPort"
                    ></v-text-field>
                    <p
                      class="error-feedback mb-5"
                      v-if="v$.specificPort.$error"
                    >
                      {{ v$.specificPort.$errors[0].$message }}
                    </p>

                    <p class="error-feedback mb-5" v-if="v$.port.$error">
                      {{ v$.port.$errors[0].$message }}
                    </p>
                  </v-col>
                </template>

                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="$t('nat.description')"
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
              <span class="pr-3 pl-3" style="color: #213e9f">{{
                $t("firewall.cancel")
              }}</span>
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
              :disabled="isfalse || isfalseSpecific"
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
import { useI18n } from "vue-i18n";

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
    const { t } = useI18n();
    const emitter = inject("emitter");
    const { isOpen, editRow, modalMode } = toRefs(props);
    const numberList = ref(Array.from({ length: 32 }, (_, i) => i + 1));

    const state = reactive({
      id: null,
      //list
      isCombo: ["Forwarding", "Port Forwarding"],
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
      listPortSourceTo: [],
      listPortDestinationTo: [],
      //
      interface: "",
      tcpIpVersion: { name: "IPv4", slug: "ipv4" },
      protocol: "",
      sourceAddress: "",
      sourcePrefix: "",
      destination: "",
      checkInterface: "Forwarding",

      //
      sourceRangeFrom: "",
      sourceRangeTo: "",
      internalAddress: "",
      externalAddress: "",
      description: "",
      port: "",
      //
      destinationRangeFrom: "",
      destinationRangeTo: "",

      //port other
      specificSourceFrom: "",
      specificSourceTo: "",

      specificDestinationFrom: "",
      specificDestinationTo: "",

      specificPort: "",
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
        populate(val);
      }
    );
    watch(
      () => modalMode.value,
      () => {
        if (modalMode.value === "create") {
          state.interface = "";
          state.tcpIpVersion = { name: "IPv4", slug: "ipv4" };
          state.protocol = "";
          state.sourceAddress = "";
          state.sourcePrefix = "";
          state.destination = "";
          state.checkInterface = "Forwarding";

          //
          state.sourceRangeFrom = "";
          state.sourceRangeTo = "";
          state.internalAddress = "";
          state.externalAddress = "";
          state.description = "";
          state.port = "";
          //
          state.destinationRangeFrom = "";
          state.destinationRangeTo = "";

          //port other
          state.specificSourceFrom = "";
          state.specificSourceTo = "";

          state.specificDestinationFrom = "";
          state.specificDestinationTo = "";

          state.specificPort = "";
        }
      }
    );

    watch(
      () => state.sourceRangeFrom,
      (val) => {
        if (val.slug) {
          state.listPortSourceTo = state.listPort.filter(
            (i) => i.slug >= val.slug
          );
        }
      }
    );
    watch(
      () => state.destinationRangeFrom,
      (val) => {
        if (val.slug) {
          state.listPortDestinationTo = state.listPort.filter(
            (i) => i.slug >= val.slug
          );
        }
      }
    );
    watch(
      () => state.checkInterface,
      (val) => {
        if (val === "Forwarding") {
          state.port = "";
          state.destinationRangeTo = "";
          state.destinationRangeFrom = "";
        }
      }
    );

    const populate = (data) => {
      if (modalMode.value === "edit") {
        console.log("data*", data);

        state.id = data.id;

        let filtredInterface = state.mapedInterface.filter(
          (i) => i.id === data?.interface
        );
        let filtredIpVersion = state.versionList.filter(
          (i) => i.slug === data?.tcp_ip
        );
        let filtredProtocol = state.protocolList.filter(
          (i) => i.slug === data?.protocol
        );

        state.interface = filtredInterface[0];
        state.tcpIpVersion = filtredIpVersion[0];
        state.protocol = filtredProtocol[0];

        let resultSource = data?.source_address
          ? data?.source_address?.split("/")
          : "";
        if (resultSource) {
          resultSource[1] = parseInt(resultSource[1], 10);
        }
        state.sourceAddress = resultSource ? resultSource[0] : "";
        state.sourcePrefix = resultSource ? resultSource[1] : "";

        let filtredSourcePortFrom = state.listPort.filter(
          (i) => i.slug === data?.source_port_from
        );

        if (filtredSourcePortFrom.length == 0) {
          state.sourceRangeFrom = data?.source_port_from
            ? { name: "OTHER", slug: "other" }
            : "";
          state.specificSourceFrom = data.source_port_from;
        } else {
          state.sourceRangeFrom = filtredSourcePortFrom[0];
        }

        let filtredSourcePorTo = state.listPort.filter(
          (i) => i.slug === data?.source_port_from
        );

        if (filtredSourcePorTo.length == 0) {
          state.sourceRangeTo = data?.source_port_from
            ? { name: "OTHER", slug: "other" }
            : "";
          state.specificSourceTo = data.source_port_to;
        } else {
          state.sourceRangeTo = filtredSourcePorTo[0];
        }

        state.externalAddress = data.external_address;
        state.internalAddress = data.internal_address;

        state.checkInterface = data.destination_port
          ? "Port Forwarding"
          : "Forwarding";

        let filtredPort = state.listPort.filter(
          (i) => i.slug === data?.destination_port
        );

        if (filtredPort.length == 0) {
          state.port = data.destination_port
            ? { name: "OTHER", slug: "other" }
            : "";
          state.specificPort = data.destination_port;
        } else {
          state.port = filtredPort[0];
        }

        let filtredDestinationPortFrom = state.listPort.filter(
          (i) => i.slug === data?.destination_port_from
        );

        if (filtredDestinationPortFrom.length == 0) {
          state.destinationRangeFrom = data?.destination_port_from
            ? { name: "OTHER", slug: "other" }
            : "";
          state.specificDestinationFrom = data.destination_port_from;
        } else {
          state.destinationRangeFrom = filtredDestinationPortFrom[0];
        }

        let filtredDestinationPortTo = state.listPort.filter(
          (i) => i.slug === data?.destination_port_to
        );

        if (filtredDestinationPortTo.length == 0) {
          state.destinationRangeTo = data?.destination_port_to
            ? { name: "OTHER", slug: "other" }
            : "";
          state.specificDestinationTo = data.destination_port_to;
        } else {
          state.destinationRangeTo = filtredDestinationPortTo[0];
        }

        state.description = data.description;
      }
    };

    const getInterface = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/network/AllInterfaces").then(
        (response) => {
          let filtredInterface = response.data.filter(
            (i) =>
              !i.ifname.startsWith("tun_") &&
              !i.ifname.startsWith("tap_") &&
              !i.name_interface.startsWith("VXLAN") &&
              !i.name_interface.startsWith("VLAN")
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
      emitter.emit("closeDnatModal");
      if (modalMode.value === "create") {
        state.interface = "";
        state.tcpIpVersion = { name: "IPv4", slug: "ipv4" };
        state.protocol = "";
        state.sourceAddress = "";
        state.sourcePrefix = "";
        state.destination = "";
        state.checkInterface = "Forwarding";

        //
        state.sourceRangeFrom = "";
        state.sourceRangeTo = "";
        state.internalAddress = "";
        state.externalAddress = "";
        state.description = "";
        state.port = "";
        //
        state.destinationRangeFrom = "";
        state.destinationRangeTo = "";

        //port other
        state.specificSourceFrom = "";
        state.specificSourceTo = "";

        state.specificDestinationFrom = "";
        state.specificDestinationTo = "";

        state.specificPort = "";
      }
    };

    const isHightSpecificSource = computed(() => {
      return (
        parseInt(state.specificSourceTo) >= parseInt(state.specificSourceFrom)
      );
    });
    const isHightSpecificDestination = computed(() => {
      return (
        parseInt(state.specificDestinationTo) >=
        parseInt(state.specificDestinationFrom)
      );
    });
    const isfalse = computed(() => {
      if (
        state.specificDestinationFrom &&
        state.specificDestinationTo &&
        !isHightSpecificDestination.value
      )
        return true;
      else return false;
    });
    const isfalseSpecific = computed(() => {
      if (
        state.specificSourceFrom &&
        state.specificSourceTo &&
        !isHightSpecificSource.value
      )
        return true;
      else return false;
    });

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
          source_port_from:
            state.sourceRangeFrom?.slug === "other"
              ? state.specificSourceFrom
              : state.sourceRangeFrom?.slug
              ? state.sourceRangeFrom?.slug
              : "",

          source_port_to:
            state.sourceRangeTo?.slug === "other"
              ? state.specificSourceTo
              : state.sourceRangeTo?.slug
              ? state.sourceRangeTo?.slug
              : "",
          external_address: state.externalAddress,
          internal_address: state.internalAddress,
          port_forwarding: state.checkInterface === "Forwarding" ? false : true,
          description: state.description,
        };
        if (state.checkInterface === "Port Forwarding") {
          payload = {
            ...payload,
            destination_port_from:
              state.destinationRangeFrom.slug === "other"
                ? state.specificDestinationFrom
                : state.destinationRangeFrom?.slug
                ? state.destinationRangeFrom?.slug
                : "",

            destination_port_to:
              state.destinationRangeTo.slug === "other"
                ? state.specificDestinationTo
                : state.destinationRangeTo?.slug
                ? state.destinationRangeTo?.slug
                : "",

            destination_port:
              state.port.slug === "other"
                ? state.specificPort
                : state.port?.slug
                ? state.port?.slug
                : "",
          };
        }

        if (modalMode.value === "edit") {
          console.log("payload", payload);
          axios
            .put(`/nat/updateDNat/${state.id}`, payload)
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
              if (i.response.status === 500) {
                state.snackbar = true;
                state.color = "red";
                state.textAlert = t("errors.errorServer");
              } else {
                state.snackbar = true;
                state.color = "red";
                state.textAlert = i.response.data.error;
              }
            });
        } else {
          axios
            .post(`/nat/createDNat`, payload)
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
              if (i.response.status === 500) {
                state.snackbar = true;
                state.color = "red";
                state.textAlert = t("errors.errorServer");
              } else {
                state.snackbar = true;
                state.color = "red";
                state.textAlert = i.response.data.error;
              }
            });
        }
      } else {
        console.log("v$", v$.value);
      }
    };
    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const formaaddress = computed(() => {
      return t("errors.formatMustBeLikeAdresseIP");
    });
    const onlynumbers = computed(() => {
      return t("errors.ChampIncludeOnlyNumbers");
    });

    const rules = computed(() => {
      return {
        interface: { required: helpers.withMessage(error, required) },

        sourceAddress: {
          isValidSourceAddress: helpers.withMessage(
            formaaddress,

            helpers.regex(
              /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
            )
          ),
        },

        sourcePrefix: {
          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(() => state.sourceAddress)
          ),
        },

        internalAddress: {
          required: helpers.withMessage(error, required),
          isValidSourceAddress: helpers.withMessage(
            formaaddress,

            helpers.regex(
              /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
            )
          ),
        },
        externalAddress: {
          required: helpers.withMessage(error, required),
          isValidSourceAddress: helpers.withMessage(
            formaaddress,

            helpers.regex(
              /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
            )
          ),
        },

        destinationRangeFrom: {
          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(() => state.checkInterface === "Port Forwarding")
          ),
        },
        destinationRangeTo: {
          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(() => state.checkInterface === "Port Forwarding")
          ),
        },
        port: {
          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(() => state.checkInterface === "Port Forwarding")
          ),
        },

        specificSourceFrom: {
          isValidSpecificSourceFrom: helpers.withMessage(
            onlynumbers,

            helpers.regex(/^[0-9]+$/)
          ),
          requiredIfFuction: helpers.withMessage(
            onlynumbers,
            requiredIf(() => state.sourceRangeFrom.slug === "other")
          ),
        },

        specificSourceTo: {
          isValidSpecificSourceTo: helpers.withMessage(
            onlynumbers,

            helpers.regex(/^[0-9]+$/)
          ),
          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(() => state.sourceRangeTo.slug === "other")
          ),
        },

        specificDestinationFrom: {
          isValidSpecificSourceTo: helpers.withMessage(
            onlynumbers,

            helpers.regex(/^[0-9]+$/)
          ),
          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(() => state.destinationRangeFrom.slug === "other")
          ),
        },
        specificDestinationTo: {
          isValidSpecificSourceTo: helpers.withMessage(
            onlynumbers,

            helpers.regex(/^[0-9]+$/)
          ),
          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(() => state.destinationRangeTo.slug === "other")
          ),
        },

        specificPort: {
          isValidSpecificSourceTo: helpers.withMessage(
            onlynumbers,

            helpers.regex(/^[0-9]+$/)
          ),
          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(() => state.port.slug === "other")
          ),
        },
      };
    });

    const v$ = useValidate(rules, state);

    return {
      isfalse,
      isfalseSpecific,
      state,
      v$,
      numberList,
      emitter,
      isHightSpecificSource,
      isHightSpecificDestination,
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
