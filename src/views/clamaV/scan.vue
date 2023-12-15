<template>
  <div class="mt-3">
    <v-row>
      <v-col cols="12">
        <h4>Virus Scan</h4>
        <v-divider></v-divider>
      </v-col>
    </v-row>

    <div id="boxes" class="mt-10">
      <div id="leftbox">
        <!-- <img
          src="../../assets/images/Fichier 2icone-Sasyx-supp 1.svg"
          style="margin-bottom: -7px"
          
        />
        <h5 class="title mr-2">Full virus scan</h5>
        <span class="mb-5 subtitle">Scan your entire device</span><br />

        <v-btn
          rounded
          outlined
          color="#213E9F"
          label-color="#ffffff"
          class="ml-2 mt-5 btn-scan"
          size="large"
          @click="save"
        >
          <span>Scan now</span>
        </v-btn> -->
      </div>

      <div id="middlebox" class="mb-5">
        <!-- <img
          src="../../assets/images/Fichier 1icone-Asguard-scanFolder 1.svg"
        />
        <h5 class="title mr-2">Targeted scan</h5>
        <span class="mb-5 subtitle">Scan spécific file or directory</span>
        <div style="text-align: center; position: relative; left: 25%">
          <v-text-field
            v-model="path"
            density="compact"
            variant="solo"
            class="w-75 mt-5"
            label="Enter specific file or directory path "
            single-line
            rounded
            hide-details
          >
            <template v-slot:append-inner>
              <v-icon
                color="#213E9F"
                icon="mdi mdi-skull-scan-outline"
                @click="save"
              />
            </template>
          </v-text-field>
        </div> -->

        <img
          src="../../assets/images/Fichier 2icone-Sasyx-supp 1.svg"
          style="margin-bottom: -7px"
        />
        <h5 class="title mr-2">Full virus scan</h5>
        <span class="mb-5 subtitle">Scan your entire device</span><br />

        <v-btn
          rounded
          outlined
          color="#213E9F"
          label-color="#ffffff"
          class="ml-2 mt-5 btn-scan"
          size="large"
          @click="save"
        >
          <span>Scan now</span>
        </v-btn>
      </div>

      <div id="rightbox">
        <!-- <img src="../../assets/images/Group 182.svg" />
        <h5 class="title mr-2">Full virus scan</h5>
        <span class="mb-6 subtitle" style="margin-left: 16px"
          >Scan your remote agent</span
        >
        <br />
        <v-btn
          rounded
          outlined
          color="#213E9F"
          label-color="#ffffff"
          class="ml-4 mt-6 btn-scan"
          size="large"
          @click="save"
        >
          <span>Scan now</span>
        </v-btn> -->
      </div>
    </div>

    <v-row class="mb-10" id="newRow">
      <v-col cols="12">
        <!-- <updateFreshclam /> -->
      </v-col>
    </v-row>

    <ModalScanResult :isOpen="state.isModalOpen" :rowData="state.rowData" />
  </div>
</template>
<script>
import { reactive, onMounted,inject } from "vue";
import VButton from "@/components/VButton.vue";
import updateFreshclam from "./component/updateFreshclam.vue";
import generalInfoPartie1 from "./component/generalInfoPartie1.vue";
import generalInfoPartie2 from "./component/generalInfoPartie2.vue";
import ModalScanResult from "@/components/modals/ModalScanResult.vue";
export default {
  components: {
    generalInfoPartie1,
    generalInfoPartie2,
    updateFreshclam,
    ModalScanResult,
    VButton,
  },

  setup() {
    const emitter = inject("emitter");

    const state = reactive({
      rowData: {},
      isModalOpen: false,
    });
    const save = () => {
      // state.rowData = response.data;
      state.isModalOpen = true;
    };
    onMounted(() => {
      emitter.on("closeModalScan", () => {
        state.isModalOpen = false;
      });
    });
    return {
      save,
      state,
      emitter,
    };
  },
};
</script>
<style>
.title {
  font-family: Nunito;
  font-size: 30px;
  font-weight: 400;
  line-height: 41px;
  letter-spacing: 0em;
  color: #213e9f;
}
.subtitle {
  font-family: Nunito;
  font-size: 16px;
  font-weight: 400;
  line-height: 27px;
  letter-spacing: 0em;
  text-align: center;
  color: #213e9f;
}

#leftbox {
  float: left;
  width: 25%;
  text-align: center;
  height: 280px;
}

#middlebox {
  float: left;
  width: 50%;
  height: 280px;
  text-align: center;
}

#rightbox {
  float: right;
  width: 25%;
  position: relative;
  right: 3%;
  height: 280px;
}
#newRow {
  clear: both;
}
.btn-scan {
  height: 43px;
  width: 183px;
  font-family: "Nunito-Regular", Helvetica;
  left: 0;
  letter-spacing: 0;
  line-height: normal;
  text-align: center;
  text-transform: capitalize;
}
</style>
