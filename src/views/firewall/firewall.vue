<template>
  <v-app id="inspire">
    <base-layout :title="$t('firewall.rules')">
      <template #content>
        <v-alert v-model="isFirewallSubscribe" density="compact" type="warning"
          ><span style="font-size: 19px"
            >{{$t("firewall.msg_subscription")}}
          </span>
          <span
            style="cursor: pointer; text-decoration: underline; font-size: 19px"
            @click="goToSub"
            >{{$t("firewall.sub_page")}}</span
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
                <FirewallComponent
                  :id="tab.name_interface"
                  :activeTab="activeTab"
                />
                <FirewallComponentOutbound
                  :id="tab.name_interface"
                  :activeTab="activeTab"
                />
              </v-card-text>
            </v-card>
          </v-window-item>
        </v-window>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import BaseLayout from "../../layouts/layout.vue";
import FirewallComponent from "../../views/firewall/rules/FirewallComponent.vue";
import FirewallComponentOutbound from "../../views/firewall/rules/FirewallComponentOutbound.vue";

export default {
  components: {
    BaseLayout,
    FirewallComponent,
    FirewallComponentOutbound,
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

    let filtredInterface = parsedArray.filter(
      (i) => !i.ifname.startsWith("vlan")
    );

    this.interfaces = filtredInterface;

    let tab = localStorage.getItem("firewall-tab");
    if (tab) {
      this.activeTab = tab;
    } else {
      this.activeTab = this.tabs[0]?.name_interface;
    }
  },
  methods: {
    goToSub() {
      window.location.href = "/asguard/subscription/";
    },
  },
};
</script>
