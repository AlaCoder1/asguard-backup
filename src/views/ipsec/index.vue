<template>
  <v-app id="inspire">
    <base-layout :title="$t('subtitle.siteToSiteVpn')">

      <template #content>
        <v-alert v-model="this.isIpsecnotrunning" density="compact" type="warning"><span style="font-size: 19px">{{
          $t("PageIpsec.IpsecStatus") }}
          </span>
        </v-alert>
        <v-tabs v-model="activeTab">
          <v-tab v-for="tab in tabs" :key="tab.id" :value="tab.label">
            <span style="color: #020202">{{ $t(tab.label) }}</span>
          </v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <v-window-item v-for="(tab, index) in tabs" :key="index" :value="tab.label">
            <v-card>
              <v-card-text>

                <helpModal v-if="activeTab === 'tabs.tunnelConfig'" help="config" />
                <helpModal v-if="activeTab === 'tabs.ipsecPeers'" help="listing" />
                <helpModal v-if="activeTab === 'tabs.monitoring'" help="monitoring" />

                <component :is="tab.component" :dataServer="dataServer" />
              </v-card-text>
            </v-card>
          </v-window-item>
        </v-window>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import helpModal from "@/components/modals/help.vue";

import BaseLayout from "@/layouts/layout.vue";
import ipsecAdvancedParams from "./ipsecAdvancedParams.vue";
import ConfigurationList from "./component/configurationList.vue";
import Monotoring from "./component/monotoring.vue";
import { getCookie } from "@/mixins/csrftoken.js";
import axios from "axios";

export default {
  name: "IpsecComponent",
  components: {
    BaseLayout,
    ipsecAdvancedParams,
    ConfigurationList,
    Monotoring,
    helpModal
  },
  inject: ["emitter"],
  data() {
    return {
      activeTab: "",
      last_Subscription: [],
      isIpsecnotrunning: false,
      tabs: [
        {
          id: 1,
          label: "tabs.tunnelConfig",
          component: ipsecAdvancedParams,
        },
        {
          id: 2,
          label: "tabs.ipsecPeers",
          component: ConfigurationList,
        },
        {
          id: 3,
          label: "tabs.monitoring",
          component: Monotoring,
        },
      ],
      rowDataServers: [],
      serverInfo: null,
      dataServer: null,
    };
  },
  watch: {
    activeTab(val) {
      localStorage.setItem("ipsec-tab", val);
      this.dataServer = val;
    },
  },
  mounted() {
    const csrfToken = getCookie("csrftoken");
    axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
    axios.get("/subscription/list_features_about_last_subscription").then((response) => {
      this.last_Subscription = response.data.list_features
      console.log('last sub', response.data.list_features)

    });

    axios.get("/ipsec/getIPsecStatus").then((response) => {
      this.isIpsecnotrunning = !response.data;
      console.log('statusipsec', !this.isIpsecnotrunning)
    });
    setTimeout(() => {
      this.emitter.on("reload-tabs", () => {
        let tab = localStorage.getItem("ipsec-tab") || "tabs.tunnelConfig";

        if (tab) this.activeTab = tab;
      });

      let ids = localStorage.getItem("ipsec-tab") || "tabs.tunnelConfig";
      if (ids) this.activeTab = ids;

      this.serverInfo =
        document.getElementById("app").attributes["servers"].value;
      this.emitter.on("add-serverIpsec", () => {
        this.activeTab = "tabs.tunnelConfig";
      });
      this.emitter.on("open-listingIpsec", () => {
        this.activeTab = "tabs.ipsecPeers";
      });

      this.rowDataServers =
        document.getElementById("app").attributes["servers"].value;
      let validJsonString = this.rowDataServers;
      let parsedArray = JSON.parse(validJsonString);
      this.rowDataServers = parsedArray;
      if (!this.last_Subscription.includes("VPN IPSEC") && this.isIpsecnotrunning === false) {
        const csrfToken = getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
        const status = "stop";
        const data = {
          "status": status,
        };
        let endpoint = "statusIPsec";
        axios
          .post(`/ipsec/${endpoint}`, data)
          .then((response) => {
            console.log("response", response);
            setTimeout(() => {
              location.reload();
            }, 1000);
          })
          .catch((i) => {
            console.error("Error in status change", error);
          });
      }
    }, 1000)
  },
};
</script>
<style>
.img-view {
  border-style: none;
  width: 100%;
  height: 250px;
  object-fit: cover;
  overflow: hidden;
}

.img-containter {
  display: flex;
  width: 100%;
  /* height: 100%; */
  padding: 0px !important;
}
</style>
