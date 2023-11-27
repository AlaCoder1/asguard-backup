<template>
  <v-select
    multiple
    chips
    no-border
    hide-details
    item-text="text"
    item-value="value"
    :items="protocols"
    v-model="selectedProtocols"
    @change="onSelectChange"
  ></v-select>
</template>

<script>
export default {
  name: "MultiSelectRenderVue",
  data() {
    return {
      protocols: [],
      selectedProtocols: [],
    };
  },
  beforeMount() {
    this.protocols = this.params.values;
    if (this.params.data.protocol) {
      this.selectedProtocols = this.params.data.protocol;
    }
    if (!this.params.data.protocol) {
      this.selectedProtocols = [this.protocols[0]];
    }
  },
  methods: {
    getValue() {
      return this.selectedProtocols;
    },
    agInit(params) {
      this.params = params;
      this.selectedProtocols = params.data.protocol;
    },
    refresh(params) {
      this.params = params;
      this.selectedProtocols = params.data.protocol;
    },
    onSelectChange() {
      this.params.node.setDataValue("protocol", this.selectedProtocols);
    },
  },
  watch: {
    selectedProtocols(newValues) {
      const hasEchoRequest = newValues.includes("icmp type echo-request");
      const hasEchoReply = newValues.includes("icmp type echo-reply");

      if (newValues.length >= 2) {
        // When both "icmp type echo-request" and "icmp type echo-reply" are selected, set the value to "icmp"
        if (hasEchoRequest && hasEchoReply) {
          this.protocols = ["tcp", "udp", "icmp"]; // You can keep the data property name as "protocols"
        }
        // Restore the available protocols
        this.protocols = ["tcp", "udp", "icmp"];
      } else {
        // Restore the available protocols
        this.protocols = this.params.values;
      }
    },
  },
};
</script>

<style scoped></style>
