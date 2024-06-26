<template>
  <v-dialog
    class="gateway-dialog"
    max-width="600px"
    v-model="showGatewayDialog"
    @close="cancelGateway"
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
          @click="addGateway"
          class="ml-2"
        />
      </v-card-actions>
    </v-card>

    <v-alert
      type="success"
      variant="outlined"
      elevation="2"
      class="ml-3"
      icon="mdi-check-circle-outline"
      style="width: 20%"
      border="top"
      v-if="showAlertGateway"
      :style="alertStyle"
    >
      Gateway saved successfully
    </v-alert>
  </v-dialog>
</template>

<script>
import VButton from "../../../../components/VButton.vue";

export default {
  name: "GatewayDialog",
  components: {
    VButton,
  },
  inject: ["emitter"],
  data() {
    return {
      gateway: {
        gwname: "",
        gwaddress: "",
        description: "",
        default_aux: false,
        far_aux: false,
        multiwan_aux: false,
      },
      showAlertGateway: false,
    };
  },
  methods: {
    cancelGateway() {
      // Emit an event to inform the parent component to close the dialog
      this.$emit("close");
    },
    addGateway() {
      console.log('tst')
      // Emit an event to inform the parent component to save the gateway data
      this.$emit("save", this.gateway);
      this.emitter.emit("gateway-object", this.gateway);
    },
  },
  components: { VButton },
};
</script>

<style scoped>
.gateway-dialog {
  position: fixed;
  overflow-x: unset;
  overflow-y: unset;
}
</style>
```
