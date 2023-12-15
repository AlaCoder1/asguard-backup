<template>
  <div style="margin-bottom: 150%; position: relative; top: -10px">
    <v-select
      :items="protocols"
      v-model="selectedProtocols"
      @change="onSelectChange"
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
    this.protocols = this.params.values ?? [];
    if (this.params.data.routage_type) {
      this.selectedProtocols = this.params.data.routage_type ?? "";
    }
    if (!this.params.data.routage_type) {
      // this.selectedProtocols = [this.protocols[0]];
    }
  },
  methods: {
    getValue() {
      return this.selectedProtocols;
    },
    agInit(params) {
      this.params = params;
      this.selectedProtocols = params.data.routage_type ?? "";
    },
    refresh(params) {
      this.params = params;
      this.selectedProtocols = params.data.routage_type ?? "";
    },
    onSelectChange() {
      this.params.node.setDataValue("routage_type", this.selectedProtocols);
    },
  },
};
</script>

<style scoped></style>
