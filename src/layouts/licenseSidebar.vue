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
        class="row-pointer asguard_primary_dark mb-2"
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
                    ><i :class="item.icon"></i
                  ></span>
                  <span class="ml-7 sidebarTitle">{{
                    $t(item.title)
                  }}</span></v-list-item
                >

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
            <v-list-item @click="showSubMenu(item)">
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
      items: [
        {
          title: "license",
          icon: "mdi mdi-cash-sync",
          href: "/asguard/subscription",
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
.v-navigation-drawer__content {
  width: 100%;
}
</style>
