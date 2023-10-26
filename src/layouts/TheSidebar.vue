<template>
  <v-navigation-drawer
    :mini-variant.sync="mini"
    class="global-drawer"
    permanent
    app
  >
    <v-app-bar dense flat class="row-pointer" @click.stop="closeSidebar">
      <v-toolbar-title>
        <span>Asguard</span>
      </v-toolbar-title>
      <v-spacer></v-spacer>
    </v-app-bar>
    <v-icon v-if="mini">mdi-close</v-icon>
    <v-icon v-if="!mini">mdi-menu</v-icon>
    <v-list dense class="text-center mt-">
      <template v-for="item in items">
        <a :href="item.href" class="custom-a">
          <v-list-item @click="showSubMenu(item)">
            <v-list-item-icon>
              <v-icon>{{ item.icon }}</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>{{ item.title }}</v-list-item-title>
            </v-list-item-content>
            <v-list-item-action v-if="item.subItems.length > 0">
              <v-icon v-if="item.subMenuVisible">mdi-chevron-up</v-icon>
              <v-icon v-else>mdi-chevron-down</v-icon>
            </v-list-item-action>
          </v-list-item>
        </a>
        <v-list-item
          v-if="item.subMenuVisible"
          v-for="subItem in item.subItems"
          :key="subItem.title"
          :class="{ 'sub-menu-visible': item.subMenuVisible }"
          class="sub-menu-item"
        >
          <a :href="subItem.href" class="custom-sub-a">
            <v-list-item-content>
              <v-list-item-title class="text-white-space">{{
                subItem.title
              }}</v-list-item-title>
            </v-list-item-content>
          </a>
        </v-list-item>
      </template>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
import { useAuthStore } from "../store/modules/auth";
const storeAuth = useAuthStore();

export default {
  name: "TheSidebar",

  data() {
    return {
      drawer: true,
      mini: false,
      items: [
        {
          title: "Dashboard",
          icon: "mdi-view-dashboard",
          href: "/dashboard",
          active: "dashboard",
          subItems: [],
          mouseOverSubMenu: false,
          subMenuVisible: false,
        },
        {
          title: "System",
          icon: "mdi-laptop",
          active: "system",
          subItems: [
            {
              title: "Assistante",
              icon: "",
              href: "/system/assistante",
              active: "Assistante",
            },
            {
              title: "User & certificat management",
              icon: "",
              href: "/system/user-certificat-management",
              active: "User & certificat management",
            },
            {
              title: "Network management",
              icon: "",
              href: "/system/network-management",
              active: "Network management",
            },
            {
              title: "System configuration",
              icon: "",
              href: "/system/system-configuration",
              active: "System configuration",
            },
            {
              title: "Settings",
              icon: "",
              href: "/settings",
              href: "/settings",
              active: "Settings",
            },
          ],
          mouseOverSubMenu: false,
          subMenuVisible: false,
        },
        {
          title: "Interfaces",
          icon: "mdi-network",
          active: "interfaces",
          subItems: [
            {
              title: "Overview",
              icon: "",
              href: "/interfaces/overview",
              active: "Overview",
            },
            {
              title: "Assignations",
              icon: "",
              href: "/interfaces/assignations",
              active: "Assignations",
            },
            {
              title: "Different Networks",
              icon: "",
              href: "/interfaces/different-networks",
              active: "Different Networks",
            },
            {
              title: "Diagnostics",
              icon: "",
              href: "/interfaces/diagnostics",
              active: "Diagnostics",
            },
            {
              title: "List of interface",
              icon: "",
              href: "/interfaces/list-of-interface",
              active: "List of interface",
            },
            {
              title: "Settings",
              icon: "",
              href: "/settings",
              href: "/settings",
              active: "Settings",
            },
          ],
          subMenuVisible: false,
        },
        {
          title: "Firewall",
          icon: "mdi-wall-fire",
          active: "Firewall",
          subItems: [
            {
              title: "Rules",
              icon: "",
              href: "/firewall/rules",
              active: "Rules",
            },
            {
              title: "Nat",
              icon: "",
              href: "/firewall/nat",
              active: "Nat",
            },
            {
              title: "Advanced settings",
              icon: "",
              href: "/firewall/advanced-settings",
              active: "Advanced settings",
            },
          ],
          subMenuVisible: false,
        },
        {
          title: "Services",
          icon: "mdi-cog",
          active: "Firewall",
          subItems: [
            {
              title: "Site to site VPN",
              icon: "",
              href: "/services/site-to-site-vpn",
              active: "Site to site VPN",
            },
            {
              title: "OPEN VPN",
              icon: "",
              href: "/openvpn",
              href: "/openvpn",
              active: "OPEN VPN",
            },
            {
              title: "IP Filter double masque",
              icon: "",
              href: "/services/ip-filter-double-masque",
              active: "IP Filter double masque",
            },
            {
              title: "Calm AV",
              icon: "",
              href: "/services/calm-av",
              active: "Calm AV",
            },
            {
              title: "DHCP V4",
              icon: "",
              href: "/services/dhcp-v4",
              active: "DHCP V4",
            },
            {
              title: "DHCP V6",
              icon: "",
              href: "/services/dhcp-v6",
              active: "DHCP V",
            },
            {
              title: "Intrusion Detection",
              icon: "",
              href: "/services/intrusion-detection",
              active: "Intrusion Detection",
            },
            {
              title: "Proxy Web",
              icon: "",
              href: "/services/proxy-web",
              active: "Proxy Web",
            },
          ],
          subMenuVisible: false,
        },
        {
          title: "Reports",
          icon: "mdi-chart-bar",
          active: "Firewall",
          subItems: [
            {
              title: "Health",
              icon: "",
              href: "/reports/health",
              active: "Health",
            },
            {
              title: "Insight",
              icon: "",
              href: "/reports/insight",
              active: "Insight",
            },
            {
              title: "Traffic",
              icon: "",
              href: "/reports/traffic",
              active: "Traffic",
            },
            {
              title: "Event logs",
              icon: "",
              href: "/reports/event-logs",
              active: "Event logs",
            },
          ],
          subMenuVisible: false,
        },
        {
          title: "Subscription",
          icon: "mdi-cash-sync",
          href: "/subscription",
          active: "Firewall",
          subItems: [],
          subMenuVisible: false,
        },
      ],
    };
  },
  methods: {
    logout() {
      storeAuth.logout();
    },
    showSubMenu(item) {
      this.items.forEach((menuItem) => {
        if (menuItem !== item) {
          menuItem.subMenuVisible = false;
        }
      });
      item.subMenuVisible = !item.subMenuVisible;
      if (item.href) {
        window.location.href = item.href;
      }
    },
    closeSidebar() {
      this.mini = !this.mini;
      this.items.forEach((menuItem) => {
        menuItem.subMenuVisible = false;
      });
    },
  },
  computed: {
    user() {
      return storeAuth.user;
    },
  },
};
</script>
