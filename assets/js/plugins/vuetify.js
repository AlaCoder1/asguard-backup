import Vue from 'vue';
import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'

Vue.use(Vuetify);

export default new Vuetify({
    theme: {
        themes: {
            light: {
                dms_white: '#FFFFFF',
                dms_grey: '#F8F8F8',
                dms_grey2: '#ECEFF1',
                dms_teal: '#6e8692',
                dms_blue: '#43aaf5',
                dms_blue_light: '#039BE5',
                dms_blue_dark: '#213E9F',
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
