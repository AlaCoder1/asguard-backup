<template>
    <div class="footer-bg">
        <span class="c-o">DMSsdwan © 2019-2023 Numeryx.</span>
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
        margin-bottom:0px;
    }
    .footer-bg{
        position: relative;
        left: 0;
        bottom: 0;
        margin-bottom:0%;
        width: 100%;
        background-color: #042439;
        color: white;
        text-align: center;
        height: 3%;

    }
</style>
