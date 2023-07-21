<template>
    <v-card>
        <v-row class="fill-height ml-3">
            <v-col cols="12" sm="6">
                <v-card-title>Basic configuration</v-card-title>
                <v-divider class="ml-3"></v-divider>
                <v-row class="ml-3 mt-3">
                    <div style="color: black;">Interface</div>
                    <input type="checkbox" class="ml-5" id="checkbox" v-model="checked">
                    <label for="checkbox" class="ml-2">Activate</label>
                </v-row>
                <v-row class="ml-3 mt-5">
                    <div style="color: black;">Lock</div>
                    <input type="checkbox" class="ml-12" id="checkbox" v-model="checked">
                    <label for="checkbox" class="ml-2">Prevent interface removal</label>
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
                    <input type="checkbox" class="ml-16" id="checkbox" v-model="checked">
                    <label for="checkbox" class="ml-2">Private</label>
                </v-row>
                <v-row class="ml-3 mt-9">
                    <div style="color: black;">Block Bogon addresses</div>
                    <input type="checkbox" class="ml-2" id="checkbox" v-model="checked">
                    <label for="checkbox" class="ml-2">Not assigned by IANA</label>
                </v-row>
                <v-row class="ml-3 mt-9">
                    <div style="color: black;" class=" mt-3">IPV4 Setup Type</div>
                    <v-select :items="items" label="DHCP" class="ml-3" dense style="width: 200px !important;
                  height: 40px !important;
                  font-size: 14px !important;
                  font-weight: 400 !important
                  line-height: 20px !important
                  letter-spacing: 0.25px !important
                  text-transform: none !important
                  color: rgba(0, 0, 0, 0.87) !important
                  top: 0px !important
                  left: 0px !important
                  right: 0px !important
                  bottom: 0px !important
                  position: absolute !important
                  padding: 6px 0px 7px !important
                  border-width: 0px !important
                  border-style: none !important
                  border-color: transparent !important
                  border-image: initial !important
                  outline: none !important
                  border-radius: 0px !important
                  background-color: transparent !important
                  box-shadow: none !important
                  box-sizing: border-box !important
                  "></v-select>
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
                <div class="ml-3 mt-9">
                    <div style="color: black;" class="inline-input">Dynamic gateway policy</div>
                    <input type="checkbox" class="ml-5 inline-input" id="checkbox" v-model="checked">
                    <label for="checkbox" class=" inline-label">The interface does not require an intermediate system to act
                        as a gateway.</label>
                </div>
            </v-col>
            <v-col cols="12" sm="6">
                <v-card-title>Static IPV4 address configuration</v-card-title>
                <v-divider class="ml-3"></v-divider>
                <div class="ml-3 mt-3">
                    <div style="color: black;" class="inline-input">IPV4 address</div>
                    <v-text-field label="Enter IP address" class="ml-3 mt-2 inline-input"></v-text-field>
                    <v-select label="DHCP" class="ml-3 mt-2 inline-input"></v-select>
                </div>
                <div class="ml-3">
                    <div style="color: black;" class="inline-input">IPV4 gateway</div>
                    <v-btn class="ml-3 mt-2 " color="primary" text>
                        <i class="fas fa-plus"></i>
                        <span class="ml-2">Add</span>
                    </v-btn>
                    <v-text-field label="Enter IP address" class="ml-3 mt-2 inline-input"></v-text-field>
                </div>
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
                    <input type="checkbox" class="ml-5" id="checkbox">
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
                    <input type="checkbox" class="ml-5 inline-input" id="checkbox">
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
                <v-card-title>Configuring the DHCP Client</v-card-title>
                <v-divider class="ml-3"></v-divider>
                <v-row class="ml-3 mt-3">
                    <div style="color: black;">Setup mode</div>
                    <v-tabs>
                        <v-tab>Basic</v-tab>
                        <v-tab>Advanced</v-tab>
                        <v-tab>Config file bypass</v-tab>
                    </v-tabs>
                </v-row>
                <div class="ml-3 mt-3">
                    <div style="color: black;" class="ml-3 inline-input">IPv4 Adress Alias</div>
                    <v-text-field label="IPv4 Adress Alias" class="ml-3 inline-input"></v-text-field>
                    <v-select class="ml-3 inline-input"></v-select>
                </div>
                <div class="ml-3 mt-3">
                    <div style="color: black;" class="ml-3 inline-input">Reject leases from</div>
                    <v-text-field label="Reject leases from" class="ml-3 inline-input"></v-text-field>
                </div>
                <div class="ml-3 mt-3">
                    <div style="color: black;" class="ml-3 inline-input">Hostname</div>
                    <v-text-field label="Hostname" class="ml-3 inline-input"></v-text-field>
                </div>
                <div class="ml-3 mt-3">
                    <div style="color: black;" class="ml-3 inline-input">Override MTU</div>
                    <input type="checkbox" class="ml-5 inline-input" id="checkbox">
                    <div style="color: black;" class="ml-2 inline-input">MTU</div>
                </div>
                <v-card-title>Protocol Timing</v-card-title>
                <v-divider class="ml-3"></v-divider>
                <div class="ml-3 mt-3">
                    <div style="color: black;" class="ml-3 inline-input">Timeout</div>
                    <input type="checkbox" class="ml-5 inline-input" id="checkbox">
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
                    <input type="checkbox" class="ml-5 inline-input" id="checkbox">
                    <div style="color: black;" class="ml-2 inline-input">Enable dial-on-demand mode</div>
                </div>
                <div class="ml-3 mt-3">
                    <div style="color: black;" class="ml-3 inline-input">Inactivity timeout</div>
                    <v-text-field label="Inactivity timeout" class="ml-3 inline-input"></v-text-field>
                </div>
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
                    <input type="checkbox" class="ml-5 inline-input" id="checkbox">
                    <div style="color: black;" class="ml-2 inline-input">USE ipv4 connectivity</div>
                </div>
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
                    <input type="checkbox" class="ml-2 inline-input" id="checkbox">
                    <v-col lg="4" style="color: black;" class="inline-input">Alow manual adjustment of DHCPv6 and Router
                        Advertisements</v-col>
                </div>
            </v-col>
        </v-row>
        <v-spacer></v-spacer>
        <div class="text-center">
            <v-btn large rounded outlined color="#042439">Cancel</v-btn>
            <v-btn large rounded color="#042439">
                <span class="mr-2 c-o">Save</span>
            </v-btn>
        </div>
        <br />
    </v-card>
</template>

<script>
export default {
    name: "WanComponent",
    data() {
        return {
            title: "",
            text: "",
            activate: false,
            checked: false,
            items: [
                { text: "DHCP", value: "DHCP" },
                { text: "Static", value: "Static" },
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
            ]
        };
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
