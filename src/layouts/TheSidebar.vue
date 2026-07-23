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
            <v-list-item @click="showSubMenu(item)" class="sidebar-nav-item">
              <div v-if="!rail">
                <div class="float-left sidebar-item-inner">
                  <span class="ml-5 icon-custom"
                    ><i :class="item.icon"></i
                  ></span>
                  <span class="ml-7 sidebarTitle">{{ $t(item.title) }}</span>
                </div>


                <v-list-item-title
                  class="float-right mr-5"
                  style="margin-top: 13px"
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
            v-for="subItem in filteredSubItems(item)"
            v-if="item.subMenuVisible"
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
            <v-list-item @click="showSubMenu(item)" style="position:relative;">
              <div>
                <span class="ml-5"
                  ><i :class="item.icon" class="icon-custom"></i
                ></span>
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
      user: null,
      drawer: true,
      rail: false,
      mini: false,
      _clockInterval: null,
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
        {
          title: "sideBar.system",
          icon: "mdi mdi-laptop",
          active: "system",
          subItems: [
            {
              title: "tabs.userManagement",
              icon: "",
              href: "/system/user-management",
              active: "User management",
            },
            {
              title: "tabs.certificateManagement",
              icon: "",
              href: "/system/certificat-management",
              active: "certificat management",
            },
            {
              title: "subtitle.rsaKeyPairs",
              icon: "",
              href: "/key_pairs",
              active: "RSA Key Pairs",
            },
            {
              title: "subtitle.systemLog",
              icon: "",
              href: "/system_log",
              active: "System Log",
            },
            {
              title: "subtitle.archivedLog",
              icon: "",
              href: "/logrotate",
              active: "Archived Logs",
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
            {
              title: "subtitle.DHCPV4",
              icon: "",
              href: "/services/server-dhcp4",
              active: "DHCP V4",
            },
            {
              title: "subtitle.routing",
              icon: "",
              href: "/routing",
              href: "/routing",
              active: "routing",
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
              title: "subtitle.openVPN",
              icon: "",
              href: "/openvpn",
              active: "OPEN VPN",
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
            {
              title: "subtitle.ZTNA",
              icon: "",
              href: "/ztna",
              active: "ZTNA",
            },
            {
              title: "subtitle.Dmasque",
              icon: "",
              href: "/double-masque",
              active: "double-masque",
            },
          ],
          subMenuVisible: false,
        },
        {
          title: "sideBar.backup",
          icon: "mdi mdi-backup-restore",
          href: "/backup",
          active: "backup",
          subItems: [],
          subMenuVisible: false,
        },
        {
          title: "sideBar.license",
          icon: "mdi mdi-cash-sync",
          href: "/asguard/license",
          active: "Subscription",
          subItems: [],
          subMenuVisible: false,
        },
      ],
    };
  },
  mounted: async function () {
    let retriveInfo = localStorage.getItem("user-info");
    let userInfo = JSON.parse(retriveInfo);
    this.user = userInfo;

  },


  methods: {
    filteredSubItems(item) {
      return item.subItems.filter((subItem) => {
        if (!this.isAdmin) {
          return (
            subItem.title !== "tabs.userManagement" &&
            subItem.title !== "subtitle.settings"
          );
        }
        return true;
      });
    },
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
    },
  },
  computed: {
    isAdmin() {
      return this.user?.currentUser?.role === "admin";
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

/* ── Sidebar item inner alignment ──────────────────────── */
.sidebar-nav-item {
  position: relative !important;
}

.sidebar-item-inner {
  display: flex !important;
  align-items: center !important;
  height: 48px;
}

/* ── Sidebar badge (absolute, centré à droite du list-item) ── */
.sidebar-badge {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 5px;
  border-radius: 99px;
  background: linear-gradient(135deg, #ef5350, #e53935);
  color: #fff;
  font-size: 10px;
  font-weight: 800;
  line-height: 1;
  box-shadow: 0 2px 6px rgba(229,57,53,0.35);
  letter-spacing: 0.2px;
  z-index: 1;
}

.sidebar-badge--rail {
  position: absolute;
  top: 2px;
  right: 2px;
  min-width: 16px;
  height: 16px;
  font-size: 8px;
  box-shadow: 0 1px 4px rgba(229,57,53,0.4);
}

/* ── Monitor actif footer ───────────────────────────────── */
.sidebar-monitor {
  padding: 10px 16px 14px;
  border-top: 1px solid rgba(0,0,0,0.07);
  background: linear-gradient(to bottom, #f9fafb, #f1f3f5);
  margin-top: 4px;
}

.sidebar-monitor--rail {
  padding: 10px 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(to bottom, #f9fafb, #f1f3f5);
  border-top: 1px solid rgba(0,0,0,0.07);
  margin-top: 4px;
}

.sidebar-live-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 5px;
}

.sidebar-live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
  flex-shrink: 0;
  animation: pulse-green 2s ease-in-out infinite;
}

@keyframes pulse-green {
  0%, 100% { box-shadow: 0 0 0 0 rgba(34,197,94,0.55); }
  50%       { box-shadow: 0 0 0 4px rgba(34,197,94,0); }
}

.sidebar-live-label {
  font-size: 10px;
  font-weight: 800;
  color: #16a34a;
  letter-spacing: 0.8px;
  text-transform: uppercase;
}

.sidebar-live-clock {
  font-size: 11px;
  font-weight: 600;
  color: #6b7280;
  margin-left: auto;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.2px;
}

.sidebar-monitor-label {
  font-size: 10px;
  color: #9ca3af;
  font-weight: 500;
  margin-bottom: 5px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sidebar-autobackup {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px 3px 6px;
  border-radius: 99px;
}

.sidebar-autobackup.on {
  background: rgba(34,197,94,0.1);
  color: #16a34a;
  border: 1px solid rgba(34,197,94,0.25);
}
.sidebar-autobackup.off {
  background: rgba(245,158,11,0.1);
  color: #b45309;
  border: 1px solid rgba(245,158,11,0.25);
}

.sidebar-autobackup-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.sidebar-autobackup.on  .sidebar-autobackup-dot { background: #22c55e; }
.sidebar-autobackup.off .sidebar-autobackup-dot { background: #f59e0b; }
</style>
