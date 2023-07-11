<template>
    <v-app id="inspire">
        <base-layout title="SETTINGS" active-menu="general">
            <template #content>
                <v-tabs v-model="activeTab">
                    <v-tab v-for="tab in tabs" :key="tab.id">
                        {{ tab.label }}
                    </v-tab>
                    <v-tab-item v-for="tab in tabs" :key="tab.id">
                        <GeneralSettingsComponent v-if="tab.id === 1" />
                        <AdministrationSettingsComponent v-if="tab.id === 2" />
                        <CronSettingsComponent v-if="tab.id === 3" />
                        <LoggingTargetsSettingsComponent v-if="tab.id === 4" />
                        <OptimisationsSettingsComponent v-if="tab.id === 5" />
                    </v-tab-item>
                </v-tabs>
            </template>
        </base-layout>
    </v-app>
</template>

<script>
import BaseLayout from '@/pages/layout.vue';
import GeneralSettingsComponent from '@/components/GeneralSettingsComponent.vue';
import AdministrationSettingsComponent from '@/components/AdministrationSettingsComponent.vue';
import CronSettingsComponent from '@/components/CronSettingsComponent.vue';
import LoggingTargetsSettingsComponent from '@/components/LoggingTargetsSettingsComponent.vue';
import OptimisationsSettingsComponent from '@/components/OptimisationsSettingsComponent.vue';

export default {
    name: 'SettingsComponent',
    components: {
        BaseLayout,
        GeneralSettingsComponent,
        AdministrationSettingsComponent,
        CronSettingsComponent,
        LoggingTargetsSettingsComponent,
        OptimisationsSettingsComponent,
    },
    data() {
        return {
            activeTab: null,
            tabs: [
                { id: 1, label: 'GENERAL' },
                { id: 2, label: 'ADMINISTRATION/VARIOS' },
                { id: 3, label: 'CRON' },
                { id: 4, label: 'LOGGING TARGETS' },
                { id: 5, label: 'OPTIMISATIONS' },
            ],
        };
    },
    methods: {

    },
};
</script>
