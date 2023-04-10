<template>
    <div class="footer-bg">
        <p class="c-o">DMSsdwan © 2019-2023 Numeryx.</p>
    </div>
</template>

<script>
export default {
    name: 'FooterComponent',
    data: () => ({
        active: true,
    }),
};
</script>

<style lang="sass">
    .c-o {
        color:#FFFFFF;
        text-align:center;
    }
    .footer-bg{
        position: fixed;
        left: 0;
        bottom: 0;
        margin-bottom:1%;
        width: 100%;
        background-color: #042439;
        color: white;
        text-align: center;
    }
</style>
