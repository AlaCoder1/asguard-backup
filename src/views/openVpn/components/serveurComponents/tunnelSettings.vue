<template>
  <div class="ml-3 mr-3">
    <h4>{{$t('openvpn.TunnelSettings')}}</h4>
    <v-divider class="mt-2"></v-divider>
    <v-row class="mt-2">
      <v-col
        v-if="!props.addressPool && !isBridge"
        cols="4"
        align-self="center"
      >
        <label>{{$t('openvpn.IPv4TunnelNetwork')}}*</label>
      </v-col>
      <v-col v-if="!props.addressPool && !isBridge" cols="8" class="mb-n6">
        <v-text-field
          :label= "$t('openvpn.IPv4TunnelNetwork')"
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
        <label>{{$t('openvpn.IPv6TunnelNetwork')}}</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          :label="$t('openvpn.IPv6TunnelNetwork')"
          v-model="ip6Tunnel"
        ></v-text-field>
      </v-col>
      <v-col cols="4" align-self="center">
        <label>{{$t('openvpn.Gateway')}}</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="isGateway" />
        <label class="ml-2">{{$t('openvpn.redirectGateway')}}</label>
      </v-col>

      <v-col cols="4" v-if="deviceMode === 'tap'" align-self="center">
        <label>{{$t('openvpn.Bridge')}}</label>
      </v-col>
      <v-col cols="8" class="mb-n6" v-if="deviceMode === 'tap'">
        <input type="checkbox" v-model="isBridge" />
        <label class="ml-2">{{$t('openvpn.DHCPbridge')}}</label>
      </v-col>

      <v-col cols="4" v-if="isBridge" align-self="center">
        <label>{{$t('openvpn.Interfacebridge')}}*</label>
      </v-col>
      <v-col cols="8" class="mb-n6" v-if="isBridge">
        <v-select
         :label="$t('openvpn.Interfacebridge')"
          v-model="interfaceBridge"
          item-title="name"
          item-value="id"
          return-object
          :items="mapedInterface"
        ></v-select>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.interfaceBridge.$errors.length"
        >
          {{ props.errors.interfaceBridge.$errors?.[0].$message }}
        </p>
      </v-col>

      <v-col cols="4" v-if="isBridge" align-self="center">
        <label>{{$t('openvpn.StartDHCPbridge')}}</label>
      </v-col>
      <v-col cols="8" class="mb-n6" v-if="isBridge">
        <v-text-field
          :label="$t('openvpn.StartDHCPbridge')"
          v-model="startDHCPBridge"
        ></v-text-field>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.startDHCPBridge.$errors.length"
        >
          {{ props.errors.startDHCPBridge.$errors?.[0].$message }}
        </p>
      </v-col>
      <v-col cols="4" v-if="isBridge" align-self="center">
        <label>E{{$t('openvpn.EndDHCPbridge')}}</label>
      </v-col>
      <v-col cols="8" class="mb-n6" v-if="isBridge">
        <v-text-field
          :label="$t('openvpn.EndDHCPbridge')"
          v-model="endDHCPBridge"
        ></v-text-field>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.endDHCPBridge.$errors.length"
        >
          {{ props.errors.endDHCPBridge.$errors?.[0].$message }}
        </p>
      </v-col>
      <v-col cols="4" align-self="center">
        <label>
          {{
            isBridge || props.addressPool
              ? $t('openvpn.IPv4LocalNetwork')
              : $t('openvpn.IPv4LocalNetwork') + '*'
          }}
        </label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          :label="$t('openvpn.IPv4LocalNetwork')"
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
        <label>{{$t('openvpn.IPv6LocalNetwork')}}</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          :label="$t('openvpn.IPv6LocalNetwork')"
          v-model="iPv6Local"
        ></v-text-field>
      </v-col>
      <v-col cols="4" align-self="center">
        <label>{{$t('openvpn.IPv4RemoteNetwork')}}</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          :label="$t('openvpn.IPv4RemoteNetwork')"
          v-model="iPv4Remote"
        ></v-text-field>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.iPv4Remote.$errors.length"
        >
          {{ props.errors.iPv4Remote.$errors?.[0].$message }}
        </p>
      </v-col>
      <v-col cols="4" align-self="center">
        <label>{{$t('openvpn.IPv6RemoteNetwork')}}</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          :label="$t('openvpn.IPv6RemoteNetwork')"
          v-model="iPv6Remote"
        ></v-text-field>
      </v-col>
      <v-col cols="4" align-self="center">
        <label>{{$t('openvpn.Concurrentconnections')}}</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          :label="$t('openvpn.Concurrentconnections')"
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
        <label>{{$t('openvpn.Typeofservice')}}</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="typefService" />
        <label class="ml-2">{{$t('openvpn.Activethetypeofservice')}}</label>
      </v-col>
      <v-col cols="4" align-self="center">
        <label>{{$t('openvpn.Connections')}}</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="Connections" />
        <label class="ml-2">{{$t('openvpn.Duplicateconnections')}}</label>
      </v-col>
      <v-col cols="4" align-self="center">
        <label>IPv6</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="IPv6" />
        <label class="ml-2">{{$t("openvpn.Disable")}} IPv6</label>
      </v-col>
      <v-col cols="4" align-self="center">
        <label>Inter clients</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="interClients" />
        <label class="ml-2">{{$t('openvpn.Communicationinterclients')}}</label>
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
  "addressPool",
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
      let filtredInterface = response.data.filter(
        (i) => !i.ifname.startsWith("tun_") && !i.ifname.startsWith("tap_")
      );

      let interfaces = filtredInterface.map((i) => {
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
