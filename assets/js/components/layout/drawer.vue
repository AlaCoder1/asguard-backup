<template>
  <div>
    <v-toolbar flat class="dms_blue_dark dms-media-print-hide dms-sticky" height="70">
      <v-toolbar-title class="dms-font-size-three white--text ml-8">
        <img src="../../../images/logoDMS.svg" height="50" />
      </v-toolbar-title>
      <v-spacer />
      <v-select v-model="lang" :items="['English', 'French']" class="select-lang" hide-details>
        <template v-slot:selection="{ item }">
          <v-chip class="dms_blue_dark white--text" small>
            <span>{{ item }}</span>
          </v-chip>
        </template>
      </v-select>
      <v-text-field background-color="white" rounded class="ml-3 input-search" hide-details v-model="searchText"
        append-icon="mdi-magnify"></v-text-field>
      <v-menu offset-y>
        <template v-slot:activator="{ on }" style=" margin-right: 10px; margin-left: 10px;">
          <v-avatar class="ml-3 mr-3" size="30" v-on="on">
            <v-icon size="30" class="dms_blue_dark white--text" color="white">mdi-account-circle-outline</v-icon>
          </v-avatar>
        </template>
        <v-list>
          <v-list-item>
            <v-btn text>Profile</v-btn>
          </v-list-item>
          <v-list-item>
            <v-btn text>Settings</v-btn>
          </v-list-item>
          <v-list-item>
            <v-list-item-title>
              <v-btn @click="logout" text>Logout</v-btn>
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
      <div style="display: flex; flex-direction: column; margin-right: 10px; margin-left: 10px;">
        <span style="color: white;">{{ user.currentUser.username }}</span>
        <span style="color: white;">{{ user.currentUser.email }}</span>
      </div>
      <br />
    </v-toolbar>
    <v-navigation-drawer :mini-variant.sync="mini" class="global-drawer" permanent app>
      <v-app-bar dense flat class="row-pointer dms_white" @click.stop="closeSidebar">
        <v-toolbar-title>
          <span>Asguard</span>
        </v-toolbar-title>
        <v-spacer></v-spacer>
        <v-icon v-if="mini">mdi-close</v-icon>
        <v-icon v-if="!mini">mdi-menu</v-icon>
      </v-app-bar>
      <v-list dense>
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
          <v-list-item v-if="item.subMenuVisible" v-for="subItem in item.subItems" :key="subItem.title"
            :class="{ 'sub-menu-visible': item.subMenuVisible }">
            <a :href="subItem.href" class="custom-sub-a">
              <!-- <v-list-item-icon>
              <v-icon size="20" v-if="subItem.icon !== ''">{{ subItem.icon }}</v-icon>
            </v-list-item-icon> -->
              <v-list-item-content>
                <v-list-item-title class="text-white-space">{{ subItem.title }}</v-list-item-title>
              </v-list-item-content>
            </a>
          </v-list-item>
        </template>
      </v-list>
    </v-navigation-drawer>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import '@mdi/font/css/materialdesignicons.min.css';

