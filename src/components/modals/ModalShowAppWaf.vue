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
                <v-col cols="12" class="mb-n5 mb-1 mt-0">
                  <ag-grid-vue
                    id="grid-wrapper"
                    domLayout="autoHeight"
                    class="ag-theme-alpine mt-3"
                    :columnDefs="columnWafAppSHOW"
                    :alwaysShowHorizontalScroll="false"
                    :alwaysShowVarticalScroll="false"
                    :rowData="rowDataAPP.value"
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
          </v-card-actions>
        </v-card>
      </form>
    </v-dialog>
  </v-row>
</template>

<script>
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import { useI18n } from "vue-i18n";
import { inject, toRefs, ref, reactive, watch, onMounted } from "vue";

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
    const { t } = useI18n();
    const emitter = inject("emitter");

    const { isOpen, editRow, modalMode } = toRefs(props);

    const rowDataAPP = ref([]);
    const paginationLocalization = reactive({
      of: "/",
    });
    const overlayTemplate = ref("");
    const gridApishow = ref(null);
    const gridColumnApishow = ref(null);

    const state = reactive({});

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
      () => {}
    );
    onMounted(() => {});

    const columnWafAppSHOW = ref([
      {
        headerName: "Id",
        field: "id",
        width: 90,
        minWidth: 50,
        flex: 1,
      },

      {
        headerName: "Application",
        field: "application",
        width: 150,
      },
    ]);

    const populate = (data) => {
      if (modalMode.value === "show") {
        console.log("datashow", data);
        rowDataAPP.value = data?.application;
      }
    };

    const closeModal = () => {
      emitter.emit("closeModalSHOW");
    };

    const onGridReady = (params) => {
      gridApishow.value = params.api;
      gridColumnApishow.value = params.columnApi;

      if (gridApishow.value) {
        gridApishow.value.setRowData(rowDataAPP.value);
      } else {
        console.error("Grid API.");
      }
    };

    return {
      state,
      emitter,
      columnWafAppSHOW,
      rowDataAPP,
      paginationLocalization,
      overlayTemplate,
      gridColumnApishow,
      gridApishow,
      closeModal,
      onGridReady,
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
