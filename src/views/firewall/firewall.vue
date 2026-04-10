<template>
  <v-app id="inspire">
    <base-layout :title="$t('firewall.rules')">
      <template #content>
        <v-alert v-model="isFirewallSubscribe" density="compact" type="warning"
          ><span style="font-size: 19px"
            >{{ $t("firewall.msg_subscription") }}
          </span>
          <span
            class="ml-2"
            style="cursor: pointer; text-decoration: underline; font-size: 19px"
            @click="goToSub"
            >{{ $t("firewall.sub_page") }}</span
          >
        </v-alert>
        <v-tabs
          v-model="activeTab"
          background-color="#f5f5f5"
          color="black"
          :class="{ 'elevation-0': true }"
          :slider-color="'#FFC300'"
        >
          <v-tab
            v-for="tab in tabs"
            :key="tab.name_interface"
            :value="tab.name_interface"
          >
            <span style="color: #020202">{{ tab.name_interface }}</span>
          </v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <v-window-item
            v-for="tab in tabs"
            :key="tab.name_interface"
            :value="tab.name_interface"
          >
            <v-card>
              <v-card-text>
                <helpModal help="rules" />

                <FirewallComponent
                  :id="tab.name_interface"
                  :uuid="tab.uuid"
                  :activeTab="activeTab"
                />
                <FirewallComponentOutbound
                  :id="tab.name_interface"
                  :uuid="tab.uuid"
                  :activeTab="activeTab"
                />
              </v-card-text>
            </v-card>
          </v-window-item>
        </v-window>
        <div
          v-if="tabs.length == 0"
          style="
            display: flex;
            flex-direction: column;
            height: 40%;
            width: 100%;
            text-align: center;
            align-items: center;
            justify-content: center;
          "
        >
          <span aria-live="polite" aria-atomic="true">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 88 88"
              width="100"
              height="100"
            >
              <path
                d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
                style="fill: #e8eaf6"
                data-name="Unbox"
              />
            </svg>
          </span>
          <h5 class="ml-2">{{ $t("noInterfaces") }}</h5>
        </div>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import helpModal from "@/components/modals/help.vue";

import { v4 as uuidv4 } from "uuid";
import BaseLayout from "../../layouts/layout.vue";
import FirewallComponent from "../../views/firewall/rules/FirewallComponent.vue";
import FirewallComponentOutbound from "../../views/firewall/rules/FirewallComponentOutbound.vue";

export default {
  components: {
    BaseLayout,
    FirewallComponent,
    FirewallComponentOutbound,
    helpModal,
  },
  inject: ["emitter"],
  data() {
    return {
      isFirewallSubscribe: false,
      activeTab: "",
      interfaces: [],
    };
  },
  watch: {
    activeTab(val) {
      localStorage.setItem("firewall-tab", val);
    },
  },
  computed: {
    tabs() {
      return this.interfaces.map((element) => ({
        uuid: uuidv4(),
        name_interface: element.name_interface,
      }));
    },
  },
  mounted() {
    this.emitter.on("firewal-subscription", () => {
      this.isFirewallSubscribe = true;
      setTimeout(() => {
        this.isFirewallSubscribe = false;
      }, 6000);
    });

    let interfaces =
      document.getElementById("app").attributes["interfaces"].value;
    let validJsonString = interfaces
      .replace(/'/g, '"')
      .replace(/True/g, "true")
      .replace(/False/g, "false")
      .replace(/None/g, "null");
    let parsedArray = JSON.parse(validJsonString);

    // let filtredInterface = parsedArray.filter(
    //   (i) => !i.ifname.startsWith("vlan")
    // );

    this.interfaces = parsedArray;

    let tab = localStorage.getItem("firewall-tab");
    if (tab) {
      this.activeTab = tab;
    } else {
      this.activeTab = this.tabs[0]?.name_interface;
    }
  },
  methods: {
    goToSub() {
      window.location.href = "/asguard/license/";
    },
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
