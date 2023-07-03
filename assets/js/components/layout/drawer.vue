<template>
  <div>
    <v-toolbar flat class="dms_blue_dark dms-media-print-hide dms-sticky" height="70">
      <v-toolbar-title class="dms-font-size-three white--text ml-8">
        <img src="../../../images/logoDMS.png" height="100" />
      </v-toolbar-title>
      <v-spacer />
      <v-select v-model="lang" :items="['frensh', 'english']" solo background-color="#042439"
        class="select-white-text select-lang" />
      <v-text-field background-color="white" rounded class="ml-3 input-search" placeholder="Search"
        hide-details></v-text-field>
      <v-menu offset-y>
        <template v-slot:activator="{ on }">
          <v-avatar class="ml-3 mr-3" size="30" v-on="on">
            <img src="../../../images/user.png" alt="Account logo">
          </v-avatar>
        </template>
        <v-list>
          <v-list-item>
            <v-list-item-title>Profile</v-list-item-title>
          </v-list-item>
          <v-list-item>
            <v-list-item-title>Settings</v-list-item-title>
          </v-list-item>
          <v-list-item>
            <v-list-item-title>Logout</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
      <span style="color: white;">johndoe@example.com</span>
    </v-toolbar>
    <v-navigation-drawer :mini-variant.sync="mini" class="global-drawer" permanent app>
      <v-app-bar dense flat class="row-pointer dms_white" @click.stop="mini = !mini">
        <v-app-bar-nav-icon color="dms_teal" />
        <v-toolbar-title class="dms_teal--text text-body-2">
          Réduire le menu
        </v-toolbar-title>
      </v-app-bar>
      <v-list dense>
        <v-list-item v-for="item in items" :key="item.title" link>
          <v-list-item-icon v-if="mini">
            <span :class="[item.icon, 'icon-size-two axe_teal--text']"></span>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-icon v-if="!mini" class="dms-menu-open">
              <span :class="[item.icon, 'icon-size-two axe_teal--text']"></span>
            </v-list-item-icon>
            <v-list-item-title class="dms_teal--text item">{{ item.title}}</v-list-item-title>
          </v-list-item-content>
          <v-list-item-action>
            <v-icon v-if="item.subItems.length > 0" @click.stop="toggleSubMenu(item)">
              {{ item.showSubMenu ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
            </v-icon>
          </v-list-item-action>
        <v-menu v-if="item.subItems.length >= 1" v-model="item.showSubMenu" :close-on-content-click="false" offset-y
          :nudge-width="290" min-width="200px" :return-value.sync="item.showSubMenu" transition="scale-transition"
          offset-x max-width="200px"
          max-height="909px" min-height="909px" background-color="white" :top="mini ? true : false">
            <template v-slot:activator="{ on }"
            :class="{ 'drawer_hover': !mini, 'axe-active-menu': activeMenu === item.active }">
              <v-list-item v-on="on">
                <v-list-item-content id='overlay'
                  :class="{ 'text-white-space': !mini, 'dms_teal--text': activeMenu === item.active }">
                  <v-list-item-icon v-if="!mini" class="dms-menu-open">
                    <span :class="[item.icon, 'icon-size-two axe_teal--text']"></span>
                  </v-list-item-icon>
                  <v-list-item-title class="dms_teal--text item">{{ item.title }}</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </template>
            <v-list dense>
              <v-list-item v-for="(subItem, subIndex) in item.subItems" :key="subIndex" @click="selectSubItem(subItem)">
                <v-list-item-content>
                  <v-list-item-icon v-if="!mini" class="dms-menu-open">
                    <span :class="[subItem.icon, 'icon-size-two axe_teal--text']"></span>
                  </v-list-item-icon>
                  <v-list-item-title class="dms_teal--text item">{{ subItem.title }}</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-menu>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
  </div>
</template>

<script>
export default {
  name: 'DrawerComponent',
  props: {
    activeMenu: {
      type: String,
      required: true,
      default: null,
    },
  },
  data() {
    return {
      drawer: true,
      mini: false,
      lang: null,
      items: [
        {
          title: 'Dashboard', icon: 'icon-home', href: '/', active: 'home',
          subItems: [],
          showSubMenu: false,
          mouseOverSubMenu: false,
        },
        {
          title: 'System', icon: 'icon-trending', href: '/system', active: 'system',
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
              href: '/system/user-certificat-management',
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
              href: '/system/settings',
              active: 'Settings',
            }

          ],
          showSubMenu: false,
          mouseOverSubMenu: false,
        },
        {
          title: 'Interfaces', icon: 'icon-business', href: '/interfaces', active: 'interfaces',
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
              title: 'LAN / WAN',
              icon: '',
              href: '/interfaces/lan-wan',
              active: 'LAN / WAN',
            }, {
              title: 'Settings',
              icon: '',
              href: '/interfaces/settings',
              active: 'Settings',
            }
          ],
        },
        {
          title: 'Firewall', icon: 'icon-business', href: '/firewall', active: 'Firewall',
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
        },
        {
          title: 'Services', icon: 'icon-business', href: '/services', active: 'Firewall',
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
              href: '/services/open-vpn',
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
        },
        {
          title: 'Reports', icon: 'icon-business', href: '/reports', active: 'Firewall',
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
        },
        {
          title: 'Subscription', icon: 'icon-business', href: '/subscription', active: 'Firewall',
          subItems: [],
        },
      ]
    };
  },
  methods: {
    showSubMenu(item, event) {
      item.showSubMenu = true;

      if (event.relatedTarget && event.relatedTarget.parentElement === event.currentTarget) {
        // If the user is already hovering over the sub-menu, don't hide it when leaving the list item
        item.mouseOverSubMenu = true;
      }
    },
    hideSubMenu(item, event) {
      item.showSubMenu = false;
      console.log(event);
      //if (event.relatedTarget && event.relatedTarget.parentElement !== event.currentTarget) {
      // If the user is already hovering over the sub-menu, don't hide it when leaving the list item
      item.mouseOverSubMenu = false;
      //}

    },
  }
};
</script>

