<template>
    <div class="mt-3">
        <v-row>
            <v-col cols="6">
                <div class="ml-3 mr-3">
                    <h4>General information</h4>
                    <v-divider class="mt-2"></v-divider>
                    <v-row class="mt-2">
                        <v-col cols="4">
                            <label>Client name</label>
                        </v-col>
                        <v-col cols="8">
                            <v-text-field type="text" label="Client name" style="background-color: #eff4f6;"
                                v-model="clientName"></v-text-field>
                        </v-col>
                        <v-col cols="4" class="mb-3">
                            <label>Description</label>
                        </v-col>
                        <v-col cols="8">
                            <v-text-field type="text" label="Description" style="background-color: #eff4f6;"
                                v-model="description"></v-text-field>
                        </v-col>
                        <v-col cols="4">
                            <label>Server mode</label>
                        </v-col>
                        <v-col cols="8">
                            <v-select label="Server mode" style="background-color: #eff4f6;"
                                v-model="serverMode"></v-select>
                        </v-col>
                        <v-col cols="4">
                            <label>Protocol</label>
                        </v-col>
                        <v-col cols="8">
                            <v-select label="Protocol" style="background-color: #eff4f6;" v-model="protocol"></v-select>
                        </v-col>
                        <v-col cols="4">
                            <label>Device Mode</label>
                        </v-col>
                        <v-col cols="8">
                            <v-select label="Device Mode" style="background-color: #eff4f6;"></v-select>
                        </v-col>
                        <v-col cols="4">
                            <label>Interface</label>
                        </v-col>
                        <v-col cols="8">
                            <v-select label="Interface" style="background-color: #eff4f6;"></v-select>
                        </v-col>
                        <v-col cols="4">
                            <label>Retry DNS resolution</label>
                        </v-col>
                        <v-col cols="8">
                            <input type="checkbox" style="background-color: #eff4f6;">
                            <label>Infinitely resolve remote server</label>
                        </v-col>
                        <v-col cols="4">
                            <label>Proxy host or address</label>
                        </v-col>
                        <v-col cols="8">
                            <v-text-field type="text" label="Proxy host or address"
                                style="background-color: #eff4f6;"></v-text-field>
                        </v-col>
                        <v-col cols="4">
                            <label>Proxy port</label>
                        </v-col>
                        <v-col cols="8">
                            <v-text-field type="text" label="Proxy port" style="background-color: #eff4f6;"></v-text-field>
                        </v-col>

                        <v-col cols="4">
                            <label>Proxy authentication extra options</label>
                        </v-col>
                        <v-col cols="8">
                            <v-select label="Proxy authentication extra options"
                                style="background-color: #eff4f6;"></v-select>
                        </v-col>
                        <v-col cols="4">
                            <label>Local port</label>
                        </v-col>
                        <v-col cols="8">
                            <v-text-field type="text" label="Local port" style="background-color: #eff4f6;"></v-text-field>
                        </v-col>
                    </v-row>
                    <v-row class="mt-2">
                        <div class="ml-3 mr-3">
                            <h4>User Authentication Settings</h4>
                            <v-divider class="mt-2"></v-divider>
                            <v-row class="mt-2">
                                <v-col cols="4">
                                    <label>Username</label>
                                </v-col>
                                <v-col cols="8">
                                    <v-text-field type="text" label="Username"
                                        style="background-color: #eff4f6;"></v-text-field>
                                </v-col>
                                <v-col cols="4">
                                    <label>Password</label>
                                </v-col>
                                <v-col cols="8">
                                    <v-text-field type="password" label="Password"
                                        style="background-color: #eff4f6;"></v-text-field>
                                </v-col>
                                <v-col cols="4">
                                    <label>Renegotiate time</label>
                                </v-col>
                                <v-col cols="8">
                                    <v-text-field type="text" label="Renegotiate time"
                                        style="background-color: #eff4f6;"></v-text-field>
                                </v-col>
                                <v-col cols="4">
                                    <label>Retry DNS resolution</label>
                                </v-col>
                                <v-col cols="8">
                                    <input type="checkbox" style="background-color: #eff4f6;">
                                    <label>Enable authentication of TLS packets</label>
                                    <br />
                                    <input type="checkbox" style="background-color: #eff4f6;">
                                    <label>Automatically generate a shared TLS authentication key</label>
                                    <br />
                                </v-col>
                                <v-col cols="4">
                                    <label>Shared key</label>
                                </v-col>
                                <v-col cols="8">
                                    <input type="checkbox" style="background-color: #eff4f6;">
                                    <label>Automatically generate a shared key.</label>
                                    <v-text-field type="text" label="Shared key"
                                        style="background-color: #eff4f6;"></v-text-field>
                                </v-col>
                                <v-col cols="4">
                                    <label>Peer Certificate Authority</label>
                                </v-col>
                                <v-col cols="8">
                                    <v-select label="Peer Certificate Authority"
                                        style="background-color: #eff4f6;"></v-select>
                                </v-col>
                                <v-col cols="4">
                                    <label>Client Certificate</label>
                                </v-col>
                                <v-col cols="8">
                                    <v-select label="Client Certificate" style="background-color: #eff4f6;"></v-select>
                                </v-col>
                                <v-col cols="4">
                                    <label>Encryption algorithm</label>
                                </v-col>
                                <v-col cols="8">
                                    <v-select label="Encryption algorithm" style="background-color: #eff4f6;"></v-select>
                                </v-col>
                                <v-col cols="4">
                                    <label>Auth Digest Algorithm</label>
                                </v-col>
                                <v-col cols="8">
                                    <v-select label="Auth Digest Algorithm" style="background-color: #eff4f6;"></v-select>
                                </v-col>
                                <v-col cols="4">
                                    <label>Hardware Crypto</label>
                                </v-col>
                                <v-col cols="8">
                                    <v-select label="Hardware Crypto" style="background-color: #eff4f6;"></v-select>
                                </v-col>
                            </v-row>
                        </div>
                    </v-row>
                    <v-spacer></v-spacer>
                </div>
            </v-col>
            <v-col cols="6">
                <div class="ml-3 mr-3">
                    <v-row class="mt-12">
                        <v-col cols="4">
                            <label>Peer Certificate Authority</label>
                        </v-col>
                        <v-col cols="8">
                            <v-select label="Peer Certificate Authority" style="background-color: #eff4f6;"></v-select>
                        </v-col>
                        <v-col cols="4">
                            <label>Client Certificate</label>
                        </v-col>
                        <v-col cols="8">
                            <v-select label="Client Certificate" style="background-color: #eff4f6;"></v-select>
                        </v-col>
                        <v-col cols="4">
                            <label>Encryption algorithm</label>
                        </v-col>
                        <v-col cols="8">
                            <v-select label="Encryption algorithm" style="background-color: #eff4f6;"></v-select>
                        </v-col>
                        <v-col cols="4">
                            <label>Auth Digest Algorithm</label>
                        </v-col>
                        <v-col cols="8">
                            <v-select label="Auth Digest Algorithm" style="background-color: #eff4f6;"></v-select>
                        </v-col>
                        <v-col cols="4">
                            <label>Hardware Crypto</label>
                        </v-col>
                        <v-col cols="8">
                            <v-select label="Hardware Crypto" style="background-color: #eff4f6;"></v-select>
                        </v-col>
                    </v-row>
                    <v-row class="mt-2">
                        <div class="ml-3 mr-3">
                            <h4>Tunnel Settings</h4>
                            <v-divider class="mt-2"></v-divider>
                            <v-row class="mt-2">
                                <v-col cols="4">
                                    <label>IPv4 Tunnel Network</label>
                                </v-col>
                                <v-col cols="8">
                                    <v-text-field type="text" label="IPv4 Tunnel Network"
                                        style="background-color: #eff4f6;"></v-text-field>
                                </v-col>
                                <v-col cols="4">
                                    <label>IPv6 Tunnel Network</label>
                                </v-col>
                                <v-col cols="8">
                                    <v-text-field type="text" label="IPv6 Tunnel Network"
                                        style="background-color: #eff4f6;"></v-text-field>
                                </v-col>
                                <v-col cols="4">
                                    <label>IPv4 Remote Network</label>
                                </v-col>
                                <v-col cols="8">
                                    <v-text-field type="text" label="IPv4 Remote Network"
                                        style="background-color: #eff4f6;"></v-text-field>
                                </v-col>
                                <v-col cols="4">
                                    <label>IPv6 Remote Network</label>
                                </v-col>
                                <v-col cols="8">
                                    <v-text-field type="text" label="IPv6 Remote Network"
                                        style="background-color: #eff4f6;"></v-text-field>
                                </v-col>
                                <v-col cols="4">
                                    <label>Limit outgoing bandwidth</label>
                                </v-col>
                                <v-col cols="8">
                                    <v-text-field type="text" label="Limit outgoing bandwidth"
                                        style="background-color: #eff4f6;"></v-text-field>
                                </v-col>
                                <v-col cols="4">
                                    <label>Compression</label>
                                </v-col>
                                <v-col cols="8">
                                    <v-select type="text" label="Compression" style="background-color: #eff4f6;"></v-select>
                                </v-col>
                                <v-col cols="4">
                                    <label>Type-of-Service</label>
                                </v-col>
                                <v-col cols="8">
                                    <input type="checkbox" style="background-color: #eff4f6;">
                                    <label>Infinitely resolve remote server</label>
                                </v-col>
                                <v-col cols="4">
                                    <label>IPv6</label>
                                </v-col>
                                <v-col cols="8">
                                    <input type="checkbox" style="background-color: #eff4f6;">
                                    <label>Infinitely resolve remote server</label>
                                </v-col>
                                <v-col cols="4">
                                    <label> pull routes</label>
                                </v-col>
                                <v-col cols="8">
                                    <input type="checkbox" style="background-color: #eff4f6;">
                                    <label>Infinitely resolve remote server</label>
                                </v-col>
                                <v-col cols="4">
                                    <label>Add/remove routes</label>
                                </v-col>
                                <v-col cols="8">
                                    <input type="checkbox" style="background-color: #eff4f6;">
                                    <label>Infinitely resolve remote server</label>
                                </v-col>
                            </v-row>
                        </div>
                    </v-row>
                    <div class="mt-2">
                        <h4 class="mt-6">Advanced Configuration</h4>
                        <v-divider class="mt-2"></v-divider>
                        <v-row class="mt-2">
                            <v-col cols="4">
                                <label>Verbosity level</label>
                            </v-col>
                            <v-col cols="8">
                                <v-select label="Verbosity level" style="background-color: #eff4f6;"></v-select>
                            </v-col>
                        </v-row>
                    </div>
                    <div class="mt-2">
                        <h4 class="mt-6">Remote server</h4>
                        <v-divider class="mt-2"></v-divider>
                        <v-row class="mt-2">
                            <v-col cols="4">
                                <label>Remote server at random</label>
                            </v-col>
                            <v-col cols="8">
                                <input type="checkbox" style="background-color: #eff4f6;">
                                <label>Select remote server at random</label>
                            </v-col>
                        </v-row>
                        <v-row class="py-8">
                            <v-col cols="12">
                                <v-data-table :headers="headers" :items="items" class="elevation-1">
                                    <template v-slot:item.action="{ item }">
                                        <div class="flex">
                                            <v-btn small color="primary" @click="editItem(item)">
                                                <i class="far fa-edit"></i>
                                            </v-btn>
                                            <v-btn small color="error" @click="deleteItem(item)">
                                                <i class="fas fa-times"></i>
                                            </v-btn>
                                        </div>
                                    </template>
                                    <template v-slot:item.serverName="{ item }">
                                        <v-text-field v-model="item.serverName" outlined class="mt-8"></v-text-field>
                                    </template>
                                    <template v-slot:item.protocolPort="{ item }">
                                        <v-text-field v-model="item.protocolPort" outlined class="mt-8"></v-text-field>
                                    </template>
                                </v-data-table>

                            </v-col>
                            <v-row class="flex py-3">
                                <v-col cols="6">
                                </v-col>
                                <v-col>
                                    <div class="mr-1 flex center">
                                        <v-btn large rounded color="#213E9F">
                                            <span class="text-white c-o">Cancel</span>
                                        </v-btn>
                                        <v-btn large rounded color="#213E9F">
                                            <span class="text-white c-o">Save</span>
                                        </v-btn>
                                    </div>
                                </v-col>
                            </v-row>
                        </v-row>
                    </div>
                </div>
            </v-col>
        </v-row>
        <v-row class="flex py-8">
            <v-col cols="4">
            </v-col>
            <v-col>
                <div class="mr-1 flex center">
                    <v-btn large rounded color="#213E9F">
                        <span class="text-white c-o">Cancel</span>
                    </v-btn>
                    <v-btn large rounded color="#213E9F">
                        <span class="text-white c-o">Save</span>
                    </v-btn>
                </div>
            </v-col>
        </v-row>
        <v-spacer></v-spacer>
        <div class="ml-3 w-full">
            <UsersList />
        </div>
        <br />

    </div>
