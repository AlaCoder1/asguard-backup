<template>
    <div>
        <div class="container">
            <h4>Inbound rules</h4>
            <v-divider></v-divider>
            <v-alert type="success" class="d-flex mt-3" v-if="alert">
                <span class="justify-end">
                    <i class="fas fa-check-circle "></i>
                </span>
                <span class="c-o ml-3">
                    <strong>Success!</strong> Rules saved successfully.
                </span>
                <span class="ml-16" style="margin-top: 20px !important;">
                    <i class="fas fa-times justify-end cursor" @click="handleRemove"></i>
                </span>
            </v-alert>
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
                    <v-btn large rounded outlined color="#086eae" class="mr-3 trac-cancel" @click="cancel"
                        :disabled="isSaveDisabled">
                        Cancel
                    </v-btn>
                    <v-btn large rounded outlined color="#ffff" class="mr-3 trac-edit" @click="save"
                        :disabled="isSaveDisabled">
                        Save
                    </v-btn>
                </div>
            </div>
        </div>

        <!-- Outbound -->
        <div class="container">
            <h4>Outbound rules</h4>
            <v-divider></v-divider>
            <v-alert type="success" class="d-flex mt-3" v-if="alertOutbound">
                <span class="justify-end">
                    <i class="fas fa-check-circle "></i>
                </span>
                <span class="c-o ml-3">
                    <strong>Success!</strong> Rules saved successfully.
                </span>
                <span class="ml-16" style="margin-top: 20px !important;">
                    <i class="fas fa-times justify-end cursor" @click="handleRemoveOutbound"></i>
                </span>
            </v-alert>
            <v-card class="mt-3">
                <v-card-title>
                    <v-row>
                        <v-col cols="12" md="6">
                            <v-text-field id="filter-text-box-outbound" v-model="filterTextOutbound"
                                append-icon="mdi-magnify" label="Search" single-line hide-details rounded outlined dense
                                @input="onFilterTextBoxChangedOutbound"></v-text-field>
                        </v-col>
                        <v-col cols="12" md="6" class="d-flex justify-end">
                            <v-btn class="ml-3 mt-2 " color="primary" text @click="addRowOutbound">
                                <i class="fas fa-plus"></i>
                                <span class="ml-2">Add</span>
                            </v-btn>
                        </v-col>
                    </v-row>
                </v-card-title>
                <v-card-text>
                    <ag-grid-vue id="grid-wrapper" domLayout="autoHeight" class="ag-theme-alpine"
                        :columnDefs="columnDefsOutbound" :rowData="rowDataOutbound" @grid-ready="onGridReadyOutbound"
                        :rowDrag="true" :defaultColDef="defaultColDefOutbound" :editType="editType" style="width: 100%;"
                        @cell-value-changed="onCellValueChangedOutbound" @row-value-changed="onRowValueChangedOutbound"
                        @selection-changed="onSelectionChangedOutbound" @column-row-group-changed="onColumnRowGroupChanged"
                        @column-row-drag-end="onColumnRowDragEnd" @row-drag-end="onRowDragEndOutbound" :pagination="true"
                        :paginationPageSize="10" :rowSelection="'multiple'">
                    </ag-grid-vue>
                </v-card-text>
            </v-card>
        </div>
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-12 text-center">
                    <v-btn large rounded outlined color="#086eae" class="mr-3 trac-cancel" @click="cancelOutbound"
                        :disabled="isSaveDisabledOutbound">
                        Cancel
                    </v-btn>
                    <v-btn large rounded outlined color="#ffff" class="mr-3 trac-edit" @click="saveOutbound"
                        :disabled="isSaveDisabledOutbound">
                        Save
                    </v-btn>
                </div>
            </div>
        </div>
        <br /> <br /> <br />
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
        id: String,
        activeTab: String,
    },
    data() {
        return {
            columnDefs: [
                {
                    width: 50,
                    minWidth: 50,
                    maxWidth: 50,
                    rowDrag: true,
                    editable: false,
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
                        values: ['accept', 'drop'],
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
                        values: ['tcp', 'udp', 'icmp request', 'icmp reply'],
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
                    // Add cellStyle function to disable cell based on protocol value
                    cellStyle: (params) => {
                        // Assuming you want to disable the cell if protocol is "icmp request" or "icmp reply"
                        if (params.data.protocol === 'icmp request' || params.data.protocol === 'icmp reply') {
                            return { 'pointer-events': 'none', 'background-color': '#eee', 'opacity': '0.6' };
                        }
                        // Return null to enable the cell for other values
                        return null;
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
                    // Add cellStyle function to disable cell based on protocol value
                    cellStyle: (params) => {
                        // Assuming you want to disable the cell if protocol is "icmp request" or "icmp reply"
                        if (params.data.protocol === 'icmp request' || params.data.protocol === 'icmp reply') {
                            return { 'pointer-events': 'none', 'background-color': '#eee', 'opacity': '0.6' };
                        }
                        // Return null to enable the cell for other values
                        return null;
                    },
                },
                {
                    headerName: 'Action',
                    cellRenderer: this.actionCellRenderer,
                    editable: false,
                },
            ],
            columnDefsOutbound: [
                {
                    width: 50,
                    minWidth: 50,
                    maxWidth: 50,
                    rowDrag: true,
                    editable: false,
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
                        values: ['accept', 'drop'],
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
                        values: ['tcp', 'udp', 'icmp request', 'icmp reply'],
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
                    // Add cellStyle function to disable cell based on protocol value
                    cellStyle: (params) => {
                        // Assuming you want to disable the cell if protocol is "icmp request" or "icmp reply"
                        if (params.data.protocol === 'icmp request' || params.data.protocol === 'icmp reply') {
                            return { 'pointer-events': 'none', 'background-color': '#eee', 'opacity': '0.6' };
                        }
                        // Return null to enable the cell for other values
                        return null;
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
                    // Add cellStyle function to disable cell based on protocol value
                    cellStyle: (params) => {
                        // Assuming you want to disable the cell if protocol is "icmp request" or "icmp reply"
                        if (params.data.protocol === 'icmp request' || params.data.protocol === 'icmp reply') {
                            return { 'pointer-events': 'none', 'background-color': '#eee', 'opacity': '0.6' };
                        }
                        // Return null to enable the cell for other values
                        return null;
                    },
                },
                {
                    headerName: 'Action',
                    cellRenderer: this.actionCellRendererOutbound,
                    editable: false,
                },
            ],
            gridApi: null,
            gridApiOutbound: null,
            columnApi: null,
            columnApiOutbound: null,
            defaultColDef: {
                flex: 1,
                editable: true,
                cellDataType: false,
            },
            defaultColDefOutbound: {
                flex: 1,
                editable: true,
                cellDataType: false,
            },
            editType: null,
            rowData: [],
            filterText: null,
            columnOrder: [],
            rules: [],
            alert: false,
            alertOutbound: false,
            filterTextOutbound: null,
            rowDataOutbound: [],
            isSaveDisabled: true,
            isSaveDisabledOutbound: true,
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
        onCellValueChangedOutbound(event) {
            const row = event.data;
            row.isModified = true;
        },
        onRowValueChanged(event) {
            var data = event.data;
        },
        onRowValueChangedOutbound(event) {
            var data = event.data;
        },
        onGridReady(params) {
            this.gridApi = params.api;
            this.gridColumnApi = params.columnApi;

            if (this.rowData && this.rowData.length > 0) {
                this.gridApi.forEachNode(node => node.setSelected(node.rowIndex === 0));
            }
        },
        onGridReadyOutbound(params) {
            this.gridApiOutbound = params.api;
            this.gridColumnApiOutbound = params.columnApi;

            if (this.rowDataOutbound && this.rowDataOutbound.length > 0) {
                this.gridApiOutbound.forEachNode(node => node.setSelected(node.rowIndex === 0));
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
        onSelectionChangedOutbound() {
            const selectedNodes = this.gridApiOutbound.getSelectedNodes();
            this.rowDataOutbound.forEach(row => {
                row.isSelected = selectedNodes.some(node => node.data === row);
                row.isRowSelected = row.isSelected;
            });

            this.gridApiOutbound.refreshCells({ columns: ['Policy', 'Rule_description', 'protocol', 'saddr', 'sport', 'daddr', 'dport', 'Action'] });
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
        actionCellRendererOutbound(params) {
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
                    this.handleActionOutbound(action, params.node.data);
                });
            });
            return eGui;
        },
        onFilterTextBoxChanged() {
            this.gridApi.setQuickFilter(
                document.getElementById('filter-text-box').value
            );
        },
        onFilterTextBoxChangedOutbound() {
            this.gridApiOutbound.setQuickFilter(
                document.getElementById('filter-text-box-outbound').value
            );
        },
        handleAction(action, rowData) {
            switch (action) {
                case 'delete':
                    if (rowData.id) {
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
                        axios.delete('/rules/deleteRule/' + rowData.id)
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
        handleActionOutbound(action, rowDataOutbound) {
            switch (action) {
                case 'delete':
                    if (rowDataOutbound.id) {
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
                        axios.delete('/rules/deleteRule/' + rowDataOutbound.id)
                            .then(response => {
                                // Access response data
                                const responseData = response.data;
                                if (responseData.msg === "delete rule Successfully!!") {
                                    // Delete the row from the grid
                                    const index = this.rowDataOutbound.indexOf(rowDataOutbound);
                                    if (index > -1) {
                                        this.rowDataOutbound.splice(index, 1);
                                    }
                                } else {
                                    console.error('Failed to delete row');
                                }
                            })
                            .catch(error => {
                                console.error(error);
                            });
                    } else {
                        const index = this.rowDataOutbound.indexOf(rowDataOutbound);
                        if (index > -1) {
                            this.rowDataOutbound.splice(index, 1);
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
                policy: 'accept',
                Rule_description: '',
                protocol: 'tcp',
                saddr: '',
                sport: '',
                daddr: '',
                dport: '',
                Action: '',
            };
            // Ensure this.rowData is defined before pushing the new row
            if (this.rowData === undefined) {
                this.rowData = [];
            }

            if (this.rowData) {
                this.rowData.push(newRow);

                // Select the newly added row
                this.gridApi.forEachNode(node => node.setSelected(node.data === newRow));
            } else {
                console.error('this.rowData is undefined');
            }

        },
        addRowOutbound() {
            const newRow = {
                isSelected: false,
                isRowSelected: false,
                isModified: false,
                policy: 'accept',
                Rule_description: '',
                protocol: 'tcp',
                saddr: '',
                sport: '',
                daddr: '',
                dport: '',
                Action: '',
            };
            // Ensure this.rowData is defined before pushing the new row
            if (this.rowDataOutbound === undefined) {
                this.rowDataOutbound = [];
            }

            if (this.rowDataOutbound) {
                this.rowDataOutbound.push(newRow);

                // Select the newly added row
                this.gridApiOutbound.forEachNode(node => node.setSelected(node.data === newRow));
            } else {
                console.error('this.rowData is undefined');
            }

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
        onRowDragEndOutbound(event) {
            const updatedRows = event.overIndex !== undefined
                ? this.arrayMove(this.rowDataOutbound, event.node.rowIndex, event.overIndex)
                : this.rowDataOutbound;

            this.rowDataOutbound = updatedRows;
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
        // isValidPortNumber(value) {
        //     const portRegex = /^\d{1,5}$/;
        //     return portRegex.test(value);
        // },
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
            this.rowData = this.rules[this.activeTab]['inbound'].filter(row => row.id);
            // cancel the changes of modfied rows
            this.rowData.forEach(row => {
                if (row.isModified) {
                    row.isModified = false;
                }
            });
        },
        cancelOutbound() {
            this.rowDataOutbound = this.rules[this.activeTab]['outbound'].filter(row => row.id);
            // cancel the changes of modfied rows
            this.rowDataOutbound.forEach(row => {
                if (row.isModified) {
                    row.isModified = false;
                }
            });
        },
        async save() {

            const isValid = this.validateGridData(this.rowData);
            if (isValid) {
                const modifiedRows = this.rowData.filter(row => row.isModified);
                console.log('Modified rows:', modifiedRows);
                const dataToSend = modifiedRows.map(row => {
                    return {
                        policy: row.policy,
                        Rule_description: row.Rule_description,
                        protocol: row.protocol === 'icmp request' ? 'icmp type echo-request' : row.protocol === 'icmp reply' ? 'icmp type echo-reply' : row.protocol,
                        saddr: row.saddr,
                        daddr: row.daddr,
                        sport: row.sport,
                        dport: row.dport,
                        type_rule: "inbound",
                        id: row.id,
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
                    const response = await axios.post('/rules/saveRules/' + this.activeTab, dataToSend);
                    if (response.status === 200 && modifiedRows.length > 0) {
                        modifiedRows.forEach(row => row.isModified = false);
                        this.alert = true;
                        setTimeout(() => {
                            this.alert = false;
                        }, 5000);

                    } else {
                        console.error('Failed to save data');
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            } else {
                console.error('Data is not valid');
                alert('Data is not valid. Please check required fields.');
            }
        },
        async saveOutbound() {

            const isValid = this.validateGridData(this.rowDataOutbound);
            if (isValid) {
                const modifiedRows = this.rowDataOutbound.filter(row => row.isModified);
                console.log('Modified rows:', modifiedRows);
                const dataToSend = modifiedRows.map(row => {
                    return {
                        policy: row.policy,
                        Rule_description: row.Rule_description,
                        protocol: row.protocol === 'icmp request' ? 'icmp type echo-request' : row.protocol === 'icmp reply' ? 'icmp type echo-reply' : row.protocol,
                        saddr: row.saddr,
                        daddr: row.daddr,
                        sport: row.sport,
                        dport: row.dport,
                        type_rule: "outbound",
                        id: row.id,
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
                    const response = await axios.post('/rules/saveRules/' + this.activeTab, dataToSend);
                    if (response.status === 200) {
                        modifiedRows.forEach(row => row.isModified = false);
                        this.alertOutbound = true;
                        setTimeout(() => {
                            this.alertOutbound = false;
                        }, 5000);

                    } else {
                        console.error('Failed to save data');
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            } else {
                console.error('Data is not valid');
                this.$toast.error('Data is not valid. Please check required fields.');
            }
        },
        handleRemove() {
            this.alert = false;
        },
        handleRemoveOutbound() {
            this.alertOutbound = false;
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
        // Whenever rules changes, rowData will be updated and if rules is empty, rowData will be set to empty array
        rules: {
            handler: function (val, oldVal) {
                if (val) {
                    this.rowData = this.rules[this.activeTab]['inbound'];
                    this.rowDataOutbound = this.rules[this.activeTab]['outbound'];
                } else {
                    this.rowData = [];
                    this.rowDataOutbound = [];
                }
            },
            deep: true,
        },

        // Whenever activeTab changes, rowData will be updated
        activeTab: {
            handler: function (val, oldVal) {
                this.rowData = this.rules[val]['inbound'];
                this.rowDataOutbound = this.rules[val]['outbound'];

                // if activeTab is changed, set filterText and filterTextOutbound to null to clear the filter text boxes in the grid header row
                this.filterText = null;
                this.filterTextOutbound = null;

            },
            deep: true,
        },

        // Whenever protocol is icmp request or icmp reply, disable the sport and dport columns and set their values to null
        // This is done to prevent users from entering values in sport and dport columns when protocol is icmp request or icmp reply
        'rowData': {
            handler: function (val, oldVal) {
                if (val) {
                    val.forEach(row => {
                        if (row.protocol === 'icmp request' || row.protocol === 'icmp reply') {
                            row.sport = null;
                            row.dport = null;
                        }

                    });
                }
            },
            deep: true,
        },
        'rowDataOutbound': {
            handler: function (val, oldVal) {
                if (val) {
                    val.forEach(row => {
                        if (row.protocol === 'icmp request' || row.protocol === 'icmp reply') {
                            row.sport = null;
                            row.dport = null;
                        }
                    });
                }
            },
            deep: true,
        },
        // if rowData is modified, enable the save button
        'rowData': {
            handler: function (val, oldVal) {
                if (val) {
                    const modifiedRows = val.filter(row => row.isModified || row.isRowSelected);
                    if (modifiedRows.length > 0) {
                        this.isSaveDisabled = false;
                    } else {
                        this.isSaveDisabled = true;
                    }
                }
            },
            deep: true,
        },
        // if rowDataOutbound is modified, enable the save button
        'rowDataOutbound': {
            handler: function (val, oldVal) {
                if (val) {
                    const modifiedRows = val.filter(row => row.isModified || row.isRowSelected);
                    if (modifiedRows.length > 0) {
                        this.isSaveDisabledOutbound = false;
                    } else {
                        this.isSaveDisabledOutbound = true;
                    }
                }
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

.v-alert.d-flex.mt-3.v-sheet.theme--dark.success {
    width: 28%;
    margin-left: auto;
}
</style>