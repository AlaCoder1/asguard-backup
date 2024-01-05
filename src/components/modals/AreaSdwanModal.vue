<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm" class="scroller">
        <v-card>
          <v-card-title>
            <span class="text-h5"> Create new Area</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Enter Area Name"
                    v-model="state.areaName"
                  ></v-text-field>
                  <p class="error-feedback mb-5" v-if="v$.areaName.$error">
                    {{ v$.areaName.$errors[0].$message }}
                  </p>
                </v-col>
              </v-row>

              <v-row class="mb-n6">
                <v-col>
                  <p class="ma-2">List WAN</p>
                </v-col>
                <v-col>
                  <p class="ma-2">Gateway</p>
                </v-col>
                <v-col cols="4">
                  <p class="ma-2">Weight</p>
                </v-col>
                <v-col cols="1">
                  <v-icon
                    title="Add Members"
                    class="mx-auto"
                    color="#213E9F"
                    @click="addRow"
                    icon="mdi mdi-plus-circle-outline"
                  ></v-icon>
                </v-col>
              </v-row>

              <v-row
                v-for="(row, index) in state.rows"
                :key="row.id"
                class="mt-0"
              >
                <v-col>
                  <!-- item-title="name"
                  item-value="id"
                  return-object
                  :items="props.mapedInterface" -->
                  <v-select v-model="row.name" label="List WAN"></v-select>
                </v-col>
                <v-col>
                  <v-text-field
                    v-model="row.description"
                    label="Gateway"
                  ></v-text-field>
                </v-col>
                <v-col>
                  <v-text-field
                    v-model="row.value"
                    label="Weight"
                  ></v-text-field>
                </v-col>
                <v-col cols="1" class="mt-4">
                  <v-icon
                    color="red"
                    @click="removeRow(index)"
                    icon="mdi mdi-delete-circle"
                  ></v-icon>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>

          <v-card-actions class="mt-3 actionBtn">
            <v-btn
              color="indigo-darken-3"
              :rounded="true"
              large
              rounded
              outlined
              label-color="#213E9F"
              variant="flat"
              @click="closeModal"
              class="mt-3 btn-add"
            >
              <span class="text-white pr-3 pl-3">Close</span>
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
              <span class="text-white pr-3 pl-3">Create</span>
            </v-btn>
          </v-card-actions>
        </v-card>
      </form>
    </v-dialog>

    <v-snackbar
      :timeout="2000"
      v-model="state.snackbar"
      location="bottom right"
      :color="state.color"
    >
      {{ state.textAlert }}
    </v-snackbar>
  </v-row>
</template>

<script>
import useValidate from "@vuelidate/core";
import { toRefs, watch, reactive, computed, inject } from "vue";
import { required, helpers } from "@vuelidate/validators";
export default {
  props: {
    isOpen: {
      type: Boolean,
      required: true,
    },
  },

  setup(props) {
    const emitter = inject("emitter");
    const { isOpen } = toRefs(props);

    const state = reactive({
      areaName: "",
      rows: [{ id: 1, name: "", description: "", value: "" }],
      nextRowId: 2,
    });

    watch(
      () => isOpen.value,
      (val) => {
        state.openModal = val;
      }
    );

    const closeModal = () => {
      emitter.emit("closeSdwanAreaModal");

      state.areaName = "";
      state.rows = [{ id: 1, name: "", description: "", value: "" }];
      state.nextRowId = 2;
    };
    const addRow = () => {
      state.rows.push({
        id: state.nextRowId++,
        name: "",
        description: "",
        value: "",
      });
    };
    const removeRow = (index) => {
      state.rows.splice(index, 1);
    };
    const submitForm = () => {
      console.log("state", state);
    };

    const rules = computed(() => {
      return {
        type: { required },

        areaName: {
          required,
          isValidkeyName: helpers.withMessage(
            `Champs can include only letters & Numbers & underscores & hyphens without space.`,

            helpers.regex(/^[A-Za-z0-9_\-]+$/)
          ),
        },
      };
    });

    const v$ = useValidate(rules, state);

    return {
      state,
      v$,
      emitter,
      submitForm,
      removeRow,
      addRow,
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
