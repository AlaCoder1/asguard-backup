<template>
  <h4>Cryptographic Settings</h4>
  <v-divider class="mt-2"></v-divider>
  <v-col cols="4">
    <label>TLS Authentication</label>
  </v-col>
  <v-col cols="8" class="mb-n6">
    <input type="checkbox" v-model="tlsGenerate" />
    <label class="ml-2"
      >Automatically generate a shared TLS authentication key</label
    >
  </v-col>
  <template v-if="!tlsGenerate">
    <v-col align-self="center" cols="4"> </v-col>
    <v-col align-self="center" cols="8" class="mb-n6">
      <v-textarea
        class="mt-3"
        v-model="sharedKey"
        label="TLS key"
        variant="outlined"
      ></v-textarea>
      <p
        class="error-feedback mb-5"
        v-if="props.errors.sharedKey.$errors.length"
      >
        {{ props.errors.sharedKey.$errors?.[0].$message }}
      </p>
    </v-col>
  </template>
  <v-col align-self="center" cols="4">
    <label>Peer Certificate Authority*</label>
  </v-col>
  <v-col align-self="center" cols="8" class="mb-n6">
    <v-select
      label="Peer Certificate Authority"
      v-model="peerCertificateAuthority"
      item-title="name"
      item-value="id"
      :items="mapedCertifAuth"
      return-object
    ></v-select>
    <p
      class="error-feedback mb-5"
      v-if="props.errors.peerCertificateAuthority.$errors.length"
    >
      {{ props.errors.peerCertificateAuthority.$errors?.[0].$message }}
    </p>
  </v-col>
  <v-col align-self="center" cols="4">
    <label>Client Certificate*</label>
  </v-col>
  <v-col align-self="center" cols="8" class="mb-n6">
    <v-select
      label="Client Certificate"
      v-model="clientCertificate"
      item-title="name"
      item-value="id"
      :items="clientCertificateList"
      return-object
    ></v-select>
    <p
      class="error-feedback mb-5"
      v-if="props.errors.clientCertificate.$errors.length"
    >
      {{ props.errors.clientCertificate.$errors?.[0].$message }}
    </p>
  </v-col>
  <v-col align-self="center" cols="4">
    <label>Encryption algorithm*</label>
  </v-col>
  <v-col align-self="center" cols="8" class="mb-n6">
    <v-select
      label="Encryption algorithm"
      v-model="encryptionAlgorithm"
      :items="encryptionAlgorithmList"
      item-title="name"
      item-value="slug"
      return-object
    ></v-select>
    <p
      class="error-feedback mb-5"
      v-if="props.errors.encryptionAlgorithm.$errors.length"
    >
      {{ props.errors.encryptionAlgorithm.$errors?.[0].$message }}
    </p>
  </v-col>
  <v-col align-self="center" cols="4">
    <label>Auth Digest Algorithm*</label>
  </v-col>
  <v-col align-self="center" cols="8" class="mb-n6">
    <v-select
      label="Auth Digest Algorithm"
      v-model="authDigestAlgorithm"
      item-title="name"
      item-value="slug"
      :items="authDigestAlgorithmList"
      return-object
    ></v-select>
    <p
      class="error-feedback mb-5"
      v-if="props.errors.authDigestAlgorithm.$errors.length"
    >
      {{ props.errors.authDigestAlgorithm.$errors?.[0].$message }}
    </p>
  </v-col>
  <v-col align-self="center" cols="4">
    <label>Hardware Crypto</label>
  </v-col>
  <v-col align-self="center" cols="8" class="mb-n6">
    <v-select
      label="Hardware Crypto"
      v-model="hardwareCrypto"
      :items="hardwareCryptoList"
      item-title="name"
      item-value="slug"
      return-object
    ></v-select>
    <!-- <p
      class="error-feedback mb-5"
      v-if="props.errors.hardwareCrypto.$errors.length"
    >
      {{ props.errors.hardwareCrypto.$errors?.[0].$message }}
    </p> -->
  </v-col>
</template>

<script setup>
import { useVModels } from "@vueuse/core";
import axios from "axios";
import { onBeforeMount, ref, reactive } from "vue";

const encryptionAlgorithmList = ref([
  {
    name: "AES-256-GCM",
    slug: "AES-256-GCM",
  },
  {
    name: "192-AES-GCM",
    slug: "192-AES-GCM",
  },
  {
    name: "AES-128-GCM",
    slug: "AES-128-GCM",
  },
  {
    name: "CHACHA20-POLY1305",
    slug: "CHACHA20-POLY1305",
  },
]);
const authDigestAlgorithmList = ref([
  {
    name: "BLAKE2b512",
    slug: "BLAKE2b512",
  },
  {
    name: "BLAKE2b256",
    slug: "BLAKE2b256",
  },
  {
    name: "SHA256",
    slug: "SHA256",
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
  {
    name: "SHA384",
    slug: "SHA384",
  },
  {
    name: "SHA512",
    slug: "SHA512",
  },
  {
    name: "SHA512-224",
    slug: "SHA512-224",
  },
  {
    name: "SHA512-256",
    slug: "SHA512-256",
  },
]);
const hardwareCryptoList = ref([
  {
    name: "No hardware Crypto acceleration",
    slug: "No hardware Crypto",
  },
  {
    name: "Intel RDRAND engine -RAND",
    slug: "Intel RDRAND engine -RAND",
  },
]);
const clientCertificateList = ref([]);
const mapedCertifAuth = ref([]);

const props = defineProps([
  "errors",
  "tlsGenerate",
  "sharedKey",
  "peerCertificateAuthority",
  "clientCertificate",
  "encryptionAlgorithm",
  "authDigestAlgorithm",
  "hardwareCrypto",
]);

const emit = defineEmits([
  "update:tlsGenerate",
  "update:peerCertificateAuthority",
  "update:serverCertif",
  "update:dhParameters",
  "update:encryptAlgo",
  "update:authDigest",
  "update:hardwareCrypto",
]);

const {
  tlsGenerate,
  sharedKey,
  peerCertificateAuthority,
  clientCertificate,
  encryptionAlgorithm,
  authDigestAlgorithm,
  hardwareCrypto,
} = useVModels(props, emit);

onBeforeMount(() => {
  getAllCertAuth();
  getAllClientCertif();
});

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

const getAllCertAuth = () => {
  const csrfToken = getCookie("csrftoken");
  axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

  axios.get("/certificates/getAllCertAuth").then(
    (response) => {
      let mapedList = response.data.map((i) => {
        return {
          id: i.id,
          name: i.name,
        };
      });
      mapedCertifAuth.value = mapedList;
    },
    (error) => {
      console.log(error);
    }
  );
};

const getAllClientCertif = () => {
  const csrfToken = getCookie("csrftoken");
  axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

  axios.get("/certificates/getAllCertificates").then(
    (response) => {
      let mapedListCertif = response.data.filter(
        (i) => i.certificate_type === "client"
      );

      clientCertificateList.value = mapedListCertif.map((i) => {
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
</script>
