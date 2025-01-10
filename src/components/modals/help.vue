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
          <v-card-title>
            <!-- <span class="headline" v-if="modalMode === 'create'">
                {{ $t("sdwan.createNewArea") }}</span
              >
              <span class="headline" v-if="modalMode === 'edit'">
                {{ $t("sdwan.updateArea") }}</span
              > -->
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <h1>HELP</h1>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>

          <v-card-actions class="mt-3 actionBtn">
            <v-spacer></v-spacer>
            <!-- <v-btn
              color="indigo-darken-3"
              :rounded="true"
              large
              rounded
              outlined
              label-color="#213E9F"
              variant="outlined"
              @click="closeModal"
              class="mt-3 btn-add"
            >
              <span class="pr-3 pl-3" style="color: #213e9f">{{
                $t("buttons.close")
              }}</span>
            </v-btn>

            <v-btn
              large
              rounded
              outlined
              label-color="#213E9F"
              type="submit"
              color="indigo-darken-3"
              :rounded="true"
              variant="flat"
              class="mt-3 btn-add"
            >
              <span class="text-white pr-3 pl-3" v-if="modalMode === 'create'">
                {{ $t("buttons.create") }}</span
              >
              <span class="text-white pr-3 pl-3" v-if="modalMode === 'edit'">
                {{ $t("buttons.update") }}</span
              >
            </v-btn> -->
          </v-card-actions>
        </v-card>
      </form>
    </v-dialog>
  </v-row>
</template>

<script>
import { reactive } from "vue";

export default {
  setup(props) {
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
.error-feedback {
  color: red;
  font-size: 0.85em;
}
.actionBtn {
  justify-content: center;
}
.scroller {
  overflow: auto;
}
</style>