<style lang="sass">
// src/sass/main.scss
@import '~vuetify/src/styles/styles.sass';

// You need to map-merge your new SASS variables
$grid-breakpoints: map-merge($grid-breakpoints, (
  xs: 0,
  sm: 476px,
  md: 668px,
  lg: 1000px,
  xl: 1300px
));

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

.axe-active-menu {
  &::before {
    opacity: 1 !important;
  }
  .v-list-item__icon,
  .v-list-item__content {
    .dms_teal--text,
    .text-wrap {
      color: white !important;
      opacity: 1 !important;
      z-index: 1 !important;
    }
  }
}

.row-pointer {
  cursor: pointer;
}

.text-white-space {
  white-space: normal !important;
}

.drawer-width {
  max-width: 120px;
}

.dms-tabs {
  .v-tabs-bar {
    height: auto;
  }
}

.item {
  height: 25px;
  display: flex;
  justify-content: center;
  align-items: center;
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
.v-list-item--active > .v-list-item__title {
  background-color: #ffc300;
}

a:hover .dms_teal--text,
.v-list-item--active .dms_teal--text {
  color: white !important;
}

.select-white-text .v-select__selection--comma {
  color: white;
}

.select-lang {
  max-width: 110px;
  margin-top: 2% !important;
}

.input-search {
  max-width: 250px;
}

.v-menu__content {
  background-color: white;
  min-width: 200px;
  top: 71px !important;
  left: 257px;
  z-index: 10;
  height: 909px;
  min-height: 909px;
}

#overlay {
    position: absolute;
    z-index:100;
}

.v-list-item--link:hover {
  background-color: #ffc300 !important;
}


</style>
