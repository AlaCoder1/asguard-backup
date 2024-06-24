<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm" class="scroller">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              {{ $t("Waf.createNewApplication") }}</span
            >
            <span class="headline" v-if="modalMode === 'edit'">
              {{ $t("Waf.updateApplication") }}</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="$t('Waf.applicationName')"
                    v-model="state.applicationName"
                  ></v-text-field>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.applicationName.$error"
                  >
                    {{ v$.applicationName.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.type"
                    label="Type"
                    item-title="name"
                    item-value="slug"
                    :items="state.listType"
                    return-object
                    :no-data-text="$t('certificat.certificatlist')"
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.type.$error">
                    {{ v$.type.$errors[0].$message }}
                  </p>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="$t('squid.value')"
                    v-model="state.value"
                  ></v-text-field>
                  <p class="error-feedback mb-5" v-if="v$.value.$error">
                    {{ v$.value.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Port"
                    v-model="state.port"
                  ></v-text-field>
                  <p class="error-feedback mb-5" v-if="v$.port.$error">
                    {{ v$.port.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Description"
                    v-model="state.description"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-autocomplete
                    multiple
                    v-model="state.country"
                    :label="$t('certificat.country')"
                    item-title="countryName"
                    item-value="countryCode"
                    return-object
                    :items="state.countriesList"
                  ></v-autocomplete>
                  <p class="error-feedback mb-5" v-if="v$.country.$error">
                    {{ v$.country.$errors[0].$message }}
                  </p>
                </v-col>

                <v-col cols="12" class="mb-n5 mb-1 mt-0">
                  <ag-grid-vue
                    id="grid-wrapper"
                    domLayout="autoHeight"
                    class="ag-theme-alpine mt-3"
                    :columnDefs="columnWafApp"
                    :alwaysShowHorizontalScroll="false"
                    :alwaysShowVarticalScroll="false"
                    :rowData="rowDataWafApp.value"
                    style="width: 100%; height: 100%"
                    :overlayNoRowsTemplate="overlayTemplate"
                    @grid-ready="onGridReady"
                    :pagination="true"
                    :paginationPageSize="10"
                    :localeText="paginationLocalization"
                  />
                </v-col>
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
import countryList from "country-list";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import { useI18n } from "vue-i18n";
import axios from "axios";
import useValidate from "@vuelidate/core";
import { toRefs, ref, watch, onMounted, reactive, computed, inject } from "vue";
import { required, helpers } from "@vuelidate/validators";
import { getCookie } from "@/mixins/csrftoken.js";

export default {
  components: {
    AgGridVue,
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
      let countries = countryList.getData();
      getAllcountryCode(countries);
      overlayTemplate.value = `
        <span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
        <path
          d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
          style="fill: #E8EAF6"
          data-name="Unbox"
        />
       </svg></span>`;

      let wafList =
        document.getElementById("app").attributes["list_rules"].value;
      let list_rules = JSON.parse(wafList);
      let mapedRow = list_rules.map((e) => {
        return {
          rule_waf: e.id,
          name: e.name,
          rule_policy: false,
          rule_log: false,
        };
      });

      rowDataWafApp.value = mapedRow;
    });
    const { t } = useI18n();

    const { isOpen, editRow, modalMode } = toRefs(props);

    const rowDataWafApp = ref([]);
    const paginationLocalization = reactive({
      of: "/",
    });
    const overlayTemplate = ref("");
    const gridApi = ref(null);
    const gridColumnApi = ref(null);

    const state = reactive({
      listType: ["ip", "domain"],
      countriesList: [],
      id: null,
      //
      snackbar: false,
      color: "",
      textAlert: "",
      openModal: false,

      type: "",
      value: "",
      description: "",
      applicationName: "",
      country: [],
      port: "",
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
          state.type = "";
          state.applicationName = "";
          state.value = "";
          state.description = "";
          state.country = [];
          state.port = "";
        }
      }
    );
    const block = computed(() => {
      return t("Waf.block");
    });
    const rule = computed(() => {
      return t("Waf.Rule");
    });
    const log = computed(() => {
      return t("Waf.log");
    });

    const columnWafApp = ref([
      {
        headerName: rule,
        field: "name",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: block,
        field: "rule_policy",

        width: 150,
        cellRenderer: (params) => {
          const checkbox = document.createElement("input");
          checkbox.type = "checkbox";
          checkbox.checked = params.value;
          if (params.data.rule_waf === 18) {
            params.data.rule_policy = true;
            checkbox.disabled = true;
            checkbox.checked = true;
          } else {
            checkbox.addEventListener("change", () => {
              params.node.setDataValue(params.colDef.field, checkbox.checked);
            });
          }
          return checkbox;
        },
        editable: (params) => {
          return params.data.rule_waf !== 18;
        },
      },
      // {
      //   headerName: log,
      //   field: "log",
      //   width: 150,
      // },
    ]);

    const populate = (data) => {
      if (modalMode.value === "edit") {
        state.id = data.id;

        let filtredCountry = [];
        data?.country.forEach((e) => {
          filtredCountry = [
            ...filtredCountry,
            ...state.countriesList.filter((i) => i.countryCode === e),
          ];
        });
        state.country = filtredCountry ?? [];

        state.type = data.application_type;
        state.applicationName = data.name;
        state.value = data.application_value;
        state.description = data.description;
        state.port = data.application_port;

        let mapedRow = data.rules.map((e) => {
          return {
            rule_waf: e.rule_waf,
            name: e.rule_name,
            rule_policy: e.rule_policy,
            rule_log: e.rule_log,
          };
        });

        rowDataWafApp.value = mapedRow;
      }
    };

    const restartNginx = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      axios.post('/waf/restartNginx');
    };

    const submitForm = async () => {
      const result = await v$.value.$validate();
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      if (result) {
        let mapedCountry = state.country.map((e) => e.countryCode);
        let mapedRuleApp = rowDataWafApp.value.map((e) => {
          return {
            rule_waf: e.rule_waf,
            rule_policy: e.rule_policy,
            rule_log: e.rule_log,
          };
        });
        let payload = {
          name: state.applicationName,
          application_type: state.type,
          application_value: state.value,
          application_port: state.port,
          description: state.description,
          country: mapedCountry,
          rules: mapedRuleApp,
        };
        console.log("payload", payload);

        if (modalMode.value === "edit") {
          axios
            .put(`/waf/updateApplicationWaf/${state.id}`, payload)
            .then((response) => {
              if (response.status == "201") {
                restartNginx()
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
            .post("/waf/createApplicationWaf", payload)
            .then((response) => {
              if (response.status == "201") {
                restartNginx()
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
      emitter.emit("closeWafApplicationModal");
      if (modalMode.value === "create") {
        state.type = "";
        state.applicationName = "";
        state.value = "";
        state.description = "";
        state.country = [];
        state.port = "";
      }
    };
    const getAllcountryCode = async (countries) => {
      // await axios.get("https://countriesnow.space/api/v0.1/countries/iso").then(
      //   (response) => {
      //     console.log("re", response);

      //     let countryList = response.data.data.map((element) => {
      //       return {
      //         countryName: element.name,
      //         countryCode: element.Iso2,
      //       };
      //     });
      //     countryList.sort((a, b) =>
      //       a.countryName.localeCompare(b.countryName)
      //     );
      //     state.countriesList = countryList;
      //   },
      //   (error) => {
      //     console.log(error);
      //   }
      // );

      let countryList = countries.map((element) => {
        return {
          countryName: element.name,
          countryCode: element.code,
        };
      });
      countryList.sort((a, b) => a.countryName.localeCompare(b.countryName));
      state.countriesList = countryList;
    };
    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const onlynumbers = computed(() => {
      return t("errors.ChampIncludeOnlyNumbers");
    });

    const rules = computed(() => {
      return {
        applicationName: {
          required: helpers.withMessage(error, required),
        },

        value: {
          required: helpers.withMessage(error, required),
        },

        type: {
          required: helpers.withMessage(error, required),
        },

        country: {
          required: helpers.withMessage(error, required),
        },
        port: {
          required: helpers.withMessage(error, required),
          isValidPort: helpers.withMessage(
            onlynumbers,
            helpers.regex(/^[0-9]+$/)
          ),
        },
      };
    });

    const v$ = useValidate(rules, state);

    const onGridReady = (params) => {
      gridApi.value = params.api;
      gridColumnApi.value = params.columnApi;
      if (gridApi.value) {
        gridApi.value.setRowData(rowDataWafApp.value);
      } else {
        console.error("Grid API.");
      }
    };

    return {
      state,
      columnWafApp,
      rowDataWafApp,
      paginationLocalization,
      overlayTemplate,
      gridColumnApi,
      gridApi,
      emitter,
      v$,
      closeModal,
      onGridReady,
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
.scroller {
  overflow: auto;
}
</style>
