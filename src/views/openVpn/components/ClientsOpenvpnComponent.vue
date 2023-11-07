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
            <v-col cols="8" class="mb-n6">
              <v-text-field
                label="Client name"
                v-model="clientName"
              ></v-text-field>
            </v-col>
            <v-col cols="4">
              <label>Description</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                label="Description"
                v-model="description"
              ></v-text-field>
            </v-col>
            <v-col cols="4">
              <label>Server mode</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select label="Server mode" v-model="serverMode"></v-select>
            </v-col>
            <v-col cols="4">
              <label>Protocol</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select label="Protocol" v-model="protocol"></v-select>
            </v-col>
            <v-col cols="4">
              <label>Device Mode</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select label="Device Mode"></v-select>
            </v-col>
            <v-col cols="4">
              <label>Interface</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select label="Interface"></v-select>
            </v-col>
            <v-col cols="4">
              <label>Retry DNS resolution</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <input type="checkbox" />
              <label class="ml-2">Infinitely resolve remote server</label>
            </v-col>
            <v-col cols="4">
              <label>Proxy host or address</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field label="Proxy host or address"></v-text-field>
            </v-col>
            <v-col cols="4">
              <label>Proxy port</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field label="Proxy port"></v-text-field>
            </v-col>

            <v-col cols="4">
              <label>Proxy authentication extra options</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select label="Proxy authentication extra options"></v-select>
            </v-col>
            <v-col cols="4">
              <label>Local port</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field label="Local port"></v-text-field>
            </v-col>
          </v-row>
          <v-row class="mt-2">
            <div class="ml-3 mr-3">
              <v-row class="mt-2">
                <userAuthSettings />
                <cryptoSettings />
              </v-row>
            </div>
          </v-row>
          <v-spacer></v-spacer>
        </div>
      </v-col>
      <v-col cols="6">
        <div class="ml-3 mr-3">
          <!-- <v-row class="mt-12">
            <v-col cols="4">
              <label>Peer Certificate Authority</label>
            </v-col>
            <v-col cols="8">
              <v-select
                label="Peer Certificate Authority"
                
              ></v-select>
            </v-col>
            <v-col cols="4">
              <label>Client Certificate</label>
            </v-col>
            <v-col cols="8">
              <v-select
                label="Client Certificate"
                
              ></v-select>
            </v-col>
            <v-col cols="4">
              <label>Encryption algorithm</label>
            </v-col>
            <v-col cols="8">
              <v-select
                label="Encryption algorithm"
                
              ></v-select>
            </v-col>
            <v-col cols="4">
              <label>Auth Digest Algorithm</label>
            </v-col>
            <v-col cols="8">
              <v-select
                label="Auth Digest Algorithm"
                
              ></v-select>
            </v-col>
            <v-col cols="4">
              <label>Hardware Crypto</label>
            </v-col>
            <v-col cols="8">
              <v-select
                label="Hardware Crypto"
                
              ></v-select>
            </v-col>
          </v-row> -->
          <v-row class="mt-0">
            <tunnelSettings />
          </v-row>
          <advancedConfig />
        </div>
      </v-col>
    </v-row>
    <v-row class="flex py-8">
      <v-col cols="4"> </v-col>
      <v-col>
        <div class="mr-3 flex center">
          <v-btn class="mr-5" large rounded color="#213E9F">
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
import UsersList from "../../system/user/components/UsersList.vue";
import tunnelSettings from "./clientComponents/tunnelSettings.vue";
import advancedConfig from "./clientComponents/advancedConfig.vue";
import userAuthSettings from "./clientComponents/userAuthSettings.vue";
import cryptoSettings from "./clientComponents/cryptoSettings.vue";
export default {
  name: "ClientsOpenvpnComponent",
  components: {
    UsersList,
    tunnelSettings,
    advancedConfig,
    userAuthSettings,
    cryptoSettings,
  },
  data: () => ({
    // add data here
    clientName: "",
    description: "",
    serverMode: "",
    protocol: "",
    deviceMode: "",
    interface: "",
    retryDnsResolution: "",
    proxyHostOrAddress: "",
    proxyPort: "",
    proxyAuthenticationExtraOptions: "",
    localPort: "",
    username: "",
    password: "",
    renegotiateTime: "",
    sharedKey: "",
    peerCertificateAuthority: "",
    clientCertificate: "",
    encryptionAlgorithm: "",
    authDigestAlgorithm: "",
    hardwareCrypto: "",
    ipv4TunnelNetwork: "",
    ipv6TunnelNetwork: "",
    ipv4RemoteNetwork: "",
    ipv6RemoteNetwork: "",
    limitOutgoingBandwidth: "",
    compression: "",
    typeOfService: "",
    ipv6: "",
    pullRoutes: "",
    addRemoveRoutes: "",
    verbosityLevel: "",
    remoteServerAtRandom: "",
    headers: [
      { text: "Server Name", value: "serverName" },
      { text: "Protocol/Port", value: "protocolPort" },
      { text: "Action", value: "action", sortable: false },
    ],
    items: [
      {
        serverName: "",
        protocolPort: "",
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
  },
};
</script>

<style lang="scss"></style>
