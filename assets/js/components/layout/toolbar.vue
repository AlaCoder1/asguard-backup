<template>
    <nav>
        <v-toolbar
            flat
            class="axe_blue_light"
        >
            <v-toolbar-title class="font-weight-black text-h5 ml-2">
                Restitutions
            </v-toolbar-title>
        </v-toolbar>
        <v-divider />

        <v-tabs
            flat
            background-color="axe_grey"
            class="axe-tabs"
        >
            <v-tab>
                A - Synthèse de l'analyse financière
            </v-tab>
            <v-tab>
                B - Description du patrimoine analysé
            </v-tab>
            <v-spacer />
            <v-switch
                v-model="active"
                class="font-weight-black black--text text-h4 mt-7 mr-9"
                label="Filtrer les données"
            />
        </v-tabs>
        <v-divider />
    </nav>
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
