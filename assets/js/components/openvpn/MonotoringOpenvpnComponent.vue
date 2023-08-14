<template>
    <div class="mt-3">
        <v-row>
            <v-col cols="6">
                <div class="ml-3 mr-3">
                    <v-row class="mt-2 ml-3 mr-3">
                        cards
                    </v-row>
                    <v-row class="mt-2 ml-3 mr-3">
                        <v-col cols="6">
                            <apexchart id="top-trafic-chart" type="bar" :options="chartOptions" :series="chartSeries" />
                        </v-col>
                        <v-col cols="6">
                            <apexchart id="top-loggins-chart" type="bar" :options="chartOptions" :series="chartSeries" />
                        </v-col>
                    </v-row>
                    <v-row class="ml-3 mr-3 mb-5">
                        cards
                    </v-row>
                </div>
            </v-col>
            <v-col cols="6">
                <div class="ml-3 mr-3">
                    <ag-grid-vue id="grid-wrapper" domLayout="autoHeight" class="ag-theme-alpine mt-3 ag-header-cell-text"
                        :columnDefs="columns" :rowData="rowData" />
                </div>
            </v-col>
        </v-row>
    </div>
</template>


<script>
import { AgGridVue } from 'ag-grid-vue';
import VueApexCharts from 'vue-apexcharts';

export default {
    name: 'MonotoringOpenvpnComponent',
    components: {
        AgGridVue,
        apexchart: VueApexCharts,
    },
    props: {
    },
    data() {
        return {
            columns: [
                {
                    headerName: 'Username',
                    field: 'username',
                    sortable: true,
                    filter: true,
                    width: 100,
                },
                {
                    headerName: 'Login Time',
                    field: 'login_time',
                    sortable: true,
                    filter: true,
                    width: 150,
                },
                {
                    headerName: 'Country',
                    field: 'country',
                    sortable: true,
                    filter: true,
                    width: 100,
                },
                {
                    headerName: 'Address',
                    field: 'address',
                    sortable: true,
                    filter: true,
                    width: 100,
                }, {
                    headerName: 'Rx',
                    field: 'rx',
                    sortable: true,
                    filter: true,
                    width: 70,
                }, {
                    headerName: 'Tx',
                    field: 'tx',
                    sortable: true,
                    filter: true,
                    width: 70,
                }
            ],
            rowData: [
                {
                    username: 'test',
                    login_time: '2021-01-01 00:00',
                    country: 'Indonesia',
                    address: '40.8.0.60',
                    rx: '225KB',
                    tx: '0.00',
                },
                {
                    username: 'test',
                    login_time: '2021-01-01 00:00',
                    country: 'Indonesia',
                    address: '40.8.0.2',
                    rx: '220KB',
                    tx: '0.00',
                },
                {
                    username: 'test',
                    login_time: '2021-01-01 00:00',
                    country: 'Indonesia',
                    address: '40.50.50.5',
                    rx: '100KB',
                    tx: '0.00',
                },
            ],
        }
    },
    computed: {
        chartOptions() {
            return {
                // Define your chart options here
                chart: {
                    id: 'top-trafic-chart',
                    height: 350,
                    type: 'bar',
                    events: {
                        click: function (chart, w, e) {
                            // console.log(chart, w, e)
                        }
                    }
                },
                colors: ['#008FFB', '#00E396', '#FEB019', '#FF4560', '#775DD0'],
                plotOptions: {
                    bar: {
                        columnWidth: '45%',
                        distributed: true,
                    }
                },
                dataLabels: {
                    enabled: false
                },
                legend: {
                    show: false
                }, xaxis: {
                    categories: this.rowData.map((row) => row.username),
                    labels: {
                        style: {
                            colors: ['#008FFB', '#00E396', '#FEB019', '#FF4560', '#775DD0'],
                            fontSize: '12px'
                        }
                    }
                },
                title: {
                    text: 'Top Trafic',
                    align: 'left',
                    color: 'primary',
                },
            };
        },
        chartSeries() {
            return [
                {
                    name: 'Rx',
                    data: this.rowData.map((row) => row.rx),
                },
            ];
        },
    },
}
</script>

<style lang="scss" scoped>
@import "~ag-grid-community/dist/styles/ag-grid.css";
@import "~ag-grid-community/dist/styles/ag-theme-alpine.css";

#grid-wrapper {
    width: 100%;
}

.ag-header-cell-text {
    font-size: 10px;
}
</style>