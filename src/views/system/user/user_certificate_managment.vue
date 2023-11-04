<template>
  <v-app id="inspire">
    <!-- <base-layout title="User & certificat management" >
            <template #content> -->
    <v-container class="axe-media-print-hide" fluid>
      <v-row>
        <v-col cols="12">
          <div>
            <v-row
              align="center"
              class="pr-4 axe-media-print-hide axe-sticky-three"
            >
              <v-col cols="6" style="height: 100%">
                <user-management :DataList="{ groups: groups, users: users }" />
              </v-col>

              <!-- <v-col cols="6" style="height: 100%;">
                                            <network-server-management :DataList="servers" />
                                        </v-col> -->

              <v-col cols="6" style="height: 100%">
                <group-management :DataList="groups" />
              </v-col>
            </v-row>

            <v-row
              align="center"
              style="overflow: hidden"
              class="pr-4 axe-media-print-hide axe-sticky-three mt-10"
            >
              <!-- <v-col cols="6" style="height: 100%;">
                                            <group-management  :DataList="groups" />
                                        </v-col> -->
              <v-col cols="6" style="height: 100%"> </v-col>
            </v-row>
          </div>
        </v-col>
      </v-row>
    </v-container>
    <!-- </template>
        </base-layout> -->
  </v-app>
</template>

<script>
import BaseLayout from "../../../layouts/layout.vue";
import UserManagement from "../user/components/user-management.vue";
import GroupManagement from "../user/components/group-management.vue";
// import NetworkServerManagement from "@/components/systemmanagment/network-server-management.vue";

export default {
  name: "DataManagment",
  components: {
    BaseLayout,
    UserManagement,
    // NetworkServerManagement,
    GroupManagement,
  },

  data() {
    return {
      tab: null,
      users: [],
      groups: [],
      servers: [],
    };
  },
  methods: {
    setData(Array_String) {
      const validJsonString = Array_String.replace(/'/g, '"')
        .replace(/True/g, "true")
        .replace(/False/g, "false")
        .replace(/None/g, "null");

      const parsedArray = JSON.parse(validJsonString);

      // this.users = parsedArray;
      // console.log("parsedarray :"+parsedArray)

      return parsedArray;
    },
    // ... other methods
  },
  // beforeMount: async function () {
  //   console.log(
  //     // "before mount data.users :" + JSON.stringify(this.$root.$data.users)
  //   );

  //   //   parsing users data
  //   let parsedData = this.setData(this.$root.$data.users);

  //   this.users = parsedData;
  //   //   parsing users data

  //   //   parsing groups data
  //   let parsedgroupsData = this.setData(this.$root.$data.groups);

  //   this.groups = parsedgroupsData;
  //   //   parsing groups data

  //   // //   parsing servers data
  //   let parsedserversData = this.setData(this.$root.$data.servers);

  //   this.servers = parsedserversData;
  //   // //   parsing servers data

  // },
  beforeMount: async function () {
    // console.log("before mount data.users :" + JSON.stringify(this.$root.$data.users));

    //   parsing users data
    let userData = document.getElementById("app").attributes["users"].value;
    let parsedData = this.setData(userData);

    this.users = parsedData;
    //   parsing users data

    //   parsing groups data
    let groupData = document.getElementById("app").attributes["groups"].value;
    let parsedgroupsData = this.setData(groupData);

    this.groups = parsedgroupsData;
    //   parsing groups data

    // //   parsing servers data
    let serversData =
      document.getElementById("app").attributes["servers"].value;
    let parsedserversData = this.setData(serversData);

    this.servers = parsedserversData;
    // //   parsing servers data
  },
};
</script>
