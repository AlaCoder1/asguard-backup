import Vue from 'vue';
import Vuetify from 'vuetify/lib';
import fr from 'vuetify/lib/locale/fr';
import VuetifyMask from 'vuetify-mask';

Vue.use(Vuetify);

Vue.use(VuetifyMask);

export default new Vuetify({
    lang: {
        locales: { fr },
        current: 'fr',
    },
    theme: {
        themes: {
            light: {
                dms_white: '#FFFFFF',
                dms_grey: '#F8F8F8',
                dms_grey2: '#ECEFF1',
                dms_teal: '#6e8692',
                dms_blue: '#43aaf5',
                dms_blue_light: '#039BE5',
                dms_blue_dark:'#042439',
            },
            dark: {
                dms_grey: '#F8F8F8',
                dms_grey2: '#ECEFF1',
                dms_teal: '#6e8692',
                dms_blue: '#43aaf5',
                dms_blue_light: '#039BE5',
            },
        },
    },
});
