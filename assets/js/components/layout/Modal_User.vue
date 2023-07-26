<template>
  <v-row justify="center">
    <v-dialog v-model="isOpen" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="text-h5">{{ mode === 'create' ? 'Create' : 'Update' }} user</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <!-- User Modal -->

                <v-col cols="12">
                  <v-text-field label="Username " v-model="formData.servername"></v-text-field>
                </v-col>

                <v-col cols="6">
                  <v-text-field label="Password" type="password" v-model="formData.password"></v-text-field>
                </v-col>

                <v-col cols="6">
                  <v-text-field label="Confirm password" type="password" v-model="formData.password"></v-text-field>
                </v-col>

                <v-col cols="12">
                  <v-text-field label="Fullname " v-model="formData.servername"></v-text-field>
                </v-col>

                <v-col cols="12">
                  <v-text-field label="Email for Ldap auth " v-model="formData.servername"></v-text-field>
                </v-col>

                <v-col cols="12">
                  <v-autocomplete :items="['LDAP', 'LDAP + time based one time password', 'Local + Mot de Passe à Usage Unique Temporel (TOTP)	'
                    , 'radius']" label="Role user" v-model="formData.type"></v-autocomplete>
                </v-col>

                <!-- User Modal -->
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
  name: 'Modal_User',
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
      required: true
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