<template>
    <div>
        <div class="container">
            <h4>Inbound rules</h4>
            <v-divider></v-divider>
            <v-card class="mt-3">
                <v-card-title>
                    <v-row>
                        <v-col cols="12" md="6">
                            <v-text-field id="filter-text-box" v-model="filterText" append-icon="mdi-magnify" label="Search"
                                single-line hide-details rounded outlined dense
                                @input="onFilterTextBoxChanged"></v-text-field>
                        </v-col>
                        <v-col cols="12" md="6" class="d-flex justify-end">
                            <v-btn class="ml-3 mt-2 " color="primary" text>
                                <i class="fas fa-plus"></i>
                                <span class="ml-2">Add</span>
                            </v-btn>
                        </v-col>
                    </v-row>
                </v-card-title>
                <v-card-text>
                    <ag-grid-vue id="grid-wrapper" domLayout="autoHeight" class="ag-theme-alpine" :columnDefs="columnDefs"
                        :rowData="rowData" @grid-ready="onGridReady" :defaultColDef="defaultColDef" :editType="editType"
                        style="width: 100%;" @cell-value-changed="onCellValueChanged" @row-value-changed="onRowValueChanged"
                        @selection-changed="onSelectionChanged" />
                </v-card-text>
                <v-card-actions class="d-flex justify-end">
                    <v-btn large rounded outlined color="#086eae" class="mr-3 trac-cancel" @click="cancel">
                        Cancel
                    </v-btn>
                    <v-btn large rounded outlined color="#ffff" class="mr-3 trac-edit" @click="finishEditing">
                        Finish editing
                    </v-btn>
                </v-card-actions>
            </v-card>
        </div>
        <div class="container">
            <h4>Outbound rules</h4>
            <v-divider></v-divider>
            <v-card class="mt-3">
                <v-card-title>
                    <v-row>
                        <v-col cols="12" md="6">
                            <v-text-field id="filter-text-box" v-model="filterText" append-icon="mdi-magnify" label="Search"
                                single-line hide-details rounded outlined dense
                                @input="onFilterTextBoxChanged"></v-text-field>
                        </v-col>
                        <v-col cols="12" md="6" class="d-flex justify-end">
                            <v-btn class="ml-3 mt-2 " color="primary" text>
                                <i class="fas fa-plus"></i>
                                <span class="ml-2">Add</span>
                            </v-btn>
                        </v-col>
                    </v-row>
                </v-card-title>
                <v-card-text>
                    <ag-grid-vue id="grid-wrapper" domLayout="autoHeight" class="ag-theme-alpine" :columnDefs="columnDefs"
                        :rowData="rowData" @grid-ready="onGridReady" :defaultColDef="defaultColDef" :editType="editType"
                        style="width: 100%;" @cell-value-changed="onCellValueChanged" @row-value-changed="onRowValueChanged"
                        @selection-changed="onSelectionChanged" />
                </v-card-text>
                <v-card-actions class="d-flex justify-end">
                    <v-btn large rounded outlined color="#086eae" class="mr-3 trac-cancel" @click="cancel">
                        Cancel
                    </v-btn>
                    <v-btn large rounded outlined color="#ffff" class="mr-3 trac-edit" @click="finishEditing">
                        Finish editing
                    </v-btn>
                </v-card-actions>
            </v-card>
        </div>
        <div class="container">
            <h4>Cellular fallover rules</h4>
            <v-divider></v-divider>
            <v-card class="mt-3">
                <v-card-title>
                    <v-row>
                        <v-col cols="12" md="6">
                            <v-text-field id="filter-text-box" v-model="filterText" append-icon="mdi-magnify" label="Search"
                                single-line hide-details rounded outlined dense
                                @input="onFilterTextBoxChanged"></v-text-field>
                        </v-col>
                        <v-col cols="12" md="6" class="d-flex justify-end">
                            <v-btn class="ml-3 mt-2 " color="primary" text>
                                <i class="fas fa-plus"></i>
                                <span class="ml-2">Add</span>
                            </v-btn>
                        </v-col>
                    </v-row>
                </v-card-title>
                <v-card-text>
                    <ag-grid-vue id="grid-wrapper" domLayout="autoHeight" class="ag-theme-alpine" :columnDefs="columnDefs"
                        :rowData="rowData" @grid-ready="onGridReady" :defaultColDef="defaultColDef" :editType="editType"
                        style="width: 100%;" @cell-value-changed="onCellValueChanged" @row-value-changed="onRowValueChanged"
                        @selection-changed="onSelectionChanged" />
                </v-card-text>
                <v-card-actions class="d-flex justify-end">
                    <v-btn large rounded outlined color="#086eae" class="mr-3 trac-cancel" @click="cancel">
                        Cancel
                    </v-btn>
                    <v-btn large rounded outlined color="#ffff" class="mr-3 trac-edit" @click="finishEditing">
                        Finish editing
                    </v-btn>
                </v-card-actions>
            </v-card>
        </div>
        <div class="container">
            <h4>Inbound cellular failover rules</h4>
            <v-divider></v-divider>
            <v-card class="mt-3">
                <v-card-title>
                    <v-row>
                        <v-col cols="12" md="6">
                            <v-text-field id="filter-text-box" v-model="filterText" append-icon="mdi-magnify" label="Search"
                                single-line hide-details rounded outlined dense
                                @input="onFilterTextBoxChanged"></v-text-field>
                        </v-col>
                        <v-col cols="12" md="6" class="d-flex justify-end">
                            <v-btn class="ml-3 mt-2 " color="primary" text>
                                <i class="fas fa-plus"></i>
                                <span class="ml-2">Add</span>
                            </v-btn>
                        </v-col>
                    </v-row>
                </v-card-title>
                <v-card-text>
                    <ag-grid-vue id="grid-wrapper" domLayout="autoHeight" class="ag-theme-alpine" :columnDefs="columnDefs"
                        :rowData="rowData" @grid-ready="onGridReady" :defaultColDef="defaultColDef" :editType="editType"
                        style="width: 100%;" @cell-value-changed="onCellValueChanged" @row-value-changed="onRowValueChanged"
                        @selection-changed="onSelectionChanged" />
                </v-card-text>
                <v-card-actions class="d-flex justify-end">
                    <v-btn large rounded outlined color="#086eae" class="mr-3 trac-cancel" @click="cancel">
                        Cancel
                    </v-btn>
                    <v-btn large rounded outlined color="#ffff" class="mr-3 trac-edit" @click="finishEditing">
                        Finish editing
                    </v-btn>
                </v-card-actions>
            </v-card>
        </div>
         <!-- Centered buttons container -->
        <div class="container">
          <div class="row justify-content-center">
            <div class="col-12 text-center">
              <v-btn large rounded outlined color="#086eae" class="mr-3 trac-cancel" @click="cancel">
                Cancel
              </v-btn>
              <v-btn large rounded outlined color="#ffff" class="mr-3 trac-edit" @click="save">
                Save
              </v-btn>
            </div>
          </div>
        </div>
        <br /><br /><br />
    </div>
