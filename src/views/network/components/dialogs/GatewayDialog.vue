<template>
 <v-dialog
 class="gateway-dialog"
        max-width="600px"
        :value="showGatewayDialog"
      >
        <v-card class="ml-3 mr-3">
          <v-card-title class="title-text">
            <span class="headline font-weight-bold">Add IPv4 Gateway</span>
          </v-card-title>
          <v-card-text>
            <v-form>
                <v-container>
              <v-row>
                <v-text-field
                  label="Enter Gateway Name"
                  v-model="gateway.gwname"
                ></v-text-field>
              </v-row>
              <v-row>
                <v-text-field
                  label="Enter Gateway IPV4"
                  clsas="w-100"
                  v-model="gateway.gwaddress"
                ></v-text-field>
              </v-row>
              <v-row>
                <v-text-field
                  label="Enter Description"
                  v-model="gateway.description"
                ></v-text-field
              ></v-row>
              <v-row>
                <input type="checkbox" v-model="gateway.default_aux" />
                <label class="ml-3">Default Gateway</label>
              </v-row>
              <v-row>
                <input type="checkbox" v-model="gateway.far_aux" />
                <label class="ml-3">Far Gateway</label>
              </v-row>
              <v-row>
                <input type="checkbox" v-model="gateway.multiwan_aux" />
                <label class="ml-3">Multi-WAN Gateway</label>
              </v-row>
            </v-container>
            </v-form>
          </v-card-text>
          <v-card-actions>
        <v-spacer></v-spacer>
               <VButton
          large
          rounded
          outlined
          color="#FFFF"
           label-color="#213E9F"
          label="cancel"
          :isLarge="true"
          @click="cancelGateway"
        />
        <VButton
          large
          rounded
          outlined
          color="#213E9F"
           label-color="#ffff"
          label="save"
          :isLarge="true"
           type="submit"
          :disabled="isFormInvalid()"
            @click="addGateway"
          class="ml-2"
          />
          </v-card-actions>
        </v-card>
      </v-dialog>
</template>


<script>
export default {
  props: {
    showGatewayDialog: Boolean,
  },
  data() {
    return {
      gateway: {
        gwname: '',
        gwaddress: '',
        description: '',
        default_aux: false,
        far_aux: false,
        multiwan_aux: false,
      },
    };
  },
  methods: {
    cancelGateway() {
      // Emit an event to inform the parent component to close the dialog
      this.$emit('close');
    },
    addGateway() {
      // Emit an event to inform the parent component to save the gateway data
      this.$emit('save', this.gateway);
    },
  },
};
</script>

<style scoped>

.gateway-dialog {
  position: fixed; overflow-x: unset; overflow-y: unset
}

</style>
```