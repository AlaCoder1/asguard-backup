<template>
  <div class="mt-3">
    <v-row>
      <v-col cols="12">
        <h4>General Information</h4>
        <v-divider></v-divider>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="6">
        <generalInfoPartie1
          v-model:enableService="state.enableService"
          v-model:enableTcpPort="state.enableTcpPort"
          v-model:enableFreshClamService="state.enableFreshClamService"
          v-model:maxNumberThread="state.maxNumberThread"
          v-model:maxNumberQueued="state.maxNumberQueued"
          v-model:idleTimeout="state.idleTimeout"
          v-model:maxDirectoryRecursion="state.maxDirectoryRecursion"
          v-model:directorySymlinks="state.directorySymlinks"
          v-model:regularFile="state.regularFile"
          v-model:cache="state.cache"
          v-model:portableExecutable="state.portableExecutable"
          v-model:linkingFormat="state.linkingFormat"
          v-model:brokenExecutables="state.brokenExecutables"
          v-model:qle2="state.qle2"
          v-model:qle2Marcos="state.qle2Marcos"
          v-model:pdfFiles="state.pdfFiles"
      /></v-col>
      <v-col cols="6"
        ><generalInfoPartie2
          v-model:scanXmlDocs="state.scanXmlDocs"
          v-model:scanHwp3="state.scanHwp3"
          v-model:maxScanSize="state.maxScanSize"
          v-model:decodeMail="state.decodeMail"
          v-model:maxFileSize="state.maxFileSize"
          v-model:maxRecursion="state.maxRecursion"
          v-model:maxFiles="state.maxFiles"
          v-model:html="state.html"
          v-model:archive="state.archive"
          v-model:encryptedArchive="state.encryptedArchive"
          v-model:freshclamLog="state.freshclamLog"
          v-model:freshclamDatabase="state.freshclamDatabase"
          v-model:freshclamConnect="state.freshclamConnect"
          v-model:malwareExpert="state.malwareExpert"
          v-model:blurlSign="state.blurlSign"
          v-model:jurlblaSign="state.jurlblaSign"
          v-model:bofhLandSign="state.bofhLandSign"
        />
      </v-col>
    </v-row>

    <v-row class="flex py-8 mb-5">
      <v-col cols="4"> </v-col>
      <v-col>
        <div class="ml-10 flex center">
          <VButton
            rounded
            outlined
            color="#213E9F"
            label-color="#ffffff"
            label="save"
            :isLarge="true"
            class="ml-2"
            @click="save"
          />
        </div>
      </v-col>
    </v-row>
    <v-row class="mb-2">
      <v-col cols="12">
        <h4>Updates freshclam</h4>
        <v-divider></v-divider>
      </v-col>
    </v-row>
    <v-row class="flex py-8 mb-1">
      <v-col cols="4"> </v-col>
      <v-col>
        <div class="ml-10 flex center">
          <VButton
            rounded
            outlined
            color="#213E9F"
            label-color="#ffffff"
            label="Make your updates"
            :isLarge="true"
            class="ml-2"
            @click="save"
          />
        </div>
      </v-col>
    </v-row>
    <v-row class="mb-10">
      <v-col cols="12">
        <updateFreshclam />
      </v-col>
    </v-row>
  </div>
</template>
<script>
import VButton from "@/components/VButton.vue";
import updateFreshclam from "./component/updateFreshclam.vue";
import generalInfoPartie1 from "./component/generalInfoPartie1.vue";
import generalInfoPartie2 from "./component/generalInfoPartie2.vue";

import { reactive } from "vue";
export default {
  components: {
    generalInfoPartie1,
    generalInfoPartie2,
    updateFreshclam,
    VButton,
  },

  setup() {
    const state = reactive({
      // general partie 1
      enableService: false,
      enableTcpPort: false,
      enableFreshClamService: false,
      maxNumberThread: "",
      maxNumberQueued: "",
      idleTimeout: "",
      maxDirectoryRecursion: "",
      directorySymlinks: false,
      regularFile: false,
      cache: false,
      portableExecutable: false,
      linkingFormat: false,
      brokenExecutables: false,
      qle2: false,
      qle2Marcos: false,
      pdfFiles: false,
      // general partie 2
      scanXmlDocs: false,
      scanHwp3: false,
      decodeMail: false,
      maxScanSize: "",
      maxFileSize: "",
      maxRecursion: "",
      maxFiles: "",
      html: false,
      archive: false,
      encryptedArchive: false,
      freshclamLog: false,
      freshclamDatabase: "",
      freshclamConnect: "",
      malwareExpert: false,
      blurlSign: false,
      jurlblaSign: false,
      bofhLandSign: false,
    });

    const save = () => {
      console.log("state", state);
    };

    return {
      state,
      save,
    };
  },
};
</script>
