<template>
  <div class="demo-datetime-picker">
    <el-date-picker
      v-model="selectedProtocols"
      type="datetime"
      placeholder="End Time"
      format="DD/MM/YYYY hh:mm:ss"
      value-format="DD/MM/YYYY hh:mm:ss"
      @change="onSelectChange"
      size="large"
      class="w-100"
    />
  </div>
</template>

<script>
export default {
  name: "EndDateFieldRenderVue",
  data() {
    return {
      protocols: "",
      selectedProtocols: "",
    };
  },
  beforeMount() {
    this.protocols = this.params.values ?? "";
    if (this.params.data.end_time) {
      this.selectedProtocols = this.params.data.end_time ?? "";
    }
    if (!this.params.data.end_time) {
      this.selectedProtocols = this.protocols ?? "";
    }
  },
  methods: {
    getValue() {
      return this.selectedProtocols;
    },
    agInit(params) {
      this.params = params;
      this.selectedProtocols = params.data.end_time ?? "";
    },
    refresh(params) {
      this.params = params;
      this.selectedProtocols = params.data.end_time ?? "";
    },
    onSelectChange() {
      this.params.node.setDataValue("end_time", this.selectedProtocols);
    },
  },
};
</script>
<style>
.demo-datetime-picker {
  display: flex;
  width: 100%;
  padding: 0px;
  flex-wrap: wrap;
  justify-content: space-around;
  align-items: stretch;
}
.demo-datetime-picker .block {
  padding: 0px;
  text-align: center;
}
.line {
  width: 1px;
  background-color: var(--el-border-color);
}
</style>
