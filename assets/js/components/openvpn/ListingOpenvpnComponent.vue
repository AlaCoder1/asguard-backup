<template>
    <div class="mt-3 ml-3 mr-3">
        <v-row>
            <v-col cols="12">
                <h4> List Servers</h4>
                <v-divider></v-divider>
                <div style="display: flex; flex-direction: column">
                    <ag-grid-vue id="grid-wrapper" domLayout="autoHeight" class="ag-theme-alpine mt-3"
                        :columnDefs="columnServers" :rowData="rowDataServers" :gridOptions="gridOptions"
                        style="width: 100%;" @first-data-rendered="onFirstDataRendered"
                        @grid-size-changed="onGridSizeChanged" :autoGroupColumnDef="autoGroupColumnDef"
                        :rowGroupPanelShow="rowGroupPanelShow" />
                    <div class="d-flex justify-end mt-3">
                        <v-btn large rounded outlined color="primary" class="mr-3" @click="publishServer">Publish
                            Server</v-btn>
                        <v-btn large rounded outlined color="primary" class="mr-3" @click="addServer">Add Server</v-btn>

                    </div>
                </div>
            </v-col>
        </v-row>
        <v-row>
            <v-col cols="12">
                <h4>List Clients</h4>
                <v-divider></v-divider>
                <div style="display: flex; flex-direction: column">
                    <ag-grid-vue id="grid-wrapper" domLayout="autoHeight" class="ag-theme-alpine mt-3"
                        :columnDefs="columnClients" :rowData="rowDataClients" :gridOptions="gridOptions"
                        style="width: 100%;" @first-data-rendered="onFirstDataRendered"
                        @grid-size-changed="onGridSizeChanged" :autoGroupColumnDef="autoGroupColumnDef"
                        :rowGroupPanelShow="rowGroupPanelShow" />
                    <div class="d-flex justify-end mt-3">
                        <v-btn large rounded outlined color="primary" class="mr-3" @click="publishClient">Publish Client</v-btn>
                            <v-btn large rounded outlined color="primary" class="mr-3" @click="addClient">Add Client</v-btn>
                    </div>
                    <br />
                </div>

            </v-col>
        </v-row>
    </div>
</template>


<script>
import { AgGridVue } from 'ag-grid-vue';

export default {
    name: 'ListingOpenvpnComponent',
    components: {
        AgGridVue,
    },
    props: {
    },
    data() {
        return {
            columnServers: [
                { headerName: 'Server Name', field: 'serverNname', sortable: true, filter: true, checkboxSelection: true },
                { headerName: 'Protocole / Port', field: 'protocolPort', sortable: true, filter: true },
                { headerName: 'Network Tunnel', field: 'networkTunnel', sortable: true, filter: true },
                { headerName: 'Description', field: 'description', sortable: true, filter: true },
                { headerName: 'Published', field: 'published', sortable: true, filter: true },
                { headerName: 'Action', cellRenderer: this.actionCellRenderer, minWidth: 150, field: 'action', sortable: true, filter: true }
            ],
            rowDataServers: [
                {
                    id: 1,
                    serverNname: 'Server 1',
                    protocolPort: 'UDP/1194',
                    networkTunnel: '256 bit AES-GCM with 128 bit ICV',
                    description: 'Server 1',
                    published: 'Yes',
                    action: 'Edit'
                }
            ],
            columnClients: [
                { headerName: 'Client Name', field: 'clientName', sortable: true, filter: true, checkboxSelection: true },
                { headerName: 'Protocole / Port', field: 'protocolPort', sortable: true, filter: true },
                { headerName: 'Server', field: 'server', sortable: true, filter: true },
                { headerName: 'Description', field: 'description', sortable: true, filter: true },
                { headerName: 'Published', field: 'published', sortable: true, filter: true },
                { headerName: 'Action', cellRenderer: this.actionCellRenderer, minWidth: 150, field: 'action', sortable: true, filter: true }
            ],
            rowDataClients: [
                {
                    id: 1,
                    clientName: 'Client 1',
                    protocolPort: 'UDP/1194',
                    server: 'Server 1',
                    description: 'Client 1',
                    published: 'Yes',
                    action: 'Edit'
                }
            ],
            gridOptions: {
                rowSelection: 'multiple',
                rowMultiSelectWithClick: true,
                onRowClicked: function (event) {
                    console.log(event.node.data);
                },
                onRowSelected: function (event) {
                    console.log(event.node.data);
                },
                onRowEditingStopped: (params) => {
                    params.api.refreshCells({
                        columns: ['action'],
                        rowNodes: [params.node],
                        force: true,
                    });
                },
            },
            autoGroupColumnDef: null,
            rowGroupPanelShow: null,
        }
    },
    created() {
        this.autoGroupColumnDef = {
            headerName: 'Server Name',
            field: 'serverNname',
            minWidth: 300,
            cellRenderer: 'agGroupCellRenderer',
            cellRendererParams: {
                checkbox: true,
            },
        };
        this.rowGroupPanelShow = 'always';
    },
    computed: {
    },
    methods: {
        onFirstDataRendered(params) {
            params.api.sizeColumnsToFit();
        },
        onGridSizeChanged(params) {
            params.api.sizeColumnsToFit();
        },
        actionCellRenderer(params) {
            let eGui = document.createElement('div');
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
            }
            else {
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
                    console.log('Edit clicked for row:', rowData);
                    break;
                case 'delete':
                    console.log('Delete clicked for row:', rowData);
                    const index = this.rowData.findIndex(item => item.id === rowData.id);
                    if (index !== -1) {
                        this.rowData.splice(index, 1);
                    }
                    break;
                default:
                    break;
            }
        },
        publishServer() {
            console.log('publishServer');
        },
        addServer() {
            console.log('addServer');
        },
        publishClient() {
            console.log('publishClient');
        },
        addClient() {
            console.log('addClient');
        }
    },

}
</script>

<style lang="scss">
@import "~ag-grid-community/dist/styles/ag-grid.css";
@import "~ag-grid-community/dist/styles/ag-theme-alpine.css";
</style>