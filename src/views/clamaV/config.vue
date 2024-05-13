<template>
  <div class="mt-3">
    <v-row>
      <v-col cols="12">
        <h4>{{ $t("dhcpV4.generalInformation") }}</h4>
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
          v-model:proxyPort="state.proxyPort"
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
        <div class="flex center" style="margin-left: 15%">
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
    <v-row class="flex py-8 mb-1" style="margin-left: 15%">
      <v-col cols="4"> </v-col>
      <v-col>
        <div class="flex center">
          <VButton
            rounded
            outlined
            color="#213E9F"
            label-color="#ffffff"
            label="Make your updates"
            :isLarge="true"
            class="ml-2"
            @click="updateFreshclam"
          />
        </div>
      </v-col>
    </v-row>
    <v-row class="mb-10">
      <v-col cols="12">
        <updateFreshclam :freshclam="state.listFreshClam" />
      </v-col>
    </v-row>
    <v-snackbar
      :timeout="2000"
      v-model="state.snackbar"
      location="bottom right"
      :color="state.color"
    >
      {{ state.textAlert }}

      <template v-slot:actions> </template>
    </v-snackbar>
  </div>
</template>
<script>
import axios from "axios";
import VButton from "@/components/VButton.vue";
import updateFreshclam from "./component/updateFreshclam.vue";
import generalInfoPartie1 from "./component/generalInfoPartie1.vue";
import generalInfoPartie2 from "./component/generalInfoPartie2.vue";

import { onMounted, reactive } from "vue";
export default {
  components: {
    generalInfoPartie1,
    generalInfoPartie2,
    updateFreshclam,
    VButton,
  },

  setup() {
    const state = reactive({
      listFreshClam: null,
      id: "",
      snackbar: false,
      color: "",
      textAlert: "",
      // general partie 1
      enableService: false,
      enableTcpPort: false,
      enableFreshClamService: false,
      maxNumberThread: "",
      maxNumberQueued: "",
      idleTimeout: "",
      proxyPort: "",
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
    onMounted(() => {
      populate();
    });
    const populate = () => {
      const configAttribute =
        document.getElementById("app").attributes["config"].value;
      const configList = JSON.parse(configAttribute);

      configList.forEach((data) => {
        state.id = data.id;
        // general partie 1
        state.enableService = data.clamd_enabled;
        state.enableTcpPort = data.tcpport;
        state.enableFreshClamService = data.freshclam_enabled;
        state.maxNumberThread = data.maxthreads;
        state.maxNumberQueued = data.maxqueue;
        state.idleTimeout = data.idletimeout;
        state.proxyPort = data.proxyport;
        state.maxDirectoryRecursion = data.maxdirectoryrecursion;
        state.directorySymlinks = data.followdirectorysymlinks;
        state.regularFile = data.followfilesymlinks;
        state.cache = data.disablecache;
        state.portableExecutable = data.scanpe;
        state.linkingFormat = data.scanelf;
        state.brokenExecutables = data.alertbrokenexecutables;
        state.qle2 = data.scanole2;
        state.qle2Marcos = data.alertole2macros;
        state.pdfFiles = data.scanpdf;
        // general partie 2
        state.scanXmlDocs = data.scanxmldocs;
        state.scanHwp3 = data.scanhwp3;
        state.decodeMail = data.scanmail;
        state.maxScanSize = data.maxscansize;
        state.maxFileSize = data.maxfilesize;
        state.maxRecursion = data.maxrecursion;
        state.maxFiles = data.maxfiles;
        state.html = data.scanhtml;
        state.archive = data.scanarchive;
        state.encryptedArchive = data.alertencryptedarchive;
        state.freshclamLog = data.logverbose;
        state.freshclamDatabase = data.freshclamdatabasemirror;
        state.freshclamConnect = data.frechclamconnectiontimeout;
      });
    };

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

    const save = () => {
      console.log("state", state);
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      let payload = {
        logverbose: state.freshclamLog,
        tcpport: state.enableTcpPort,
        tcpsocket: "3310",
        maxthreads: state.maxNumberThread,
        maxqueue: state.maxNumberQueued,
        idletimeout: state.idleTimeout,
        maxdirectoryrecursion: state.maxDirectoryRecursion,
        followdirectorysymlinks: state.directorySymlinks,
        followfilesymlinks: state.regularFile,
        disablecache: state.cache,
        alertbrokenexecutables: state.brokenExecutables,
        alertencryptedarchive: state.encryptedArchive,
        alertole2macros: state.qle2Marcos,
        scanpe: state.portableExecutable,
        scanelf: state.linkingFormat,
        scanole2: state.qle2,
        scanpdf: state.pdfFiles,
        scanxmldocs: state.scanXmlDocs,
        scanhwp3: state.scanHwp3,
        scanmail: state.decodeMail,
        scanhtml: state.html,
        scanarchive: state.archive,
        maxscansize: state.maxScanSize,
        maxfilesize: state.maxFileSize,
        maxrecursion: state.maxRecursion,
        maxfiles: state.maxFiles,

        freshclamdatabasemirror: state.freshclamDatabase,
        frechclamconnectiontimeout: state.freshclamConnect,
        proxyport: state.proxyPort,
        clamd_enabled: state.enableService,
        freshclam_enabled: state.enableFreshClamService,
      };

      axios
        .put(`/clamaV/updateClamav/${state.id}`, payload)
        .then((response) => {
          if (response.status == "200") {
            state.snackbar = true;
            state.color = "success";
            state.textAlert = response.data.msg;

            setTimeout(() => {
              location.reload();
            }, 1000);
          }
        })
        .catch((i) => {
          state.snackbar = true;
          state.color = "red";
          state.textAlert = i.response.data.error;
        });
    };

    const updateFreshclam = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios
        .post("/clamaV/Updatefreshclam")
        .then((response) => {
          if (response.status == "200") {
            state.snackbar = true;
            state.color = "success";
            state.textAlert = response.data.message;
            state.listFreshClam = response.data.data;
          }
        })
        .catch((i) => {
          state.snackbar = true;
          state.color = "red";
          state.textAlert = i.response.data.error;
        });
    };

    return {
      state,
      populate,
      updateFreshclam,
      save,
    };
  },
};
</script>
