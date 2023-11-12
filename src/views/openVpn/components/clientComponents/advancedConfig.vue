<template>
  <div class="mt-3">
    <h4 class="mt-6">Advanced Configuration</h4>
    <v-divider class="mt-2"></v-divider>
    <v-row class="mt-2">
      <v-col cols="4">
        <label>Verbosity level</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select
          label="Verbosity level"
          v-model="verbosityLevel"
          :items="verbosityLevelList"
          item-title="name"
          item-value="slug"
          return-object
        ></v-select>
      </v-col>
    </v-row>
  </div>
  <div class="mt-2">
    <h4 class="mt-6">Remote server</h4>
    <v-divider class="mt-2"></v-divider>
    <v-row class="mt-2">
      <v-col cols="4">
        <label>Server</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select
          label="Server"
          v-model="remoteServer"
          :items="serverList"
          item-title="name"
          item-value="id"
          return-object
        ></v-select>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { useVModels } from "@vueuse/core";
import axios from "axios";
import { onBeforeMount, ref } from "vue";

const props = defineProps(["verbosityLevel", "remoteServer"]);

const emit = defineEmits(["update:verbosityLevel", "update:remoteServer"]);

const { verbosityLevel, remoteServer } = useVModels(props, emit);

const serverList = ref([]);
const verbosityLevelList = ref([
  {
    name: "0 (none)",
    slug: "0",
  },
  {
    name: "1 (default)",
    slug: "1",
  },
  {
    name: "2",
    slug: "2",
  },
  {
    name: "3",
    slug: "3",
  },
  {
    name: "4",
    slug: "4",
  },
  {
    name: "5",
    slug: "5",
  },
  {
    name: "6",
    slug: "6",
  },
  {
    name: "7",
    slug: "7",
  },
  {
    name: "8",
    slug: "8",
  },
  {
    name: "9",
    slug: "9",
  },
  {
    name: "10",
    slug: "10",
  },
  {
    name: "11",
    slug: "11",
  },
]);

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

const getServer = () => {
  const csrfToken = getCookie("csrftoken");
  axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

  axios.get("/openvpn/getAllServerOpenvpn").then(
    (response) => {
      serverList.value = response.data.map((i) => {
        return {
          id: i.id,
          name: i.name,
        };
      });
    },
    (error) => {
      console.log(error);
    }
  );
};

onBeforeMount(() => {
  getServer();
});
</script>
