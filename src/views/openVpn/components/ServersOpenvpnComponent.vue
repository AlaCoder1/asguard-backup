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
                v-model="state.clientName"
              ></v-text-field>
            </v-col>
            <v-col cols="4">
              <label>Description</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                label="Description"
                v-model="state.description"
              ></v-text-field>
            </v-col>
            <v-col cols="4">
              <label>Server mode</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select
                label="Server mode"
                v-model="state.serverMode"
                item-title="name"
                item-value="id"
                return-object
                :items="[
                  {
                    id: '1',
                    name: 'Remote Access (SSL/TLS)',
                    slug: 'remote_access',
                  },
                  { id: '2', name: 'Peer to peer(SSL/TLS)', slug: 'peer' },
                  {
                    id: '3',
                    name: 'Remote Access (Shared key)',
                    slug: 'shared',
                  },
                ]"
              ></v-select>
            </v-col>
            <v-col cols="4">
              <label>Protocol</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select
                label="Protocol"
                v-model="state.protocol"
                item-title="name"
                item-value="id"
                return-object
                :items="[
                  {
                    id: '1',
                    name: 'UDP',
                    slug: 'udp',
                  },
                  { id: '2', name: 'UDP4', slug: 'udp4' },
                  { id: '3', name: 'UDP6', slug: 'udp6' },
                  { id: '4', name: 'TCP', slug: 'tcp' },
                  { id: '5', name: 'TCP4', slug: 'tcp4' },
                  { id: '6', name: 'TCP6', slug: 'tcp6' },
                ]"
              ></v-select>
            </v-col>
            <v-col cols="4">
              <label>Device Mode</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select
                v-model="state.deviceMode"
                label="Device Mode"
                item-title="name"
                item-value="id"
                return-object
                :items="[
                  {
                    id: '1',
                    name: 'TUN',
                    slug: 'tun',
                  },
                  { id: '2', name: 'TAP', slug: 'tap' },
                ]"
              ></v-select>
            </v-col>
            <v-col cols="4">
              <label>Interface</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-select
                v-model="state.interface"
                label="Interface"
                item-title="name"
                item-value="id"
                return-object
                :items="state.mapedInterface"
              ></v-select>
            </v-col>

            <v-col cols="4">
              <label>Local port</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                label="Local port"
                v-model="state.localPort"
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row class="mt-2">
            <div class="ml-3 mr-3">
              <v-row class="mt-2">
                <cryptoSettings
                  v-model:isEnableAuth="cryptographic.isEnableAuth"
                  v-model:tlsGenerate="cryptographic.tlsGenerate"
                  v-model:peerCertif="cryptographic.peerCertif"
                  v-model:serverCertif="cryptographic.serverCertif"
                  v-model:dhParameters="cryptographic.dhParameters"
                  v-model:encryptAlgo="cryptographic.encryptAlgo"
                  v-model:authDigest="cryptographic.authDigest"
                  v-model:hardwareCrypto="cryptographic.hardwareCrypto"
                />
              </v-row>
            </div>
          </v-row>
          <v-spacer></v-spacer>
        </div>
      </v-col>
      <v-col cols="6">
        <div class="ml-3 mr-3">
          <v-row class="mt-0">
            <tunnelSettings
              v-model:ip4Tunnel="tunnelSettings.ip4Tunnel"
              v-model:ip6Tunnel="tunnelSettings.ip6Tunnel"
              v-model:isGateway="tunnelSettings.isGateway"
              v-model:isBridge="tunnelSettings.isBridge"
              v-model:interfaceBridge="tunnelSettings.interfaceBridge"
              v-model:startDHCPBridge="tunnelSettings.startDHCPBridge"
              v-model:endDHCPBridge="tunnelSettings.endDHCPBridge"
              v-model:iPv4Local="tunnelSettings.iPv4Local"
              v-model:iPv6Local="tunnelSettings.iPv6Local"
              v-model:iPv4Remote="tunnelSettings.iPv4Remote"
              v-model:iPv6Remote="tunnelSettings.iPv6Remote"
              v-model:concurrentConnections="
                tunnelSettings.concurrentConnections
              "
              v-model:compression="tunnelSettings.compression"
              v-model:typefService="tunnelSettings.typefService"
              v-model:Connections="tunnelSettings.Connections"
              v-model:IPv6="tunnelSettings.IPv6"
              v-model:interClients="tunnelSettings.interClients"
              :deviceMode="state.deviceMode.slug"
            />
          </v-row>
          <clientSettings
            v-model:dynamicIP="clientSettings.dynamicIP"
            v-model:adressPool="clientSettings.adressPool"
            v-model:topology="clientSettings.topology"
            v-model:dnsDefaultDomain="clientSettings.dnsDefaultDomain"
            v-model:dnsServers="clientSettings.dnsServers"
            v-model:forceDNS="clientSettings.forceDNS"
            v-model:ntpServers="clientSettings.ntpServers"
            v-model:clientPort="clientSettings.clientPort"
            v-model:startAddressPool="clientSettings.startAddressPool"
            v-model:endAddressPool="clientSettings.endAddressPool"
            v-model:activeDnsDefault="clientSettings.activeDnsDefault"
            v-model:activeDnsServer1="clientSettings.activeDnsServer1"
            v-model:activeDnsServer2="clientSettings.activeDnsServer2"
            v-model:activeNtpServer1="clientSettings.activeNtpServer1"
            v-model:activeNtpServer2="clientSettings.activeNtpServer2"
          />
        </div>
      </v-col>
    </v-row>
    <v-row class="flex py-8 mb-5">
      <v-col cols="4"> </v-col>
      <v-col>
        <div class="mr-3 flex center">
          <v-btn class="mr-5" large rounded color="#213E9F">
            <span class="text-white c-o">Cancel</span>
          </v-btn>
          <v-btn @click="submitForm" large rounded color="#213E9F">
            <span class="text-white c-o">Save</span>
          </v-btn>
        </div>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import axios from "axios";
