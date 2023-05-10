<template>
    <v-container fluid>
        <ag-grid-vue
            style="width: 100%;height:100%"
            class="ag-theme-alpine"
            :columnDefs="columnDefs"
            :rowData="rowData"
        />
    </v-container>
</template>
<script>
import { AgGridVue } from 'ag-grid-vue';

export default {
    name: 'UserManagement',
    props: {
        users: {
            type: Object,
            required: true,
        },
        columnDefs: [
            { headerName: "Make", field: "make" },
            { headerName: "Model", field: "model" },
            { headerName: "Price", field: "price" },
        ],
        rowData: [
            { make: "Toyota", model: "Celica", price: 35000 },
            { make: "Ford", model: "Mondeo", price: 32000 },
            { make: "Porsche", model: "Boxster", price: 72000 },
        ],
    },
    methods: {
    },
};
</script>
<style lang="scss">
   @import "~ag-grid-community/dist/styles/ag-grid.css";
   @import "~ag-grid-community/dist/styles/ag-theme-alpine.css";
</style>