</template>


<script>
import UsersList from '@/components/users/UsersList.vue';

export default {
    name: "ClientsOpenvpnComponent",
    components: {
        UsersList
    },
    data: () => ({
        // add data here
        clientName: '',
        description: '',
        serverMode: '',
        protocol: '',
        deviceMode: '',
        interface: '',
        retryDnsResolution: '',
        proxyHostOrAddress: '',
        proxyPort: '',
        proxyAuthenticationExtraOptions: '',
        localPort: '',
        username: '',
        password: '',
        renegotiateTime: '',
        sharedKey: '',
        peerCertificateAuthority: '',
        clientCertificate: '',
        encryptionAlgorithm: '',
        authDigestAlgorithm: '',
        hardwareCrypto: '',
        ipv4TunnelNetwork: '',
        ipv6TunnelNetwork: '',
        ipv4RemoteNetwork: '',
        ipv6RemoteNetwork: '',
        limitOutgoingBandwidth: '',
        compression: '',
        typeOfService: '',
        ipv6: '',
        pullRoutes: '',
        addRemoveRoutes: '',
        verbosityLevel: '',
        remoteServerAtRandom: '',
        headers: [
            { text: "Server Name", value: "serverName" },
            { text: "Protocol/Port", value: "protocolPort" },
            { text: "Action", value: "action", sortable: false },
        ],
        items: [
            {
                serverName: "",
                protocolPort: ""
            },
        ],

    }),
    methods: {
        editItem(item) {
            // Handle edit action
        },
        deleteItem(item) {
            // Handle delete action
        },
    },
    mounted() {
        //
    }
}

</script>

<style lang="scss"></style>