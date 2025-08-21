<template>
  <div style="margin-bottom: 150%; position: relative; top: -10px">
    <v-select
      :items="protocols"
      v-model="selectedProtocols"
      @change="onSelectChange"
      :no-data-text="$t('certificat.certificatlist')"
    ></v-select>
  </div>
</template>

<script>
export default {
  name: "MultiSelectRenderVue",
  data() {
    return {
      protocols: [],
      selectedProtocols: "",
    };
  },
  beforeMount() {
    // this.protocols = this.params.values ?? [];
    if (this.params.data.type) {
      this.selectedProtocols = this.params.data.type ?? "";
    }
    if (!this.params.data.type) {
      // this.selectedProtocols = [this.protocols[0]];
    }
  },
  methods: {
    getValue() {
      return this.selectedProtocols;
    },
    // agInit(params) {
    //   this.params = params;
    //   this.selectedProtocols = params.data.type ?? "";
    // },
    // refresh(params) {

    //   this.params = params;
    //   this.selectedProtocols = params.data.type ?? "";
    // },
    // onSelectChange() {

    //   this.params.node.setDataValue("type", this.selectedProtocols);
    // },
  },
};
</script>

<style scoped></style>
