<template>
  <div class="mt-6 ml-5" style="display: flex; flex-direction: column">
    <v-row>
      <v-col cols="6">
        <h4>General information</h4>
        <v-divider class="mt-2"></v-divider>

        <v-row class="mt-1">
          <v-col cols="4">
            <label>Enable</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <input type="checkbox" v-model="state.offState" />
            <label class="ml-2">Off</label>
            <br />
            <input type="checkbox" v-model="state.onState" />
            <label class="ml-2">On</label>
          </v-col>

          <v-col cols="4" class="mt-7">
            <label>Proxy port</label>
          </v-col>
          <v-col cols="5" class="mt-3">
            <v-text-field
              label="Proxy Port"
              v-model="state.proxyPort"
            ></v-text-field>
            <p class="error-feedback mb-5" v-if="v$.proxyPort.$error">
              {{ v$.proxyPort.$errors[0].$message }}
            </p>
          </v-col>
        </v-row>
        <v-row class="mt-5">
          <div>
            <VButton
              rounded
              outlined
              color="#213E9F"
              label-color="#ffffff"
              label="Validation"
              :isLarge="true"
              class="ml-2"
              @click="testValidation"
            />
          </div>
        </v-row>
      </v-col>

      <v-col cols="6">
        <h4>Squid authentification</h4>
        <v-divider class="mt-2"></v-divider>
        <v-row class="mt-1">
          <v-col cols="4">
            <label>Authentification</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <input type="checkbox" v-model="state.enable" />
            <label class="ml-2">Enable</label>
          </v-col>

          <div style="overflow: hidden; flex-grow: 1">
            <ag-grid-vue
              id="grid-wrapper"
              domLayout="autoHeight"
              class="ag-theme-alpine mt-3"
              style="width: 100%"
              @grid-ready="onGridReady"
              :columnDefs="columnUser"
              :rowData="rowDataUser.value"
            />
          </div>
        </v-row>

        <v-row class="d-flex justify-end mt-5">
          <div>
            <VButton
              rounded
              outlined
              color="#213E9F"
              label-color="#ffffff"
              label="Add User"
              :isLarge="true"
              class="ml-2"
              @click="openModalAdd"
            />
          </div>
        </v-row>
      </v-col>
      <ModalSquidUser
        :isOpen="state.isModalOpen"
        :editRow="state.editRow"
        :modalMode="state.modalMode"
      />
    </v-row>
  </div>
</template>

<script>
import { reactive, ref, computed, onMounted,inject  } from "vue";
import useValidate from "@vuelidate/core";
import { required } from "@vuelidate/validators";
import { AgGridVue } from "ag-grid-vue3";
import VButton from "@/components/VButton.vue";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import ModalSquidUser from "@/components/modals/ModalSquidUser.vue";
export default {
  components: {
    AgGridVue,
    VButton,
    ModalSquidUser,
  },
  setup() {
    const emitter = inject("emitter");
    const state = reactive({
      offState: false,
      onState: false,
      proxyPort: "",
      enable: false,
      modalData: {},
      isOpen: null,
      modalMode: "",
      isModalOpen: false,
      editRow: null,
    });

    const rules = computed(() => {
      return {
        proxyPort: { required },
      };
    });

    const v$ = useValidate(rules, state);

    const testValidation = async () => {
      const result = await v$.value.$validate();
      console.log("result", result);

      if (result) {
        console.log("state", state);
      } else {
        console.log("error", v$.value);
      }
    };

    const rowDataUser = reactive({});
    const gridApi = ref(null);

    const columnUser = [
      {
        headerName: "Username",
        field: "username",
        sortable: true,
        autoHeight: true,
        filter: true,
      },
      {
        headerName: "Actions",
        cellRenderer: actionCellRenderer,
        sortable: true,
        filter: true,
      },
    ];

    const onGridReady = (params) => {
      gridApi.value = params.api;

      gridApi.value.sizeColumnsToFit();
      window.addEventListener("resize", function () {
        setTimeout(function () {
          gridApi.value.sizeColumnsToFit();
        });
      });

      if (gridApi.value) {
        gridApi.value.setRowData(rowDataUser.value);
      } else {
        console.error("Grid API.");
      }
    };

    const openModalAdd = () => {
      state.modalData = {};
      state.modalMode = "create";
      state.isModalOpen = true;
    };

    onMounted(() => {
      emitter.on("closeSquidUserModal", () => {
        state.isModalOpen = false;
      });
      if (!rowDataUser.value) {
        rowDataUser.value = [];
      }
      const newRow = {
        username: "souhail",
      };
      rowDataUser.value.push(newRow);
    });

    function actionCellRenderer(params) {
      let eGui = document.createElement("div");

      let editingCells = params.api.getEditingCells();
      // checks if the rowIndex matches in at least one of the editing cells
      let isCurrentRowEditing = editingCells.some((cell) => {
        return cell.rowIndex === params.node.rowIndex;
      });

      if (isCurrentRowEditing) {
        eGui.innerHTML = `
    <button  
      class="action-button update"
      data-action="update">
           update  
    </button>
    <button  
      class="action-button cancel"
      data-action="cancel">
           cancel
    </button>
    `;
      } else {
        eGui.innerHTML = `
    <button 
      class="action-button edit"  
      data-action="edit">
         <i class="far fa-edit" style="color: #086eae;"></i> 
      </button>
    `;
      }

      // Add event listeners to handle button clicks
      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          handleAction(action, params.node.data, params.node.rowIndex);
        });
      });

      return eGui;
    }

    const handleAction = (action, rowData) => {
      switch (action) {
        case "edit":
          console.log("rowData", rowData);

          state.modalData = {};
          state.editRow = rowData;
          state.modalMode = "edit";
          state.isModalOpen = true;

          break;
        default:
          break;
      }
    };

    return {
      v$,
      state,
      emitter,
      columnUser,
      rowDataUser,
      onGridReady,
      actionCellRenderer,
      testValidation,
      openModalAdd,
    };
  },
};
</script>
<style>
.actionBtn {
  justify-content: end;
}
.error-feedback {
  color: red;
  font-size: 0.85em;
}
</style>
