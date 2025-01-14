<template>
  <div class="mt-2 mr-5 d-flex justify-end">
    <span
      @click="openModal"
      style="font-size: 30px; color: #213e9f"
      class="mdi mdi-help-circle-outline cursor-pointer"
    ></span>
  </div>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm" class="scroller">
        <v-card>
          <v-card-title> </v-card-title>
          <v-card-text>
            <v-container>
              <div class="d-flex justify-space-between align-center mb-2">
                <span class="headline text-black"> HELP</span>
                <span
                  class="mdi mdi-close cursor-pointer text-black"
                  @click="state.openModal = false"
                ></span>
              </div>
              <div v-if="help" style="display: flex; justify-content: center">
                {{ help }}
              </div>
            </v-container>
          </v-card-text>

          <v-card-actions class="mt-3 actionBtn">
            <v-spacer></v-spacer>
          </v-card-actions>
        </v-card>
      </form>
    </v-dialog>
  </v-row>
</template>

<script>
import { reactive, toRefs } from "vue";

export default {
  props: {
    help: {
      type: Object,
      Array,
      required: true,
    },
  },

  setup(props) {
    const { help } = toRefs(props);

    const state = reactive({
      openModal: false,
    });

    const openModal = () => {
      state.openModal = true;
    };

    return {
      state,
      openModal,
    };
  },
};
</script>
<style>
.scroller {
  overflow: auto;
}
</style>
