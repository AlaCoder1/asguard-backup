<template>
  <div>
    <h4>Networks admins</h4>
    <ag-grid-vue domLayout="autoHeight" class="ag-theme-alpine mt-3 m-w-80" :columnDefs="columnDefs" :rowData="rowData"
      :gridOptions="gridOptions" />
    <v-btn color="dms_blue_dark" :rounded="true" class="mt-3 add-btn-user" @click="openModal">
      <span class="text-white">Add user</span>
    </v-btn>
    <Modal_User :mode="modalMode" :isOpen="isModalOpen" @closeModal="closeModal" :initialData="modalData"
      @updateModalData="handleModalUpdate" />
  </div>
</template>

<script>
import { AgGridVue } from 'ag-grid-vue';
import Modal_User from '../components/layout/Modal_User.vue';

export default {
  name: 'UserManagement',
  components: {
    AgGridVue,
    Modal_User,
  },
  props: {
    DataList: {
      type: Array, // Assuming DataList is an array
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
    // Watch for changes in the DataList prop
    DataList: {
      handler(newData) {
        this.rowData = newData; // Update rowData with the new prop value
      },
      immediate: true, // This will trigger the watcher when the component is created to initialize rowData
    },
  },
  methods: {
    // Rest of the methods
  },
};
</script>

<style lang="scss">
@import "~ag-grid-community/dist/styles/ag-grid.css";
@import "~ag-grid-community/dist/styles/ag-theme-alpine.css";
</style>