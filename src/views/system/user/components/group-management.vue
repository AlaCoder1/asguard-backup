<template>
  <div>
    <h4>Networks groups</h4>
    <ag-grid-vue domLayout="autoHeight" class="ag-theme-alpine mt-3 m-w-80" :columnDefs="columnDefs" :rowData="rowData"
      :gridOptions="gridOptions" />
    <v-btn color="dms_blue_dark" :rounded="true" class="mt-3 add-btn-user"  @click="openModal">
      <span class="text-white">Add Group</span>
    </v-btn>
    <Modal_Group :editRow="rowEdit" :mode="modalMode" :isOpen="isModalOpen" @closeModal="closeModal" :initialData="modalData"
      @updateModalData="handleModalUpdate" />
      <v-dialog v-model="deleteDialog" max-width="500px">
                <v-card>
                    <v-card-title class="headline">Delete Confirmation</v-card-title>
                    <v-card-text>Are you sure you want to delete this group?</v-card-text>
                    <v-card-actions>
                        <v-spacer></v-spacer>
                         <v-btn color="blue darken-1" text @click="cancelDelete">Cancel</v-btn>
                          <v-btn color="blue darken-1" text @click="confirmDelete">Delete</v-btn>
                    </v-card-actions>
                </v-card>
            </v-dialog>
  </div>
</template>
<script>
import { AgGridVue } from 'ag-grid-vue3';
// import Modal_Group from '../layout/Modal_Group.vue';
import axios from 'axios';

export default {
  name: 'GroupManagement',
  components: {
    AgGridVue,
    // Modal_Group
  },
  props: {
    DataList: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      deletedRow:null,
      deleteDialog:false,
      rowEdit: {},
      modalMode: '',
      isModalOpen: false,
      modalData: {},
      selectedRowIndex: null,
      columnDefs: [
        { headerName: "Group", field: "groupname" },
        { headerName: "Description", field: "description" },
        { headerName: "Actions", cellRenderer: this.actionCellRenderer },
      ],
      rowData: [
      ],
      gridOptions: {
        pagination: true,
        paginationPageSize: 5,
        rowSelection: 'single',

      }
    };
  },

  watch: {
    DataList: {
      handler(newData) {
        console.log('datttattata',newData)
        this.rowData = newData; // Update rowData with the new prop value
      },
      immediate: true, // This will trigger the watcher when the component is created to initialize rowData
    },
  },

  methods: {
    cancelDelete() {
            this.deleteDialog = false;
        },
        confirmDelete(){
          const csrfToken = this.getCookie('csrftoken')
      axios.defaults.headers.common['X-CSRFToken'] = csrfToken;

      console.log("token :" + csrfToken)
      console.log("group id :" + this.deletedRow.id)

      axios.delete(`/groups/deleteGroup/${this.deletedRow.id}`)

        .then((response) => {
          // Handle the successful response
          this.deleteDialog = false;
          location.reload()
          console.log('Resource deleted:', response.data);
        })
        .catch((error) => {
          // Handle any errors that occur during the request
          console.error('Error deleting resource:', error);
        });

        },
    openModal() {
      this.modalData = {
      };
      this.modalMode = 'create'; // Assuming you want to open the modal in create mode
      this.isModalOpen = true;
    },
    closeModal() {
      this.isModalOpen = false;
      location.reload()
    },

    handleModalUpdate(formData) {
      console.log('formDataformDataformDataformData',formData)
      //
      this.modalData = formData;
      console.log("formData", formData)
      console.log("this.selectedRowIndex", this.rowData[this.selectedRowIndex])

      // this.rowData[this.modalData.id - 1] = updatedData;
      if (this.modalMode === "update") {
        console.log("update action ..." + JSON.stringify(this.rowData))
        this.update(formData,
          () => {
            console.log("old DataList :" + JSON.stringify(this.DataList[this.selectedRowIndex]))

            this.$set(this.DataList, this.selectedRowIndex,   {
              groupname: formData.groupname,
              description: formData.description,
              sudoers: formData.sudoers,
            });


            // this.DataList[this.selectedRowIndex] =
            // {
            //   groupname: formData.groupname,
            //   description: formData.description,
            //   sudoers: formData.sudoers,
            // };

            console.log("new formData :" + JSON.stringify(formData))
            // this.selectedRowIndex = null;
          })
      }
      else {
        console.log("create action ...")

        console.log("formData : " + JSON.stringify(formData))
        // Handle the data returned from the modal here
        this.Create(formData, () => { this.DataList.push(formData) })

        // this.$set(this.rowData, this.rowData.length, formData);
      }
      this.closeModal();
    },

    actionCellRenderer(params) {
      let eGui = document.createElement('div');

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
        <button 
          class="action-button delete"
          data-action="delete">
            <i class="fas fa-times" style="color: #086eae;"></i>
        </button>
        `;
      }

      // Add event listeners to handle button clicks
      eGui.querySelectorAll('.action-button').forEach((button) => {
        button.addEventListener('click', () => {
          const action = button.getAttribute('data-action');
          this.handleAction(action, params.node.data, params.node.rowIndex);
        });
      });

      return eGui;
    },
    handleAction(action, rowData, CurrentIndex) {
      // Perform the desired action based on the action type
      switch (action) {
        case 'edit':
          {
            this.selectedRowIndex = CurrentIndex;
            this.openModal()
              this.modalMode = 'update';
              this.rowEdit = rowData;

            this.getgroup(rowData.id, (data) => {
              console.log('Edit clicked for row Group:', rowData);
              console.log('response data local 1:', data);

             
              

              // this.modalData = {
              //   id: data?.id,
              //   gid: data?.gid,
              //   groupname: data?.groupname,
              //   description: data?.description,
              //   sudoers: data?.sudoers,
              //   // Add more form fields as needed
              // }
            })

            break;
            // Perform edit action
          }
        case 'delete':
          console.log('Delete clicked for row:', rowData);
          this.deleteDialog = true;
          this.deletedRow = rowData

          // const index = this.rowData.findIndex(item => item.id === rowData.id);

          // this.delete(rowData.id, () => {
          //   if (index !== -1) {
          //     this.rowData.splice(index, 1);
          //   }
          // })

          break;
        case 'update':
          console.log('Update clicked for row:', rowData);
          // Perform update action
          break;
        case 'cancel':
          console.log('Cancel clicked for row:', rowData);
          // Perform cancel action
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
    async Create(data, callback) {

      const csrfToken = this.getCookie('csrftoken')
      axios.defaults.headers.common['X-CSRFToken'] = csrfToken;

      console.log("token :" + csrfToken)
      console.log("DataList :" + JSON.stringify(this.DataList))

      // {"email":"mohamedkaabi90@gmail.com","role":"root","groups":["Group 2","Group 3"],"deactivateUser":true,"fullname":"name","password":"password","username":"username"}

      const params = {
        groupname: data.groupname,
        description: data.description,
        sudoers: data.sudoers
      }

      console.log("params are : " + JSON.stringify(params))

      axios.post('/groups/createGroup', params)
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
      console.log("group id :" + id)

      axios.delete(`/groups/deleteGroup/${id}`)

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
    async update(data, callback) {

      const csrfToken = this.getCookie('csrftoken')
      axios.defaults.headers.common['X-CSRFToken'] = csrfToken;

      console.log("token :" + csrfToken)
      console.log("DataList :" + JSON.stringify(data))

      axios.put(`/groups/groupChangeGroupname/${data.id}`
        , {
          "Newgroupname": data.groupname,
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
    async getgroup(id, callback) {

      axios.get(`/groups/getGroup/${id}`)
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
