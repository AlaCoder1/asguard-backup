<template>
  <v-row justify="center">
    <v-dialog v-model="isOpen" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="text-h5">{{ mode === 'create' ? 'Create' : 'Update' }} group</span>
          </v-card-title>
          <v-card-text>
            
            <v-container>
              <v-row>
                <!-- Group Modal -->
                <v-col cols="12">
                  <v-text-field label="Group name" v-model="formData.groupname"></v-text-field>
                </v-col>

                <v-col cols="12">
                  <v-text-field label="Description" v-model="formData.description"></v-text-field>
                </v-col>

                <v-col cols="12">
                  <label for="Deactivate User">add group in sudoers</label>
                  <input type="checkbox" id="Deactivate User" v-model="formData.sudoers" />
                </v-col>
                <!-- Group Modal -->
              </v-row>
            </v-container>

            <small>*indicates required field</small>
          </v-card-text>
          <v-card-actions>

            <v-spacer></v-spacer>
            <v-btn color="blue-darken-1" variant="text" type="submit">
              Save
            </v-btn>
            <v-btn color="blue-darken-1" variant="text" @click="closeModal">
              Close
            </v-btn>
          </v-card-actions>
        </v-card>
      </form>
    </v-dialog>
  </v-row>
</template>

<script>
export default {
  name: 'Modal_Group',
  props: {
    isOpen: {
      type: Boolean,
      required: true,
    },
    initialData: {
      type: Object,
      required: true,
    },
    mode: {
      type: String,
      required: true,
    },
 
  },
  data() {
    return {

      formData: { ...this.initialData },

    };
  },
  watch: {
    initialData(newValue) {
      // React to prop changes
      this.formData = newValue;
      console.log('Prop changed:', newValue);
    }
  },
  methods: {

    closeModal() {
      // this.resetForm();
      this.$emit('closeModal');
    },
    resetForm() {
      this.formData = {
        firstname: '',
        // Reset other form fields as needed
      };
      this.$refs.myForm.reset();
    },
    submitForm() {
      // Perform form submission actions here
      this.closeModal();
      // Emit an event to send form data to the parent component
      this.$emit('updateModalData', this.formData);

      console.log("submitForm :", this.formData)
    },
  },
  // components: {
  //   VTextField: Vue.extend(VTextField),
  // },
};
</script>