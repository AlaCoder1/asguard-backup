<template>
    <v-card>
        <v-toolbar>
            <v-tabs>
                <v-tab>LAN</v-tab>
                <v-tab>WAN</v-tab>
            </v-tabs>
        </v-toolbar>
        <!-- divide the page into 2 rows -->
        <v-row class="fill-height ml-3">
            <!-- first row -->
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
            <!-- second row -->
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
                        <v-icon>mdi-plus</v-icon>
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
                    <div style="color: black;" class="ml-3 mt-2">Use IPV4 connectivity</div>
                    <input type="checkbox" class="ml-5" id="checkbox">
                    <div style="color: black;" class="ml-3 mt-2">IPV4 Connectivity</div>
                </v-row>
                <div class="ml-3 mt-3">
                    <div style="color: black;" class="ml-3 mt-2 inline-input">Use VLAN Priority</div>
                    <v-select class="ml-3 mt-2 inline-input"></v-select>
                </div>
            </v-col>
        </v-row>
    </v-card>
</template>

<script>
export default {
    data() {
        return {
            model: "tab-1",
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
```
