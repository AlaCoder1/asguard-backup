<template>
  <v-overlay v-model="loading">
    <v-dialog
      v-model="isLoadingDialogue"
      :scrim="false"
      persistent
      width="auto"
    >
      <v-card color="#193286">
        <v-card-text>
          {{ $t("requiredfield.attente") }}
          <v-progress-linear
            indeterminate
            color="white"
            class="mb-0"
          ></v-progress-linear>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-overlay>
  <div
    class="certificats-management"
    style="display: flex; flex-direction: column; height: 100%"
  >
    <h4>{{ $t("agGrid.certificates") }}</h4>
    <v-divider></v-divider>

    <ag-grid-vue
      id="grid-wrapper"
      domLayout="autoHeight"
      class="ag-theme-alpine mt-3"
      :columnDefs="columnCertificats"
      style="width: 100%; height: 100%"
      :gridOptions="gridOptions"
      :overlayNoRowsTemplate="overlayTemplate"
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
          $t("buttons.ajoutcertifcat")
        }}</span>
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
          <v-card-title class="headline">{{
            $t("requiredfield.download")
          }}</v-card-title>
          <v-card-text>
            <div>
              <a> </a>
            </div>
            <v-container>
              <v-row>
                <v-col cols="6">
                  <v-text-field
                    :label="$t('form.password')"
                    type="password"
                    v-model="state.formData.password"
                  ></v-text-field>
                </v-col>

                <v-col cols="6">
                  <v-text-field
                    :label="$t('form.confirmPassword')"
                    type="password"
                    v-model="state.formData.confirm_password"
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" text @click="cancelDelete">{{
              $t("PageGeneral.form.Cancel")
            }}</v-btn>
            <v-btn
              color="blue darken-1"
              text
              @click="confirmDownload"
              :disabled="!isPassword || !isSame"
              >{{ $t("buttons.download") }}</v-btn
            >
          </v-card-actions>
        </v-card>
      </form>
    </v-dialog>
    <v-dialog v-model="deleteDialogCertif" max-width="500px">
      <v-card>
        <v-card-title class="headline">{{
          $t("delete.DeleteConfirmation")
        }}</v-card-title>
        <v-card-text>{{ $t("delete.questioncertificat") }}</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="cancelDeleteCertif">{{
            $t("PageGeneral.form.Cancel")
          }}</v-btn>
          <v-btn color="blue darken-1" text @click="confirmDeleteCertif">{{
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

      <template v-slot:actions> </template>
    </v-snackbar>
  </div>
</template>

<script>
import axios from "axios";
import useValidate from "@vuelidate/core";
import { helpers, sameAs } from "@vuelidate/validators";
import { reactive, computed, defineAsyncComponent } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import ModalAddEditCertif from "@/components/modals/ModalAddEditCertif.vue";
import ModalRevocation from "@/components/modals/ModalRevocation.vue";
// import FileP12 from `../../../../downloads/${this.rowName}.p12`
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
    const state = reactive({
      formData: {
        password: "",
        confirm_password: "",
      },
      userRole: null,
      userName: null,
    });
    const paginationLocalization = reactive({
      of: "/",
    });
    const isSame = computed(() => {
      return state.formData.confirm_password == state.formData.password;
    });

    const isPassword = computed(() => {
      let password =
        state.formData.password && state.formData.confirm_password
          ? true
          : false;
      return password;
    });

    return {
      state,
      isSame,
      isPassword,
      paginationLocalization,
    };
  },
  async mounted() {
    let downloadCert = localStorage.getItem("cert-name");
    if (downloadCert) {
      this.localName = downloadCert;
      this.downloadCertificatP12();
    }
  },
  data() {
    return {
      isLoadingDialogue: false,
      loading: false,
      localName: "",
      rowName: "",
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
        {
          headerName: this.namecertif,
          field: "nom",
          width: 90,
          minWidth: 50,
          flex: 1
        },
        {
          headerName: this.distingushedname,
          cellRenderer: this.formatedDn,
          width: 90,
          minWidth: 50,
          flex: 1
        },
        {
          headerName: "Actions",
          cellRenderer: this.actionCellRenderer,
          width:150,
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
            nom: element.name ?? "",
            certificats: element.certificates,
            nom_unique: element.common_name,
            country_code: element.country_code,
            state: element.state,
            city: element.city,
            organization: element.organization,
            email: element.email,
            is_private_key: element.is_private_key,
          };
        });

        let mapedListCertifAuth = infoAuth.filter((i) => i.is_private_key);

        this.allCertifAuth = mapedListCertifAuth;
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
            is_private_key: element.is_private_key,
          };
        });

        this.rowDataCertificats = infoCertif;
        setTimeout(() => {
          this.gridApi.setRowData(this.rowDataCertificats);
        }, 5);
      }
    },
    namecertif: {
      handler(val) {
        this.columnCertificats[0].headerName = val;
      },
      immediate: true,
    },
    distingushedname: {
      handler(val) {
        this.columnCertificats[1].headerName = val;
      },
      immediate: true,
    },
  },
  computed: {
    namecertif() {
      return this.$t("agGrid.name");
    },
    distingushedname() {
      return this.$t("agGrid.distinguishedname");
    },
  },
  methods: {
    downloadCertificatP12() {
      const link = document.createElement("a");
      import(`@/downloads/${this.localName}.p12`).then((module) => {
        if (module.default) {
          link.href = module.default;
          link.download = `${this.localName}.p12`;
          link.click();
          localStorage.removeItem("cert-name");
        } else {
          console.log("error");
        }
      });
    },

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
    async confirmDownload() {
      const csrfToken = this.getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      let payload = {
        download_type: "p12",
        password: this.state.formData?.password,
      };
      axios
        .post(`/certificates/exportCert/${this.rowId}`, payload)
        .then((response) => {
          this.deleteDialog = false;
          this.state.formData.password = "";
          this.state.formData.confirm_password = "";
          localStorage.setItem("cert-name", this.rowName);
          this.isLoadingDialogue = true;
          this.loading = true;
          setTimeout(() => {
            this.isLoadingDialogue = false;
            this.loading = false;
            location.reload();
          }, 2000);
        })
        .catch((i) => {
          this.snackbar = true;
          this.color = "red";
          this.textAlert = i.response.data.error;
        });
    },
    cancelDeleteCertif() {
      this.deleteDialogCertif = false;
    },
    onGridReady(params) {
      this.gridApi = params.api;
      this.gridColumnApi = params.columnApi;
    },
    openModalAdd() {
      this.modalData = {};
      this.modalMode = "create"; // Assuming you want to open the modal in create mode
      this.isModalOpen = true;
    },
    openModalRevoce() {
      this.modalData = {};
      this.modalMode = "revoce"; // Assuming you want to open the modal in create mode
      this.isModalOpenRevoce = true;
    },
    closeModal() {
      this.isModalOpen = false;
      this.isModalOpenRevoce = false;
      this.deleteDialogCertif = false;
    },
    actionCellRenderer(params) {
      let eGui = document.createElement("div");
      let editingCells = params.api.getEditingCells();
      let isCurrentRowEditing = editingCells.some((cell) => {
        return cell.rowIndex === params.node.rowIndex;
      });

      if (
        params.data.activation &&
        params.data.certificate_authority &&
        params.data.is_private_key
      ) {
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
      } else if (
        params.data.activation &&
        params.data.certificate_authority &&
        !params.data.is_private_key
      ) {
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
          class="action-button delete"
          data-action="delete">
            <i class="fas fa-times" style="color: #086eae; font-size: 20px;"></i>
        </button>

          `;
      }

      if (!params.data.activation && params.data.is_private_key) {
        eGui.innerHTML = `  <button
         class="action-button lock"
         data-action="lock">

         <i class="fa fa-unlock-alt" aria-hidden="true" style="color: #086eae;font-size: 20px;"></i>
         </button>
         <button
           class="action-button download"
           data-action="exportP12"  title="download P12 file">
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
      } else if (!params.data.activation && !params.data.is_private_key) {
        eGui.innerHTML = `  <button
         class="action-button lock"
         data-action="lock">

         <i class="fa fa-unlock-alt" aria-hidden="true" style="color: #086eae;font-size: 20px;"></i>
         </button>
         <button
           class="action-button download"
           data-action="exportP12"  title="download P12 file">
              <i class="mdi mdi-download-circle" style="color: #086eae;font-size: 20px;"></i>
           </button>
           <button
           class="action-button download"
           data-action="export" title="download CRT">
              <i class="mdi mdi-download-circle" style="color: #086eae; font-size: 20px;"></i>
           </button>
           <button
          class="action-button delete"
          data-action="delete">
            <i class="fas fa-times" style="color: #086eae; font-size: 20px;"></i>
        </button>
         `;
      }

      if (
        params.data.activation &&
        !params.data.certificate_authority &&
        params.data.is_private_key
      ) {
        eGui.innerHTML = `
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
      } else if (
        params.data.activation &&
        !params.data.certificate_authority &&
        !params.data.is_private_key
      ) {
        eGui.innerHTML = `
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
          class="action-button delete"
          data-action="delete">
            <i class="fas fa-times" style="color: #086eae; font-size: 20px;"></i>
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
      axios
        .post(`/certificates/exportCert/${id}`, payload)
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
          if (response.status == 201) {
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
    handleAction(action, rowData) {
      switch (action) {
        case "exportP12":
          this.deleteDialog = true;
          this.rowId = rowData.id;
          this.rowName = rowData.nom;

          break;

        case "delete":
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
          const csrfToken = this.getCookie("csrftoken");
          axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

          axios
            .put(`/certificates/unrevokeCertificate/${rowData.id}`)
            .then((response) => {
              this.closeModal();

              this.snackbar = true;
              this.color = "success";
              this.textAlert = response.data.msg;

              setTimeout(() => {
                location.reload();
              }, 1000);
            });
          // .catch((i) => {
          //   this.snackbar = true;
          //   this.color = "red";
          //   this.textAlert = i.response.data.error;
          // });

          break;
        case "export":
          let id = rowData.id;
          let type = "certificate";
          let fileExtention = `${rowData.nom}.crt`;
          this.download(id, type, fileExtention);

          break;
        case "exportKey":
          let rowId = rowData.id;
          let typeName = "private_key";
          let fileExt = `${rowData.nom}.key`;
          this.download(rowId, typeName, fileExt);

          break;
        case "revoce":
          this.rowEdit = rowData;
          this.openModalRevoce();
          this.modalMode = "revoce";
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
