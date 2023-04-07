<template>
    <v-navigation-drawer
        :mini-variant.sync="mini"
        class="axe_grey global-drawer"
        permanent
        app
    >
        <v-list-item class="px-2 logo">
            <v-img
                :src="require('../../../images/homeLogo.svg')"
            />
        </v-list-item>

        <v-list-item class="px-2 logoM">
            <v-img
                :src="require('../../../images/homeLogoM.svg')"
            />
        </v-list-item>

        <v-divider />

        <v-app-bar
            dense
            flat
            class="row-pointer axe_grey"
            @click.stop="mini = !mini"
        >
            <v-app-bar-nav-icon color="axe_teal" />

            <v-toolbar-title class="axe_teal--text text-body-2">
                Réduire le menu
            </v-toolbar-title>
        </v-app-bar>

        <v-divider />

        <v-list
            dense
            class="pb-0"
        >
            <v-list-item
                v-for="item in items"
                :key="item.title"
                link
                :href="item.href"
                :class="[item.active === activeMenu ? 'axe-active-menu' : '', 'drawer_hover']"
            >
                <v-list-item-icon>
                    <span
                        :class="[item.icon, 'icon-size-two axe_teal--text']"
                    />
                </v-list-item-icon>
                <v-list-item-content>
                    <v-list-item-title
                        class="axe_teal--text text-wrap"
                    >
                        {{ item.title }}
                    </v-list-item-title>
                </v-list-item-content>
            </v-list-item>
        </v-list>

        <v-list
            dense
            class="pt-0"
        >
            <v-list-item
                v-for="item in parametre"
                :key="item.title"
                link
                :href="item.href"
                :class="[item.active === activeMenu ?
                             'axe-active-menu' : '',
                         'pr-0 drawer_hover drawer_hover_sp']"
            >
                <v-list-item-icon>
                    <span
                        :class="[item.icon, 'icon-size-two axe_teal--text']"
                    />
                </v-list-item-icon>
                <v-list-item-content>
                    <v-list-item-title
                        class="axe_teal--text text-white-space drawer-width"
                    >
                        {{ item.title }}
                    </v-list-item-title>
                </v-list-item-content>
            </v-list-item>
        </v-list>

        <template #append>
            <v-list
                dense
                class="white lighten-1"
            >
                <v-list-item
                    v-for="item in compte"
                    :key="item.title"
                    link
                    :href="item.href"
                >
                    <v-list-item-icon>
                        <span
                            :class="[item.icon, 'icon-size-two axe_teal--text']"
                        />
                    </v-list-item-icon>
                    <v-list-item-content>
                        <v-list-item-title
                            class="axe_teal--text"
                        >
                            {{ item.title }}
                        </v-list-item-title>
                    </v-list-item-content>
                </v-list-item>
            </v-list>
        </template>
    </v-navigation-drawer>
</template>

<script>
export default {
    name: 'DrawerComponent',
    props: {
        activeMenu: {
            type: String,
            required: true,
            default: null,
        },
    },
    data: () => ({
        drawer: true,
        items: [
            {
                title: 'dashboard', icon: 'icon-home', href: '/', active: 'home',
            },
            {
                title: 'system', icon: 'icon-trending', href: '/system', active: 'system',
            },
            {
                title: 'interfaces', icon: 'icon-business', href: '/interfaces', active: 'interfaces',
            },
            {
                title: 'Firewall', icon: 'icon-business', href: '/Firewall', active: 'Firewall',
            },
        ],
        parametre: [
            {
                title: 'dashboard', icon: ' icon-browsers', href: '/home', active: '',
            },
            {
                title: 'system', icon: 'icon-card', href: '/system', active: 'system',
            },
            {
                title: 'interfaces', icon: 'icon-people', href: '/interfaces', active: '',
            },
            {
                title: 'Firewall', icon: 'icon-book', href: '/Firewall', active: 'Firewall',
            },
        ],
        compte: [
            { title: 'Mon compte', icon: 'icon-person', href: '/mon-compte' },
            { title: 'Déconnexion', icon: 'icon-power', href: '/logout' },
        ],
        mini: true,
    }),
};
</script>
<style lang="sass">

    // src/sass/main.scss
    @import '~vuetify/src/styles/styles.sass';

    // You need to map-merge your new SASS variables
    $grid-breakpoints: map-merge($grid-breakpoints, (
        xs: 0,
        sm: 476px,
        md: 668px,
        lg: 1000px,
        xl: 1300px
    ));

    .drawer_hover{
        &:hover{
            &::before{
                opacity: 1 !important;
            }
            .axe_teal--text, .text-wrap{
                color: white !important;
                opacity: 1 !important;
                z-index: 1 !important;
            }
        }
        &::before{
            -webkit-border-top-left-radius: 10px;
            -webkit-border-bottom-left-radius: 10px;
            -moz-border-radius-topleft: 10px;
            -moz-border-radius-bottomleft: 10px;
            border-top-left-radius: 10px;
            border-bottom-left-radius: 10px;
            left: 8px;
            background-color: #43aaf5 !important;
        }

    }
    .axe-active-menu{
        &::before{
            opacity: 1 !important;
        }
        .v-list-item__icon, .v-list-item__content{
            .axe_teal--text, .text-wrap{
                color: white !important;
                opacity: 1 !important;
                z-index: 1 !important;
            }
        }

    }
    .row-pointer {
        cursor: pointer;
    }
    .text-white-space{
        white-space: normal !important;
    }
    .drawer-width{
        max-width: 120px;
    }
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
    .axe-tabs-border-bottom{
        border-bottom: 1px solid #e0e0e0;
    }

</style>
