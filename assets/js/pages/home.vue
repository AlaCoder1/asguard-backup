<template>
    <v-app id="inspire">
        <base-layout
            title="home"
            active-menu="home"
        >
        <template #content>
            <!-- content -->
            <v-container
                class=" axe-media-print-hide"
                fluid
           >
                <v-row
                    align="center"
                    class=" pr-4 axe-media-print-hide axe-sticky-three"
                >
                    <v-col cols="12">
                        <v-tabs
                            v-model="tab"
                            flat
                        >
                            <v-tab
                                href="#user-management"
                            >
                                User Management
                            </v-tab>
                            <v-tab
                                href="#certificats-management"
                            >
                                Certificats Management
                            </v-tab>
                        </v-tabs>
                        <v-divider
                            style="width: 100%"
                        />
                    </v-col>
                </v-row>
                <v-row>
                    <v-col cols="12">
                        <v-tabs-items v-model="tab">
                            <v-tab-item
                                :value="'user-management'"
                                :transition="false"
                            >
                                <v-row
                                 align="center"
                                 class=" pr-4 axe-media-print-hide axe-sticky-three"
                                >
                    <v-col cols="6">
                      <v-table>
    <thead>
      <tr>
        <th>
          User
        </th>
        <th >
          Role
        </th>
        <th >
          Actions
        </th>
      </tr>
    </thead>
    <tbody>
      <tr
      >
        <td>tst</td>
        <td>role test </td>
        <td>action tst</td>

      </tr>
    </tbody>
  </v-table>


                    </v-col>
                     <v-col cols="6">
                     test 02
                    </v-col>
                    </v-row>
                                     <v-row
                                 align="center"
                                 class=" pr-4 axe-media-print-hide axe-sticky-three"
                                >
                    <v-col cols="6">
                    test 03
                    </v-col>
                     <v-col cols="6">
                     test 04
                    </v-col>
                    </v-row>
                            </v-tab-item>
                            <v-tab-item
                                :value="'certificats-management'"
                                :transition="false"
                            >
                                test 2
                            </v-tab-item>
                        </v-tabs-items>
                    </v-col>
                </v-row>
                 </v-container>
            </template>
        </base-layout>
    </v-app>
</template>

<script>
import BaseLayout from '@/pages/layout.vue';


export default {
    name: 'HomeComponent',
    components: {
        BaseLayout,
    },
    data() {
        return {
            users:'',
            test:[],
            tab: null,
        };
    },
    beforeMount: async function () {
        this.users= this.$root.$data.tab ;
        console.log("out data from django",this.users);
    }
};
</script>