</template>


<script>
import { AgGridVue } from 'ag-grid-vue';

export default {
    name: 'FirewallComponent',
    components: {
        AgGridVue
    },
    data() {
        return {
            columnDefs: [
                {
                    headerCheckboxSelection: true,
                    checkboxSelection: true,
                    width: 5,
                    editable: false,
                    headerCheckboxSelectionFilteredOnly: true,
                    suppressMenu: false,
                    suppressMovable: false,
                    suppressNavigable: false,
                    suppressResize: false,
                    suppressSizeToFit: false,
                    suppressSorting: false,
                    suppressToolPanel: false,
                    suppressColumnsToolPanel: false,
                    suppressFiltersToolPanel: false,
                    suppressRowDrag: false,
                    suppressMoveWhenRowDragging: false,
                    suppressScrollOnNewData: false,
                    suppressPaginationPanel: false,
                    suppressFieldDotNotation: false,
                    suppressFocusAfterRefresh: false,
                },
                {
                    field: 'Policy',
                    cellEditor: 'agSelectCellEditor',
                    cellEditorParams: {
                        values: ['Allow', 'Deny'],
                    },
                    editable: params => params.node.data.isRowSelected
                },
                {
                    field: 'ruleDescription',
                    editable: params => params.node.data.isRowSelected,
                    headerName: 'Rule Description',
                },
                {
                    field: 'Protocol',
                    cellEditor: 'agSelectCellEditor',
                    cellEditorParams: {
                        values: ['TCP', 'UDP', 'ICMP'],
                    },
                    editable: params => params.node.data.isRowSelected
                },
                {
                    field: 'Source',
                    editable: params => params.node.data.isRowSelected
                },
                {
                    field: 'srcPort',
                    headerName: 'Src Port',
                    editable: params => params.node.data.isRowSelected
                },
                {
                    headerName: 'Destination',
                    editable: params => params.node.data.isRowSelected
                },
                {
                    field: 'dstPort',
                    headerName: 'Dst Port',
                    editable: params => params.node.data.isRowSelected
                },
                {
                    headerName: 'Action',
                    cellRenderer: this.actionCellRenderer,
                    editable: false,
                },
            ],
            gridApi: null,
            columnApi: null,
            defaultColDef: {
                flex: 1,
                editable: true,
                cellDataType: false,
            },
            editType: null,
            rowData: [
                {
                    isSelected: false,
                    isRowSelected: false,
                    Policy: 'Allow',
                    ruleDescription: 'Rule 1',
                    Protocol: 'TCP',
                    Source: ' ',
                    srcPort: 'ANY',
                    Destination: ' ',
                    dstPort: 'ANY',
                    Action: ' ',
                },
                {
                    isSelected: false,
                    isRowSelected: false,
                    Policy: 'Allow',
                    ruleDescription: 'Rule 2',
                    Protocol: 'UDP',
                    Source: ' ',
                    srcPort: 'ANY ',
                    Destination: ' ',
                    dstPort: 'ANY',
                    Action: ' ',
                },
                {
                    isSelected: false,
                    isRowSelected: false,
                    Policy: 'Allow',
                    ruleDescription: 'Rule 3',
                    Protocol: 'ICMP',
                    Source: ' ',
                    srcPort: 'ANY',
                    Destination: ' ',
                    dstPort: 'ANY',
                    Action: ' ',
                }
            ],
            filterText: null,
        };
    },
    created() {
        this.editType = 'fullRow';
    },
    methods: {
        onCellValueChanged(event) {
            console.log('onCellValueChanged: ' + event.colDef.field + ' = ' + event.newValue);
        },
        onRowValueChanged(event) {
            var data = event.data;
            console.log('onRowValueChanged: (' + data.Policy + ', ' + data.ruleDescription + ', ' + data.Protocol + ', ' + data.Source + ', ' + data.srcPort + ', ' + data.Destination + ', ' + data.dstPort + ', ' + data.Action + ')');
        },
        onGridReady(params) {
            this.gridApi = params.api;
            this.gridColumnApi = params.columnApi;

            if (this.rowData.length > 0) {
                this.gridApi.forEachNode(node => node.setSelected(node.rowIndex === 0));
            }
        },
        onSelectionChanged() {
            const selectedNodes = this.gridApi.getSelectedNodes();
            this.rowData.forEach(row => {
                row.isSelected = selectedNodes.some(node => node.data === row);
                row.isRowSelected = row.isSelected;
            });

            this.gridApi.refreshCells({ columns: ['Policy', 'ruleDescription', 'Protocol', 'Source', 'srcPort', 'Destination', 'dstPort', 'Action'] });
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
        onFilterTextBoxChanged() {
            this.gridApi.setQuickFilter(
                document.getElementById('filter-text-box').value
            );
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
        cancel() {
            console.log('Cancel clicked');
        },
        finishEditing() {
            console.log('Finish Editing clicked');
        },
        save() {
            console.log('Save clicked');
        },
    },
};

</script>

<style lang="scss">
@import "~ag-grid-community/dist/styles/ag-grid.css";
@import "~ag-grid-community/dist/styles/ag-theme-alpine.css";

.action-button:hover {
    color: #086eae;
}

.action-button.update {
    color: #00b300;
}

.action-button.cancel {
    color: #ff0000;
}

.action-button.edit {
    color: #086eae;
}

.action-button.delete {
    color: #086eae;
}


.ag-theme-alpine .ag-header {
    background-color: #f5f5f5;
}

.trac-edit {
    height: 43px;
    width: 183px;
    background-color: #086eae;
    color: #ffffff;
    font-family: "Nunito-Regular", Helvetica;
    font-size: 20px;
    font-weight: 400;
    left: 0;
    letter-spacing: 0;
    line-height: normal;
    text-align: center;
    text-transform: capitalize;
}

.trac-cancel {
    height: 43px;
    width: 183px;

    font-family: "Nunito-Regular", Helvetica;
    font-size: 20px;
    font-weight: 400;
    left: 0;
    letter-spacing: 0;
    line-height: normal;
    text-align: center;
    text-transform: capitalize;
}
</style>
