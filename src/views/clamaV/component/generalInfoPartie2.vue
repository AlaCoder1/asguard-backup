<template>
  <div class="ml-3 mr-3">
    <v-row class="mt-2">
      <v-col cols="4" class="mt-0">
        <label>XMLDOCS</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="scanXmlDocs" />
        <label class="ml-2"> Scan XMLDOCS</label>
      </v-col>
      <v-col cols="4" class="mt-0">
        <label>HWP3</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="scanHwp3" />
        <label class="ml-2"> Scan HWP3</label>
      </v-col>

      <v-col cols="4" class="mt-0">
        <label>mail files</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="decodeMail" />
        <label class="ml-2"> Decode mail files</label>
      </v-col>

      <v-col cols="4" class="mt-0">
        <label>HTML</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="html" />
        <label class="ml-2">Scan XMLDOCS</label>
      </v-col>

      <v-col cols="4" class="mt-0">
        <label>Archives</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="archive" />
        <label class="ml-2">Scan archives</label>
      </v-col>

      <v-col cols="4" class="mt-0">
        <label>Encrypted archive</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="encryptedArchive" />
        <label class="ml-2">Block encrypted archive</label>
      </v-col>

      <v-col cols="4" class="mt-5">
        <label>Max scan size</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          label="Max scan size"
          v-model="maxScanSize"
        ></v-text-field>
      </v-col>

      <v-col cols="4" class="mt-5">
        <label>Max file size</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          label="Max file size"
          v-model="maxFileSize"
        ></v-text-field>
      </v-col>
      <v-col cols="4" class="mt-5">
        <label>Max recursion</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          label="Max recursion"
          v-model="maxRecursion"
        ></v-text-field>
      </v-col>
      <v-col cols="4" class="mt-5">
        <label>Max files</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field label="Max files" v-model="maxFiles"></v-text-field>
      </v-col>

      <v-col cols="4" class="mt-0">
        <label>Freshclam log verbose</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="freshclamLog" />
        <label class="ml-2">Enable Freshclam log verbose</label>
      </v-col>

      <v-col cols="4" class="mt-5">
        <label>Freshclam database mirror</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          label="Freshclam database mirror"
          v-model="freshclamDatabase"
        ></v-text-field>
      </v-col>

      <v-col cols="4" class="mt-5">
        <label>Freshclam connect timeout</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          label="Freshclam connect timeout"
          v-model="freshclamConnect"
        ></v-text-field>
      </v-col>

      <!-- <v-col cols="4" class="mt-0">
        <label>Malware Expert Signatures</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="malwareExpert" />
        <label class="ml-2">Add Malware Expert Signatures</label>
      </v-col> -->

      <!-- <v-col cols="4" class="mt-0">
        <label>BLURL Signatures</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="blurlSign" />
        <label class="ml-2">Add BLURL Signatures</label>
      </v-col>

      <v-col cols="4" class="mt-0">
        <label>JURLBLA Signatures</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="jurlblaSign" />
        <label class="ml-2">Add JURLBLA Signatures</label>
      </v-col>

      <v-col cols="4" class="mt-0">
        <label>BOFHLand Signatures</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="bofhLandSign" />
        <label class="ml-2">Add BOFHLand Signatures</label>
      </v-col> -->
    </v-row>
  </div>
</template>
<script setup>
import { useVModels } from "@vueuse/core";

const props = defineProps([
  "scanXmlDocs",
  "scanHwp3",
  "decodeMail",
  "maxScanSize",
  "maxFileSize",
  "maxRecursion",
  "Max files",
  "html",
  "archive",
  "encryptedArchive",
  "freshclamLog",
  "freshclamDatabase",
  "freshclamConnect",
  // "malwareExpert",
  // "blurlSign",
  // "jurlblaSign",
  // "bofhLandSign",
]);
const emit = defineEmits([
  "update:scanXmlDocs",
  "update:scanHwp3",
  "update:decodeMail",
  "update:maxScanSize",
  "update:maxFileSize",
  "update:maxRecursion",
  "update:maxFiles",
  "update:html",
  "update:archive",
  "update:encryptedArchive",
  "update:freshclamLog",
  "update:freshclamDatabase",
  "update:freshclamConnect",
  // "update:malwareExpert",
  // "update:blurlSign",
  // "update:jurlblaSign",
  // "update:bofhLandSign",
]);
const {
  scanXmlDocs,
  scanHwp3,
  maxScanSize,
  decodeMail,
  maxFileSize,
  maxRecursion,
  maxFiles,
  html,
  archive,
  encryptedArchive,
  freshclamLog,
  freshclamDatabase,
  freshclamConnect,
  // malwareExpert,
  // blurlSign,
  // jurlblaSign,
  // bofhLandSign,s
} = useVModels(props, emit);
</script>
