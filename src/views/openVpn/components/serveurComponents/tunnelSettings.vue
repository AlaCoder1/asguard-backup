<template>
  <div class="ml-3 mr-3">
    <h4>Tunnel Settings</h4>
    <v-divider class="mt-2"></v-divider>
    <v-row class="mt-2">
      <v-col cols="4" align-self="center">
        <label>IPv4 Tunnel Network</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          label="IPv4 Tunnel Network"
          v-model="ip4Tunnel"
        ></v-text-field>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.ip4Tunnel.$errors.length"
        >
          {{ props.errors.ip4Tunnel.$errors?.[0].$message }}
        </p>
      </v-col>
      <v-col cols="4" align-self="center">
        <label>IPv6 Tunnel Network</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          label="IPv6 Tunnel Network"
          v-model="ip6Tunnel"
        ></v-text-field>
      </v-col>
      <v-col cols="4" align-self="center">
        <label>Gateway</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="isGateway" />
        <label class="ml-2">redirect Gateway</label>
      </v-col>

      <v-col cols="4" v-if="deviceMode === 'tap'" align-self="center">
        <label>Bridge</label>
      </v-col>
      <v-col cols="8" class="mb-n6" v-if="deviceMode === 'tap'">
        <input type="checkbox" v-model="isBridge" />
        <label class="ml-2">DHCP bridge</label>
      </v-col>

      <v-col cols="4" v-if="isBridge" align-self="center">
        <label>Interface bridge</label>
      </v-col>
      <v-col cols="8" class="mb-n6" v-if="isBridge">
        <v-select
          label="Interface bridge"
          v-model="interfaceBridge"
          item-title="name"
          item-value="id"
          return-object
          :items="mapedInterface"
        ></v-select>
      </v-col>

      <v-col cols="4" v-if="isBridge" align-self="center">
        <label>Start DHCP bridge</label>
      </v-col>
      <v-col cols="8" class="mb-n6" v-if="isBridge">
        <v-text-field
          label="Start DHCP bridge"
          v-model="startDHCPBridge"
        ></v-text-field>
      </v-col>
      <v-col cols="4" v-if="isBridge" align-self="center">
        <label>End DHCP bridge</label>
      </v-col>
      <v-col cols="8" class="mb-n6" v-if="isBridge">
        <v-text-field
          label="End DHCP bridge"
          v-model="endDHCPBridge"
        ></v-text-field>
      </v-col>
      <v-col cols="4" align-self="center">
        <label>IPv4 Local Network</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          label="IPv4 Local Network"
          v-model="iPv4Local"
        ></v-text-field>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.iPv4Local.$errors.length"
        >
          {{ props.errors.iPv4Local.$errors?.[0].$message }}
        </p>
      </v-col>
      <v-col cols="4" align-self="center">
        <label>IPv6 Local Network</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          label="IPv6 Local Network"
          v-model="iPv6Local"
        ></v-text-field>
      </v-col>
      <v-col cols="4" align-self="center">
        <label>IPv4 Remote Network</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          label="IPv4 Remote Network"
          v-model="iPv4Remote"
        ></v-text-field>
      </v-col>
      <v-col cols="4" align-self="center">
        <label>IPv6 Remote Network</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          label="IPv6 Remote Network"
          v-model="iPv6Remote"
        ></v-text-field>
      </v-col>
      <v-col cols="4" align-self="center">
        <label>Concurrent connections</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          label="Concurrent connections"
          v-model="concurrentConnections"
        ></v-text-field>
      </v-col>
      <v-col cols="4" align-self="center">
        <label>Compression</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select
          label="Compression"
          v-model="compression"
          item-title="name"
          :items="[
            { name: 'No preference', slug: 'no_preference' },
            { name: 'Disable-No Compression', slug: 'disabled' },
            { name: 'Enabled with Adaptive Compression', slug: 'adaptive' },
            { name: 'Enabled without Adaptive Compression', slug: 'enabled' },
          ]"
          return-object
        ></v-select>
      </v-col>

      <v-col cols="4" align-self="center">
        <label>Type of service</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="typefService" />
        <label class="ml-2">Active type of service</label>
      </v-col>
      <v-col cols="4" align-self="center">
        <label>Connections</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="Connections" />
        <label class="ml-2">Duplicate connections</label>
      </v-col>
      <v-col cols="4" align-self="center">
        <label>IPv6</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="IPv6" />
        <label class="ml-2">Disable IPv6</label>
      </v-col>
      <v-col cols="4" align-self="center">
        <label>Inter clients</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="interClients" />
        <label class="ml-2">Communication inter clients</label>
      </v-col>
    </v-row>
  </div>
</template>
<script setup>
import { useVModels } from "@vueuse/core";
import axios from "axios";
import { onMounted, ref } from "vue";
onMounted(() => {
  getInterface();
});

const props = defineProps([
  "errors",
  "deviceMode",
  "ip4Tunnel",
  "ip6Tunnel",
  "isGateway",
  "isBridge",
  "interfaceBridge",
  "startDHCPBridge",
  "endDHCPBridge",
  "iPv4Local",
  "iPv6Local",
  "iPv4Remote",
  "iPv6Remote",
  "concurrentConnections",
  "compression",
  "typefService",
  "Connections",
  "IPv6",
  "interClients",
]);
const emit = defineEmits([
  "update:ip6Tunnel",
  "update:isGateway",
  "update:isBridge",
  "update:interfaceBridge",
  "update:startDHCPBridge",
  "update:endDHCPBridge",
  "update:iPv4Local",
  "update:iPv6Local",
  "update:iPv4Remote",
  "update:iPv6Remote",
  "update:concurrentConnections",
  "update:compression",
  "update:typefService",
  "update:Connections",
  "update:IPv6",
  "update:interClients",
  "update:ip4Tunnel",
]);
const {
  ip6Tunnel,
  isGateway,
  isBridge,
  startDHCPBridge,
  interfaceBridge,
  endDHCPBridge,
  iPv4Local,
  iPv6Local,
  iPv4Remote,
  iPv6Remote,
  concurrentConnections,
  compression,
  typefService,
  Connections,
  IPv6,
  interClients,
  ip4Tunnel,
} = useVModels(props, emit);

const mapedInterface = ref([]);

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
      mapedInterface.value = interfaces;
    },
    (error) => {
      console.log(error);
    }
  );
};
</script>
