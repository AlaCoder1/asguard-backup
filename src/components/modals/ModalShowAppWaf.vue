<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-container>
          <v-row>
            <v-col cols="12" class="mb-n5 mb-5 mt-0">
              <!-- <v-card elevation="0">
                <v-card-item
                  v-if="rowApplication.length"
                  v-for="app in rowApplication"
                  :key="app.id"
                >
                  {{ app.name }}
                </v-card-item>
                <v-card-item v-else class="d-flex justify-center mt-5">
                  {{ $t("noApp") }}
                </v-card-item>
              </v-card> -->

              <!-- style="background-color: #193286" -->
              <v-card
                elevation="16"
                class="mb-10"
                style="background-color: #193286"
              >
                <v-card-title>
                  <div class="d-flex justify-space-between align-center mb-2">
                    <span class="headline text-white"> Applications</span>
                    <span
                      class="mdi mdi-close cursor-pointer text-white"
                      @click="closeModal"
                    ></span>
                  </div>
                </v-card-title>
                <!-- <v-card-item class="text-subtitle-1 text-white w-100 mb-10 mt-1">
                  {{ description ?? $t("noDesc") }}
                </v-card-item> -->
                <v-card-item>
                  <!-- {{ app.name }} -->
                  <!-- <div class="d-flex  ga-2">
                    <v-chip color="primary cursor-pointer text-white ">
                      {{ app.name }}
                    </v-chip>
                  </div> -->
                  <!-- <div class="flex-container"> -->
                  <div
                    class="text-white"
                    v-if="rowApplication.length"
                    v-for="app in rowApplication"
                    :key="app.id"
                  >
                    <v-chip
                      class="cursor-pointer mb-4"
                      color="white"
                      variant="outlined"
                    >
                      {{ app.name }}
                    </v-chip>
                    <!-- </div> -->
                  </div>
                </v-card-item>
                <v-card-item
                  v-if="!rowApplication.length"
                  class="d-flex justify-center text-white mt-5 mb-14 py-5"
                >
                  {{ $t("noApp") }}
                </v-card-item>
              </v-card>
            </v-col>
          </v-row>
        </v-container>
      </form>
      <!-- <form ref="myForm" @submit.prevent="submitForm" class="scroller">
        <v-card>
          <v-card-title>
            <span
              class="mdi mdi-close cursor-pointer text-end justify-end d-flex"
              @click="closeModal"
            ></span>
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
                <v-col cols="12" class="mb-n5 mb-1 mt-0"> -->
      <!-- <ag-grid-vue
                    id="grid"
                    domLayout="autoHeight"
                    class="ag-theme-alpine mt-3"
                    :columnDefs="columnWafAppSHOW"
                    :alwaysShowHorizontalScroll="false"
                    :alwaysShowVarticalScroll="false"
                    :rowData="rowApplication.value"
                    style="width: 100%; height: 100%"
                    :overlayNoRowsTemplate="overlayTemplate"
                    :pagination="true"
                    :paginationPageSize="10"
                    :localeText="paginationLocalization"
                  /> -->

      <!-- <v-card elevation="0">
                    <v-card-item
                      v-if="rowApplication.length"
                      v-for="app in rowApplication"
                      :key="app.id"
                    >
                      {{ app.name }}
                    </v-card-item>
                    <v-card-item v-else class="d-flex justify-center mt-5">
                      {{ $t("noApp") }}
                    </v-card-item>
                  </v-card>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions class="mt-3 actionBtn"> -->
      <!-- <v-btn
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
            </v-btn> -->
      <!-- </v-card-actions>
        </v-card>
      </form> -->
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

    const rowApplication = ref([]);
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
        rowApplication.value = data.application;
      }
    };

    const closeModal = () => {
      emitter.emit("closeModalSHOW");
    };

    const onGridReadyApplication = (params) => {
      gridApishow.value = params.api;
      gridColumnApishow.value = params.columnApi;
    };

    return {
      state,
      emitter,
      columnWafAppSHOW,
      rowApplication,
      paginationLocalization,
      overlayTemplate,
      gridColumnApishow,
      gridApishow,
      closeModal,
      onGridReadyApplication,
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
.flex-container {
  display: flex;
  flex-wrap: wrap;
  flex-direction: row;
  gap: 10px;
}
</style>