import UsersList from "../../system/user/components/UsersList.vue";
import tunnelSettings from "./serveurComponents/tunnelSettings.vue";
import clientSettings from "./serveurComponents/clientSettings.vue";
import cryptoSettings from "./serveurComponents/cryptoSettings.vue";
import { reactive, onMounted } from "vue";
export default {
  name: "ClientsOpenvpnComponent",
  components: {
    UsersList,
    tunnelSettings,
    clientSettings,
    cryptoSettings,
  },
  setup() {
    const state = reactive({
      clientName: "",
      description: "",
      serverMode: "",
      protocol: "",
      deviceMode: "",
      interface: "",
      localPort: "",
      mapedInterface: [],
    });
    const cryptographic = reactive({
      isEnableAuth: true,
      tlsGenerate: "",
      peerCertif: "",
      serverCertif: "",
      dhParameters: "",
      encryptAlgo: "",
      authDigest: "",
      hardwareCrypto: "",
    });
    const tunnelSettings = reactive({
      ip4Tunnel: "",
      ip6Tunnel: "",
      isGateway: false,
      isBridge: false,
      interfaceBridge: "",
      startDHCPBridge: "",
      endDHCPBridge: "",
      iPv4Local: "",
      iPv6Local: "",
      iPv4Remote: "",
      iPv6Remote: "",
      concurrentConnections: "",
      compression: "",
      typefService: false,
      Connections: false,
      IPv6: false,
      interClients: false,
    });

    const clientSettings = reactive({
      dynamicIP: false,
      adressPool: false,
      topology: false,
      dnsDefaultDomain: false,
      dnsServers: false,
      forceDNS: false,
      ntpServers: false,
      clientPort: false,
      startAddressPool: "",
      endAddressPool: "",
      activeDnsDefault: "",
      activeDnsServer1: "",
      activeDnsServer2: "",
      activeNtpServer1: "",
      activeNtpServer2: "",
    });

    const getCookie = (name) => {
      let cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === name + "=") {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    };

    const getInterface = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/network/AllInterfaces").then(
        (response) => {
          let interfaces = response.data.map((i) => {
            return {
              id: i.id,
              name: i.name_interface,
            };
          });
          state.mapedInterface = interfaces;
        },
        (error) => {
          console.log(error);
        }
      );
    };

    onMounted(() => {
      getInterface();
    });

    const submitForm = () => {
     
    };

    return {
      getCookie,
      getInterface,
      submitForm,
      state,
      cryptographic,
      tunnelSettings,
      clientSettings,
    };
  },
};
</script>

<style lang="scss"></style>
