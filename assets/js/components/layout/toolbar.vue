<template>
    <v-app>
        <v-main>
            <!-- header -->
            <v-toolbar
                 color="blue-darken-3"
                flat
                class="axe-media-print-hide axe-sticky"
                height="60"
            >
                <v-toolbar-title class="axe-font-size-three white--text ml-2">
                </v-toolbar-title>
                <v-spacer />
                <div v-if="back">
                    <v-btn
                        text
                        x-small
                        class="white--text axe-btn-bg text-caption"
                        href="/"
                    >
                        <span class="icon-arrow-left  icon-size-one mr-2" />
                        <p class="text-capitalize mt-3">
                           titleback
                        </p>
                    </v-btn>
                </div>
            </v-toolbar>
            <v-divider class="axe-media-print-hide" />
            <!-- content -->
            <slot name="content" />
        </v-main>
    </v-app>
</template>

<script>
export default {
    name: 'ToolbarComponent',
    data: () => ({
        active: true,
    }),
};
</script>

<style lang="sass">
    .axe-tabs{
        .v-tabs-bar{
            height: auto ;
        }
    }
    .axe-tabs {
        .v-tab{
            max-width: none;
            font-size: 1rem;
            font-weight: 600;
            padding: 1.5rem;
        }
    }
    .axe-tabs{
        .v-tabs-slider-wrapper{
            height: 4px;
        }
    }
</style>
