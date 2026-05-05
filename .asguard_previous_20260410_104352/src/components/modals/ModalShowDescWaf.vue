<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="700">
      <form ref="myForm" @submit.prevent="submitForm">
        <!-- <v-card elevation="16" class="mx-auto my-8">
          <v-card-text> -->
        <v-container>
          <v-row>
            <v-col cols="12" class="mb-n5 mb-1 mt-0">
              <v-card elevation="16" style="background-color: #193286">
                <v-card-title>
                  <div class="d-flex justify-space-between align-center">
                    <span class="headline text-white"> Description</span>
                    <span
                      class="mdi mdi-close cursor-pointer text-white"
                      @click="closeModal"
                    ></span>
                  </div>
                </v-card-title>
                <v-card-item
                  class="text-subtitle-1 text-white w-100 mb-10 mt-1"
                >
                  {{ description ?? $t("noDesc") }}
                </v-card-item>
                <!-- <v-card-actions class="mt-1 actionBtn"> </v-card-actions> -->
              </v-card>
            </v-col>
          </v-row>
        </v-container>
        <!-- </v-card-text>  -->
        <!-- <v-card-actions class="mt-3 actionBtn"> -->
        <!-- <v-btn
              color="indigo-darken-3"
              large
              rounded
              outlined
              label-color="#213E9F"
              variant="flat"
              @click="closeModal"
              class="mt-3 btn-add"
            >
              <span class="text-white pr-3 pl-3">{{
                $t("buttons.close")
              }}</span>
            </v-btn> -->
        <!-- </v-card> -->
      </form>
    </v-dialog>
  </v-row>
</template>

<script>
import { inject, toRefs, ref, reactive, watch } from "vue";

export default {
  props: {
    isOpen: {
      type: Boolean,
      required: true,
    },
    editRow: {
      type: Object,
      Array,
      required: true,
    },
    modalMode: {
      required: true,
    },
  },

  setup(props) {
    const emitter = inject("emitter");
    const { isOpen, editRow, modalMode } = toRefs(props);

    const description = ref(null);
    const state = reactive({});

    watch(
      () => isOpen.value,
      (val) => {
        state.openModal = val;
      }
    );
    watch(
      () => editRow.value,
      (val) => {
        populate(val);
      }
    );

    const populate = (data) => {
      if (modalMode.value === "show") {
        let lang = localStorage.getItem("lang");
        description.value =
          lang === "en" ? data.description_english : data.description_french;
      }
    };

    const closeModal = () => {
      emitter.emit("closeModalSHOWDescription");
    };

    return {
      state,
      emitter,
      description,
      closeModal,
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
