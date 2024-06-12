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
    console.log("befor");
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
      console.log("valueGet****");
      return this.selectedProtocols;
    },
    // agInit(params) {
    //   console.log("agInit");
    //   this.params = params;
    //   this.selectedProtocols = params.data.type ?? "";
    // },
    // refresh(params) {
    //   console.log("refresh");

    //   this.params = params;
    //   this.selectedProtocols = params.data.type ?? "";
    // },
    // onSelectChange() {
    //   console.log("onSelectChange");

    //   this.params.node.setDataValue("type", this.selectedProtocols);
    // },
  },
};
</script>

<style scoped></style>
