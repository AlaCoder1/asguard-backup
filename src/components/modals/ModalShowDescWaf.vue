<template>
    <v-row justify="center">
        <v-dialog v-model="state.openModal" persistent width="600">
            <form ref="myForm" @submit.prevent="submitForm" class="scroller">
                <v-card>
                    <v-card-title>
                        <span class="headline">
                            Description</span>

                    </v-card-title>
                    <v-card-text>
                        <v-container>
                            <v-row>
                                <v-col cols="12" class="mb-n5 mb-1 mt-0">
                                    <v-card elevation="0">
                                        <v-card-item>
                                            {{ description ?? 'No Desrciption' }}
                                        </v-card-item>

                                    </v-card>
                                </v-col>
                            </v-row>
                        </v-container>
                    </v-card-text>
                    <v-card-actions class="mt-3 actionBtn">
                        <v-btn color="indigo-darken-3" large rounded outlined label-color="#213E9F" variant="flat"
                            @click="closeModal" class="mt-3 btn-add">
                            <span class="text-white pr-3 pl-3">{{
                                $t("buttons.close")
                            }}</span>
                        </v-btn>
                    </v-card-actions>
                </v-card>
            </form>
        </v-dialog>
    </v-row>
</template>

<script>
import { inject, toRefs, ref, reactive, watch } from "vue";

export default {

    props: {
        isOpen: {
            type: Boolean,
            required: true,
        },
        editRow: {
            type: Object,
            Array,
            required: true,
        },
        modalMode: {
            required: true,
        },
    },

    setup(props) {
        const emitter = inject("emitter");
        const { isOpen, editRow, modalMode } = toRefs(props);

        const description = ref(null);
        const state = reactive({});

        watch(
            () => isOpen.value,
            (val) => {
                state.openModal = val;
            }
        );
        watch(
            () => editRow.value,
            (val) => {
                populate(val);
            }
        );


        const populate = (data) => {
            if (modalMode.value === "show") {
                description.value = data.description
            }
        };

        const closeModal = () => {
            emitter.emit("closeModalSHOWDescription");
        };

        return {
            state,
            emitter,
            description,
            closeModal
        };
    },
};
</script>
<style>
.error-feedback {
    color: red;
    font-size: 0.85em;
}

.actionBtn {
    justify-content: center;
}

.scroller {
    overflow: auto;
}
</style>