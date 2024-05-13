<template>
  <v-app id="inspire">
    <base-layout title="Personal informations">
      <template #content>
        <div>
          <div>
            <div class="d-flex justify-center mt-5">
              <v-badge
                location="bottom right"
                color="#205dc2"
                offsetX="20"
                offsetY="30"
                @click="launchFilePicker()"
                style="cursor: pointer"
              >
                <template v-slot:badge>
                  <span class="mdi mdi-pencil" v-if="imageURL"></span>
                  <span class="mdi mdi-camera-outline" v-else></span>
                </template>

                <v-avatar
                  size="150px"
                  v-ripple
                  v-if="!imageURL"
                  class="grey lighten-3 mb-3 bg-grey"
                  style="cursor: pointer"
                >
                  <!-- border: 1px solid rgb(33, 62, 159) -->
                  <span>
                    <svg
                      width="500px"
                      height="200px"
                      viewBox="0 0 24 24"
                      fill="white"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        opacity="0.4"
                        d="M12 22.01C17.5228 22.01 22 17.5329 22 12.01C22 6.48716 17.5228 2.01001 12 2.01001C6.47715 2.01001 2 6.48716 2 12.01C2 17.5329 6.47715 22.01 12 22.01Z"
                      />
                      <path
                        d="M12 6.93994C9.93 6.93994 8.25 8.61994 8.25 10.6899C8.25 12.7199 9.84 14.3699 11.95 14.4299C11.98 14.4299 12.02 14.4299 12.04 14.4299C12.06 14.4299 12.09 14.4299 12.11 14.4299C12.12 14.4299 12.13 14.4299 12.13 14.4299C14.15 14.3599 15.74 12.7199 15.75 10.6899C15.75 8.61994 14.07 6.93994 12 6.93994Z"
                        fill="white"
                      />
                      <path
                        d="M18.7807 19.36C17.0007 21 14.6207 22.01 12.0007 22.01C9.3807 22.01 7.0007 21 5.2207 19.36C5.4607 18.45 6.1107 17.62 7.0607 16.98C9.7907 15.16 14.2307 15.16 16.9407 16.98C17.9007 17.62 18.5407 18.45 18.7807 19.36Z"
                        fill="white"
                      />
                    </svg>
                  </span>
                </v-avatar>

                <v-avatar
                  size="150px"
                  v-ripple
                  v-else
                  class="mb-3"
                  style="cursor: pointer"
                >
                  <img :src="imageURL" alt="avatar" />
                </v-avatar>
              </v-badge>
            </div>
            <!-- <div
              v-if="imageURL && saved == false"
              class="d-flex justify-center"
            >
              <v-btn class="primary" @click="uploadImage" :loading="saving"
                >Save Avatar</v-btn
              >
            </div> -->

            <input
              type="file"
              ref="file"
              :name="uploadFieldName"
              @change="onFileChange($event.target.name, $event.target.files)"
              style="display: none"
            />
            <v-dialog v-model="errorDialog" max-width="300">
              <v-card>
                <v-card-text class="subheading">{{ errorText }}</v-card-text>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn @click="errorDialog = false" flat>Got it!</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </div>
          <v-row class="d-flex justify-center align-center mt-5">
            <v-col cols="4" class="mb-n6">
              <v-text-field label="Username System"></v-text-field>
            </v-col>
            <v-col cols="4" class="mb-n6">
              <v-text-field label="Address"></v-text-field>
            </v-col>
          </v-row>
          <v-row class="d-flex justify-center align-center mt-5">
            <v-col cols="4" class="mb-n6">
              <v-text-field label="Firstname"></v-text-field>
            </v-col>
            <v-col cols="4" class="mb-n6">
              <v-text-field label="Region"></v-text-field>
            </v-col>
          </v-row>
          <v-row class="d-flex justify-center align-center mt-5">
            <v-col cols="4" class="mb-n6">
              <v-text-field label="Phone number"></v-text-field>
            </v-col>
            <v-col cols="4" class="mb-n6">
              <v-text-field label="Country"></v-text-field>
            </v-col>
          </v-row>
          <v-row class="d-flex justify-center align-center mt-5">
            <v-col cols="4" class="mb-n6">
              <v-text-field label="Email Ldap"></v-text-field>
            </v-col>
            <v-col cols="4" class="mb-n6">
              <v-text-field label="Postal code"></v-text-field>
            </v-col>
          </v-row>
          <v-row class="d-flex justify-center align-center mt-5">
            <v-col cols="4" class="mb-n6">
              <v-text-field label="LastName"></v-text-field>
            </v-col>
            <v-col cols="4" class="mb-n6">
              <v-row>
                <v-col cols="8">
                  <label>Activate 2 factor authentification </label>
                </v-col>
                <v-spacer></v-spacer>
                <v-col cols="4" class="mb-n6">
                  <input type="checkbox" hide-details />
                  <label class="ml-1"> Activate OTP </label>
                </v-col>
              </v-row>
            </v-col>
          </v-row>

          <v-row class="flex py-8">
            <v-col>
              <div class="d-flex justify-center align-center">
                <VButton
                  rounded
                  outlined
                  color="#213E9F"
                  label-color="#ffffff"
                  label="Update"
                  :isLarge="true"
                />
              </div>
            </v-col>
          </v-row>

          <v-row class="d-flex justify-center align-center mt-0">
            <v-col cols="8" class="mb-n6">
              <v-text-field label="Old password"></v-text-field>
            </v-col>
          </v-row>

          <v-row class="d-flex justify-center align-center">
            <v-col cols="4" class="mb-n6">
              <v-text-field label="New passowrd"></v-text-field>
            </v-col>
            <v-col cols="4" class="mb-n6">
              <v-text-field label="Confirm New passowrd"></v-text-field>
            </v-col>
          </v-row>
          <v-row class="flex py-8 mb-10">
            <v-col>
              <div class="d-flex justify-center align-center">
                <VButton
                  rounded
                  outlined
                  color="#213E9F"
                  label-color="#ffffff"
                  label="Change Password"
                  :isLarge="true"
                />
              </div>
            </v-col>
          </v-row>
        </div>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import VButton from "@/components/VButton.vue";
import BaseLayout from "@/layouts/layout.vue";
export default {
  name: "Profile",
  components: {
    BaseLayout,
    VButton,
  },
  data: () => ({
    errorDialog: false,
    errorText: "",
    uploadFieldName: "file",
    maxSize: 1024,
    avatar: null,
    saving: false,
    saved: false,
    imageURL: null,
  }),

  methods: {
    uploadImage() {
      this.saving = true;
      setTimeout(() => this.savedAvatar(), 1000);
    },
    savedAvatar() {
      this.saving = false;
      this.saved = true;
    },
    //
    launchFilePicker() {
      this.$refs.file.click();
    },
    onFileChange(fieldName, file) {
    console.log('test')
      const { maxSize } = this;
      let imageFile = file[0];
      if (file.length > 0) {
        let size = imageFile.size / maxSize / maxSize;
        if (!imageFile.type.match("image.*")) {
          this.errorDialog = true;
          this.errorText = "Please choose an image file";
        } else if (size > 1) {
          this.errorDialog = true;
          console.log("this.errorDialog", this.errorDialog);
          this.errorText =
            "Your file is too big! Please select an image under 1MB";
        } else {
          let formData = new FormData();
          let imageURL = URL.createObjectURL(imageFile);
          formData.append(fieldName, imageFile);
          this.$emit("input", { formData, imageURL });
          this.imageURL = imageURL;
        }
      }
    },
  },
};
</script>
<style scoped lang="scss"></style>
