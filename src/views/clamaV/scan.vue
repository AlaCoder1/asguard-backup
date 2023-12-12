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
        <img
          src="../../assets/images/Fichier 2icone-Sasyx-supp 1.svg"
          class="ml-10"
        />
        <h5 class="title mr-2">Full virus scan</h5>
        <span class="mb-5 subtitle">Scan your entire device</span><br />
        <VButton
          rounded
          outlined
          color="#213E9F"
          label-color="#ffffff"
          label="Scan now"
          class="ml-2 mt-5 w-80"
          @click="save"
        />
      </div>

      <div id="middlebox" class="mb-5">
        <img
          src="../../assets/images/Fichier 1icone-Asguard-scanFolder 1.svg"
        />
        <h5 class="title mr-2">Targeted scan</h5>
        <span class="mb-5 subtitle">Scan spécific file or directory</span>
        <div style="text-align: center; position: relative; left: 27%">
          <v-text-field
            v-model="path"
            density="compact"
            variant="solo"
            class="w-50 mt-7"
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
        </div>
      </div>

      <div id="rightbox">
        <img src="../../assets/images/Group 182.svg" />
        <h5 class="title mr-2">Full virus scan</h5>
        <span class="mb-5 subtitle" style="margin-left: 16px"
          >Scan your remote agent</span
        >
        <br />
        <VButton
          rounded
          outlined
          color="#213E9F"
          label-color="#ffffff"
          label="Scan now"
          :isLarge="true"
          class="ml-5 mt-5"
          @click="save"
        />
      </div>
    </div>

    <v-row class="mb-10" id="newRow">
      <v-col cols="12">
        <updateFreshclam />
      </v-col>
    </v-row>
  </div>
</template>
<script>
import { ref } from "vue";
import VButton from "@/components/VButton.vue";
import updateFreshclam from "./component/updateFreshclam.vue";
import generalInfoPartie1 from "./component/generalInfoPartie1.vue";
import generalInfoPartie2 from "./component/generalInfoPartie2.vue";
export default {
  components: {
    generalInfoPartie1,
    generalInfoPartie2,
    updateFreshclam,
    VButton,
  },

  setup() {
    const path = ref("");
    const save = () => {
      console.log("Path : ", path.value);
    };

    return {
      save,
      path,
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
  width: 35%;
  height: 280px;
  text-align: center;
}

#rightbox {
  float: right;
  width: 25%;
  position: relative;
  right: 9%;
  height: 280px;
}
#newRow {
  clear: both;
}
</style>
