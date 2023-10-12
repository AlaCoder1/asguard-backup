<template>
    <div class="custom-multi-select">
        <div class="selected-protocols" style="max-height: 60px; overflow-y: auto; overflow-x: hidden;">
            <v-select v-model="selectedValues" :items="availableValues" multiple chips class="custom-select" no-border
                hide-details item-text="text" @change="handleValueChange"></v-select>
        </div>
    </div>
</template>

<script>
export default {
    name: "MultiSelectEditor",
    data() {
        return {
            selectedValues: [],
            availableValues: [
                { value: "tcp", text: "TCP" },
                { value: "udp", text: "UDP" },
                { value: "icmp type echo-request", text: "ICMP Request" },
                { value: "icmp type echo-reply", text: "ICMP Reply" },
            ],
        };
    },
    methods: {
        handleValueChange() {
            this.params.node.setDataValue("protocol", this.selectedValues);
        },
    },
    created() {
        this.selectedValues = this.params.value;
    },
};
</script>

<style scoped>
.custom-multi-select {
    margin: 0;
    padding: 0;
    max-width: 180px;
    max-height: 20px;
    text-align: center;
}

.custom-select {
    width: 175px;
    max-width: 175px;
    border: none;
    border-radius: 0;
    font-size: 14px;
    max-height: 43px;
}

.custom-select .v-chip {
    background-color: hsla(47, 100%, 50%, 0.551);
    color: white;
    margin-right: 4px;
    white-space: nowrap;
}

.custom-select .v-list-item {
    font-size: 14px;
    max-height: 40px;
}
</style>
