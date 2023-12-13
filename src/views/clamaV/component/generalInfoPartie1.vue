<template>
  <div class="ml-3 mr-3">
    <v-row class="mt-2">
      <v-col cols="4" class="mt-0">
        <label>ClamaV service</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="enableService" />
        <label class="ml-2"> Enable service</label>
      </v-col>
      <v-col cols="4" class="mt-0">
        <label>Freshclam service</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="enableFreshClamService" />
        <label class="ml-2"> Enable freshclam service</label>
      </v-col>
      <v-col cols="4" class="mt-0">
        <label>TCP Port</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="enableTcpPort" />
        <label class="ml-2"> Enable TCP Port</label>
      </v-col>
      <v-col cols="4" class="mt-5">
        <label>Maximum number of thread running</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          label="Max Number Thread"
          v-model="maxNumberThread"
        ></v-text-field>
      </v-col>
      <v-col cols="4" class="mt-5">
        <label>Maximum number of queued items</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          label="Max Number Queued"
          v-model="maxNumberQueued"
        ></v-text-field>
      </v-col>
      <v-col cols="4" class="mt-5">
        <label>Idle timeout</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field label="Idle Timeout" v-model="idleTimeout"></v-text-field>
      </v-col>
      <v-col cols="4" class="mt-5">
        <label>Max directory recursion</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          label="Max directory recursion"
          v-model="maxDirectoryRecursion"
        ></v-text-field>
      </v-col>

      <v-col cols="4" class="mt-0">
        <label>directory symlinks</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="directorySymlinks" />
        <label class="ml-2">Follow directory symlinks</label>
      </v-col>
      <v-col cols="4" class="mt-0">
        <label>regular file symlinks</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="regularFile" />
        <label class="ml-2">Follow regular file symlinks</label>
      </v-col>
      <v-col cols="4" class="mt-0">
        <label>cache</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="cache" />
        <label class="ml-2">Disable cache</label>
      </v-col>
      <v-col cols="4" class="mt-0">
        <label>portable executable</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="portableExecutable" />
        <label class="ml-2">Scan portable executable</label>
      </v-col>
      <v-col cols="4" class="mt-0">
        <label>executable and linking format</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="linkingFormat" />
        <label class="ml-2">Scan executable and linking format</label>
      </v-col>

      <v-col cols="4" class="mt-0">
        <label>Broken executables</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="brokenExecutables" />
        <label class="ml-2">Detect broken executables</label>
      </v-col>
      <v-col cols="4" class="mt-0">
        <label>OLE2</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="qle2" />
        <label class="ml-2">Scan OLE2</label>
      </v-col>

      <v-col cols="4" class="mt-0">
        <label>OLE2 macros</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="qle2Marcos" />
        <label class="ml-2">Block OLE2 macros</label>
      </v-col>
      <v-col cols="4" class="mt-0">
        <label>PDF files</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="pdfFiles" />
        <label class="ml-2">Scan PDF files</label>
      </v-col>
    </v-row>
  </div>
</template>
<script setup>
import { useVModels } from "@vueuse/core";

const props = defineProps([
  "enableService",
  "enableFreshClamService",
  "enableTcpPort",
  "maxNumberThread",
  "maxNumberQueued",
  "idleTimeout",
  "maxDirectoryRecursion",
  "directorySymlinks",
  "regularFile",
  "cache",
  "portableExecutable",
  "linkingFormat",
  "brokenExecutables",
  "qle2",
  "qle2Marcos",
  "pdfFiles",
]);
const emit = defineEmits([
  "update:enableService",
  "update:enableFreshClamService",
  "update:enableTcpPort",
  "update:maxNumberThread",
  "update:maxNumberQueued",
  "update:idleTimeout",
  "update:maxDirectoryRecursion",
  "update:directorySymlinks",
  "update:regularFile",
  "update:cache",
  "update:portableExecutable",
  "update:linkingFormat",
  "update:brokenExecutables",
  "update:qle2",
  "update:qle2Marcos",
  "update:pdfFiles",
]);
const {
  enableService,
  enableFreshClamService,
  maxNumberThread,
  enableTcpPort,
  maxNumberQueued,
  idleTimeout,
  maxDirectoryRecursion,
  directorySymlinks,
  regularFile,
  cache,
  portableExecutable,
  linkingFormat,
  brokenExecutables,
  qle2,
  qle2Marcos,
  pdfFiles,
} = useVModels(props, emit);
</script>
