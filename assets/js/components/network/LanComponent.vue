<template>
    <v-card>
        <v-row class="fill-height ml-3">
            <v-col cols="12" sm="6">
                <v-card-title>Basic configuration</v-card-title>
                <v-divider class="ml-3"></v-divider>
                <v-row class="ml-3 mt-3">
                    <div style="color: black;">Interface</div>
                    <input type="checkbox" class="ml-5" v-model="activate">
                    <label class="ml-2">Activate</label>
                </v-row>
                <v-row class="ml-3 mt-5">
                    <div style="color: black;">Lock</div>
                    <input type="checkbox" class="ml-12" v-model="lock">
                    <label class="ml-2">Prevent interface removal</label>
                </v-row>
                <div style="background-color: #D0D3D4;" class="ml-3">
                    <v-row class="ml-3 mt-5">
                        <div style="color: black;">Device</div>
                    </v-row>
                    <v-text-field label="Enter device name" class="ml-3 mt-2" v-model="deviceName"></v-text-field>
                </div>
                <div style="background-color: #D0D3D4;" class="ml-3">
                    <v-row class="ml-3 mt-2">
                        <div style="color: black;">Description</div>
                    </v-row>
                    <v-text-field label="Enter Description" class="ml-3 mt-2" v-model="description"></v-text-field>
                </div>
                <v-card-title>Generic configuration</v-card-title>
                <v-divider class="ml-3"></v-divider>
                <v-row class="ml-3 mt-2">
                    <div style="color: black;">Block networks</div>
                    <input type="checkbox" class="ml-16" v-model="private_aux">
                    <label class="ml-2">Private</label>
                </v-row>
                <v-row class="ml-3 mt-9">
                    <div style="color: black;">Block Bogon addresses</div>
                    <input type="checkbox" class="ml-2" v-model="bogon_aux">
                    <label class="ml-2">Not assigned by IANA</label>
                </v-row>
                <v-row class="ml-3 mt-9">
                    <div style="color: black;" class=" mt-3">IPV4 Setup Type</div>
                    <v-select :items="items" label="Setup IPV4 Type" class="ml-3" dense v-model="typeIP4"></v-select>
                </v-row>
                <v-row class="ml-3 mt-9">
                    <div style="color: black;" class=" mt-6">IPV6 Setup Type</div>
                    <v-select label="Setup IPV6 Type" class="ml-3" v-model="ipv6SetupType"></v-select>
                </v-row>
                <v-row class="ml-3 mt-9">
                    <div style="color: black;" class=" mt-6">MAC address</div>
                    <v-text-field label="Enter MAC address" class="ml-3 mt-2" v-model="addmac"></v-text-field>
                </v-row>
                <v-row class="ml-3 mt-9">
                    <div style="color: black;" class=" mt-6">MTU (Maximum Transmission Unit)</div>
                    <v-text-field label="Enter MTU" class="ml-3 mt-2" v-model="mtuV"></v-text-field>
                </v-row>
                <v-row class="ml-3 mt-9">
                    <div style="color: black;" class=" mt-6">MSS</div>
                    <v-text-field label="Enter MSS" class="ml-3 mt-2" v-model="mssV"></v-text-field>
                </v-row>
                <v-row class="ml-3 mt-9">
                    <div style="color: black;" class=" mt-6">Speed and Duplex</div>
                    <v-select label="Speed and Duplex" class="ml-3" :items="speedDuplexItems" default-value="100baseTX"
                        v-model="speed_duplex"></v-select>
                </v-row>
                <div class="ml-3 mt-9">
                    <div style="color: black;" class="inline-input">Dynamic gateway policy</div>
                    <input type="checkbox" class="ml-5 inline-input" v-model="dynamicGatewayPolicy">
                    <label class=" inline-label">The interface does not require an intermediate system to act
                        as a gateway.</label>
                </div>
            </v-col>
            <v-col cols="12" sm="6" v-if="ip_address != null || ip_address != null">
                <div v-if="typeIP4 === 'static'">
                    <v-card-title>Static IPV4 address configuration</v-card-title>
                    <v-divider class="ml-3"></v-divider>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="inline-input">IPV4 address</div>
                        <v-text-field label="Enter IP address" class="ml-3 mt-2 inline-input"
                            v-model="ip_address"></v-text-field>
                        <v-select :items="netmaskItems" label="netmask" class="ml-3 mt-2 inline-input"
                            v-model="netmask"></v-select>
                    </div>
                    <div class="ml-3">
                        <div style="color: black;" class="inline-input">IPV4 gateway</div>
                        <v-btn class="ml-3 mt-2 " color="primary" text>
                            <i class="fas fa-plus"></i>
                            <span class="ml-2">Add</span>
                        </v-btn>
                        <v-select label="IPv4 gateway" class="ml-3 mt-2 inline-input" v-model="gateway"></v-select>
                    </div>
                </div>
                <div v-if="ipv6SetupType === 'DHCP'">
                    <v-card-title>Configuring the DHCPv6 client</v-card-title>
                    <v-divider class="ml-3"></v-divider>
                    <v-row class="ml-3 mt-3">
                        <div style="color: black;">Setup mode</div>
                        <v-tabs>
                            <v-tab>Basic</v-tab>
                            <v-tab>Advanced</v-tab>
                            <v-tab>Config file bypass</v-tab>
                        </v-tabs>
                    </v-row>
                    <v-row class="ml-3 mt-9">
                        <div style="color: black;" class="ml-3">Use IPV4 connectivity</div>
                        <input type="checkbox" class="ml-5">
                        <div style="color: black;" class="ml-3">IPV4 Connectivity</div>
                    </v-row>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Use VLAN Priority</div>
                        <v-select class="ml-3 inline-input"></v-select>
                    </div>
                    <v-card-title>Interface status</v-card-title>
                    <v-divider class="ml-3"></v-divider>
                    <div class="ml-3 mt-2">
                        <div style="color: black;" class="ml-3 inline-input">Informations</div>
                        <input type="checkbox" class="ml-5 inline-input">
                        <div style="color: black;" class="ml-3 inline-input">Information only</div>
                    </div>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Send options</div>
                        <v-text-field label="Send options" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Request options</div>
                        <v-text-field label="Request options" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Script</div>
                        <v-text-field label="Script" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Identity association</div>
                        <div class="ml-16">
                            <input type="checkbox" class="inline-input">
                            <div style="color: black;" class="ml-2 inline-input">Non-temporary address allocation</div>
                            <br />
                            <input type="checkbox" class="inline-input">
                            <div style="color: black;" class="ml-2 inline-input">Prefix delegation</div>
                        </div>
                    </div>
                </div>
                <div v-if="false">
                    <v-card-title>Authentication</v-card-title>
                    <v-divider class="ml-3"></v-divider>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Authname</div>
                        <v-text-field label="Authname" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Protocol</div>
                        <v-text-field label="Protocol" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Algorithm</div>
                        <v-text-field label="Algorithm" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">rdm</div>
                        <v-text-field label="rdm" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <v-card-title>Key info</v-card-title>
                    <v-divider class="ml-3"></v-divider>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Keyname</div>
                        <v-text-field label="Keyname" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Royaume</div>
                        <v-text-field label="royaume" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Keyid</div>
                        <v-text-field label="keyid" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Secret</div>
                        <v-text-field label="secret" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Expire</div>
                        <v-text-field label="expire" class="ml-3 inline-input"></v-text-field>
                    </div>
                </div>
                <div v-if="typeIP4 === 'DHCP'">
                    <v-card-title>Configuring the DHCP Client</v-card-title>
                    <v-divider class="ml-3"></v-divider>
                    <v-row class="ml-3 mt-3">
                        <div style="color: black;">Setup mode</div>
                        <v-tabs v-model="activeTab">
                            <v-tab v-for="tab in tabs" :key="tab.id">
                                {{ tab.label }}
                            </v-tab>
                            <v-tab-item v-for="tab in tabs" :key="tab.id">
                                <BasicConfigDHCPv4 v-if="tab.id == 1" />
                                <AdvancedConfigDHCPv4 v-if="tab.id == 2" />
                                <ConfigFileBypassDHCPv4 v-if="tab.id == 3" />
                            </v-tab-item>
                        </v-tabs>
                    </v-row>
                </div>
                <div v-if="false">
                    <v-card-title>Protocol Timing</v-card-title>
                    <v-divider class="ml-3"></v-divider>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Timeout</div>
                        <input type="checkbox" class="ml-5 inline-input">
                        <div style="color: black;" class="ml-2 inline-input">information only</div>

                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Try again</div>
                        <v-text-field label="Hostname" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Select expiration</div>
                        <v-text-field label="Select expiration" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">restart</div>
                        <v-text-field label="restart" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Backoff Cutoff</div>
                        <v-text-field label="Backoff Cutoff" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Initial Interval</div>
                        <v-text-field label="Initial Interval" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <v-card-title>Lease Requirements</v-card-title>
                    <v-divider class="ml-3"></v-divider>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Send options</div>
                        <v-text-field label="Send options" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Request Options</div>
                        <v-text-field label="Request Options" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Required Options</div>
                        <v-text-field label="Required Options" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Option Modifiers</div>
                        <v-text-field label="Option Modifiers" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Use IPv4 connectivity</div>
                        <v-text-field label="Use IPv4 connectivity" class="ml-3 inline-input"></v-text-field>
                    </div>
                </div>
                <div v-if="typeIP4 === 'PPP'">
                    <v-card-title>Configuration PPP</v-card-title>
                    <v-divider class="ml-3"></v-divider>
                    <v-card elevation="9" class="ml-3 mt-3 mr-3" title="Service provider (FAI)">
                        <v-card-title class="headline grey lighten-2 text-center" primary-title>
                            <v-row justify="center">
                                <h5>Service provider(FAI)</h5>
                            </v-row>
                        </v-card-title>
                        <v-card-text>
                            <v-container class="grey lighten-5">
                                <v-row no-gutters>
                                    <v-col sm="5" md="6" class="mt-7">
                                        Country
                                    </v-col>
                                    <v-col sm="5" offset-sm="2" md="6" offset-md="0">
                                        <v-select :items="items" label="Country" class="inline-input"></v-select>
                                    </v-col>
                                </v-row>
                                <v-row no-gutters>
                                    <v-col sm="5" md="6" class="mt-7">
                                        Access provider
                                    </v-col>
                                    <v-col sm="5" offset-sm="2" md="6" offset-md="0">
                                        <v-select :items="items" label="Access provider" class="inline-input"></v-select>
                                    </v-col>
                                </v-row>
                                <v-row no-gutters>
                                    <v-col sm="5" md="6" class="mt-7">
                                        Plan
                                    </v-col>
                                    <v-col sm="5" offset-sm="2" md="6" offset-md="0">
                                        <v-select :items="items" label="Plan" class="inline-input"></v-select>
                                    </v-col>
                                </v-row>
                            </v-container>
                        </v-card-text>
                    </v-card>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Username</div>
                        <v-text-field label="Username" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Password</div>
                        <v-text-field label="Password" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Local IP @</div>
                        <v-text-field label="Local IP @" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Distant IP @</div>
                        <v-text-field label="Distant IP @" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Host-uniq</div>
                        <v-text-field label="Host-uniq" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Connection on demand</div>
                        <input type="checkbox" class="ml-5 inline-input">
                        <div style="color: black;" class="ml-2 inline-input">Enable dial-on-demand mode</div>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Inactivity timeout</div>
                        <v-text-field label="Inactivity timeout" class="ml-3 inline-input"></v-text-field>
                    </div>
                </div>
                <div v-if="ipv6SetupType === 'static'">
                    <v-card-title>Static IPv6 address configuration</v-card-title>
                    <v-divider class="ml-3"></v-divider>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Username</div>
                        <v-text-field label="Username" class="ml-3 inline-input"></v-text-field>
                        <v-select class="ml-3 inline-input"></v-select>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">IPv6 gateway</div>
                        <v-btn class="ml-3 mt-2 " color="primary" text>
                            <v-icon>mdi-plus</v-icon>
                            <span class="ml-2">Add</span>
                        </v-btn>
                        <v-text-field label="IPv6 gateway" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">USE ipv4 connectivity</div>
                        <input type="checkbox" class="ml-5 inline-input">
                        <div style="color: black;" class="ml-2 inline-input">USE ipv4 connectivity</div>
                    </div>
                </div>
                <div v-if="false">
                    <v-card-title>6RD Rapid Deployment</v-card-title>
                    <v-divider class="ml-3"></v-divider>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Préfix 6RD</div>
                        <v-text-field label="Préfix 6RD" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">6RD Edge Relay</div>
                        <v-text-field label="6RD Edge Relay" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Préfixe length IPv4 6RD</div>
                        <v-select class="ml-3 inline-input"></v-select>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">6RD IPv4 Prefix address</div>
                        <v-text-field label="6RD IPv4 Prefix address" class="ml-3 inline-input"></v-text-field>
                    </div>
                </div>
                <div v-if="false">
                    <v-card-title>Track IPv6 interface</v-card-title>
                    <v-divider class="ml-3"></v-divider>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">IPv6 interface</div>
                        <v-select class="ml-3 inline-input"></v-select>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Prefix ID IPv6</div>
                        <v-text-field label="Prefix ID IPv6" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Manual configuration</div>
                        <input type="checkbox" class="ml-2 inline-input">
                        <v-col lg="4" style="color: black;" class="inline-input">Alow manual adjustment of DHCPv6 and Router
                            Advertisements
                        </v-col>
                    </div>
                </div>
            </v-col>
        </v-row>
        <v-spacer></v-spacer>
        <br />
        <div class="text-center">
            <v-btn large rounded outlined color="#042439" @click="cancel">Cancel</v-btn>
            <v-btn large rounded color="#042439" @click="addNetwork">
                <span class="mr-2 c-o">Save</span>
            </v-btn>
        </div>
        <br />
        <v-alert type="success" variant="outlined" elevation="2" class="ml-3" icon="mdi-check-circle-outline"
            style="width: 20%;" border="top" v-if="showAlert" :style="alertStyle">
            Configuration saved successfully
        </v-alert>
    </v-card>
