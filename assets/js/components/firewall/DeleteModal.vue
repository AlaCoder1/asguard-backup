<template>
    <v-dialog id="deleteModal" title="Delete Confirmation">
        <p>Are you sure you want to delete this row?</p>
    </v-dialog>
</template>

<script>
export default {
    mounted() {
        this.$on('show', this.showModal);
    },
    methods: {
        showDeleteModal() {
            // Show the delete confirmation modal in this component
            this.$refs.deleteModal.show();
        },
        hideDeleteModal() {
            // Hide the delete confirmation modal in this component
            this.$refs.deleteModal.hide();
        },
        confirmDelete() {
            // Perform the delete action here
            this.$emit('delete');
        },

        showModal(title, message, rowData) {
            // Show the dialog and set title, message, and rowData
            // this.$refs.deleteModal.setTitle(title);
            // this.$refs.deleteModal.setMessage(message);
            // this.$refs.deleteModal.setRowData(rowData);
            // this.$refs.deleteModal.show(); // You may need to call a method that shows the dialog in your implementation.
        },
    },
};
</script>