export default {
  name: 'DrawerComponent',
  props: {
  },
  components: {
  },
  data() {
    return {
      drawer: true,
      mini: false,
      searchText: '',
      lang: 'English',
      items: [
        {
          title: 'Dashboard',
          icon: 'mdi-view-dashboard',
          href: '/dashboard', active: 'dashboard',
          subItems: [],
          mouseOverSubMenu: false,
          subMenuVisible: false,
        },
        {
          title: 'System',
          icon: 'mdi-laptop',
          active: 'system',
          subItems: [
            {
              title: 'Assistante',
              icon: '',
              href: '/system/assistante',
              active: 'Assistante',
            },
            {
              title: 'User & certificat management',
              icon: '',
              href: '/userCertifMang',
              active: 'User & certificat management',
            },
            {
              title: 'Network management',
              icon: '',
              href: '/system/network-management',
              active: 'Network management',
            },
            {
              title: 'System configuration',
              icon: '',
              href: '/system/system-configuration',
              active: 'System configuration',
            },
            {
              title: 'Settings',
              icon: '',
              href: '/settings',
              href: '/settings',
              active: 'Settings',
            }

          ],
          mouseOverSubMenu: false,
          subMenuVisible: false,
        },
        {
          title: 'Interfaces',
          icon: 'mdi-network',
          active: 'interfaces',
          subItems: [
            {
              title: 'Overview',
              icon: '',
              href: '/interfaces/overview',
              active: 'Overview',
            },
            {
              title: 'Assignations',
              icon: '',
              href: '/interfaces/assignations',
              active: 'Assignations',
            },
            {
              title: 'Different Networks',
              icon: '',
              href: '/interfaces/different-networks',
              active: 'Different Networks',
            },
            {
              title: 'Diagnostics',
              icon: '',
              href: '/interfaces/diagnostics',
              active: 'Diagnostics',
            },
            {
              title: 'List of interface',
              icon: '',
              href: '/interfaces/list-of-interface',
              active: 'List of interface',
            }, {
              title: 'Settings',
              icon: '',
              href: '/settings',
              href: '/settings',
              active: 'Settings',
            }
          ],
          subMenuVisible: false,
        },
        {
          title: 'Firewall',
          icon: 'mdi-wall-fire', active: 'Firewall',
          subItems: [
            {
              title: 'Rules',
              icon: '',
              href: '/firewall/rules',
              active: 'Rules',
            },
            {
              title: 'Nat',
              icon: '',
              href: '/firewall/nat',
              active: 'Nat',
            },
            {
              title: 'Advanced settings',
              icon: '',
              href: '/firewall/advanced-settings',
              active: 'Advanced settings',
            }
          ],
          subMenuVisible: false,
        },
        {
          title: 'Services',
          icon: 'mdi-cog', active: 'Firewall',
          subItems: [
            {
              title: 'Site to site VPN',
              icon: '',
              href: '/services/site-to-site-vpn',
              active: 'Site to site VPN',
            },
            {
              title: 'OPEN VPN',
              icon: '',
              href: '/openvpn',
              href: '/openvpn',
              active: 'OPEN VPN',
            },
            {
              title: 'IP Filter double masque',
              icon: '',
              href: '/services/ip-filter-double-masque',
              active: 'IP Filter double masque',
            },
            {
              title: 'Calm AV',
              icon: '',
              href: '/services/calm-av',
              active: 'Calm AV',
            },
            {
              title: 'DHCP V4',
              icon: '',
              href: '/services/dhcp-v4',
              active: 'DHCP V4'
            },
            {
              title: 'DHCP V6',
              icon: '',
              href: '/services/dhcp-v6',
              active: 'DHCP V'
            },
            {
              title: 'Intrusion Detection',
              icon: '',
              href: '/services/intrusion-detection',
              active: 'Intrusion Detection'
            },
            {
              title: 'Proxy Web',
              icon: '',
              href: '/services/proxy-web',
              active: 'Proxy Web'
            }

          ],
          subMenuVisible: false,
        },
        {
          title: 'Reports',
          icon: 'mdi-chart-bar', active: 'Firewall',
          subItems: [
            {
              title: 'Health',
              icon: '',
              href: '/reports/health',
              active: 'Health',
            },
            {
              title: 'Insight',
              icon: '',
              href: '/reports/insight',
              active: 'Insight',
            },
            {
              title: 'Traffic',
              icon: '',
              href: '/reports/traffic',
              active: 'Traffic',
            }, {
              title: 'Event logs',
              icon: '',
              href: '/reports/event-logs',
              active: 'Event logs',
            }
          ],
          subMenuVisible: false,
        },
        {
          title: 'Subscription',
          icon: 'mdi-cash-sync',
          href: '/subscription', active: 'Firewall',
          subItems: [],
          subMenuVisible: false,
        },
      ]
    };
  },
  methods: {
    ...mapActions('auth', ['logout']),
    logout() {
      this.$store.dispatch('auth/logout');
    },
    showSubMenu(item) {
      // Close all submenus except for the clicked item
      this.items.forEach((menuItem) => {
        if (menuItem !== item) {
          menuItem.subMenuVisible = false;
        }
      });

      // Toggle the submenu visibility for the clicked item
      item.subMenuVisible = !item.subMenuVisible;

      // Navigate to the selected item's href
      if (item.href) {
        window.location.href = item.href;
      }
    },
    closeSidebar() {
      // Close the sidebar
      this.mini = !this.mini;

      // Close all submenus
      this.items.forEach((menuItem) => {
        menuItem.subMenuVisible = false;
      });
    },
  },

  computed: {
    ...mapState('auth', ['loggedIn', 'user']),
  },
};
</script>
<style>
.drawer_hover {
  &:hover {
    &::before {
      opacity: 1 !important;
    }

    .dms_teal--text,
    .text-wrap {
      color: white !important;
      opacity: 1 !important;
      z-index: 1 !important;
    }
  }

  &::before {
    -webkit-border-top-left-radius: 10px;
    -webkit-border-bottom-left-radius: 10px;
    -moz-border-radius-topleft: 10px;
    -moz-border-radius-bottomleft: 10px;
    border-top-left-radius: 10px;
    border-bottom-left-radius: 10px;
    left: 8px;
    background-color: #43aaf5 !important;
  }
}

.row-pointer {
  cursor: pointer;
}

.text-white-space {
  white-space: normal !important;
}

.drawer-width {
  max-width: 180px;
}

.dms-tabs {
  .v-tabs-bar {
    height: auto;
  }
}

.dms-tabs {
  .v-tab {
    max-width: none;
    font-size: 1rem;
    font-weight: 600;
    padding: 1.5rem;
  }
}

.dms-tabs {
  .v-tabs-slider-wrapper {
    height: 4px;
  }
}

.dms-tabs-border-bottom {
  border-bottom: 1px solid #e0e0e0;
}

.dms-menu-open {
  justify-content: center !important;
}

a:hover,
.v-list-item--active>.v-list-item__title {
  background-color: #FFC300;
}

a:hover .dms_teal--text,
.v-list-item--active .dms_teal--text {
  color: white !important;
}

.select-white-text .v-select__selection--comma {
  color: white;
}

.input-search {
  max-width: 250px;
}

.select-lang {
  max-width: 100px;
  max-height: 100px;
  margin-top: 50px;
}

.v-list-item--link:hover {
  background-color: #FFC300 !important;
}

.v-application--is-ltr .v-toolbar__content>.v-btn.v-btn--icon:first-child,
.v-application--is-ltr .v-toolbar__extension>.v-btn.v-btn--icon:first-child {
  margin-left: 180px;
}

.v-list-item.sub-menu-visible::before {
  content: "";
  position: absolute;
  left: 20%;
  top: 0;
  bottom: 0;
  width: 2px;
  background-color: hsla(47, 100%, 50%, 0.551);
}

.custom-a {
  text-decoration: none;
  color: inherit;
  display: inline-block;
  padding: 0;
  margin: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
  outline: none;
  border: none;
  background: none;
  font-family: inherit;
}

.custom-sub-a {
  margin-left: 50px;
  text-decoration: none;
  color: #000;
  display: inline-block;
  padding: 0;
  width: 100%;
  height: 1%;
  cursor: pointer;
  outline: none;
  border: none;
  background: none;
  font-family: inherit;
  display: flex;
  align-items: center;
}

.v-list-item {
  color: #ffffff;
  font-size: 16px;
  padding: 10px 20px;
}
</style>