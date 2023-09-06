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
                            <v-btn class="ml-3 mt-2 " color="primary" text @click="addRow">
                                <i class="fas fa-plus"></i>
                                <span class="ml-2">Add</span>
                            </v-btn>
                        </v-col>
                    </v-row>
                </v-card-title>
                <v-card-text>
                    <ag-grid-vue id="grid-wrapper" domLayout="autoHeight" class="ag-theme-alpine" :columnDefs="columnDefs"
                        :rowData="rowData" @grid-ready="onGridReady" :rowDrag="true" :defaultColDef="defaultColDef"
                        :editType="editType" style="width: 100%;" @cell-value-changed="onCellValueChanged"
                        @row-value-changed="onRowValueChanged" @selection-changed="onSelectionChanged"
                        @column-row-group-changed="onColumnRowGroupChanged" @column-row-drag-end="onColumnRowDragEnd"
                        @row-drag-end="onRowDragEnd" :pagination="true" :paginationPageSize="10" :rowSelection="'multiple'">
                    </ag-grid-vue>
                </v-card-text>
            </v-card>
        </div>
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
import axios from 'axios';

export default {
    name: 'FirewallComponent',
    components: {
        AgGridVue,
    },
    props: {
        activeTab: {
            type: String,
        },
    },
    data() {
        return {
            columnDefs: [
                {
                    width: 50,
                    minWidth: 50,
                    maxWidth: 50,
                    rowDrag: true,
                    rowDragText: (params) => {
                        return params.rowNode.data.Rule_description;
                    },
                },
                {
                    headerCheckboxSelection: true,
                    checkboxSelection: true,
                    editable: false,
                    width: 100,
                    minWidth: 100,
                    maxWidth: 100,
                },
                {
                    field: 'policy',
                    headerName: 'Policy',
                    cellEditor: 'agSelectCellEditor',
                    cellEditorParams: {
                        values: ['Allow', 'Deny'],
                    },
                    editable: params => params.node.data.isRowSelected,
                },
                {
                    field: 'Rule_description',
                    headerName: 'Rule Description',
                    editable: params => params.node.data.isRowSelected,
                    headerName: 'Rule Description',
                },
                {
                    field: 'protocol',
                    headerName: 'Protocol',
                    cellEditor: 'agSelectCellEditor',
                    cellEditorParams: {
                        values: ['TCP', 'UDP', 'ICMP'],
                    },
                    editable: params => params.node.data.isRowSelected,
                },
                {
                    field: 'saddr',
                    headerName: 'Src Address',
                    editable: params => params.node.data.isRowSelected,
                    valueSetter: (params) => {
                        const value = params.newValue;
                        if (this.isValidIPAddress(value)) {
                            params.data.saddr = value;
                            return true; // Value is valid, update the cell
                        } else {
                            // Value is invalid, display a validation message
                            alert('Please enter a valid source IP address');
                            return false; // Value is not updated
                        }
                    },
                },
                {
                    field: 'sport',
                    headerName: 'Src Port',
                    editable: params => params.node.data.isRowSelected,
                    valueParser: this.numericValueParser,
                    valueSetter: (params) => {
                        const value = params.newValue;
                        if (this.isValidPortNumber(value)) {
                            params.data.sport = value;
                            return true; // Value is valid, update the cell
                        } else {
                            // Value is invalid, display a validation message
                            alert('Please enter a valid source port number');
                            return false; // Value is not updated
                        }
                    },
                },
                {
                    headerName: 'Dst Address',
                    field: 'daddr',
                    editable: params => params.node.data.isRowSelected,
                    valueSetter: (params) => {
                        const value = params.newValue;
                        if (this.isValidIPAddress(value)) {
                            params.data.daddr = value;
                            return true; // Value is valid, update the cell
                        } else {
                            // Value is invalid, display a validation message without using alert
                            alert('Please enter a valid destination IP address');
                            return false; // Value is not updated
                        }
                    },
                },
                {
                    field: 'dport',
                    headerName: 'Dst Port',
                    editable: params => params.node.data.isRowSelected,
                    valueParser: this.numericValueParser,
                    valueSetter: (params) => {
                        const value = params.newValue;
                        if (this.isValidPortNumber(value)) {
                            params.data.dport = value;
                            return true; // Value is valid, update the cell
                        } else {
                            // Value is invalid, display a validation message
                            alert('Please enter a valid destination port number');
                            return false; // Value is not updated
                        }
                    },
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
            rowData: [],
            filterText: null,
            columnOrder: [],
            rules: [],
        };
    },
    created() {
        this.editType = 'fullRow';
    },
    methods: {
        onCellValueChanged(event) {
            const row = event.data;
            row.isModified = true;
        },
        onRowValueChanged(event) {
            var data = event.data;
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

            this.gridApi.refreshCells({ columns: ['Policy', 'Rule_description', 'protocol', 'saddr', 'sport', 'daddr', 'dport', 'Action'] });
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
          class="action-button delete"
          data-action="delete">
            <i class="fas fa-times" style="color: #086eae;"></i>
        </button>
        `;
            }
            else {
                eGui.innerHTML = `
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
            console.log('Row data:', rowData);
            switch (action) {
                case 'delete':
                    if (rowData.id) {
                        axios.delete('http://127.0.0.1:8000/rules/deleteRule/' + rowData.id)
                            .then(response => {
                                // Access response data
                                const responseData = response.data;
                                if (responseData.msg === "delete rule Successfully!!") {
                                    // Delete the row from the grid
                                    const index = this.rowData.indexOf(rowData);
                                    if (index > -1) {
                                        this.rowData.splice(index, 1);
                                    }
                                } else {
                                    console.error('Failed to delete row');
                                }
                            })
                            .catch(error => {
                                console.error(error);
                            });

                    } else {
                        const index = this.rowData.indexOf(rowData);
                        if (index > -1) {
                            this.rowData.splice(index, 1);
                        }
                    }
                    break;
                default:
                    break;
            }
        },
        addRow() {
            const newRow = {
                isSelected: false,
                isRowSelected: false,
                isModified: false,
                policy: 'Allow',
                Rule_description: '',
                protocol: 'TCP',
                saddr: '',
                sport: 'ANY',
                daddr: '',
                dport: 'ANY',
                Action: '',
            };
            this.rowData.push(newRow);

            // Select the newly added row
            this.gridApi.forEachNode(node => node.setSelected(node.data === newRow));

        },
        arrayMove(arr, fromIndex, toIndex) {
            const element = arr[fromIndex];
            arr.splice(fromIndex, 1);
            arr.splice(toIndex, 0, element);
            return arr.slice(); // Create a new array reference
        },
        onRowDragEnd(event) {
            const updatedRows = event.overIndex !== undefined
                ? this.arrayMove(this.rowData, event.node.rowIndex, event.overIndex)
                : this.rowData;

            this.rowData = updatedRows;
        },
        onColumnRowGroupChanged(event) {
            const newColumnOrder = event.columns.map(column => column.colId);
            this.gridApi.setColumnDefs(this.columnDefs);
            this.gridApi.setColumnOrder(newColumnOrder);
        },
        onColumnRowDragEnd(event) {
            if (event && event.columns) {
                this.columnOrder = event.columns.map(column => column.colId);

                // Apply the new column order to the grid
                this.gridApi.setColumnDefs(this.columnDefs);
                this.gridApi.setColumnOrder(this.columnOrder);
            } else {
                console.log('event.columns is undefined or null');
            }
        },
        numericValueParser(params) {
            const parsedValue = parseInt(params.newValue);
            if (isNaN(parsedValue)) {
                // Return the original value if parsing fails
                return params.oldValue;
            }
            return parsedValue;
        },
        isValidIPAddress(value) {
            const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/;
            return ipRegex.test(value);
        },
        isValidPortNumber(value) {
            const portRegex = /^\d{1,5}$/;
            return portRegex.test(value);
        },
        isValidRowData(rowData) {
            const requiredColumns = ['policy', 'Rule_description', 'protocol', 'saddr', 'daddr'];
            for (const column of requiredColumns) {
                if (!rowData[column]) {
                    return false; // Data in a required column is missing
                }
            }
            return true; // All required columns have data
        },
        validateGridData(gridData) {
            const requiredColumns = ['policy', 'Rule_description', 'protocol', 'saddr', 'daddr'];
            for (const row of gridData) {
                for (const column of requiredColumns) {
                    if (!row[column]) {
                        return false; // Data in a required column is missing
                    }
                }
            }
            return true; // All required columns have data
        },
        cancel() {
            console.log('Cancel clicked');
        },
        async save() {

            const isValid = this.validateGridData(this.rowData);
            if (isValid) {
                // Data is valid, proceed with your logic

                // Filter the modified rows
                const modifiedRows = this.rowData.filter(row => row.isModified);
                console.log('Modified rows:', modifiedRows);

                // Prepare data for API
                const dataToSend = modifiedRows.map(row => {
                    // Convert row data to the required format for your API
                    return {
                        policy: row.policy === 'Allow' ? 'accept' : 'drop',
                        Rule_description: row.Rule_description,
                        protocol: row.protocol === 'TCP' ? 'tcp' : row.protocol === 'UDP' ? 'udp' : 'icmp',
                        saddr: row.saddr,
                        daddr: row.daddr,
                        sport: row.sport === 'ANY' ? '' : row.sport,
                        dport: row.dport,
                        type_rule: "inbound",
                    };
                });
                function getCookie(name) {
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
                }
                const csrfToken = getCookie('csrftoken')
                axios.defaults.headers.common['X-CSRFToken'] = csrfToken;

                try {
                    // Send data to API
                    const response = await axios.post('http://127.0.0.1:8000/rules/saveRules/LAN', dataToSend);

                    // Handle API response
                    if (response.status === 200) {
                        // Clear the modified flag for the saved rows
                        modifiedRows.forEach(row => row.isModified = false);
                    } else {
                        console.error('Failed to save data');
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            } else {
                // Data is not valid, show an error message or take appropriate action
                console.error('Data is not valid');
                this.$toast.error('Data is not valid. Please check required fields.');
            }
        },
    },
    mounted() {
        this.rules = this.$root.$data.rules;
        let validJsonString = this.rules
            .replace(/'/g, '"')
            .replace(/True/g, 'true')
            .replace(/False/g, 'false')
            .replace(/None/g, 'null');
        let parsedArray = JSON.parse(validJsonString);
        this.rules = parsedArray;
    },
    watch: {
        // Whenever rules changes, rowData will be updated
        rules: {
            handler: function (val, oldVal) {
                this.rowData = val[this.activeTab]['inbound'];
            },
            deep: true,
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