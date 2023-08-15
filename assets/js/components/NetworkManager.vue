<template>
    <v-card>

        <v-toolbar>

            <v-tab>LAN</v-tab>

            <v-tab>WAN</v-tab>

        </v-toolbar>

        <!-- divide the page into 2 rows -->

        <v-row class="fill-height ml-3">

            <!-- first row -->

            <v-col cols="12" sm="6">

                <v-card-title>Basic configuration</v-card-title>

                <v-divider class="ml-3"></v-divider>

                <v-row class="ml-3 mt-3">

                    <div style="color: black;">Interface</div>

                    <v-checkbox label="Activate" class="ml-3" value="activate"></v-checkbox>

                </v-row>

                <v-row class="ml-3 mt-5">

                    <div style="color: black;">Lock</div>

                    <v-checkbox label="Prevent interface removal" color="indigo" class="ml-10 mt-1"></v-checkbox>

                </v-row>

                <div style="background-color: #D0D3D4;" class="ml-3">

                    <v-row class="ml-3 mt-5">

                        <div style="color: black;">Device</div>

                    </v-row>

                    <v-text-field label="Enter device name" class="ml-3 mt-2"></v-text-field>

                </div>

                <div style="background-color: #D0D3D4;" class="ml-3">

                    <v-row class="ml-3 mt-2">

                        <div style="color: black;">Description</div>

                    </v-row>

                    <v-text-field label="Enter Description" class="ml-3 mt-2"></v-text-field>

                </div>

                <v-card-title>Generic configuration</v-card-title>

                <v-divider class="ml-3"></v-divider>

                <v-row class="ml-3 mt-2">

                    <div style="color: black;">Block networks</div>

                    <v-checkbox label="Private" value="tab-1 mt-2" class="ml-16"></v-checkbox>

                </v-row>

                <v-row class="ml-3 mt-9">

                    <div style="color: black;">Block Bogon addresses</div>

                    <v-checkbox label="not assignedby " value="tab-2" class="ml-3"></v-checkbox>

                </v-row>

                <v-row class="ml-3 mt-9">

                    <div style="color: black;" class=" mt-6">IPV4 Setup Type</div>

                    <v-select label="DHCP" class="ml-3"></v-select>

                </v-row>

                <v-row class="ml-3 mt-9">

                    <div style="color: black;" class=" mt-6">IPV6 Setup Type</div>

                    <v-select label="DHCP" class="ml-3"></v-select>

                </v-row>

                <v-row class="ml-3 mt-9">

                    <div style="color: black;" class=" mt-6">MAC address</div>

                    <v-text-field label="Enter MAC address" class="ml-3 mt-2"></v-text-field>

                </v-row>

                <v-row class="ml-3 mt-9">

                    <div style="color: black;" class=" mt-6">MTU (Maximum Transmission Unit)</div>

                    <v-select label="DHCP" class="ml-3"></v-select>

                </v-row>

                <v-row class="ml-3 mt-9">

                    <div style="color: black;" class=" mt-6">MSS</div>

                    <v-text-field label="Enter MSS" class="ml-3 mt-2"></v-text-field>

                </v-row>

                <v-row class="ml-3 mt-9">

                    <div style="color: black;" class=" mt-6">Speed and Duplex</div>

                    <v-select label="DHCP" class="ml-3"></v-select>

                </v-row>

                <v-row class="ml-3 mt-9">

                    <div style="color: black;" class=" mt-6">Dynamic gateway policy</div>

                    <v-checkbox label="This interface does not require intermidate system to act as a gateway"
                        class="ml-3"></v-checkbox>

                </v-row>

            </v-col>

            <!-- second row -->

            <v-col cols="12" sm="6">

                <v-card-title>second Part</v-card-title>

                <v-card-text>




                </v-card-text>

            </v-col>

        </v-row>

    </v-card>
</template>

<script>

import { VCard, VToolbar, VTab, VRow, VCol, VDivider, VCheckbox, VTextField, VSelect } from 'vuetify/lib';




export default {

    components: {

        VCard,

        VToolbar,

        VTab,

        VRow,

        VCol,

        VDivider,

        VCheckbox,

        VTextField,

        VSelect

    },




    data() {

        return {

            model: 'tab-1',

            title: '',

            text: '',

        }

    },

}

</script>