<template>
  <h4>Cryptographic Settings</h4>
  <v-divider class="mt-3"></v-divider>
  <v-col cols="4">
    <label>TLS Authentification</label>
  </v-col>
  <v-col cols="8" class="mb-n6">
    <input type="checkbox" v-model="isEnableAuth" />

    <label class="ml-2"
      >Automatically generate a shared TLS authentication key</label
    >
    <v-textarea
      class="mt-3"
      v-model="tlsGenerate"
      label="shared TLS"
      variant="outlined"
      v-if="!isEnableAuth"
    ></v-textarea>
    <p
      class="error-feedback mb-5"
      v-if="props.errors.tlsGenerate.$errors.length"
    >
      {{ props.errors.tlsGenerate.$errors?.[0].$message }}
    </p>
  </v-col>

  <v-col cols="4" align-self="center">
    <label>Peer Certificate Authority*</label>
  </v-col>
  <v-col cols="8" class="mb-n6">
    <v-select
      label="Peer Certificate Authority"
      v-model="peerCertif"
      item-title="name"
      item-value="id"
      :items="state.mapedCertifAuth"
      return-object
    ></v-select>
    <p
      class="error-feedback mb-5"
      v-if="props.errors.peerCertif.$errors.length"
    >
      {{ props.errors.peerCertif.$errors?.[0].$message }}
    </p>
  </v-col>
  <v-col cols="4" align-self="center">
    <label>Serveur Certificate*</label>
  </v-col>
  <v-col cols="8" class="mb-n6">
    <v-select
      label="Serveur Certificate"
      v-model="serverCertif"
      item-title="name"
      item-value="id"
      :items="state.mapedCertifServer"
      return-object
    ></v-select>
    <p
      class="error-feedback mb-5"
      v-if="props.errors.serverCertif.$errors.length"
    >
      {{ props.errors.serverCertif.$errors?.[0].$message }}
    </p>
  </v-col>
  <v-col cols="4" align-self="center">
    <label>DH Parameters Length algorithm*</label>
  </v-col>
  <v-col cols="8" class="mb-n6">
    <v-select
      label="DH"
      v-model="dhParameters"
      :items="['2048', '3072', '4096', '8192']"
    ></v-select>
    <p
      class="error-feedback mb-5"
      v-if="props.errors.dhParameters.$errors.length"
    >
      {{ props.errors.dhParameters.$errors?.[0].$message }}
    </p>
  </v-col>
  <v-col cols="4" align-self="center">
    <label>Encryption algorithm*</label>
  </v-col>
  <v-col cols="8" class="mb-n6">
    <v-select
      label="Algorithm"
      v-model="encryptAlgo"
      :items="['AES-256-GCM', 'AES-128-GCM', 'CHACHA20-POLY1305']"
    ></v-select>
    <p
      class="error-feedback mb-5"
      v-if="props.errors.encryptAlgo.$errors.length"
    >
      {{ props.errors.encryptAlgo.$errors?.[0].$message }}
    </p>
  </v-col>
  <v-col cols="4" align-self="center">
    <label>Auth Digest Algorithm*</label>
  </v-col>
  <v-col cols="8" class="mb-n6">
    <v-select
      label="Auth Digest Algorithm"
      v-model="authDigest"
      item-title="name"
      item-value="slug"
      return-object
      :items="authDigestList"
    ></v-select>
    <p
      class="error-feedback mb-5"
      v-if="props.errors.authDigest.$errors.length"
    >
      {{ props.errors.authDigest.$errors?.[0].$message }}
    </p>
  </v-col>
  <!-- <v-col cols="4" align-self="center">
    <label>Hardware Crypto</label>
  </v-col> -->
  <!-- <v-col cols="8" class="mb-n6">
    <v-select
      label="Hardware Crypto"
      v-model="hardwareCrypto"
      item-title="name"
      item-value="slug"
      :items="[
        {
          name: 'No Hardware Crypto acceleration',
          slug: 'No Hardware Crypto',
        },

        { name: 'Intel RDRAND engine -RAND', slug: 'Intel RDRAND engine' },
      ]"
      return-object
    ></v-select>
  </v-col> -->
</template>

<script setup>
import axios from "axios";
import { onBeforeMount, reactive, ref } from "vue";
import { useVModels } from "@vueuse/core";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";

const props = defineProps([
  "errors",
  "tlsGenerate",
  "isEnableAuth",
  "peerCertif",
  "serverCertif",
  "dhParameters",
  "encryptAlgo",
  "authDigest",
  "hardwareCrypto",
]);
const emit = defineEmits([
  "update:isEnableAuth",
  "update:peerCertif",
  "update:serverCertif",
  "update:dhParameters",
  "update:encryptAlgo",
  "update:authDigest",
  "update:hardwareCrypto",
  "update:tlsGenerate",
]);
const {
  isEnableAuth,
  peerCertif,
  serverCertif,
  encryptAlgo,
  dhParameters,
  authDigest,
  hardwareCrypto,
  tlsGenerate,
} = useVModels(props, emit);

onBeforeMount(() => {
  getCertif();
  getAllCertAuth();
});

const state = reactive({
  authoritesData: null,
  certifData: null,
  mapedCertifAuth: [],
  mapedCertifServer: [],
});
const authDigestList = ref([
  {
    name: "SHA224",
    slug: "sha224",
  },
  {
    name: "SHA256",
    slug: "SHA256",
  },
  {
    name: "SHA384",
    slug: "SHA384",
  },

  {
    name: "SHA512",
    slug: "SHA512",
  },
  {
    name: "SHA3-224",
    slug: "SHA3-224",
  },
  {
    name: "SHA3-256",
    slug: "SHA3-256",
  },
  {
    name: "SHA3-384",
    slug: "SHA3-384",
  },
  {
    name: "SHA3-512",
    slug: "SHA3-512",
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

const getCertif = () => {
  const csrfToken = getCookie("csrftoken");
  axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

  axios.get("/certificates/getAllCertificates").then(
    (response) => {
      let mapedListCertif = response.data.filter(
        (i) => i.certificate_type === "server"
      );
      let mapedCertServer = mapedListCertif.map((i) => {
        return {
          id: i.id,
          name: i.name,
          is_private_key: i.is_private_key,
        };
      });
      state.mapedCertifServer = mapedCertServer.filter((i) => i.is_private_key);
    },
    (error) => {
      console.log(error);
    }
  );
};
const getAllCertAuth = () => {
  const csrfToken = getCookie("csrftoken");
  axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

  axios.get("/certificates/getAllCertAuth").then(
    (response) => {
      let mapedList = response.data.map((i) => {
        return {
          id: i.id,
          name: i.name,
          is_private_key: i.is_private_key,
        };
      });
      state.mapedCertifAuth = mapedList.filter((i) => i.is_private_key);
    },
    (error) => {
      console.log(error);
    }
  );
};
</script>

<style lang="scss"></style>