</template>

<script>
// import { network } from "@/services/network.js";
import axios from 'axios';
import BasicConfigDHCPv4 from '../shared/BasicConfigDHCPv4.vue';
import AdvancedConfigDHCPv4 from '../shared/AdvancedConfigDHCPv4.vue';
import ConfigFileBypassDHCPv4 from '../shared/ConfigFileBypassDHCPv4.vue';

export default {
    name: "LanComponent",
    components: {
        BasicConfigDHCPv4,
        AdvancedConfigDHCPv4,
        ConfigFileBypassDHCPv4
    },
    data() {
        return {
            activeTab: 0,
            tabs: [
                { id: 1, label: "Basic" },
                { id: 2, label: "Advanced" },
                { id: 3, label: "Config file bypass" },
            ],
            items: [
                { text: "DHCP", value: "DHCP" },
                { text: "Static", value: "static" },
                { text: "PPP", value: "PPP" },
                { text: "PPPoE", value: "PPPoE" },
                { text: "L2TP", value: "L2TP" },
                { text: "PPTP", value: "PPTP" },
                { text: "SLIP", value: "SLIP" },
                { text: "6RD", value: "6RD" },
                { text: "6to4", value: "6to4" },
                { text: "Track Interface", value: "Track Interface" },
                { text: "GRE", value: "GRE" },
                { text: "IPsec", value: "IPsec" },
            ],
            speedDuplexItems: [
                '100baseTx-FD',
                '100baseTx-HD',
                '10baseT-FD',
                '10baseT-HD',
                '100baseTX',
                '10BaseT/UTP full duplex',
                '10BaseT/UTP',
            ],
            netmaskItems: [
                '1',
                '2',
                '3',
                '4',
                '5',
                '6',
                '7',
                '8',
                '9',
                '10',
                '11',
                '12',
                '13',
                '14',
                '15',
                '16',
                '17',
                '18',
                '19',
                '20',
                '21',
                '22',
                '23',
                '24',
                '25',
                '26',
                '27',
                '28',
                '29',
                '30',
                '31',
                '32',
            ],
            activate: false,
            lock: false,
            deviceName: "",
            description: "",
            private_aux: false,
            bogon_aux: false,
            typeIP4: "",
            ipv6SetupType: "",
            addmac: "",
            mtuV: "",
            mssV: "",
            speed_duplex: "",
            dynamicGatewayPolicy: false,
            ip_address: "",
            gateway: "",
            netmask: "",
            showAlert: false,
        };
    },
    computed: {
        alertStyle() {
            return {
                position: "fixed",
                top: "20px",
                right: "20px",
                width: "20%",
            };
        },
    },
    methods: {
        addNetwork() {
            const params = {
                // activate: this.activate,
                // lock: this.lock,
                // deviceName: this.deviceName,
                // description: this.description,
                // dynamicGatewayPolicy: this.dynamicGatewayPolicy,
                // ipv6SetupType: this.ipv6SetupType,
                private_aux: this.private_aux,
                bogon_aux: this.bogon_aux,
                typeIP4: this.typeIP4,
                // addmac: this.addmac,
                mtuV: this.mtuV,
                mssV: this.mssV,
                speed_duplex: this.speed_duplex,
                ip_address: this.ip_address,
                gateway: this.gateway,
                netmask: this.netmask,
            };
            axios.put('http://127.0.0.1:8000/network/conf/2', params)
                .then((response) => {
                    console.log(response);
                    this.showAlert = true;
                    setTimeout(() => {
                        this.showAlert = false;
                    }, 3000);
                }, (error) => {
                    console.log(error);
                });
        },
        cancel() {
            // this.activate = false;
            // this.lock = false;
            // this.deviceName = "";
            // this.description = "";
            // this.dynamicGatewayPolicy = false;
            // this.ipv6SetupType = "";
            this.private_aux = false;
            this.bogon_aux = false;
            this.typeIP4 = "";
            this.addmac = "";
            this.mtuV = "";
            this.mssV = "";
            this.speed_duplex = "";
            this.ip_address = "";
            this.gateway = "";
            this.netmask = "";
        },
    },
};
</script>
<style scoped>
.inline-label {
    display: inline-block;
    vertical-align: middle;
}

.inline-input {
    display: inline-block;
    vertical-align: middle;
}
</style>
