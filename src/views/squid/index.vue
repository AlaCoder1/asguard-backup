<template>
  <v-app id="inspire">
    <base-layout title="Proxy" active-menu="Key_Pair">
      <template #content>
        <div class="mr-6 ml-3">
          <general_info />
          <list />
          <acl_list />
        </div>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import { reactive, onMounted } from "vue";
import BaseLayout from "@/layouts/layout.vue";
import general_info from "./component/general_info.vue";
import list from "./component/list.vue";
import acl_list from "./component/acl_list.vue";

export default {
  name: "Proxy",
  components: {
    BaseLayout,
    general_info,
    acl_list,
    list,
  },
  setup() {
    const state = reactive({});

    onMounted(() => {});

    const getCookie = (name) => {
      let cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === name + "=") {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    };

    return {
      state,
      getCookie,
    };
  },
};
</script>
