<template>
  <v-navigation-drawer
    v-model="drawer"
    :rail="rail"
    hover
    permanent
    foating
    :rail-width="67"
    class="global-drawer"
    :class="{ 'w-auto': rail, 'w-20': !rail }"
  >
    <div v-if="!rail">
      <div
        dense
        flat
        class="row-pointer asguard_primary_dark"
        @click.stop="closeSidebar"
      >
        <div class="d-flex">
          <v-toolbar-title class="ml-5 mt-5">
            <span>Asguard</span>
          </v-toolbar-title>

          <div class="ml-5 mt-5 mr-5">
            <v-icon v-if="!rail"
              ><i class="mdi mdi-close icon-custom"></i
            ></v-icon>
          </div>
        </div>
      </div>

      <v-list>
        <template v-for="item in items">
          <a :href="item.href" class="custom-a">
            <v-list-item @click="showSubMenu(item)">
              <div v-if="!rail">
                <v-list-item class="float-left">
                  <span class="ml-5 icon-custom"
                    ><i :class="item.icon"></i> &nbsp;</span
                  >
                  <span class="ml-7 sidebarTitle">{{
                    $t(item.title)
                  }}</span></v-list-item
                >

                <v-list-item-title
                  class="float-right justify-end mr-5"
                  style="margin-top: 15px"
                  v-if="item.subItems.length > 0"
                >
                  <v-icon v-if="item.subMenuVisible"
                    ><i class="mdi mdi-chevron-up" aria-hidden="true"></i>
                  </v-icon>
                  <v-icon v-else
                    ><i class="mdi mdi-chevron-down" aria-hidden="true"></i
                  ></v-icon>
                </v-list-item-title>
              </div>
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
              <v-list-item>
                <v-list-item-title class="text-white-space">{{
                  $t(subItem.title)
                }}</v-list-item-title>
              </v-list-item>
            </a>
          </v-list-item>
        </template>
      </v-list>
    </div>
    <div v-else>
      <div
        class="ml-5 mt-5 mr-5 row-pointer asguard_primary_dark"
        @click="closeSidebar"
      >
        <v-icon v-if="rail"><i class="mdi mdi-menu icon-custom"></i></v-icon>
      </div>

      <v-list>
        <template v-for="item in items">
          <a :href="item.href" style="text-decoration: none; color: black">
            <v-list-item @click="showSubMenu(item)">
              <div>
                <span class="ml-5"
                  ><i :class="item.icon" class="icon-custom"></i> &nbsp;</span
                >
              </div>
            </v-list-item>
          </a>
        </template>
      </v-list>
    </div>
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
      rail: false,
      mini: false,
      items: [
        {
          title: "sideBar.dashboard",
          icon: "mdi mdi-view-dashboard",
          href: "/dashboard",
          active: "dashboard",
          subItems: [],
          mouseOverSubMenu: false,
          subMenuVisible: false,
        },
        // {
        //   title: "testMoni",
        //   icon: "mdi mdi-view-dashboard",
        //   href: "/vpnmonitoring",
        //   active: "vpnmonitoring",
        //   subItems: [],
        //   mouseOverSubMenu: false,
        //   subMenuVisible: false,
        // },
        {
          title: "sideBar.system",
          icon: "mdi mdi-laptop",
          active: "system",
          subItems: [
            {
              title: "subtitle.assistant",
              icon: "",
              href: "/system/assistante",
              active: "Assistante",
            },
            {
              title: "subtitle.userCertificatemanagement",
              icon: "",
              href: "/system/user-certificat-management",
              active: "User & certificat management",
            },
            {
              title: "subtitle.networkManagement",
              icon: "",
              href: "/system/network-management",
              active: "Network management",
            },
            {
              title: "subtitle.systemConfig",
              icon: "",
              href: "/system/system-configuration",
              active: "System configuration",
            },
            {
              title: "subtitle.settings",
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
          title: "sideBar.interfaces",
          icon: "mdi mdi-network",
          active: "interfaces",
          subItems: [
            {
              title: "subtitle.listOfInterface",
              icon: "",
              href: "/interfaces/list-of-interface",
              active: "List of interface",
            },
            {
              title: "subtitle.typeOfInterface",
              icon: "",
              href: "/interfaces/type-of-interface",
              active: "Type of interface",
            },
            // {
            //   title: "subtitle.overview",
            //   icon: "",
            //   href: "/interfaces/overview",
            //   active: "Overview",
            // },
            // {
            //   title: "subtitle.assignations",
            //   icon: "",
            //   href: "/interfaces/assignations",
            //   active: "Assignations",
            // },
            {
              title: "subtitle.differentNetworks",
              icon: "",
              href: "/interfaces/different-networks",
              active: "Different Networks",
            },
            {
              title: "subtitle.routing",
              icon: "",
              href: "/routing",
              href: "/routing",
              active: "routing",
            },
            {
              title: "subtitle.diagnostics",
              icon: "",
              href: "/interfaces/diagnostics",
              active: "Diagnostics",
            },

            {
              title: "subtitle.settings",
              icon: "",
              href: "/settings",
              href: "/settings",
              active: "Settings",
            },
          ],
          subMenuVisible: false,
        },
        {
          title: "sideBar.firewall",
          icon: "mdi mdi-wall-fire",
          active: "Firewall",
          subItems: [
            {
              title: "subtitle.rules",
              icon: "",
              href: "/firewall/rules",
              active: "Rules",
            },
            {
              title: "subtitle.nat",
              icon: "",
              href: "/firewall/nat",
              active: "Nat",
            },
            {
              title: "subtitle.advancedSettings",
              icon: "",
              href: "/firewall/advanced-settings",
              active: "Advanced settings",
            },
          ],
          subMenuVisible: false,
        },
        {
          title: "sideBar.services",
          icon: "mdi mdi-cog",
          active: "Firewall",
          subItems: [
            {
              title: "subtitle.siteToSiteVpn",
              icon: "",
              href: "/ipsec",
              active: "Site to site VPN",
            },
            {
              title: "subtitle.rsaKeyPairs",
              icon: "",
              href: "/key_pairs",
              active: "RSA Key Pairs",
            },
            {
              title: "subtitle.openVPN",
              icon: "",
              href: "/openvpn",
              active: "OPEN VPN",
            },
            {
              title: "subtitle.ipFilterDoubleMasque",
              icon: "",
              href: "/services/ip-filter-double-masque",
              active: "IP Filter double masque",
            },
            {
              title: "subtitle.clamAV",
              icon: "",
              href: "/clamaV",
              active: "Clam AV",
            },
            {
              title: "subtitle.DHCPV4",
              icon: "",
              href: "/services/server-dhcp4",
              active: "DHCP V4",
            },
            {
              title: "subtitle.DHCPV6",
              icon: "",
              href: "/services/dhcp-v6",
              active: "DHCP V",
            },
            {
              title: "subtitle.intrusionDetection",
              icon: "",
              href: "/ids-ips",
              active: "Intrusion Detection",
            },
            {
              title: "subtitle.proxyWeb",
              icon: "",
              href: "/proxy",
              active: "Proxy Web",
            },
            {
              title: "subtitle.SDWAN",
              icon: "",
              href: "/sdwan",
              active: "SDWAN",
            },
            {
              title: "subtitle.WAF",
              icon: "",
              href: "/waf",
              active: "WAF",
            },
          ],
          subMenuVisible: false,
        },
        {
          title: "sideBar.reports",
          icon: "mdi mdi-chart-bar",
          active: "Firewall",
          subItems: [
            {
              title: "subtitle.health",
              icon: "",
              href: "/reports/health",
              active: "Health",
            },
            {
              title: "subtitle.insight",
              icon: "",
              href: "/reports/insight",
              active: "Insight",
            },
            {
              title: "subtitle.traffic",
              icon: "",
              href: "/reports/traffic",
              active: "Traffic",
            },
            {
              title: "subtitle.eventLogs",
              icon: "",
              href: "/reports/event-logs",
              active: "Event logs",
            },
          ],
          subMenuVisible: false,
        },
        {
          title: "subtitle.subscription",
          icon: "mdi mdi-cash-sync",
          href: "/asguard/subscription",
          active: "Subscription",
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
      if (this.rail == true) this.rail = false;

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
      this.rail = !this.rail;

      // this.mini = !this.mini;
      // this.items.forEach((menuItem) => {
      //   menuItem.subMenuVisible = false;
      // });
    },
  },
  computed: {
    user() {
      return storeAuth.user;
    },
  },
};
</script>
<style lang="scss">
@import "font-awesome/css/font-awesome.css";
@import "~@mdi/font/css/materialdesignicons.min.css";

.flex-width {
  flex: 0 0 auto;
}

.margin-auto {
  margin-left: auto;
}

.icon-custom {
  color: rgb(104, 100, 100);
  font-size: 24px;
}

.sidebarTitle {
  color: #020202;
  font-size: 20px;
  font-family: Nunito;
  font-weight: 400;
  word-wrap: break-word;
}
</style>
