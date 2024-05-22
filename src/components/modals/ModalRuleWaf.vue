<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm" class="scroller">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              {{ $t("sdwan.createNewRule") }}</span
            >
            <span class="headline" v-if="modalMode === 'edit'">
              {{ $t("sdwan.updateRule") }}</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="$t('sdwan.ruleName')"
                    v-model="state.ruleName"
                  ></v-text-field>
                  <p class="error-feedback mb-5" v-if="v$.ruleName.$error">
                    {{ v$.ruleName.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.variable"
                    label="Variable"
                    item-title="name"
                    item-value="slug"
                    :items="state.listVariable"
                    return-object
                    :no-data-text="$t('certificat.certificatlist')"
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.variable.$error">
                    {{ v$.variable.$errors[0].$message }}
                  </p>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.operator"
                    :label="$t('Waf.operator')"
                    item-title="name"
                    item-value="slug"
                    :items="state.listOperator"
                    return-object
                    :no-data-text="$t('certificat.certificatlist')"
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.operator.$error">
                    {{ v$.operator.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.transformationFun"
                    :label="$t('Waf.transformations')"
                    item-title="name"
                    item-value="slug"
                    :items="state.listTrans"
                    return-object
                    :no-data-text="$t('certificat.certificatlist')"
                  ></v-select>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.transformationFun.$error"
                  >
                    {{ v$.transformationFun.$errors[0].$message }}
                  </p>
                </v-col>

                <v-col cols="4">
                  <label>{{ $t("Waf.activate") }}</label>
                </v-col>
                <v-col cols="8" class="mb-n6">
                  <input
                    type="checkbox"
                    hide-details
                    v-model="state.xml_request"
                  />
                  <label class="ml-2">{{ $t("Waf.useTransformation") }}</label>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="$t('Waf.typeTransformations')"
                    v-model="state.typeTransf"
                  ></v-text-field>
                  <p class="error-feedback mb-5" v-if="v$.typeTransf.$error">
                    {{ v$.typeTransf.$errors[0].$message }}
                  </p>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.actions"
                    label="Actions"
                    item-title="name"
                    item-value="slug"
                    :items="state.listActions"
                    return-object
                    :no-data-text="$t('certificat.certificatlist')"
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.actions.$error">
                    {{ v$.actions.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="d-flex justify-end mb-n6">
                  <v-btn
                    color="#F6F6F6"
                    class="text-none"
                    variant="flat"
                    @click="addNewRow"
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
                <v-col cols="12" class="mb-n5 mb-1 mt-0">
                  <ag-grid-vue
                    id="grid-wrapper"
                    domLayout="autoHeight"
                    class="ag-theme-alpine mt-3"
                    :columnDefs="columnWaf"
                    :alwaysShowHorizontalScroll="false"
                    :alwaysShowVarticalScroll="false"
                    :rowData="rowDataWaf.value"
                    style="width: 100%; height: 100%"
                    :overlayNoRowsTemplate="overlayTemplate"
                    @grid-ready="onGridReady"
                    :pagination="true"
                    :paginationPageSize="4"
                    :localeText="paginationLocalization"
                  />
                </v-col>

                <!-- <button @click="show">test</button> -->
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions class="mt-3 actionBtn">
            <v-btn
              color="indigo-darken-3"
              large
              rounded
              outlined
              label-color="#213E9F"
              variant="flat"
              @click="closeModal"
              class="mt-3 btn-add"
            >
              <span class="text-white pr-3 pl-3">{{
                $t("buttons.close")
              }}</span>
            </v-btn>

            <v-btn
              large
              rounded
              outlined
              label-color="#213E9F"
              type="submit"
              color="indigo-darken-3"
              variant="flat"
              class="mt-3 btn-add"
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
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import { useI18n } from "vue-i18n";
import axios from "axios";
import useValidate from "@vuelidate/core";
import { toRefs, ref, watch, onMounted, reactive, computed, inject } from "vue";
import { required, helpers, requiredIf } from "@vuelidate/validators";
import { getCookie } from "@/mixins/csrftoken.js";
import MultiSelectRenderVue from "../../views/waf/agGridSelectType/MultiSelectRenderVue.vue";

export default {
  components: {
    AgGridVue,
    MultiSelectRenderVue,
  },
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
    onMounted(() => {
      overlayTemplate.value = `
      <span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
     </svg></span>`;
    });
    const { t } = useI18n();

    const { isOpen, editRow, modalMode } = toRefs(props);

    const rowDataWaf = ref([]);
    const paginationLocalization = reactive({
      of: "/",
    });
    const overlayTemplate = ref("");
    const gridApi = ref(null);
    const gridColumnApi = ref(null);

    const state = reactive({
      listVariable: [],
      listOperator: [],
      listTrans: [],
      listActions: [],
      id: null,
      //
      snackbar: false,
      color: "",
      textAlert: "",
      openModal: false,

      variable: "",
      operator: "",
      transformationFun: "",
      description: "",
      ruleName: "",
      typeTransf: "",
      actions: "",
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
          state.variable = "";
          state.ruleName = "";
          state.operator = "";
          state.transformationFun = "";
        }
      }
    );
    const value = computed(() => {
      return t("squid.value");
    });

    const columnWaf = ref([
      {
        headerName: "Type",
        cellEditor: MultiSelectRenderVue,
        field: "type",
        width: 90,
        minWidth: 50,
        flex: 1,
        editable: true,
        // cellEditorParams: {
        // values: [

        // ],
        // formatValue: (value) => value.toUpperCase(),
        // cellRenderer: (params) => params.value.toUpperCase(),
        // searchDebounceDelay: 200,
        // onProtocolsSelected: (event) => {
        //   console.log('***event**** : ',event)
        //   params.setValue(event);
        // },
        // },
      },
      {
        headerName: value,
        field: "value",
        width: 90,
        minWidth: 50,
        flex: 1,
        editable: true,
      },
      {
        headerName: "Actions",
        cellRenderer: actionCellRenderer,
        width: 150,
      },
    ]);

    const populate = (data) => {
      if (modalMode.value === "edit") {
      }
    };

    const submitForm = async () => {
      const result = await v$.value.$validate();
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      if (result) {
        let payload = {
          parent_variable: state.variable?.id,
          vlan_tag: state.ruleName,
          vlan_priority: state.operator,
          description: state.description,
        };
        console.log("payload", payload);

        if (modalMode.value === "edit") {
          axios
            .put(`/vlan/updateVlan/${state.id}`, payload)
            .then((response) => {
              if (response.status == "200") {
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
              state.textAlert = i.response.data.msg;
            });
        } else {
          axios
            .post("/vlan/addVlan", payload)
            .then((response) => {
              if (response.status == "200") {
                state.openModal = false;
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
              state.textAlert = i.response.data.msg;
            });
        }
      } else {
        console.log("v$", v$.value);
      }
    };

    const closeModal = () => {
      emitter.emit("closeWafRuleModal");
      if (modalMode.value === "create") {
        state.variable = "";
        state.ruleName = "";
        state.operator = "";
        state.transformationFun = "";
        state.typeTransf = "";
        state.actions = "";
      }
    };
    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const champInclude = computed(() => {
      return t("errors.ChampIncludeOnlyNumbers");
    });
    const rules = computed(() => {
      return {
        ruleName: {
          required: helpers.withMessage(error, required),
        },

        operator: {
          required: helpers.withMessage(error, required),
        },

        variable: {
          required: helpers.withMessage(error, required),
        },
        transformationFun: {
          required: helpers.withMessage(error, required),
        },
        typeTransf: {
          required: helpers.withMessage(error, required),
        },
        actions: {
          required: helpers.withMessage(error, required),
        },
      };
    });

    const v$ = useValidate(rules, state);

    const show = () => {
      console.log("row", rowDataWaf.value);
    };

    const onGridReady = (params) => {
      gridApi.value = params.api;
      gridColumnApi.value = params.columnApi;
      if (gridApi.value) {
        gridApi.value.setRowData(rowDataWaf.value);
      } else {
        console.error("Grid API.");
      }
    };
    const addNewRow = () => {
      const newRow = { type: "", value: "" };
      rowDataWaf.value.push(newRow);
      if (gridApi.value) {
        gridApi.value.setRowData(rowDataWaf.value);
      } else {
        console.error("Grid API.");
      }
    };
    function actionCellRenderer(params) {
      let eGui = document.createElement("div");

      {
        eGui.innerHTML = `
        <button
          class="action-button delete"
          data-action="delete">
            <i class="fas fa-times" style="color: #086eae; font-size: 20px;"></i>
        </button>

            `;
      }
      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          handleAction(action, params.node.data, params.node.rowIndex);
        });
      });

      return eGui;
    }
    const handleAction = (action, rowData, index) => {
      switch (action) {
        case "delete":
          const index = rowDataWaf.value.findIndex(
            (item) => item.host === rowData.host
          );

          if (index !== -1) {
            rowDataWaf.value.splice(index, 1);
            if (gridApi.value) {
              gridApi.value.setRowData(rowDataWaf.value);
            } else {
              console.error("Grid API.");
            }
          }
          break;
        default:
          break;
      }
    };

    return {
      state,
      columnWaf,
      rowDataWaf,
      paginationLocalization,
      overlayTemplate,
      gridColumnApi,
      gridApi,
      emitter,
      v$,
      closeModal,
      onGridReady,
      submitForm,
      addNewRow,
      show,
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
