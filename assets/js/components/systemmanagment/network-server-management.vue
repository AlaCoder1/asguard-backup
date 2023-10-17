<template>
  <div>
    <h4>Networks servers</h4>
    <ag-grid-vue domLayout="autoHeight" class="ag-theme-alpine mt-3 " :columnDefs="columnDefs" :rowData="rowData"
      :gridOptions="gridOptions" />
    <v-btn color="dms_blue_dark" :rounded="true" class="mt-3 add-btn-server" @click="openModal">
      <span>Add Server </span>
    </v-btn>

    <Modal :mode="modalMode" :isOpen="isModalOpen" @closeModal="closeModal" :initialData="modalData"
      @updateModalData="handleModalUpdate" />

  </div>
</template>

<script>
import { AgGridVue } from 'ag-grid-vue';
import Modal from '../layout/Modal.vue';
import axios from 'axios';

export default {
  name: 'NetworkServerManagement',
  components: {
    AgGridVue,
    Modal,
    // NetworkModal : WithModal(Modal),
  },
  props: {
    DataList: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      isModalOpen: false,
      modalData: {}, // Add this line
      modalMode: '', // Mode of the modal ('create' or 'update')

      columnDefs: [
        { headerName: "Server name", field: "name_server" },
        { headerName: "Type", field: "type" },
        { headerName: "Host Name", field: "hostname" },
        { headerName: "Actions", cellRenderer: this.actionCellRenderer },
      ],
      rowData: [
        { id: 1, servername: "mfa", type: "Local + Mot de Passe à Usage Unique Temporel (TOTP)	", hostname: "DMS sdwan" },
        { id: 2, servername: "mfa", type: "Local + Mot de Passe à Usage Unique Temporel (TOTP)	", hostname: "DMS sdwan" },
        { id: 3, servername: "mfa", type: "Local + Mot de Passe à Usage Unique Temporel (TOTP)	", hostname: "DMS sdwan" },
        { id: 4, servername: "mfa", type: "Local + Mot de Passe à Usage Unique Temporel (TOTP)	", hostname: "DMS sdwan" },
        { id: 5, servername: "mfa", type: "Local + Mot de Passe à Usage Unique Temporel (TOTP)	", hostname: "DMS sdwan" },
        { id: 6, servername: "mfa2", type: "Local + Mot de Passe à Usage Unique Temporel (TOTP)	", hostname: "DMS sdwan" },
      ],
      gridOptions: {
        pagination: true,
        paginationPageSize: 5,
        rowSelection: 'single',
        onRowEditingStarted: (params) => {
          params.api.refreshCells({
            columns: ['action'],
            rowNodes: [params.node],
            force: true,
          });
        },
        onRowEditingStopped: (params) => {
          params.api.refreshCells({
            columns: ['action'],
            rowNodes: [params.node],
            force: true,
          });
        },
      }
    };
  },
  watch: {
    DataList: {
      handler(newData) {
        this.rowData = newData; // Update rowData with the new prop value
      },
      immediate: true, // This will trigger the watcher when the component is created to initialize rowData
    },
  },
  methods: {
    handleModalUpdate(updatedData) {
      // Do something with the updated data
      this.modalData = updatedData;
      console.log("updatedData", updatedData)
      console.log("this.rowData[this.modalData.id]", this.rowData[this.modalData.id])

      // this.rowData[this.modalData.id - 1] = updatedData;
      if (this.modalMode === "update") {
        this.$set(this.rowData, this.modalData.id - 1, updatedData);
      }
      else {
        console.log("create action ...")

        console.log("formData : " + JSON.stringify(updatedData))
        console.log("this.DataList.servers : " + JSON.stringify(this.DataList))

        this.createServer(updatedData, () => {
          this.DataList.push(
            {
              id: updatedData.id,
              name_server: updatedData.servername,
              hostname:updatedData.hostname,
              transport: updatedData.transport,
              protocol_version: updatedData.protocolVersion,
              scope: updatedData.searchScope,
              domaine_name: updatedData.domaine_name,
              type: updatedData.type,
              type_name: updatedData.type_name

            }
          

          )
        })

      }

      // Additional actions if needed
    },
    openModal() {

      this.modalMode = 'create';

      this.modalData = {
        servername: '',
        type: '',
        hostname: '',
        transport: [],
        protocolVersion: [],
        bindingIdentities: '',
        password: '',
        searchScope: [],
        baseDN: '',
        // Add more form fields as needed
      }

      this.isModalOpen = true;
    },
    closeModal() {
      this.isModalOpen = false;
    },
    actionCellRenderer(params) {
      let eGui = document.createElement('div');

      let editingCells = params.api.getEditingCells();
      let isCurrentRowEditing = editingCells.some((cell) => {
        return cell.rowIndex === params.node.rowIndex;
      });

      if (isCurrentRowEditing) {
        eGui.innerHTML = `
          <button class="action-button update" data-action="update">update</button>
          <button class="action-button cancel" data-action="cancel">cancel</button>
        `;
      } else {
        eGui.innerHTML = `
          <button class="action-button edit" data-action="edit">
            <i class="far fa-edit" style="color: #086eae;"></i>
          </button>
          <button class="action-button delete" data-action="delete">
            <i class="fas fa-times" style="color: #086eae;"></i>
          </button>
        `;
      }

      eGui.querySelectorAll('.action-button').forEach((button) => {
        button.addEventListener('click', () => {
          const action = button.getAttribute('data-action');
          this.handleAction(action, params.node.data);
        });
      });

      return eGui;
    },
    handleAction(action, rowData) {
      switch (action) {
        case 'edit':
          {
            console.log('Edit clicked for row:', rowData);

            this.openModal()

            this.modalMode = 'update';

            this.modalData = {
              id: rowData.id,
              servername: rowData.name_server,
              type: rowData.type,
              hostname: rowData.hostname,
              transport: [],
              protocolVersion: [],
              bindingIdentities: '',
              password: '',
              searchScope: [],
              baseDN: '',
              username: ''
              // Add more form fields as needed
            }

            break;
          }
        case 'delete':
          console.log('Delete clicked for row:', rowData);
          const index = this.rowData.findIndex(item => item.id === rowData.id);
          if (index !== -1) {
            this.rowData.splice(index, 1);
          }
          break;
        case 'update':
          console.log('Update clicked for row:', rowData);
          break;
        case 'cancel':
          console.log('Cancel clicked for row:', rowData);
          break;
        default:
          break;
      }
    },

    // Fetch APIs
    getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    },
    async createServer(data, callback) {

      const csrfToken = this.getCookie('csrftoken')
      axios.defaults.headers.common['X-CSRFToken'] = csrfToken;

      console.log("token :" + csrfToken)
      console.log("DataList :" + JSON.stringify(this.DataList))

      const params = {
        "name_server": data.servername,
        "hostname": data.hostname,
        "transport": data.transport,
        "protocol_version": data.protocolVersion,
        "scope": data.searchScope,
        "domaine_name": data.baseDN,
        "type": data.type,
        "username": "root",
        "password": data.password
      }

      console.log("params are : " + JSON.stringify(params))

      axios.post('/servers/createServer', params)
        .then((response) => {
          callback();
          console.log(response);
        }, (err) => {
          if (err.response && err.response.status === 401) {
            const responseData = err.response.data; // Access the response data
            console.log("401 Error Response:", responseData);
            // this.invalid = true ;
            this.message = responseData.message;
            // Handle the 401 error here
          } else {
            console.error("Error occurred:", err);
            // Handle other errors
          }
        });

    },
    async deleteServer(id, callback) {

      const csrfToken = this.getCookie('csrftoken')
      axios.defaults.headers.common['X-CSRFToken'] = csrfToken;

      console.log("token :" + csrfToken)
      console.log("server id :" + id)

      axios.delete(`/servers/deleteServer/${id}`)

        .then((response) => {
          callback();
          // Handle the successful response
          console.log('Resource deleted:', response.data);
        })
        .catch((error) => {
          // Handle any errors that occur during the request
          console.error('Error deleting resource:', error);
        });

    },
    async updateServer(data, callback) {

      const csrfToken = this.getCookie('csrftoken')
      axios.defaults.headers.common['X-CSRFToken'] = csrfToken;

      console.log("token :" + csrfToken)
      console.log("DataList :" + JSON.stringify(data))

      axios.put(`/servers/modifyServer/${data.id}`
        , {
          "name_server": "test",
          "hostname": "eeeeeeeeeeeeeeeeeeee",
          "transport": "transport",
          "protocol_version": 2,
          "scope": "scope",
          "domaine_name": "domaine_name",
          "type": 1,
          "username": "root",
          "password": "root"
        })
        .then((response) => {
          callback();
          // Handle the successful response
          console.log('Resource updated:', response.data);
        })
        .catch((error) => {
          // Handle any errors that occur during the request
          console.error('Error updating resource:', error);
        });

    },
    async getuserServer(id, callback) {

      axios.get(`/servers/getServer/${id}`)
        .then((response) => {
          callback(response.data);
          // Handle the successful response
          console.log('Data received:', response.data);
        })
        .catch((error) => {
          // Handle any errors that occur during the request
          console.error('Error fetching data:', error);
        });
    }
    // Fetch APIs

  }
};
</script>

<style lang="scss">
@import "~ag-grid-community/dist/styles/ag-grid.css";
@import "~ag-grid-community/dist/styles/ag-theme-alpine.css";
</style>
