<template>
  <v-overlay v-model="state.viewModal">
    <v-dialog
      v-model="state.isviewModal"
      persistent
      :scrim="false"
      width="auto"
    >
      <v-card color="#193286" class="alert-box">
        <v-card-title class="img-containter">
          <img
            src="@/assets/images/view.png"
            alt="logo"
            class="img-view"
            width="100"
            height="100"
        /></v-card-title>
        <v-card-text>
          {{ $t("profil.NoPermission") }}
          <br />
          {{ $t("profil.ContactAdmin") }}
        </v-card-text>

        <div class="mr-3 mb-5 d-flex justify-end">
          <VButton
            rounded
            outlined
            color="#ffffff"
            label-color="#213E9F"
            :label="$t('buttons.close')"
            :isLarge="true"
            @click="close"
          />
        </div>
      </v-card>
    </v-dialog>
  </v-overlay>
  <div class="mt-3">
    <v-overlay v-model="state.loading">
      <v-dialog
        v-model="state.isLoadingDialogue"
        :scrim="false"
        persistent
        width="auto"
      >
        <v-card color="#193286">
          <v-card-text>
            {{ $t("sdwan.pleaseWait") }}
            <v-progress-linear
              indeterminate
              color="white"
              class="mb-0"
            ></v-progress-linear>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-overlay>
    <div class="ml-3 mr-3 mt-5">
      <h4>{{ $t("dhcpV4.generalInformation") }}</h4>

      <v-divider class="mb-2"></v-divider>
    </div>
    <v-row class="ml-3 mr-3">
      <v-col cols="6">
        <v-row class="mt-2">
          <v-col cols="4" align-self="center">
            <label>{{ $t("dhcpV4.DHCPServer") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <input
              type="checkbox"
              hide-details
              disabled
              v-model="state.enable_dhcpv4"
            />
            <label class="ml-2"> {{ $t("dhcpV4.enableDHCPServer") }}</label>
          </v-col>
          <v-col cols="4" align-self="center">
            <label>{{ $t("dhcpV4.subnetAddress") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-text-field
              :label="$t('dhcpV4.subnetAddress')"
              v-model="state.subnet_addr"
              required
              readonly
            ></v-text-field>
            <p class="error-feedback mb-5" v-if="v$.subnet_addr.$error">
              {{ v$.subnet_addr.$errors[0].$message }}
            </p>
          </v-col>
          <v-col cols="4" align-self="center">
            <label>{{ $t("dhcpV4.subnetMask") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <!-- <label class="ml-2"> {{state.subnet_mask}}</label> -->
            <v-text-field
              :label="$t('dhcpV4.subnetMask')"
              v-model="state.subnet_mask"
              required
              readonly
            ></v-text-field>
            <p class="error-feedback mb-5" v-if="v$.subnet_mask.$error">
              {{ v$.subnet_mask.$errors[0].$message }}
            </p>
          </v-col>
          <v-col cols="4" align-self="center">
            <label>{{ $t("dhcpV4.availableRange") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-text-field
              :label="$t('dhcpV4.availableRange')"
              v-model="state.available_range"
              required
              readonly
            ></v-text-field>
            <p class="error-feedback mb-5" v-if="v$.available_range.$error">
              {{ v$.available_range.$errors[0].$message }}
            </p>
          </v-col>
          <!-- <v-col cols="4" align-self="center">
            <label>Range from</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-text-field v-model="state.range_from" required></v-text-field>
          </v-col>
          <v-col cols="4" align-self="center">
            <label>Range to</label>
          </v-col> -->
          <!-- <v-col cols="8" class="mb-n6">
            <v-text-field v-model="state.range_to" required></v-text-field>
          </v-col> -->

          <v-col cols="12">
            <div class="d-flex justify-end mt-3">
              <VButton
                rounded
                outlined
                color="#213E9F"
                label-color="#ffffff"
                :label="$t('buttons.Add')"
                :isLarge="true"
                type="submit"
                class="ml-2"
                @click="openModalAdd"
              />
            </div>
            <div style="overflow: hidden; flex-grow: 1">
              <ag-grid-vue
                id="grid-wrapper"
                domLayout="autoHeight"
                class="ag-theme-alpine mt-3"
                style="width: 100%"
                @grid-ready="onGridReady"
                :columnDefs="columnRanges"
                :rowData="rowDataRanges.value"
                :overlayNoRowsTemplate="overlayTemplate"
                :pagination="true"
                :paginationPageSize="5"
                :localeText="paginationLocalization"
              />
            </div>
          </v-col>
          <v-col cols="4" align-self="center">
            <label>{{ $t("dhcpV4.dnsServer") }}</label>
          </v-col>
          <template
            v-for="(row, index) in state.rows"
            :key="index"
            class="mt-0"
          >
            <v-col cols="4" align-self="center" v-if="index > 0"> </v-col>
            <v-col :cols="index !== 0 ? '7' : '8'" class="mb-n6">
              <v-text-field
                :label="$t('dhcpV4.dnsServer')"
                v-model="row.dns_server"
              ></v-text-field>
            </v-col>
            <v-col
              :cols="index !== 0 ? '1' : '0'"
              class="mt-4"
              v-if="index !== 0"
            >
              <v-icon
                color="red"
                @click="removeRow(index)"
                icon="mdi mdi-delete-circle"
              ></v-icon>
            </v-col>
          </template>

          <div style="margin-left: 35%; margin-top: 1%">
            <p class="error-feedback mb-5" v-if="state.textDnsServer">
              {{ state.textDnsServer }}
            </p>
          </div>
          <v-col cols="12" class="d-flex justify-end">
            <v-btn
              color="#F6F6F6"
              class="text-none"
              variant="flat"
              @click="addRow"
            >
              <svg
                width="17"
                height="17"
                viewBox="0 0 17 17"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <mask
                  id="mask0_50_190"
                  style="mask-type: luminance"
                  maskUnits="userSpaceOnUse"
                  x="0"
                  y="0"
                  width="17"
                  height="17"
                >
                  <path d="M17 0H0V17H17V0Z" fill="white" />
                </mask>
                <g mask="url(#mask0_50_190)">
                  <path
                    d="M8.70871 0.219971C10.3463 0.219971 11.9472 0.705584 13.3088 1.6154C14.6705 2.52522 15.7317 3.81838 16.3584 5.33135C16.9851 6.84432 17.1491 8.50916 16.8296 10.1153C16.5101 11.7215 15.7215 13.1968 14.5636 14.3548C13.4056 15.5128 11.9302 16.3014 10.3241 16.6209C8.7179 16.9404 7.05306 16.7764 5.54009 16.1497C4.02712 15.523 2.73396 14.4617 1.82414 13.1001C0.914324 11.7385 0.428711 10.1376 0.428711 8.49997C0.428976 6.30406 1.30142 4.19816 2.85416 2.64542C4.4069 1.09268 6.5128 0.220236 8.70871 0.219971Z"
                    fill="#086EAE"
                  />
                  <path
                    d="M13.6689 8.03597C13.7332 8.09478 13.7842 8.16654 13.8187 8.24652C13.8531 8.32651 13.8703 8.41289 13.8689 8.49997C13.8703 8.58779 13.8542 8.675 13.8216 8.75654C13.789 8.83808 13.7405 8.91233 13.6789 8.97497C13.6167 9.04086 13.5412 9.09277 13.4574 9.12725C13.3736 9.16173 13.2835 9.178 13.1929 9.17497H9.36591V12.981C9.36918 13.0709 9.35391 13.1606 9.32105 13.2443C9.28819 13.3281 9.23845 13.4042 9.17491 13.468C9.11435 13.5295 9.04187 13.578 8.96191 13.6105C8.88195 13.643 8.7962 13.6588 8.70991 13.657C8.62268 13.6583 8.53614 13.6412 8.45599 13.6068C8.37585 13.5723 8.30391 13.5212 8.24491 13.457C8.18336 13.3943 8.13487 13.3201 8.10225 13.2385C8.06963 13.157 8.05354 13.0698 8.05491 12.982V9.17697H4.22791C4.04915 9.17414 3.87848 9.10194 3.75197 8.97562C3.62546 8.84929 3.553 8.67873 3.54991 8.49997C3.54829 8.41285 3.5653 8.32639 3.59979 8.24637C3.63428 8.16635 3.68546 8.09462 3.74991 8.03597C3.81266 7.97421 3.88704 7.92552 3.96876 7.89274C4.05047 7.85995 4.13788 7.84371 4.22591 7.84497H8.05491V4.03797C8.04956 3.85273 8.11789 3.67292 8.24491 3.53797C8.30487 3.47498 8.37701 3.42483 8.45694 3.39056C8.53688 3.35629 8.62294 3.33862 8.70991 3.33862C8.79688 3.33862 8.88294 3.35629 8.96288 3.39056C9.04281 3.42483 9.11495 3.47498 9.17491 3.53797C9.3023 3.67276 9.37099 3.85259 9.36591 4.03797V7.84497H13.1929C13.2809 7.84377 13.3683 7.86003 13.45 7.89281C13.5317 7.9256 13.6061 7.97426 13.6689 8.03597Z"
                    fill="white"
                  />
                </g>
              </svg>
              <span class="ml-2" style="color: #086eae">{{
                $t("buttons.Add")
              }}</span>
            </v-btn>
          </v-col>

          <v-col cols="4" align-self="center">
            <label>{{ $t("dhcpV4.gateway") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-text-field
              :label="$t('dhcpV4.gateway')"
              v-model="state.gateway"
              required
            ></v-text-field>
            <p class="error-feedback mb-5" v-if="v$.gateway.$error">
              {{ v$.gateway.$errors[0].$message }}
            </p>
          </v-col>

          <v-col cols="4" align-self="center">
            <label>{{ $t("dhcpV4.domainName") }}</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-text-field
              :label="$t('dhcpV4.domainName')"
              v-model="state.domain_name"
              required
            ></v-text-field>
          </v-col>
        </v-row>
      </v-col>
    </v-row>

    <ModalAddRanges
      :isOpen="state.isModalOpen"
      :editRow="state.editRow"
      :modalMode="state.modalMode"
      :rowDataList="rowDataRanges.value"
      :initialRanges="state.available_range"
    />

    <v-row class="flex py-8 mb-5">
      <v-col cols="4"> </v-col>
      <v-col>
        <div class="mr-3 flex center">
          <VButton
            rounded
            outlined
            color="#ffffff"
            label-color="#213E9F"
            :label="$t('buttons.cancel')"
            :isLarge="true"
            @click="cancel"
          />
          <VButton
            rounded
            outlined
            color="#213E9F"
            label-color="#ffffff"
            :label="$t('buttons.save')"
            :isLarge="true"
            class="ml-2"
            @click="submitForm"
          />
        </div>
      </v-col>
    </v-row>
  </div>

  <v-alert
    v-model="state.snackbar"
    :type="state.color"
    class="d-flex mt-3"
    style="position: fixed; top: 80px; right: 10px"
  >
    <span class="c-o ml-3">
      <strong>{{ state.color }} </strong> {{ state.textAlert }}
    </span>
    <span class="ml-16" style="margin-top: 20px !important">
      <i class="fas fa-times justify-end cursor" @click="handleRemove"></i>
    </span>
  </v-alert>
</template>

<script>
import { useI18n } from "vue-i18n";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import axios from "axios";
import VButton from "@/components/VButton.vue";
import UsersList from "../../system/user/components/UsersList.vue";
import { reactive, onMounted, ref, inject, computed } from "vue";
import ModalAddRanges from "@/components/modals/ModalAddRanges.vue";
import { v4 as uuidv4 } from "uuid";
import useValidate from "@vuelidate/core";
import { required, helpers, requiredIf, email } from "@vuelidate/validators";
import { user_privilege } from "@/mixins/user_privilege.js";

export default {
  name: "ConfigServerDhcp4Component",
  components: {
    UsersList,
    VButton,
    AgGridVue,
    ModalAddRanges,
  },
  props: {
    configInfo: {},
  },
  setup(props) {
    const { t } = useI18n();
    const overlayTemplate = ref("");
    const paginationLocalization = reactive({
      of: "/",
    });
    const emitter = inject("emitter");
    const switchValue = ref(false);
    const state = reactive({
      textDnsServer: "",
      isviewModal: false,
      viewModal: false,
      rows: [{ dns_server: "" }],
      //
      modalData: {},
      modalMode: "",
      isModalOpen: false,
      isOpen: null,
      editRow: {},
      //
      loading: false,
      isLoadingDialogue: false,

      snackbar: false,
      color: "",
      textAlert: "",
      //General information
      enable_dhcpv4: true,
      subnet_addr: null,
      subnet_mask: null,
      available_range: null,
      range_from: [],
      range_to: [],
      dns_server: [],
      gateway: null,
      domain_name: null,
    });

    const gridApi = ref(null);

    const close = () => {
      state.isviewModal = false;
      state.viewModal = false;
    };

    const rangeFrom = computed(() => {
      return t("dhcpV4.rangeFrom");
    });
    const rangeTo = computed(() => {
      return t("dhcpV4.rangeTo");
    });

    const columnRanges = ref([
      {
        headerName: rangeFrom,
        field: "range_from",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: rangeTo,
        field: "range_to",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Actions",
        cellRenderer: actionCellRenderer,
        field: "actions",
        width: 150,
      },
    ]);
    const rowDataRanges = reactive({});
    // state.enable_dhcpv4 = props.configInfo.enable_dhcpv4;
    state.subnet_addr = props.configInfo.subnet_addr;
    state.subnet_mask = props.configInfo.subnet_mask;
    state.available_range = props.configInfo.available_range;
    console.log("state.available_range", state.available_range);
    state.range_from = props.configInfo.range_from;
    state.range_to = props.configInfo.range_to;
    state.dns_server = props.configInfo.dns_server;
    state.gateway = props.configInfo.gateway;
    state.domain_name = props.configInfo.domain_name;

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

    const addRow = () => {
      const user = user_privilege();
      if (user === "viewer") {
        console.log("View Mode");
        state.isviewModal = true;
        state.viewModal = true;
      } else {
        state.rows.push({
          dns_server: "",
        });
      }
    };
    const removeRow = (index) => {
      const user = user_privilege();
      if (user === "viewer") {
        console.log("View Mode");
        state.isviewModal = true;
        state.viewModal = true;
      } else {
        state.rows.splice(index, 1);
      }
    };
    const handleRemove = () => {
      state.snackbar = false;
    };

    onMounted(async () => {
      overlayTemplate.value = `<span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
    </svg></span>`;

      emitter.on("closeModalAddRange", () => {
        state.isModalOpen = false;
        state.isOpen = false;
        state.modalMode = "";
        state.editRow = {};
      });
      emitter.on("add-range", (data) => {
        if (data.idConf === props.configInfo.id) {
          if (!rowDataRanges.value) {
            rowDataRanges.value = [];
          }

          let test = {
            uuid: data.uuid,
            range_from: data.range_from,
            range_to: data.range_to,
          };
          rowDataRanges.value.push(test);
          if (gridApi.value) {
            gridApi.value.setRowData(rowDataRanges.value);
          } else {
            console.error("Grid API.");
          }
        }
      });

      function updateObjectById(uuid, updatedObject) {
        const index = rowDataRanges.value.findIndex((obj) => obj.uuid === uuid);

        if (index !== -1) {
          rowDataRanges.value[index] = {
            ...rowDataRanges.value[index],
            ...updatedObject,
          };
        }
      }

      emitter.on("edit-range", (data) => {
        let test = {
          uuid: data.uuid,
          range_from: data.range_from,
          range_to: data.range_to,
        };

        updateObjectById(data.uuid, test);

        if (!rowDataRanges.value) {
          rowDataRanges.value = [];
        }

        if (gridApi.value) {
          gridApi.value.setRowData(rowDataRanges.value);
        } else {
          console.error("Grid API.");
        }
      });

      rowDataRanges.value = props.configInfo.ranges_address.map((i) => {
        return {
          uuid: uuidv4(),
          range_from: i.range_from,
          range_to: i.range_to,
        };
      });
      if (props.configInfo.dns_server != null) {
        let filtredServer = props.configInfo.dns_server.map((i) => {
          return {
            dns_server: i,
          };
        });
        state.rows = filtredServer;
      } else {
        state.rows = [{ dns_server: "" }];
      }

      if (!rowDataRanges.value) {
        rowDataRanges.value = [];
      }

      if (gridApi.value) {
        gridApi.value.setRowData(rowDataRanges.value);
      } else {
        console.error("Grid API.");
      }
    });

    const formatBeLike = computed(() => {
      return t("errors.formatMustBeLikeAdresseIP");
    });
    const error = computed(() => {
      return t("errors.valueRequired");
    });

    const rules = computed(() => {
      return {
        available_range: { required: helpers.withMessage(error, required) },
        subnet_mask: { required: helpers.withMessage(error, required) },
        subnet_addr: { required: helpers.withMessage(error, required) },
        gateway: {
          isValidlRemoteGateway: helpers.withMessage(
            formatBeLike,

            helpers.regex(
              /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
            )
          ),
        },
      };
    });

    const v$ = useValidate(rules, state);

    const openModalAdd = () => {
      const user = user_privilege();
      if (user === "viewer") {
        console.log("View Mode");
        state.isviewModal = true;
        state.viewModal = true;
      } else {
        state.modalData = {};
        state.modalMode = "create";
        state.isModalOpen = true;
        emitter.emit("id-range", props.configInfo.id);
      }
    };

    const onGridReady = (params) => {
      gridApi.value = params.api;
      if (gridApi.value) {
        gridApi.value.setRowData(rowDataRanges.value);
      } else {
        console.error("Grid API.");
      }
    };

    function actionCellRenderer(params) {
      let eGui = document.createElement("div");

      eGui.innerHTML = `
      <button class="action-button edit" data-action="edit">
        <i class="far fa-edit" style="color: #086eae;"></i>
      </button>
      <button
        class="action-button delete"
        data-action="delete">
          <i class="fas fa-times" style="color: #086eae;"></i>
      </button>
      `;

      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          handleAction(action, params.node.data, params.node.rowIndex);
        });
      });

      const handleAction = (action, rowData) => {
        const user = user_privilege();
        switch (action) {
          case "edit":
            if (user === "viewer") {
              console.log("View Mode");
              state.isviewModal = true;
              state.viewModal = true;
            } else {
              state.modalData = {};
              state.modalMode = "edit";
              state.isModalOpen = true;
              state.editRow = rowData;
            }

            break;
          case "delete":
            if (user === "viewer") {
              console.log("View Mode");
              state.isviewModal = true;
              state.viewModal = true;
            } else {
              const index = rowDataRanges.value.findIndex(
                (item) => item.id === rowData.id
              );

              if (index !== -1) {
                rowDataRanges.value.splice(index, 1);
                if (gridApi.value) {
                  gridApi.value.setRowData(rowDataRanges.value);
                } else {
                  console.error("Grid API.");
                }
              }
            }

            break;
          default:
            break;
        }
      };

      return eGui;
    }
    const hasEmptyProperty = (obj) => {
      var invalidHostChars =
        !/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(
          obj.dns_server
        ) && obj.dns_server != "";
      return invalidHostChars;
    };

    const hasDuplicates = (arr) => {
      const uniqueAddresses = new Set(arr.map((item) => item.dns_server));
      return uniqueAddresses.size !== arr.length;
    };

    const submitForm = async () => {
      const user = user_privilege();
      const result = await v$.value.$validate();
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      if (user === "viewer") {
        console.log("View Mode");
        state.isviewModal = true;
        state.viewModal = true;
      } else {
        if (!rowDataRanges.value) {
          rowDataRanges.value = [];
        }
        if (rowDataRanges.value.length === 0) {
          state.snackbar = true;
          state.color = "error";
          state.textAlert = t("errors.minimumOneRange");
          setTimeout(() => {
            state.snackbar = false;
          }, 2000);
          return;
        }

        if (result) {
          var hasEmptyElement = state.rows.some(hasEmptyProperty);

          if (hasEmptyElement) {
            state.snackbar = true;
            state.color = "error";
            state.textAlert = t("errors.formatMustBeLikeAdresseIP");
            setTimeout(() => {
              state.snackbar = false;
            }, 2000);
            return;
          }
          let dup = hasDuplicates(state.rows);
          console.log("dup", dup);
          if (dup) {
            // state.snackbar = true;
            // state.color = "error";
            state.textDnsServer = t("duplicatedServer");
            setTimeout(() => {
              state.textDnsServer = "";
            }, 1000);
            return;
          }

          let mapredRow = rowDataRanges.value.map((e) => {
            return {
              range_from: e.range_from,
              range_to: e.range_to,
            };
          });

          let mapredServer = state.rows
            .filter((i) => i.dns_server != "")
            .map((e) => e.dns_server);

          let payload = {
            enable_dhcpv4: state.enable_dhcpv4,
            subnet_addr: state.subnet_addr,
            subnet_mask: state.subnet_mask,
            available_range: state.available_range,
            dns_server: mapredServer,
            gateway: state.gateway,
            domain_name: state.domain_name,
            ranges_address: mapredRow,
          };

          state.loading = true;
          state.isLoadingDialogue = true;

          axios
            .put(
              `/server_dhcp4/updateDhcp4Server/${props.configInfo.id}`,
              payload
            )
            .then((response) => {
              if (response.status == 200) {
                state.loading = false;
                state.isLoadingDialogue = false;
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.msg;
                setTimeout(() => {
                  state.snackbar = false;
                  location.reload();
                }, 3000);
              }
            })
            .catch((i) => {
              state.loading = false;
              state.isLoadingDialogue = false;

              if (i.response.status === 500) {
                state.snackbar = true;
                state.color = "red";
                state.textAlert = t("errors.errorServer");
              } else {
                state.snackbar = true;
                state.color = "red";
                state.textAlert = i.response.data.msg;
              }
            });
        } else {
          console.log("error", v$.value);

          var hasEmptyElement = state.rows.some(hasEmptyProperty);

          if (hasEmptyElement) {
            state.snackbar = true;
            state.color = "error";
            state.textAlert = t("errors.formatMustBeLikeAdresseIP");
            setTimeout(() => {
              state.snackbar = false;
            }, 2000);
            return;
          }
          let dup = hasDuplicates(state.rows);
          if (dup) {
            state.snackbar = true;
            state.color = "error";
            state.textAlert = t("duplicatedServer");
            return;
          }
        }
      }
    };

    return {
      switchValue,
      overlayTemplate,
      v$,
      close,
      getCookie,
      submitForm,
      openModalAdd,
      onGridReady,
      rowDataRanges,
      addRow,
      removeRow,
      columnRanges,
      paginationLocalization,
      state,
      handleRemove,
      emitter,
    };
  },
};
</script>
<style lang="scss">
.error-feedback {
  color: orange;
  font-size: 0.85em;
}

.label-style {
  color: #020202;
  font-family: Nunito;
  font-size: 15px;
  font-style: normal;
  font-weight: 300;
  line-height: normal;
}

/* CSS to style the text */
.text-xs {
  font-size: 12px;
  /* Example font size for small text */
}

.container {
  height: 50px;
}
</style>
