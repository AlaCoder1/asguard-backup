<template>
    <div>
        <h4>User management</h4>
        <v-divider></v-divider>
        <ag-grid-vue domLayout="autoHeight" class="ag-theme-alpine mt-3" :columnDefs="columnDefs" :rowData="rowData"
            :gridOptions="gridOptions" />
        <v-row class="mt-3 flex">
            <v-spacer></v-spacer>
            <v-btn color="dms_blue_dark" :rounded="true">
                <span class="text-white c-o">Cancel</span>
            </v-btn>
            <v-btn color="dms_blue_dark" :rounded="true" class="ml-2">
                <span class="text-white c-o">Save</span>
            </v-btn>
        </v-row>
    </div>
</template>

<script>
import { AgGridVue } from 'ag-grid-vue';
export default {
    name: 'UserManagement',
    components: {
        AgGridVue,
    },
    props: {
    },
    data() {
        return {
            columnDefs: [
                { headerName: "Username", field: "username", sortable: true, filter: true, editable: true },
                { headerName: "Email", field: "email", sortable: true, filter: true, editable: true },
                { headerName: "Role", field: "role", sortable: true, filter: true, editable: true },
                {
                    headerName: "Authorized for open VPN clien",
                    field: "authorized_for_openvpn_client",
                    sortable: true,
                    filter: true,
                    editable: true,
                },
                { headerName: "Expires", field: "expires", sortable: true, filter: true, editable: true },
                { headerName: "Created", field: "created", sortable: true, filter: true, editable: true },
                { headerName: "Authorized By", field: "authorized_by", sortable: true, filter: true, editable: true },
            ],

            rowData: [
                {
                    id: 1, username: "John", email: "username@gmail.com",
                    role: "Admin", authorized_for_openvpn_client: "Yes", expires: "2021-01-01",
                    created: "2021-01-01", authorized_by: "Admin"
                },
            ],
            gridOptions: {
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

    methods: {
    }
};
</script>
<style lang="scss">
@import "~ag-grid-community/dist/styles/ag-grid.css";
@import "~ag-grid-community/dist/styles/ag-theme-alpine.css";
</style>
