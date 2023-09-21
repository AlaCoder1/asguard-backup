<template>

    <v-app id="inspire">
        <Drawer :active-menu="activeMenu" />
        <v-main>
            <!-- header -->
            <v-toolbar
                flat
                class="dms_grey axe-media-print-hide axe-sticky"
                height="60"
            >
                <v-toolbar-title class="axe-font-size-three text-color ml-2">
                    {{ title }}
                </v-toolbar-title>
                <v-spacer />
                <div v-if="back">
                    <v-btn
                        text
                        x-small
                        class="white--text axe-btn-bg text-caption"
                        :href="urlback"
                    >
                        <span class="icon-arrow-left  icon-size-one mr-2" />
                        <p class="text-capitalize mt-3">
                            {{ titleback }}
                        </p>
                    </v-btn>
                </div>
            </v-toolbar>
            <v-divider class="axe-media-print-hide" />
            <!-- content -->
            <slot name="content" />
        </v-main>
        <Footer />  
    </v-app>
</template>

<script>
import Drawer from '@/components/layout/drawer.vue';
import Footer from '@/components/layout/footer.vue';


export default {
    name: 'BaseLayout',
    components: {
        Drawer,
        Footer,
    },
    props: {
        title: {
            type: String,
            required: true,
        },
        activeMenu: {
            type: Number,
            required: true,
            default: null,
        },
        back: {
            type: Boolean,
            required: false,
        },
        urlback: {
            type: String,
            default: null,
            required: false,
        },
        titleback: {
            type: String,
            default: null,
            required: false,
        },
    },
};
</script>
