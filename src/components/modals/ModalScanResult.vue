<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModalResult" persistent width="600">
      <form>
        <v-card>
          <v-card-title class="card-title">
            <span class="text-h5">{{ $t("clamaV.scanResult") }}</span>
            <v-spacer></v-spacer>
            <i
              class="mdi mdi-close mt-1"
              style="color: #213e9f; font-size: 20px; cursor: pointer"
              @click="closeModal"
            ></i>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row
                class="mb-5"
                justify="center"
                style="
                  border-radius: 10px;
                  background-color: #213e9f;
                  padding: 4px;
                "
              >
                <v-col cols="6" style="background-color: #213e9f">
                  <span class="resultTitle" style="color: #fff"
                    >{{ $t("clamaV.knownViruses") }} </span
                  ><br />
                  <span class="resultTitle" style="color: #fff">{{
                    $t("clamaV.engineVersion")
                  }}</span
                  ><br />
                  <span class="resultTitle" style="color: #fff">{{
                    $t("clamaV.scannedDirectories")
                  }}</span
                  ><br />
                  <span class="resultTitle" style="color: #fff">{{
                    $t("clamaV.scannedFiles")
                  }}</span
                  ><br />
                  <span class="resultTitle" style="color: #fff"
                    >{{ $t("clamaV.infectedFiles") }} </span
                  ><br />
                  <span class="resultTitle" style="color: #fff"
                    >{{ $t("clamaV.dataScanned") }} </span
                  ><br />
                  <span class="resultTitle" style="color: #fff">{{
                    $t("clamaV.dataRead")
                  }}</span
                  ><br />
                  <span class="resultTitle" style="color: #fff">{{
                    $t("clamaV.time")
                  }}</span
                  ><br />
                  <span class="resultTitle" style="color: #fff">{{
                    $t("clamaV.startDate")
                  }}</span
                  ><br />
                  <span class="resultTitle" style="color: #fff">{{
                    $t("clamaV.endDate")
                  }}</span>
                </v-col>
                <v-col cols="6" style="background-color: #fff">
                  <span class="resultTitle" style="color: #213e9f">{{
                    state.known
                  }}</span
                  ><br />
                  <span class="resultTitle" style="color: #213e9f">{{
                    state.engine
                  }}</span
                  ><br />
                  <span class="resultTitle" style="color: #213e9f">{{
                    state.directories
                  }}</span
                  ><br />
                  <span class="resultTitle" style="color: #213e9f">{{
                    state.scannedFiles
                  }}</span
                  ><br />
                  <span class="resultTitle" style="color: #213e9f">{{
                    state.infectedFiles
                  }}</span
                  ><br />
                  <span class="resultTitle" style="color: #213e9f">{{
                    state.dataScanned
                  }}</span
                  ><br />
                  <span class="resultTitle" style="color: #213e9f">{{
                    state.dataRead
                  }}</span
                  ><br />
                  <span class="resultTitle" style="color: #213e9f">{{
                    state.time
                  }}</span
                  ><br />
                  <span class="resultTitle" style="color: #213e9f">{{
                    state.startDate
                  }}</span
                  ><br />
                  <span class="resultTitle" style="color: #213e9f">{{
                    state.endDate
                  }}</span>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
        </v-card>
      </form>
    </v-dialog>
  </v-row>
</template>
<script>
import { reactive, toRefs, watch, inject } from "vue";

export default {
  name: "Modal_Scan_Result",

  props: {
    isOpen: {
      type: Boolean,
      required: true,
    },
    rowData: {
      type: Object,
      required: true,
    },
  },

  setup(props) {
    const { isOpen, rowData } = toRefs(props);
    // const { isOpen } = toRefs(props);
    const emitter = inject("emitter");
    const state = reactive({
      openModalResult: false,
      known: "",
      engine: "",
      directories: "",
      scannedFiles: "",
      infectedFiles: "",
      dataScanned: "",
      dataRead: "",
      time: "",
      startDate: "",
      endDate: "",
    });

    watch(
      () => isOpen.value,
      (val) => {
        state.openModalResult = val;
      }
    );
    watch(
      () => rowData.value,
      (val) => {
        state.known = val.known_viruses;
        state.engine = val.engine_version;
        state.directories = val.scanned_directories;
        state.scannedFiles = val.scanned_files;
        state.infectedFiles = val.infected_files;
        state.dataScanned = `${val.data_scanned.value} ${val.data_scanned.unit}`;
        state.dataRead = val.known_viruses;
        state.time = `${val.scan_time.value} ${val.scan_time.unit}`;
        state.startDate = val.start_date;
        state.endDate = val.end_date;
      }
    );

    const closeModal = () => {
      emitter.emit("closeModalScan");
    };

    return {
      state,
      emitter,
      closeModal,
    };
  },
};
</script>
<style>
.resultTitle {
  font-family: Nunito;
  font-size: 20px;
  font-weight: 400;
  line-height: 27px;
  letter-spacing: 0em;
  text-align: left;
}
.card-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
