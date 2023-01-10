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
                axe_grey: '#FBFBFC',
                axe_grey2: '#ECEFF1',
                axe_teal: '#6e8692',
                axe_blue: '#43aaf5',
                axe_blue_light: '#039BE5',
            },
            dark: {
                axe_grey: '#FBFBFC',
                axe_grey2: '#ECEFF1',
                axe_teal: '#6e8692',
                axe_blue: '#43aaf5',
                axe_blue_light: '#039BE5',
            },
        },
    },
});
