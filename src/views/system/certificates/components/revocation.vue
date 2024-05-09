<template>
  <div
    class="certificats-management"
    style="display: flex; flex-direction: column; height: 100%"
  >
    <h4>{{ $t("agGrid.ListRevocation") }}</h4>
    <v-divider></v-divider>

    <div style="height: 100%">
      <div style="display: flex; flex-direction: row; height: 100%">
        <div style="overflow: hidden; flex-grow: 1">
          <ag-grid-vue
            id="grid-wrapper"
            domLayout="autoHeight"
            class="ag-theme-alpine mt-3"
            :columnDefs="columnRevocation"
            :overlayNoRowsTemplate="overlayTemplate"
            style="width: 100%; height: 100%"
            @grid-ready="onGridReady"
            :pagination="true"
            :paginationPageSize="4"
            :localeText="paginationLocalization"
          />
        </div>
      </div>
    </div>

    <div style="display: flex; justify-content: flex-end; margin-top: 20px">
      <v-btn color="dms_blue_dark" :rounded="true" class="mt-3 add-btn-user">
        <span class="text-white" style="text-transform: lowercase"
          >Ajouter révocation</span
        >
      </v-btn>
    </div>
    <ModalCertifRevocation
      :isOpen="isModalOpen"
      :editRow="rowEdit"
      v-model="isModalOpen"
      :mode="modalMode"
      @closeModal="closeModal"
      :initialData="modalData"
    />
  </div>
  <v-snackbar
    :timeout="2000"
    v-model="snackbar"
    location="bottom right"
    :color="color"
  >
    {{ textAlert }}

    <template v-slot:actions> </template>
  </v-snackbar>
</template>
<script>
import axios from "axios";
import { AgGridVue } from "ag-grid-vue3";
import ModalCertifRevocation from "@/components/modals/ModalCertifRevocation.vue";
export default {
  props: {
    authoritesData: {
      type: Array,
      required: true,
    },
  },
  components: {
    AgGridVue,
    ModalCertifRevocation,
  },

  data() {
    return {
      paginationLocalization: {
        of: "/",
      },
      snackbar: false,
      color: "",
      textAlert: "",
      listAuthRevoc: null,
      modalMode: "",
      rowEdit: {},
      modalData: {},
      isModalOpen: false,

      columnRevocation: [
        {
          headerName: this.namerevoc,
          field: "nom",
          width: 90,
          minWidth: 50,
          flex: 1,
        },
        {
          headerName: this.listrevoc,
          field: "list_revoc",
          width: 90,
          minWidth: 50,
          flex: 1,
        },
        {
          headerName: "Actions",
          cellRenderer: this.actionCellRenderer,
          editable: false,
          width: 150,
          sortable: false,
          filter: false,
        },
      ],
      rowDataRevocation: null,
      overlayTemplate: `<span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
    </svg></span>`,
    };
  },
  watch: {
    authoritesData(newValue) {
      this.listAuthRevoc = newValue;

      if (newValue) {
        console.log("newValue", newValue);
        let infoRevocCertif = newValue.map((element) => {
          return {
            id: element.id,
            nom: element.name,
            list_revokation: element.list_revokation,
            list_revoc: element.list_revokation.map((i) => {
              return i.name;
            }),
            is_private_key: element.is_private_key,
          };
        });

        let mapedListAuth = infoRevocCertif.filter((i) => i.is_private_key);
        this.rowDataRevocation = mapedListAuth;
        setTimeout(() => {
          this.gridApi.setRowData(this.rowDataRevocation);
        }, 5);
      }
    },
    namerevoc: {
      handler(val) {
        this.columnRevocation[0].headerName = val;
      },
      immediate: true,
    },
    listrevoc: {
      handler(val) {
        this.columnRevocation[1].headerName = val;
      },
      immediate: true,
    },
  },
  computed: {
    namerevoc() {
      return this.$t("agGrid.name");
    },
    listrevoc() {
      return this.$t("agGrid.Listauthoriy");
    },
  },
  methods: {
    openModal() {
      this.modalData = {};
      this.isModalOpen = true;
    },
    closeModal() {
      this.isModalOpen = false;
    },
    onGridReady(params) {
      this.gridApi = params.api;
      this.gridColumnApi = params.columnApi;
    },

    actionCellRenderer(params) {
      let eGui = document.createElement("div");
      let editingCells = params.api.getEditingCells();
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
          class="action-button show"  
          data-action="show">
          <span class="mdi mdi-eye  fa-lg" style="color: #086eae;font-size: 24px;"></span>
          </button>
          <button
           class="action-button download"
           data-action="export" title="CRL">
              <span class="mdi mdi-download-circle fa-lg" style="color: #086eae;  font-size: 22px;"></span>
           </button>
        `;
      }
      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          this.handleAction(action, params.node.data);
        });
      });

      return eGui;
    },
    getCookie(name) {
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
    },
    handleAction(action, rowData) {
      switch (action) {
        case "show":
          this.rowEdit = rowData;
          this.openModal();
          this.modalMode = "update";
          break;
        case "export":
          let id = rowData.id;
          let fileExtention = `${rowData.nom}_crl.crl`;

          const csrfToken = this.getCookie("csrftoken");
          axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

          axios
            .post(`/certificates/exportCertAuthListRev/${id}`)
            .then((response) => {
              const text = response.data.list_revocation;
              const blob = new Blob([text], {
                type: "application/x-x509-ca-cert",
              });

              const url = window.URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.style.display = "none";
              a.href = url;
              a.download = fileExtention;

              document.body.appendChild(a);
              a.click();

              window.URL.revokeObjectURL(url);
              document.body.removeChild(a);
            })
            .catch((i) => {
              this.snackbar = true;
              this.color = "red";
              this.textAlert = i.response.data.error;
            });

          break;
        default:
          break;
      }
    },
  },
};
</script>
