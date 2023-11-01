<template>
    <div class="custom-multi-select">
        <div class="selected-protocols" style="max-height: 39px; overflow-y: auto; overflow-x: hidden; max-width: 186px; min-width: 186px;">
            <v-select multiple chips class="custom-select" no-border hide-details item-text="text" item-value="value"
                v-model="selectedValues" :items="protocols" :deletable-chips="true" :close-on-select="true"
                :return-object="true" :menu-props="{ maxHeight: '300px' }" :rules="[v => !!v || 'Item is required']"
                @popup:show="isPopup" @change="onSelectChange"></v-select>
        </div>
    </div>
</template>

<script>
export default {
    name: 'CustomRichSelect',
    data() {
        return {
            selectedValues: [],
            protocols: [], // You can keep the data property name as "protocols"
        }
    },
    computed: {},
    mounted() {
        this.protocols = this.params.values;
        if (this.params.data.protocol) {
            this.selectedValues = this.params.data.protocol;
        }
        if (!this.params.data.protocol) {
            this.selectedValues = [this.protocols[0]];
        }
    },
    methods: {
        getValue() {
            console.log("getValue");
            return this.selectedValues;
        },
        isPopup() {
            return true;
        },
        isCancelBeforeStart() {
            return false;
        },
        isCancelAfterEnd() {
            return false;
        },
        agInit(params) {
            this.params = params;
            this.selectedValues = params.data.protocol;
        },
        refresh(params) {
            this.params = params;
            this.selectedValues = params.data.protocol;
        },
        onSelectChange() {
            this.params.node.setDataValue("protocol", this.selectedValues);
        },
    },
   watch: {
        selectedValues(newValues) {
            const hasEchoRequest = newValues.includes("icmp type echo-request");
            const hasEchoReply = newValues.includes("icmp type echo-reply");

            if (newValues.length >= 2) {
                // When both "icmp type echo-request" and "icmp type echo-reply" are selected, set the value to "icmp"
                if (hasEchoRequest && hasEchoReply) {
                    this.protocols = ["tcp", "udp", "icmp"] // You can keep the data property name as "protocols"
                }
                // Restore the available protocols
                this.protocols = ["tcp", "udp", "icmp"];
            } else {
                // Restore the available protocols
                this.protocols = this.params.values;
            }

            console.log("selectedValues", this.selectedValues);
        },
    },

};
</script>

<style scoped>
.ag-grid-select {
    display: inline-block;
    width: 175px;
    /* Set the fixed width here */
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: #fff;
}

.selected-protocols {
    max-height: 39px;
    min-height: 39px;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 8px;
    max-width: 175px;
    min-width: 175px;
}

.custom-select {
    width: 100%;
    max-width: 175px;
    font-size: 14px;
    border: none;
    border-radius: 0;
    border-bottom: 1px solid #ccc;
    padding: 0;
    min-height: auto;
    margin: 0;
}

.custom-select .v-chip {
    background-color: hsla(47, 100%, 50%, 0.551);
    color: white;
    margin-right: 2px;
    white-space: nowrap;
}

.custom-select .v-list-item {
    font-size: 14px;
    max-height: 40px;
    padding: 0 8px;
}

.custom-select .v-select__selection {
    border: none;
    padding: 0;
    min-height: auto;
}

.custom-select[data-v-0adf8998] {
    width: 175px;
    height: 40px;
    font-size: 14px;
    border: none;
    border-radius: 0;
}

.v-select__slot {
    /* position: relative; */
    align-items: center;
    display: flex;
    max-width: 90%;
    min-width: 90%;
    width: 90%;
}

</style>