<template>
  <v-navigation-drawer v-model="drawer" :rail="rail" hover foating :rail-width="67" class="global-drawer"
    :class="{ 'w-auto': rail, 'w-20': !rail }">
    <div v-if="!rail">
      <div dense flat class="row-pointer asguard_primary_dark" @click.stop="closeSidebar">
        <div class="d-flex">
          <v-toolbar-title class="ml-5 mt-5">
            <span>Asguard</span>
          </v-toolbar-title>

          <div class="ml-5 mt-5 mr-5">
            <v-icon v-if="!rail"><i class="mdi mdi-menu icon-custom"></i></v-icon>
          </div>
        </div>
      </div>

      <v-list>
        <template v-for="item in items">
          <a :href="item.href" class="custom-a">
            <v-list-item @click="showSubMenu(item)">
              <div v-if="!rail">
                <v-list-item class="float-left">

                  <span class="ml-5 icon-custom"><i :class="item.icon"></i> &nbsp;</span>
                  <span class="ml-7 sidebarTitle">{{ item.title }}</span></v-list-item>


                <v-list-item-title class="float-right justify-end mr-5" v-if="item.subItems.length > 0">
                  <v-icon v-if="item.subMenuVisible"><i class="mdi mdi-chevron-up" aria-hidden="true"></i>
                  </v-icon>
                  <v-icon v-else><i class="mdi mdi-chevron-down" aria-hidden="true"></i></v-icon>
                </v-list-item-title>
              </div>
            </v-list-item>
          </a>
          <v-list-item v-if="item.subMenuVisible" v-for="subItem in item.subItems" :key="subItem.title"
            :class="{ 'sub-menu-visible': item.subMenuVisible }" class="sub-menu-item">
            <a :href="subItem.href" class="custom-sub-a">
              <v-list-item>
                <v-list-item-title class="text-white-space">{{
                  subItem.title
                }}</v-list-item-title>
              </v-list-item>
            </a>
          </v-list-item>
        </template>
      </v-list>
    </div>
    <div v-else>
      <div class="ml-5 mt-5 mr-5 row-pointer asguard_primary_dark" @click="closeSidebar">
        <v-icon v-if="rail"><i class="mdi mdi-close icon-custom"></i></v-icon>
      </div>

      <v-list>
        <template v-for="item in items">
          <a :href="item.href" style="text-decoration: none; color: black;">
            <v-list-item @click="showSubMenu(item)">
              <div>
                <span class="ml-5"><i :class="item.icon" class="icon-custom"></i> &nbsp;</span>
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
          title: "Dashboard",
          icon: "mdi mdi-view-dashboard",
          href: "/dashboard",
          active: "dashboard",
          subItems: [],
          mouseOverSubMenu: false,
          subMenuVisible: false,
        },
        {
          title: "System",
          icon: "mdi mdi-laptop",
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
          icon: "mdi mdi-network",
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
          icon: "mdi mdi-wall-fire",
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
          icon: "mdi mdi-cog",
          active: "Firewall",
          subItems: [
            {
              title: "Site to site VPN",
              icon: "",
              href: "/ipsec",
              active: "Site to site VPN",
            },
            {
              title: "RSA Key Pairs",
              icon: "",
              href: "/key_pairs",
              active: "RSA Key Pairs",
            },
            {
              title: "OPEN VPN",
              icon: "",
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
              href: "/proxy-web",
              active: "Proxy Web",
            },
          ],
          subMenuVisible: false,
        },
        {
          title: "Reports",
          icon: "mdi mdi-chart-bar",
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
          icon: "mdi mdi-cash-sync",
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
@import '~@mdi/font/css/materialdesignicons.min.css';


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
  word-wrap: break-word
}
</style>
