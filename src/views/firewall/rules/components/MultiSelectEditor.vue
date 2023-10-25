<template>
    <div class="custom-multi-select">
        <div class="selected-protocols" style="max-height: 39px; overflow-y: auto; overflow-x: hidden;">
            <v-select multiple chips class="custom-select" no-border hide-details item-text="text" item-value="value"
                v-model="selectedValues" :items="protocols" :deletable-chips="true" :close-on-select="true"
                :return-object="true" :menu-props="{ maxHeight: '300px' }" :rules="[v => !!v || 'Item is required']"
                @change="onSelectChange"></v-select>
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
    computed: {
    },
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
            if (newValues.length >= 2) {
                this.protocols = ["tcp", "udp", "icmp"];
            } else if (newValues.includes("icmp type echo-request") && newValues.includes("icmp type echo-reply")) {
                this.selectedValues = ["icmp"];
            } else {
                this.protocols =this.params.values;
            }
        }
    },
};
</script>


<style scoped>
.ag-grid-select {
    display: inline-block;
    width: 180px;
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
</style>