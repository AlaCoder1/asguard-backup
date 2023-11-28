<template>
  <v-row justify="center">
    <!-- <v-dialog v-model="isOpen" persistent width="600"> -->
    <v-dialog  persistent width="600">

      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="text-h5">{{ mode === 'create' ? 'Create' : 'Update' }} server</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <!-- Network Modal -->

                <v-col cols="12">
                  <v-text-field label="Server " v-model="formData.servername"></v-text-field>
                </v-col>

                <v-col cols="12">
                  <v-autocomplete :items="[
                    { id: 1, name: 'LDAP' },
                    { id: 2, name: 'LDAP + time based one time password' },
                    { id: 3, name: 'Local + Mot de Passe à Usage Unique Temporel (TOTP)' },
                    { id: 4, name: 'LDAP' },
                    { id: 5, name: 'radius' }
                  ]" label="Type" v-model="formData.type" item-text="name" item-value="id"></v-autocomplete>
                </v-col>

                <v-col cols="12">
                  <v-text-field label="Hostname or IP address" v-model="formData.hostname"></v-text-field>
                </v-col>

                <v-col cols="12">
                  <v-autocomplete :items="['TCP', 'startTls', 'SSL-chifré']" label="Transport"
                    v-model="formData.transport"></v-autocomplete>
                </v-col>

                <v-col cols="12">
                  <v-autocomplete :items="['2', '3']" label="Protocol version"
                    v-model="formData.protocolVersion"></v-autocomplete>
                </v-col>

                <v-col cols="6">
                  <v-text-field label="Binding identities" v-model="formData.bindingIdentities"></v-text-field>
                </v-col>

                <v-col cols="6">
                  <v-text-field label="Password" type="password" v-model="formData.password"></v-text-field>
                </v-col>

                <v-col cols="12">
                  <v-autocomplete :items="['niveau', 'sous aborecessence complete']" label="Search Scope"
                    v-model="formData.searchScope"></v-autocomplete>
                </v-col>

                <v-col cols="12">
                  <v-text-field label="Base DN" v-model="formData.baseDN"></v-text-field>
                </v-col>

                <!-- Network Modal -->
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
  name: 'Modal',
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

    },
  },
  // components: {
  //   VTextField: Vue.extend(VTextField),
  // },
};
</script>