<template>
  <v-overlay v-model="viewModal">
            <v-dialog v-model="isviewModal" :scrim="false" width="auto">
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
                  You do not have the required permissions to perform any
                  actions.<br />
                  Please contact the administrator if you believe this is an
                  error.
                </v-card-text>

                <div class="mr-3 mb-5 d-flex justify-end">
                  <VButton
                    rounded
                    outlined
                    color="#ffffff"
                    label-color="#213E9F"
                    label="Close"
                    :isLarge="true"
                    @click="close"
                  />
                </div>
              </v-card>
            </v-dialog>
          </v-overlay>
  <div
    class="certificats-management"
    style="display: flex; flex-direction: column; height: 100%"
  >
    <h4>{{ $t("agGrid.authority") }}</h4>
    <v-divider></v-divider>
    <ag-grid-vue
      id="grid-wrapper"
      domLayout="autoHeight"
      class="ag-theme-alpine mt-3"
      :columnDefs="columnAuthority"
      :gridOptions="gridOptions"
      :overlayNoRowsTemplate="overlayTemplate"
      style="width: 100%; height: 100%"
      @grid-ready="onGridReady"
      :localeText="paginationLocalization"
    />
    <div style="display: flex; justify-content: flex-end; margin-bottom: 10px">
      <v-btn
        type="submit"
        color="asguard_primary_light"
        :rounded="true"
        class="mt-3 btn-add"
        @click="openModalAdd"
      >
        <span class="text-white" style="text-transform: lowercase">{{
          $t("buttons.ajoutauthority")
        }}</span>
      </v-btn>
    </div>
    <ModalAddAuth
      :isOpen="isModalOpen"
      :editRow="rowEdit"
      v-model="isModalOpen"
      :mode="modalMode"
      @closeModal="closeModal"
      :initialData="modalData"
    />
    <v-dialog v-model="deleteDialog" max-width="500px">
      <v-card>
        <v-card-title class="headline">{{
          $t("delete.DeleteConfirmation")
        }}</v-card-title>
        <v-card-text>{{ $t("delete.questioncertif") }}</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="cancelDelete">{{
            $t("PageGeneral.form.Cancel")
          }}</v-btn>
          <v-btn color="blue darken-1" text @click="confirmDelete">{{
            $t("PageGeneral.form.Delete")
          }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-snackbar
      :timeout="2000"
      v-model="snackbar"
      location="bottom right"
      :color="color"
    >
      {{ textAlert }}
    </v-snackbar>
  </div>
</template>

<script>
import { user_privilege } from "@/mixins/user_privilege.js";
import axios from "axios";
import ModalAddAuth from "@/components/modals/ModalAddAuth.vue";
import { AgGridVue } from "ag-grid-vue3";
import VButton from "@/components/VButton.vue";

export default {
  props: {
    authoritesData: {
      type: Array,
      required: true,
    },
  },
  components: {
    AgGridVue,
    ModalAddAuth,
    VButton,
  },
  data() {
    return {
      paginationLocalization: {
        of: "/",
      },
      textAlert: "",
      color: "",
      snackbar: false,
      deletedRow: null,
      deleteDialog: false,
      getRowId: null,
      dataAuth: null,
      modalData: {},
      isviewModal: false,
      viewModal: false,
      modalMode: "",
      rowEdit: {},
      isModalOpen: false,
      columnAuthority: [
        {
          headerName: this.nameauth,
          field: "nom",
          width: 90,
          minWidth: 50,
          flex: 1,
        },
        {
          headerName: this.certificates,
          field: "certificats",
          width: 90,
          minWidth: 50,
          flex: 1,
        },
        {
          headerName: this.distingushedname,
          cellRenderer: this.formatedDn,
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
      rowDataAuthority: null,

      gridOptions: {
        rowHeight: 120,
        pagination: true,
        paginationPageSize: 5,
        rowSelection: "single",
      },
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
      this.dataAuth = newValue;
      if (newValue) {
        let infoAuth = newValue.map((element) => {
          return {
            id: element.id,
            nom: element.name,
            certificats: element.certificates,
            nom_unique: element.common_name,
            country_code: element.country_code,
            state: element.state,
            city: element.city,
            organization: element.organization,
            email: element.email,
            valid_from: element.valid_from,
            valid_until: element.valid_until,
            is_private_key: element.is_private_key,
          };
        });
        this.rowDataAuthority = infoAuth;
        setTimeout(() => {
          this.gridApi.setRowData(this.rowDataAuthority);
        }, 5);
      }
    },
    nameauth: {
      handler(val) {
        this.columnAuthority[0].headerName = val;
      },
      immediate: true,
    },
    certificates: {
      handler(val) {
        this.columnAuthority[1].headerName = val;
      },
      immediate: true,
    },
    distingushedname: {
      handler(val) {
        this.columnAuthority[2].headerName = val;
      },
      immediate: true,
    },
  },
  computed: {
    nameauth() {
      return this.$t("agGrid.name");
    },
    certificates() {
      return this.$t("agGrid.certificates");
    },
    distingushedname() {
      return this.$t("agGrid.distinguishedname");
    },
  },
  methods: {
    formatedDn(data) {
      let eGui = document.createElement("div");

      eGui.innerHTML = `
      emailAddress= ${data.data.email},ST=${data.data.state}, O=${data.data.organization}, <br/>
        L=${data.data.city},CN=${data.data.nom_unique},C=${data.data.country_code}<br/>
        Valide à partir du :${data.data.valid_from}<br/>
        Valide jusqu'au :${data.data.valid_until}
        `;
      eGui.style.lineHeight = "2";

      return eGui;
    },

    onGridReady(params) {
      this.gridApi = params.api;
      this.gridColumnApi = params.columnApi;
    },
    openModalAdd() {
      const user = user_privilege();

      if (user !=='viewer') {
        this.modalData = {};
      this.modalMode = "create";
      this.isModalOpen = true;
          } else {
            this.isviewModal = true;
            this.viewModal = true;
            };
    },
    closeModal() {
      this.isModalOpen = false;
      this.deleteDialog = false;
      // location.reload()
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
        // const user = user_privilege();
        // if (user === "viewer") {
        //   eGui.innerHTML = `View Mode`;
        // } else 
        // {
          if (params.data.is_private_key) {
            eGui.innerHTML = `
        
        <button 
          class="action-button download"
          data-action="export" title="CRT">
             <i class="mdi mdi-download-circle" style="color: #086eae; font-size: 20px;"></i> 
          </button>
          <button 
          class="action-button download"
          data-action="exportKey" title=${this.$t("titleAgGrid.privateKey")}>
             <i class="mdi mdi-download-circle" style="color: #086eae; font-size: 20px;"></i> 
          </button>
        <button 
          class="action-button delete"
          data-action="delete">
            <i class="fas fa-times" style="color: #086eae; font-size: 20px;"></i>
        </button>
        `;
          } else {
            eGui.innerHTML = `
        
        <button 
          class="action-button download"
          data-action="export" title="CRT">
             <i class="mdi mdi-download-circle" style="color: #086eae; font-size: 20px;"></i> 
          </button>
       
        <button 
          class="action-button delete"
          data-action="delete">
            <i class="fas fa-times" style="color: #086eae; font-size: 20px;"></i>
        </button>
        `;
          // }
        }
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

    download(id, type, fileExtention) {
      const csrfToken = this.getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      let payload = {
        type: type,
      };
      axios
        .post(`/certificates/exportCertAuth/${id}`, payload)
        .then((response) => {
          const text = response.data.cert;
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
    },
    cancelDelete() {
      this.deleteDialog = false;
    },
    confirmDelete() {
      const csrfToken = this.getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios
        .delete(`/certificates/deleteCertAuth/${this.deletedRow.id}`)
        .then((response) => {
          if (response.status == "200") {
            this.closeModal();

            this.snackbar = true;
            this.color = "success";
            this.textAlert = response.data.msg;

            setTimeout(() => {
              location.reload();
            }, 1000);
          }
        })
        .catch((i) => {
          this.snackbar = true;
          this.color = "red";
          this.textAlert = i.response.data.error;
        });
    },
    close(){
      this.isviewModal = false;
      this.viewModal = false;
    },
    handleAction(action, rowData) {
      const user = user_privilege();
      switch (action) {
        case "edit":
        if (user !=='viewer') {
          this.rowEdit = rowData;
          this.openModalAdd();
          this.modalMode = "update";
          } else {
            this.isviewModal = true;
            this.viewModal = true;
            };

          break;
        case "export":
        if (user !=='viewer') {
          let id = rowData.id;
          let type = "certificate";
          let fileExtention = `${rowData.nom}.crt`;

          this.download(id, type, fileExtention);
          } else {
            this.isviewModal = true;
            this.viewModal = true;
            };
          

          break;
        case "delete":
        if (user !=='viewer') {
          this.deleteDialog = true;
          this.deletedRow = rowData;
          } else {
            this.isviewModal = true;
            this.viewModal = true;
            };


          break;
        case "exportKey":
        if (user !=='viewer') {
          let rowId = rowData.id;
          let typeName = "private_key";
          let fileExt = `${rowData.nom}.key`;
          this.download(rowId, typeName, fileExt);
          } else {
            this.isviewModal = true;
            this.viewModal = true;
            };


          break;
        case "cancel":
          break;
        default:
          break;
      }
    },
  },
};
</script>
