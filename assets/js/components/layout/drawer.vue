<template>
<div>
 
            <v-toolbar
                flat
                class="dms_blue_dark dms-media-print-hide dms-sticky"
                height="70">
                        <v-toolbar-title class="dms-font-size-three white--text ml-8">
                            <img
                                src="../../../images/logoDMS.png" 
                                height="100" 
                            />
                        </v-toolbar-title>
                        <v-spacer />
                        <v-select
                            v-model="lang"
                            :items="['frensh','english']"
                            solo
                            background-color="#042439"
                            class="select-white-text select-lang "
                        />

                    <v-text-field background-color="white" rounded class="ml-3  input-search" placeholder="Search" hide-details></v-text-field>
                 
                    <v-menu offset-y>
                        <template v-slot:activator="{ on }">
                           <v-avatar class="ml-3 mr-3" size="30" v-on="on">
                                <img src="../../../images/user.png" alt="Account logo">
                            </v-avatar>
                        </template>
                        <v-list>
                            <v-list-item>
                            <v-list-item-title>Profile</v-list-item-title>
                            </v-list-item>
                            <v-list-item>
                            <v-list-item-title>Settings</v-list-item-title>
                            </v-list-item>
                            <v-list-item>
                            <v-list-item-title>Logout</v-list-item-title>
                            </v-list-item>
                        </v-list>
                    </v-menu>
                    <span  style="color: white;">johndoe@example.com</span>
        </v-toolbar>
     

    <v-navigation-drawer
        :mini-variant.sync="mini"
        class="dms_grey global-drawer"
        permanent
        app>
        <v-app-bar
            dense
            flat
            class="row-pointer dms_white"
            @click.stop="mini = !mini">
            <v-app-bar-nav-icon color="dms_teal" />
            <v-toolbar-title class="dms_teal--text text-body-2">
                Réduire le menu
            </v-toolbar-title>
        </v-app-bar>

        <v-list
            dense
            class="white lighten-1 pb-0">
            <v-list-item
                v-for="item in items"
                :key="item.title"
                link
                :href="item.href"
            >
                <v-list-item-icon  v-if="mini"> 
                    <span
                        :class="[item.icon, 'icon-size-two axe_teal--text']"
                    />
                </v-list-item-icon>
                <v-list-item-content>
                    <v-list-item-icon v-if="!mini" class="dms-menu-open" > 
                        <span
                            :class="[item.icon, 'icon-size-two axe_teal--text']"
                        />
                    </v-list-item-icon>
                    <v-list-item-title
                        class="dms_teal--text item"
                    >
                        {{ item.title }}
                    </v-list-item-title>
                </v-list-item-content>
            </v-list-item>
        </v-list>
    </v-navigation-drawer>
</div>
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
        lang:'frensh',
        items: [
            {
                title: 'Dashboard', icon: 'icon-home', href: '/', active: 'home',
            },
            {
                title: 'System', icon: 'icon-trending', href: '/system', active: 'system',
            },
            {
                title: 'Interfaces', icon: 'icon-business', href: '/interfaces', active: 'interfaces',
            },
            {
                title: 'Firewall', icon: 'icon-business', href: '/firewall', active: 'Firewall',
            },
            {
                title: 'Services', icon: 'icon-business', href: '/services', active: 'Firewall',
            },
            {
                title: 'Reports', icon: 'icon-business', href: '/reports', active: 'Firewall',
            },  
            {
                title: 'Subscription', icon: 'icon-business', href: '/subscription', active: 'Firewall',
            },                     
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
            .dms_teal--text, .text-wrap{
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
            .dms_teal--text, .text-wrap{
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
    .dms-tabs{
        .v-tabs-bar{
            height: auto ;
        }
    }
    .item {
        height: 25px;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .dms-tabs {
        .v-tab{
            max-width: none;
            font-size: 1rem;
            font-weight: 600;
            padding: 1.5rem;
        }
    }
    .dms-tabs{
        .v-tabs-slider-wrapper{
            height: 4px;
        }
    }
    .dms-tabs-border-bottom{
        border-bottom: 1px solid #e0e0e0;
    }

    .dms-menu-open {
        justify-content: center!important;
    }

    a:hover {
        background-color: #FFC300;
        transition: background-color 0.2s ease-in-out;
    }
    .select-white-text .v-select__selection--comma {
        color: white;
        
    }
    .select-lang   {
        max-width: 110px;
        margin-top: 2%!important;
    }
    .input-search   {
        max-width: 250px;
    }


</style>
