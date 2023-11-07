<template>
  <div class="mt-3">
    <v-row>
      <v-col cols="6">
        <div class="ml-3 mr-3">
          <h4>General information</h4>
          <v-divider class="mt-2"></v-divider>
          <v-row class="mt-2">
            <v-col cols="4">
              <label>Serveur name</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                label="Serveur name"
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
              <label>Local port</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select label="Local port"></v-select>
            </v-col>
          </v-row>
          <v-row class="mt-2">
            <div class="ml-3 mr-3">
              <v-row class="mt-2">
                <cryptoSettings />
              </v-row>
            </div>
          </v-row>
          <v-spacer></v-spacer>
        </div>
      </v-col>
      <v-col cols="6">
        <div class="ml-3 mr-3">
          <v-row class="mt-0">
            <tunnelSettings />
          </v-row>
          <clientSettings />
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
  </div>
</template>

<script>
import UsersList from "../../system/user/components/UsersList.vue";
import tunnelSettings from "./serveurComponents/tunnelSettings.vue";
import clientSettings from "./serveurComponents/clientSettings.vue";
import cryptoSettings from "./serveurComponents/cryptoSettings.vue";
export default {
  name: "ClientsOpenvpnComponent",
  components: {
    UsersList,
    tunnelSettings,
    clientSettings,
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
