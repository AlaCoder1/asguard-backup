<template>
  <div
    class="certificats-management"
    style="display: flex; flex-direction: column; height: 100%"
  >
    <h4>certificats</h4>
    <v-divider></v-divider>

    <ag-grid-vue
      id="grid-wrapper"
      domLayout="autoHeight"
      class="ag-theme-alpine mt-3"
      :columnDefs="columnCertificats"
      style="width: 100%; height: 100%"
      :gridOptions="gridOptions"
      @grid-ready="onGridReady"
    />

    <div style="display: flex; justify-content: flex-end; margin-bottom: 10px">
      <v-btn
        type="submit"
        color="asguard_primary_light"
        :rounded="true"
        class="mt-3 btn-add"
        @click="openModalAdd"
      >
        <span class="text-white" style="text-transform: lowercase"
          >Ajouter certificats</span
        >
      </v-btn>
    </div>
    <ModalAddEditCertif
      :allCertifAuth="allCertifAuth"
      :isOpen="isModalOpen"
      :editRow="rowEdit"
      v-model="isModalOpen"
      :mode="modalMode"
      @closeModal="closeModal"
      :initialData="modalData"
    />
    <ModalRevocation
      :isOpen="isModalOpenRevoce"
      :editRow="rowEdit"
      v-model="isModalOpenRevoce"
      :mode="modalMode"
      @closeModal="closeModal"
      :initialData="modalData"
    />

    <v-dialog v-model="deleteDialog" max-width="500px">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title class="headline">Download Validation</v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="6">
                  <v-text-field
                    label="Password"
                    type="password"
                    v-model="state.formData.password"
                  ></v-text-field>
                  <span
                    class="error-feedback"
                    v-if="v$.formData.password.$error"
                    >{{ v$.formData.password.$errors[0].$message }}</span
                  >
                </v-col>

                <v-col cols="6">
                  <v-text-field
                    label="Confirm password"
                    type="password"
                    v-model="state.formData.confirm_password"
                  ></v-text-field>
                  <span
                    class="error-feedback"
                    v-if="v$.formData.confirm_password.$error"
                    >{{
                      v$.formData.confirm_password.$errors[0].$message
                    }}</span
                  >
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" text @click="cancelDelete"
              >Cancel</v-btn
            >
            <v-btn color="blue darken-1" text @click="confirmDownload"
              >Download</v-btn
            >
          </v-card-actions>
        </v-card>
      </form>
    </v-dialog>
    <v-dialog v-model="deleteDialogCertif" max-width="500px">
      <v-card>
        <v-card-title class="headline">Delete Confirmation</v-card-title>
        <v-card-text>Are you sure you want to delete this certif ?</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="cancelDeleteCertif"
            >Cancel</v-btn
          >
          <v-btn color="blue darken-1" text @click="confirmDeleteCertif"
            >Delete</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-snackbar v-model="snackbar" location="bottom right" :color="color">
      {{ textAlert }}

      <template v-slot:actions> </template>
    </v-snackbar>
  </div>
</template>

