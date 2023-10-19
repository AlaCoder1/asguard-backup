<template>
    <div class="d-flex flex-column footer-bg">
        Asguard 1.0 © {{ new Date().getFullYear() }} Numeryx.
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

<style>
.footer-bg {
    display: flex;
    /* Use flexbox display */
    align-items: center;
    /* Vertically center items */
    justify-content: center;
    /* Horizontally center items */
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background-color: #193286;
    color: white;
    text-align: center;
    height: 47px;
    font-family: Nunito;
    font-size: 18px;
    font-style: normal;
    font-weight: 400;
    line-height: normal;
    z-index: 1000;
}
</style>

