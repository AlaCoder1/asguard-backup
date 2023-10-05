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
                  <v-text-field label="Username " v-model="formData.username"></v-text-field>
                </v-col>

                <v-col cols="6">
                  <v-text-field label="Password" type="password" v-model="formData.password"></v-text-field>
                </v-col>

                <v-col cols="6">
                  <v-text-field label="Confirm password" type="password" v-model="formData.password"></v-text-field>
                </v-col>

                <v-col cols="12">
                  <v-text-field label="Fullname " v-model="formData.fullname"></v-text-field>
                </v-col>

                <v-col cols="12">
                  <v-text-field label="Email for Ldap auth " v-model="formData.email"></v-text-field>
                </v-col>

                <v-col cols="12">
                  <v-autocomplete :items="['root', 'admin', 'user']" label="Role user"
                    v-model="formData.role"></v-autocomplete>
                </v-col>

                <v-col cols="12">
                  <v-autocomplete :items="groups" label="Assign to Group" multiple item-text="groupname" item-value="id"  v-model="formData.groups"
                    @change="handleGroupChange"></v-autocomplete>
                </v-col>

                <v-col cols="12">
                  <label for="Deactivate User">Deactivate User</label>
                  <input type="checkbox" id="Deactivate User" v-model="formData.deactivateUser" />
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
      required: true,
    },
    groups: {
      type: Array,
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
    handleGroupChange(selectedItems) {
      console.log('Selected Groups:', JSON.stringify(selectedItems));
      console.log('formData Groups:', JSON.stringify(this.formData.groups));
    },

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