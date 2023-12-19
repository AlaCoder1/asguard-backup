<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModalResult" persistent width="600">
      <form>
        <v-card>
          <v-card-title class="card-title">
            <span class="text-h5">Résultat de Scan</span>
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
                justify="center"
                style="
                  border-radius: 10px;
                  background-color: #213e9f;
                  padding: 4px;
                "
              >
                <v-col cols="6" style="background-color: #213e9f">
                  <span class="resultTitle" style="color: #fff"
                    >Known viruses </span
                  ><br />
                  <span class="resultTitle" style="color: #fff"
                    >Engine version</span
                  ><br />
                  <span class="resultTitle" style="color: #fff"
                    >Scanned directories</span
                  ><br />
                  <span class="resultTitle" style="color: #fff"
                    >Scanned files</span
                  ><br />
                  <span class="resultTitle" style="color: #fff"
                    >Infected files </span
                  ><br />
                  <span class="resultTitle" style="color: #fff"
                    >Data scanned </span
                  ><br />
                  <span class="resultTitle" style="color: #fff">Data Read</span
                  ><br />
                  <span class="resultTitle" style="color: #fff">Time</span
                  ><br />
                  <span class="resultTitle" style="color: #fff">Start date</span
                  ><br />
                  <span class="resultTitle" style="color: #fff">End date</span>
                </v-col>
                <v-col cols="6" style="background-color: #fff">
                  <span class="resultTitle" style="color: #213e9f">Test</span
                  ><br />
                  <span class="resultTitle" style="color: #213e9f">Test</span
                  ><br />
                  <span class="resultTitle" style="color: #213e9f">Test</span
                  ><br />
                  <span class="resultTitle" style="color: #213e9f">Test</span
                  ><br />
                  <span class="resultTitle" style="color: #213e9f">Test</span
                  ><br />
                  <span class="resultTitle" style="color: #213e9f">Test</span
                  ><br />
                  <span class="resultTitle" style="color: #213e9f">Test</span
                  ><br />
                  <span class="resultTitle" style="color: #213e9f">Test</span
                  ><br />
                  <span class="resultTitle" style="color: #213e9f">Test</span
                  ><br />
                  <span class="resultTitle" style="color: #213e9f">Test</span>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              :rounded="true"
              class="mt-3 btn-add text-white"
              color="blue-darken-1"
              variant="text"
              type="submit"
            >
              <span class="text-white">Save</span>
            </v-btn>
            <v-btn
              :rounded="true"
              class="mt-3 btn-add text-white"
              color="blue-darken-1"
              variant="text"
            >
              <span class="text-white">Close</span>
            </v-btn>
          </v-card-actions>
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
    //   rowData: {
    //     type: Object,
    //     required: true,
    //   },
  },

  setup(props) {
    const { isOpen } = toRefs(props);
    const emitter = inject("emitter");
    const state = reactive({ openModalResult: false });

    watch(
      () => isOpen.value,
      (val) => {
        state.openModalResult = val;
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