<script>
import axios from "axios";
import useValidate from "@vuelidate/core";
import { required, sameAs, helpers } from "@vuelidate/validators";
import { reactive, computed } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import ModalAddEditCertif from "@/components/modals/ModalAddEditCertif.vue";
import ModalRevocation from "@/components/modals/ModalRevocation.vue";
export default {
  props: {
    certifData: {
      type: Array,
      required: true,
    },
    authoritesData: {
      type: Array,
      required: true,
    },
  },
  components: {
    AgGridVue,
    ModalAddEditCertif,
    ModalRevocation,
  },
  setup() {
    //data
    const state = reactive({
      formData: {
        password: "",
        confirm_password: "",
      },
      userRole: null,
      userName: null,
    });
    const rules = computed(() => {
      return {
        formData: {
          password: {
            required: helpers.withMessage(
              "This field must be indicated",
              required
            ),
            isValidPassword: helpers.withMessage(
              `There must be at least 12 characters, including at least one uppercase, one number, and one special character.`,

              helpers.regex(
                /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~])[A-Za-z\d!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]{12,}$/
              )
            ),
          },
          confirm_password: {
            sameAsPassword: helpers.withMessage(
              "Your password does not match",

              sameAs(state.formData.password)
            ), // can be a reference to a field or computed property
            required: helpers.withMessage(
              "This field must be indicated",
              required
            ),

            isValidPassword: helpers.withMessage(
              `There must be at least 12 characters, including at least one uppercase, one number, and one special character.`,

              helpers.regex(
                /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~])[A-Za-z\d!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]{12,}$/
              )
            ),
          },
        },
      };
    });

    const v$ = useValidate(rules, state);
    return {
      state,
      v$,
    };
  },
  data() {
    return {
      textAlert: "",
      color: "",
      snackbar: false,
      deletedRow: null,
      deleteDialogCertif: false,
      rowId: null,
      deleteDialog: false,
      allCertifAuth: null,
      modalMode: "",
      rowEdit: {},
      isModalOpenRevoce: false,
      modalData: {},
      isModalOpen: false,
      columnCertificats: [
        { headerName: "nom", field: "nom" },
        { headerName: "distingushed name", cellRenderer: this.formatedDn },
        {
          headerName: "Actions",
          cellRenderer: this.actionCellRenderer,

          editable: false,
          sortable: false,
          filter: false,
        },
      ],
      gridOptions: {
        rowHeight: 120,
        pagination: true,
        paginationPageSize: 5,
        rowSelection: "single",
      },
      rowDataCertificats: null,
    };
  },
  watch: {
    authoritesData(newValue) {
      this.dataAuth = newValue;
      if (newValue) {
        let infoAuth = newValue.map((element) => {
          return {
            id: element.id,
            nom: element.name ?? "",
            certificats: element.certificates,
            nom_unique: element.common_name,
            country_code: element.country_code,
            state: element.state,
            city: element.city,
            organization: element.organization,
            email: element.email,
          };
        });
        this.allCertifAuth = infoAuth;
      }
    },
    certifData(newValue) {
      if (newValue) {
        let infoCertif = newValue.map((element) => {
          return {
            nom: element.name,
            nom_unique: element.common_name,
            id: element.id,
            activation: element.activation,
            country_code: element.country_code,
            state: element.state,
            city: element.city,
            organization: element.organization,
            email: element.email,
            valid_from: element.valid_from,
            valid_until: element.valid_until,
            certificate_authority: element.certificate_authority,
          };
        });

        this.rowDataCertificats = infoCertif;
        setTimeout(() => {
          this.gridApi.setRowData(this.rowDataCertificats);
        }, 5);
      }
    },
  },
  methods: {
    formatedDn(data) {
      let eGui = document.createElement("div");

      eGui.innerHTML = `
      emailAddress= ${data.data.email},ST=${data.data.state}, O=${data.data.organization}, <br/>
        L=${data.data.city},CN=${data.data.nom_unique},CN=${data.data.country_code}<br/>
        Valide à partir du :${data.data.valid_from}<br/>
        Valide jusqu'au :${data.data.valid_until}
        `;
      eGui.style.lineHeight = "2";

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
    confirmDownload() {
      this.v$.$validate();
      if (!this.v$.$error) {
        const csrfToken = this.getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
        console.log("ths", this.state.formData);
        let payload = {
          download_type: "p12",
          password: this.state.formData?.password,
        };
        axios.post(`/certificates/exportCert/${this.rowId}`, payload).then(
          (response) => {
            console.log("res", response.data.cert);

            // const text = response.data.cert;
            // const blob = new Blob([text], {
            //   type: "application/x-x509-ca-cert",
            // });

            const url = "@/download/";
            window.location.href = url;

            // const url = window.URL.createObjectURL(blob);
            // const a = document.createElement("a");
            // a.style.display = "none";
            // a.href = url;
            // a.download = "p12.p12";

            // document.body.appendChild(a);
            // a.click();

            // window.URL.revokeObjectURL(url);
            // document.body.removeChild(a);

            if (response.status == "201") {
              console.log("success");
            } else {
              console.log("error");
            }
          },
          (error) => {
            console.log(error);
          }
        );
      }
    },
    cancelDeleteCertif() {
      this.deleteDialogCertif = false;
    },
    onGridReady(params) {
      this.gridApi = params.api;
      this.gridColumnApi = params.columnApi;

      params.api.sizeColumnsToFit();
      window.addEventListener("resize", function () {
        setTimeout(function () {
          params.api.sizeColumnsToFit();
        });
      });

      params.api.sizeColumnsToFit();
    },
    openModalAdd() {
      console.log("ok");
      this.modalData = {};
      this.modalMode = "create"; // Assuming you want to open the modal in create mode
      this.isModalOpen = true;
    },
    openModalRevoce() {
      console.log("ok");
      this.modalData = {};
      this.modalMode = "revoce"; // Assuming you want to open the modal in create mode
      this.isModalOpenRevoce = true;
    },
    closeModal() {
      this.isModalOpen = false;
      this.isModalOpenRevoce = false;
      // location.reload()
    },
    actionCellRenderer(params) {
      let eGui = document.createElement("div");
      let editingCells = params.api.getEditingCells();
      let isCurrentRowEditing = editingCells.some((cell) => {
        return cell.rowIndex === params.node.rowIndex;
      });

      if (params.data.activation && params.data.certificate_authority) {
        eGui.innerHTML = `
       

       <button 
           class="action-button revoce"
           data-action="revoce">
           <i class="mdi mdi-skull-outline" style="color: #086eae;font-size: 20px;"></i>
           </button>
     
    
           <button 
           class="action-button download"
           data-action="exportP12" title="download P12 file">
              <i class="mdi mdi-download-circle" style="color: #086eae;font-size: 20px;"></i> 
           </button>
           <button 
           class="action-button download"
           data-action="export" title="download CRT">
              <i class="mdi mdi-download-circle" style="color: #086eae; font-size: 20px;"></i> 
           </button>
           <button 
           class="action-button download"
           data-action="exportKey" title="download Private Key">
              <i class="mdi mdi-download-circle" style="color: #086eae; font-size: 20px;"></i> 
           </button>
           <button 
          class="action-button delete"
          data-action="delete">
            <i class="fas fa-times" style="color: #086eae; font-size: 20px;"></i>
        </button>

         `;
      } else if (!params.data.activation) {
        eGui.innerHTML = `  <button 
         class="action-button lock"
         data-action="lock">
      
         <i class="fa fa-unlock-alt" aria-hidden="true" style="color: #086eae;font-size: 20px;"></i>
         </button>
         <button 
           class="action-button download"
           data-action="exportP12">
              <i class="mdi mdi-download-circle" style="color: #086eae;font-size: 20px;"></i> 
           </button>
           <button 
           class="action-button download"
           data-action="export">
              <i class="mdi mdi-download-circle" style="color: #086eae; font-size: 20px;"></i> 
           </button>
           <button 
           class="action-button download"
           data-action="exportKey">
              <i class="mdi mdi-download-circle" style="color: #086eae; font-size: 20px;"></i> 
           </button>
         `;
      } else if (params.data.activation && !params.data.certificate_authority) {
        eGui.innerHTML = `
         <button 
           class="action-button download"
           data-action="exportP12">
              <i class="mdi mdi-download-circle" style="color: #086eae;font-size: 20px;"></i> 
           </button>
           <button 
           class="action-button download"
           data-action="export">
              <i class="mdi mdi-download-circle" style="color: #086eae; font-size: 20px;"></i> 
           </button>
           <button 
           class="action-button download"
           data-action="exportKey">
              <i class="mdi mdi-download-circle" style="color: #086eae; font-size: 20px;"></i> 
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
    download(id, type, fileExtention) {
      const csrfToken = this.getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      let payload = {
        download_type: type,
      };
      axios.post(`/certificates/exportCert/${id}`, payload).then(
        (response) => {
          console.log("res", response.data.cert);

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

          if (response.status == "201") {
            console.log("success");
          } else {
            console.log("error");
          }
        },
        (error) => {
          console.log(error);
        }
      );
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
    cancelDelete() {
      this.deleteDialog = false;
    },
    confirmDeleteCertif() {
      const csrfTok = this.getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfTok;

      axios
        .delete(`/certificates/deleteCertificate/${this.deletedRow.id}`)
        .then((response) => {
          console.log("Resource deleted:", response.data);
          this.snackbar = true;
          this.color = "success";
          this.textAlert = response.data.msg;
          setTimeout(() => {
            this.closeModal();
            location.reload();
          }, 2000);
        })
        .catch((error) => {
          // Handle any errors that occur during the request
          console.error("Error deleting resource:", error);
          this.snackbar = true;
          this.color = "red";
          this.textAlert = "error";
        });
    },
    handleAction(action, rowData) {
      switch (action) {
        case "exportP12":
          this.deleteDialog = true;
          this.rowId = rowData.id;
          this.rowName = rowData.name;

          break;

        case "delete":
          console.log("Delete clicked for row:", rowData);
          this.deleteDialogCertif = true;
          this.deletedRow = rowData;

          // const index = this.rowData.findIndex(
          //   (item) => item.id === rowData.id
          // );
          // if (index !== -1) {
          //   this.rowData.splice(index, 1);
          // }
          break;
        case "lock":
          console.log("lock:", rowData);

          const csrfToken = this.getCookie("csrftoken");
          axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

          axios
            .put(`/certificates/unrevokeCertificate/${rowData.id}`)
            .then((response) => {
              console.log("res", response);
              this.snackbar = true;
              this.color = "success";
              this.textAlert = response.data.msg;
              setTimeout(() => {
                this.closeModal();
                location.reload();
              }, 2000);
            })
            .catch((error) => {
              console.error("Error :", error);
              this.snackbar = true;
              this.color = "red";
              this.textAlert = "error";
            });

          break;
        case "export":
          let id = rowData.id;
          let type = "certificate";
          let fileExtention = `${rowData.nom}.crt`;
          this.download(id, type, fileExtention);

          break;
        case "exportKey":
          console.log("Update clicked for row:", rowData);
          let rowId = rowData.id;
          let typeName = "private_key";
          let fileExt = `${rowData.nom}.key`;
          this.download(rowId, typeName, fileExt);

          break;
        case "revoce":
          console.log("revoce row:", rowData);
          this.rowEdit = rowData;
          this.openModalRevoce();
          this.modalMode = "revoce";
          break;
        case "cancel":
          console.log("Cancel clicked for row:", rowData);
          break;
        default:
          break;
      }
    },
  },
};
</script>
