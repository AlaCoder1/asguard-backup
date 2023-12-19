<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="text-h5"> Edit Black List </span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Username"
                    v-model="state.formData.userName"
                  ></v-text-field>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.formData.userName.$error"
                  >
                    {{ v$.formData.userName.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Category"
                    v-model="state.formData.category"
                  ></v-text-field>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.formData.category.$error"
                  >
                    {{ v$.formData.category.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    label="URL List"
                    v-model="state.formData.urlList"
                    multiple
                    item-title="name"
                    item-value="slug"
                    return-object
                    :items="[
                      { name: 'Facebook', slug: 'fb' },
                      { name: 'Youtube', slug: 'YB' },
                      { name: 'TikTok', slug: 'tik' },
                    ]"
                  ></v-select>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.formData.urlList.$error"
                  >
                    {{ v$.formData.urlList.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-textarea
                    class="mt-3"
                    v-model="state.formData.description"
                    label="Description"
                    variant="outlined"
                  ></v-textarea>
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
              <span class="text-white pr-3 pl-3">{{
                modalMode === "create" ? "Create" : "Edit"
              }}</span>
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
import { required } from "@vuelidate/validators";
import { reactive, computed, toRefs, watch, inject } from "vue";
import VButton from "@/components/VButton.vue";
export default {
  name: "Modal_User_Squid",
  components: {
    VButton,
  },
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
      type: Object,
      Array,
      String,
      required: true,
    },
  },
  setup(props) {
    const { isOpen, editRow, modalMode } = toRefs(props);
    const emitter = inject("emitter");
    const state = reactive({
      formData: {
        password: "",
        confirm_password: "",
        userName: null,
        category: "",
        description: "",
        urlList: [],
      },
      openModal: false,
      textAlert: "",
      color: "",
      snackbar: false,
    });
    const rules = computed(() => {
      return {
        formData: {
          userName: { required },
          category: { required },
          urlList: { required },
        },
      };
    });

    const v$ = useValidate(rules, state);

    watch(
      () => isOpen.value,
      (val) => {
        state.openModal = val;
      }
    );
    watch(
      () => editRow.value,
      (val) => {
        console.log("val*", val);
      }
    );
    watch(
      () => modalMode.value,
      (val) => {
        console.log("modalMode*s", val);
      }
    );
    const closeModal = () => {
      emitter.emit("closeAclListModal");
    };

    return {
      state,
      v$,
      emitter,
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
</style>
