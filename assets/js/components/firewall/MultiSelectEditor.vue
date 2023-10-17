<template>
    <div class="custom-multi-select">
        <div class="selected-protocols" style="max-height: 60px; overflow-y: auto; overflow-x: hidden;">
            <v-select v-model="selectedValues" :items="availableValues" multiple chips class="custom-select" no-border
                hide-details item-text="text" @change="handleValueChange" @input="handleSelectedProtocolsChange"></v-select>
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
   created() {
        // Set the initial value of selectedValues when the component is created
        const initialSelectedValues = this.params.node.data.protocol.map(value => {
            const matchingItem = this.availableValues.find(item => item.value === value);
            if (matchingItem) {
                return { value: matchingItem.value, text: matchingItem.text.toUpperCase() };
            } else {
                return { value: value, text: value.toUpperCase() }; // Create an object with value and text properties
            }
        });
       // Transform the initialSelectedValues to the desired format
        this.selectedValues = initialSelectedValues.map(item => ({
            value: item.value.trim(), // Remove leading and trailing spaces
            text: item.text.trim().toUpperCase() // Remove leading and trailing spaces and convert to uppercase
        }));
        console.log(this.selectedValues);
    },

    methods: {
        handleValueChange() {
            this.params.node.setDataValue("protocol", this.selectedValues);
        },
        handleSelectedProtocolsChange() {
            // Emit a custom event with the selected protocols
            this.$emit('protocols-selected', this.selectedProtocols);
        },
    },
    watch: {
        selectedValues(newValues) {
            if (newValues.length >= 2) {
                this.availableValues = [
                    { value: "tcp", text: "TCP" },
                    { value: "udp", text: "UDP" },
                    { value: "icmp", text: "ICMP" },
                ];
            } else if (newValues.includes("icmp type echo-request") && newValues.includes("icmp type echo-reply")) {
                // If both ICMP Request and Reply are selected, update to just "icmp"
                this.selectedValues = ["icmp"];
            }
        }
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
