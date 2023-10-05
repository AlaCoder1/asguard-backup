<template>
  <div>
    <h4>Networks admins</h4>
    <ag-grid-vue domLayout="autoHeight" class="ag-theme-alpine mt-3 m-w-80" :columnDefs="columnDefs" :rowData="rowData"
      :gridOptions="gridOptions" />
    <v-btn color="dms_blue_dark" :rounded="true" class="mt-3 add-btn-user" @click="openModal">
      <span class="text-white">Add user</span>
    </v-btn>
    <Modal_User :mode="modalMode" :isOpen="isModalOpen" @closeModal="closeModal" :initialData="modalData"
      @updateModalData="handleModalUpdate" :groups="DataList.groups" />
  </div>
</template>

<script>
import { AgGridVue } from 'ag-grid-vue';
import axios from 'axios';

import Modal_User from '../components/layout/Modal_User.vue';

import {
  createUser
} from '../services/users';

export default {
  name: 'UserManagement',
  components: {
    AgGridVue,
    Modal_User,
  },
  props: {
    DataList: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      isModalOpen: false,
      modalData: {},
      modalMode: '',
      columnDefs: [
        { headerName: 'User', field: 'username' },
        { headerName: 'Role', field: 'role' },
        { headerName: 'Actions', cellRenderer: this.actionCellRenderer },
      ],
      rowData: [], // Initialize rowData as an empty array
      gridOptions: {
        pagination: true,
        paginationPageSize: 5,
        rowSelection: 'single',
        // Rest of the gridOptions
      },
    };
  },
  watch: {
    DataList: {
      handler(newData) {
        this.rowData = newData.users; // Update rowData with the new prop value
      },
      immediate: true, // This will trigger the watcher when the component is created to initialize rowData
    },
  },
  methods: {

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
              servername: rowData.servername,
              type: rowData.type,
              hostname: rowData.hostname,
              transport: [],
              protocolVersion: [],
              bindingIdentities: '',
              password: '',
              searchScope: [],
              baseDN: '',
              // Add more form fields as needed
            }

            break;
          }
        case 'delete':
          console.log('Delete clicked for row:', rowData);

          const index = this.rowData.findIndex(item => item.id === rowData.id);

          this.delete(index, () => {
            if (index !== -1) {
              this.rowData.splice(index, 1);
            }

          })

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

    openModal() {
      // Set modalData and modalMode as needed
      this.modalData = {

      };
      this.modalMode = 'create'; // Assuming you want to open the modal in create mode
      this.isModalOpen = true;
    },
    closeModal() {
      this.isModalOpen = false;
    },
    handleModalUpdate(formData) {
      console.log("formData : " + JSON.stringify(formData))
      // Handle the data returned from the modal here
      this.Create(formData, () => { this.DataList.users.push(formData) })
      this.closeModal();
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
    async Create(data, callback) {

      const csrfToken = this.getCookie('csrftoken')
      axios.defaults.headers.common['X-CSRFToken'] = csrfToken;

      console.log("token :" + csrfToken)
      console.log("DataList :" + JSON.stringify(this.DataList))

      // {"email":"mohamedkaabi90@gmail.com","role":"root","groups":["Group 2","Group 3"],"deactivateUser":true,"fullname":"name","password":"password","username":"username"}

      const params = {
        "username": data.username,
        "password": data.password,
        "fullname": data.fullname,
        "email": data.email,
        "role": data.role,
        "group": data.groups
      }

      console.log("params are : " + JSON.stringify(params))

      axios.post('/users/createUser', params)
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
    async delete(id, callback) {

      const csrfToken = this.getCookie('csrftoken')
      axios.defaults.headers.common['X-CSRFToken'] = csrfToken;

      console.log("token :" + csrfToken)
      console.log("DataList :" + JSON.stringify(this.DataList))

      axios.post('/users/deleteUser/', id)
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
    // Fetch APIs

    // Rest of the methods
  },
};
</script>

<style lang="scss">
@import "~ag-grid-community/dist/styles/ag-grid.css";
@import "~ag-grid-community/dist/styles/ag-theme-alpine.css";
</style>