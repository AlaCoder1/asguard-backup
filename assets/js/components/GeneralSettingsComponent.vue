<template>
    <div class="mt-3">
        <v-row>
            <v-col cols="6">
                <div class="ml-3 mr-3">
                    <h3>GENERAL PARAMETERS</h3>
                    <v-divider class="mt-1"></v-divider>
                    <h3>System</h3>
                    <v-divider class="mt-1"></v-divider>
                    <v-text-field label="Host name" style="background-color: #eff4f6; margin-left: 2px;"></v-text-field>
                    <v-text-field label="Domain" style="background-color: #eff4f6; margin-left: 2px;"></v-text-field>
                    <v-select label="Time zone" :items="timeZones"
                        style="background-color: #eff4f6; margin-left: 2px;"></v-select>
                    <h3 class="mt-3">Network</h3>
                    <v-divider class="mt-1"></v-divider>
                    <v-row class="mt-2">
                        <v-col cols="6">
                        </v-col>
                        <v-col cols="6">
                            <input type="checkbox" id="dnsServer" name="dnsServer" value="dnsServer">
                            <label for="dnsServer">Prefer to use IPv4 even if IPv6 is available</label>
                        </v-col>
                    </v-row>
                    <v-row class="mt-2">
                        <v-col cols="4">
                            <h4>DNS Server</h4>
                            <v-text-field style="background-color: #eff4f6; margin-left: 2px;">
                            </v-text-field>
                            <v-text-field style="background-color: #eff4f6; margin-left: 2px; margin-bottom: 2px;">
                            </v-text-field>
                        </v-col>
                        <v-col cols="6">
                            <h4>Use the gateway</h4>
                            <v-select style="background-color: #eff4f6; margin-left: 2px; margin-bottom: 2px;"></v-select>
                            <v-select style="background-color: #eff4f6; margin-left: 2px; margin-bottom: 2px;"></v-select>
                        </v-col>
                        <v-col cols="2">
                            <div class="d-flex" style="margin-top: 56px !important;">
                                <v-btn class="btn btn-primary" color="primary" text>
                                    <i class="fas fa-edit"></i>
                                </v-btn>
                                <v-btn class="btn btn-primary" color="primary" text>
                                    <i class="fas fa-trash"></i>
                                </v-btn>
                            </div>
                            <div style="margin-top: 30px !important;">
                                <v-btn class="btn btn-primary" color="primary" text>
                                    <i class="fas fa-plus"></i>
                                    <span class="ml-2">Add</span>
                                </v-btn>
                            </div>
                        </v-col>
                    </v-row>
                    <v-row class="mt-2">
                        <v-col cols="6">
                            <p>
                                Options du serveur DNS
                            </p>
                        </v-col>
                        <v-col cols="6">
                            <input type="checkbox" id="dnsServer" name="dnsServer" value="dnsServer">
                            <label for="dnsServer">Allow remplacement of DNS servers with those obtained by DHCP/PP on the
                                WAN</label>
                            <br />
                            <input type="checkbox" id="dnsServer" name="dnsServer" value="dnsServer">
                            <label for="dnsServer">Do not use the local DNS service as a nameserver</label>
                        </v-col>
                    </v-row>
                    <v-row>
                        <v-col cols="6">
                            <p>Gateway Failover</p>
                        </v-col>
                        <v-col cols="6">
                            <v-select label="Exclude interfaces"
                                style="background-color: #eff4f6; margin-bottom: 2px;"></v-select>
                            <input type="checkbox" id="dnsServer" name="dnsServer" value="dnsServer" class="mt-2">
                            <label for="dnsServer">Allow default gateway failover</label>
                        </v-col>
                    </v-row>
                    <v-row class="d-flex mb-2 text-center justify-end" style="height: 100%;">
                        <v-btn large rounded color="primary">
                            <span class="mr-2 c-o">Save</span>
                        </v-btn>
                    </v-row>
                </div>
            </v-col>
            <v-col cols="6">
                <div class="ml-3 mr-3">
                    <h3>SERVEURS RESEAU</h3>
                    <v-divider class="mt-1"></v-divider>
                    <h3>Local Logging Options</h3>
                    <v-divider class="mt-1"></v-divider>
                    <!-- Add your content for local logging options here -->
                </div>
            </v-col>
        </v-row>
    </div>
</template>

<script>
export default {
    name: 'GeneralSettingsComponent',
    data() {
        return {
            timeZones: [
                'GMT',
                'EST',
                'PST',
                // Add more time zones as needed
            ],
        };
    },
};
</script>

<style scoped></style>
