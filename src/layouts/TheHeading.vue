<template>
  <v-app-bar>
    <v-toolbar>
      <v-toolbar-title class="ml-8">
        <img src="../assets/images/logo.svg" alt="logo" height="50" />
      </v-toolbar-title>
      <v-spacer />
      <div
        class="lang d-flex align-center"
        style="gap: 5px; cursor: pointer"
        id="language-btn"
      >
        <span v-html="selectedLang[0].icon" style="margin-top: 4px"></span>

        <span>{{ $t(selectedLang[0].language) }}</span>
        <v-icon>mdi-chevron-down</v-icon>

        <v-menu activator="#language-btn">
          <v-list v-model:selected="selectedLang">
            <v-list-item v-for="lang in langs" :key="lang.lang" :value="lang">
              <v-list-item-title class="d-flex align-center" style="gap: 10px">
                <span v-html="lang.icon"></span> {{ $t(lang.language) }}
              </v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </div>
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-avatar class="ml-3 mr-3" size="30" v-bind="props">
            <v-icon size="30" class="white--text" color="white"
              >mdi-account-circle-outline</v-icon
            >
          </v-avatar>
        </template>
        <v-list style="cursor: pointer; padding: 15px">
          <v-list-item> {{ $t("header.profile") }} </v-list-item>
          <v-list-item> {{ $t("subtitle.settings") }} </v-list-item>

          <v-list-item>
            <span @click="logout">{{ $t("header.logout") }}</span>
          </v-list-item>
        </v-list>
      </v-menu>

      <div class="userInfo">
        <span class="white-color">{{ state.currentInfo.username }}</span>
        <span class="white-color">{{ state.currentInfo.email }}</span>
      </div>

      <br />
    </v-toolbar>
  </v-app-bar>
</template>

<script>
import axios from "axios";
import { reactive, onMounted, ref } from "vue";
export default {
  name: "ToolbarComponent",

  setup() {
    onMounted(() => {
      let retriveInfo = localStorage.getItem("user-info");
      let userInfo = JSON.parse(retriveInfo);
      let user = userInfo;
      state.currentInfo = { ...user.currentUser };

      let getLang = localStorage.getItem("lang");
      if (getLang) selectedLang.value = JSON.parse(getLang);
    });
    const state = reactive({
      currentInfo: {},
    });
    const selectedLang = ref([
      {
        icon: ` <svg
                xmlns="http://www.w3.org/2000/svg"
                version="1.1"
                x="0px"
                y="0px"
                viewBox="0 0 512 512"
                style="enable-background: new 0 0 512 512; width: 20px;margin-top:5px"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                xml:space="preserve"
            >
                <circle
                style="fill: #f0f0f0"
                cx="256"
                cy="256"
                r="256"
                ></circle>
                <g>
                <path
                    style="fill: #0052b4"
                    d="M52.92,100.142c-20.109,26.163-35.272,56.318-44.101,89.077h133.178L52.92,100.142z"
                ></path>
                <path
                    style="fill: #0052b4"
                    d="M503.181,189.219c-8.829-32.758-23.993-62.913-44.101-89.076l-89.075,89.076H503.181z"
                ></path>
                <path
                    style="fill: #0052b4"
                    d="M8.819,322.784c8.83,32.758,23.993,62.913,44.101,89.075l89.074-89.075L8.819,322.784L8.819,322.784   z"
                ></path>
                <path
                    style="fill: #0052b4"
                    d="M411.858,52.921c-26.163-20.109-56.317-35.272-89.076-44.102v133.177L411.858,52.921z"
                ></path>
                <path
                    style="fill: #0052b4"
                    d="M100.142,459.079c26.163,20.109,56.318,35.272,89.076,44.102V370.005L100.142,459.079z"
                ></path>
                <path
                    style="fill: #0052b4"
                    d="M189.217,8.819c-32.758,8.83-62.913,23.993-89.075,44.101l89.075,89.075V8.819z"
                ></path>
                <path
                    style="fill: #0052b4"
                    d="M322.783,503.181c32.758-8.83,62.913-23.993,89.075-44.101l-89.075-89.075V503.181z"
                ></path>
                <path
                    style="fill: #0052b4"
                    d="M370.005,322.784l89.075,89.076c20.108-26.162,35.272-56.318,44.101-89.076H370.005z"
                ></path>
                </g>
                <g>
                <path
                    style="fill: #d80027"
                    d="M509.833,222.609h-220.44h-0.001V2.167C278.461,0.744,267.317,0,256,0   c-11.319,0-22.461,0.744-33.391,2.167v220.44v0.001H2.167C0.744,233.539,0,244.683,0,256c0,11.319,0.744,22.461,2.167,33.391   h220.44h0.001v220.442C233.539,511.256,244.681,512,256,512c11.317,0,22.461-0.743,33.391-2.167v-220.44v-0.001h220.442   C511.256,278.461,512,267.319,512,256C512,244.683,511.256,233.539,509.833,222.609z"
                ></path>
                <path
                    style="fill: #d80027"
                    d="M322.783,322.784L322.783,322.784L437.019,437.02c5.254-5.252,10.266-10.743,15.048-16.435   l-97.802-97.802h-31.482V322.784z"
                ></path>
                <path
                    style="fill: #d80027"
                    d="M189.217,322.784h-0.002L74.98,437.019c5.252,5.254,10.743,10.266,16.435,15.048l97.802-97.804   V322.784z"
                ></path>
                <path
                    style="fill: #d80027"
                    d="M189.217,189.219v-0.002L74.981,74.98c-5.254,5.252-10.266,10.743-15.048,16.435l97.803,97.803   H189.217z"
                ></path>
                <path
                    style="fill: #d80027"
                    d="M322.783,189.219L322.783,189.219L437.02,74.981c-5.252-5.254-10.743-10.266-16.435-15.047   l-97.802,97.803V189.219z"
                ></path>
                </g></svg
            >`,
        lang: "En",
        language: "english",
      },
    ]);
    const langs = ref([
      {
        icon: ` <svg
                xmlns="http://www.w3.org/2000/svg"
                version="1.1"
                x="0px"
                y="0px"
                viewBox="0 0 512 512"
                style="enable-background: new 0 0 512 512; width: 20px;margin-top:5px"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                xml:space="preserve"
            >
                <circle
                style="fill: #f0f0f0"
                cx="256"
                cy="256"
                r="256"
                ></circle>
                <g>
                <path
                    style="fill: #0052b4"
                    d="M52.92,100.142c-20.109,26.163-35.272,56.318-44.101,89.077h133.178L52.92,100.142z"
                ></path>
                <path
                    style="fill: #0052b4"
                    d="M503.181,189.219c-8.829-32.758-23.993-62.913-44.101-89.076l-89.075,89.076H503.181z"
                ></path>
                <path
                    style="fill: #0052b4"
                    d="M8.819,322.784c8.83,32.758,23.993,62.913,44.101,89.075l89.074-89.075L8.819,322.784L8.819,322.784   z"
                ></path>
                <path
                    style="fill: #0052b4"
                    d="M411.858,52.921c-26.163-20.109-56.317-35.272-89.076-44.102v133.177L411.858,52.921z"
                ></path>
                <path
                    style="fill: #0052b4"
                    d="M100.142,459.079c26.163,20.109,56.318,35.272,89.076,44.102V370.005L100.142,459.079z"
                ></path>
                <path
                    style="fill: #0052b4"
                    d="M189.217,8.819c-32.758,8.83-62.913,23.993-89.075,44.101l89.075,89.075V8.819z"
                ></path>
                <path
                    style="fill: #0052b4"
                    d="M322.783,503.181c32.758-8.83,62.913-23.993,89.075-44.101l-89.075-89.075V503.181z"
                ></path>
                <path
                    style="fill: #0052b4"
                    d="M370.005,322.784l89.075,89.076c20.108-26.162,35.272-56.318,44.101-89.076H370.005z"
                ></path>
                </g>
                <g>
                <path
                    style="fill: #d80027"
                    d="M509.833,222.609h-220.44h-0.001V2.167C278.461,0.744,267.317,0,256,0   c-11.319,0-22.461,0.744-33.391,2.167v220.44v0.001H2.167C0.744,233.539,0,244.683,0,256c0,11.319,0.744,22.461,2.167,33.391   h220.44h0.001v220.442C233.539,511.256,244.681,512,256,512c11.317,0,22.461-0.743,33.391-2.167v-220.44v-0.001h220.442   C511.256,278.461,512,267.319,512,256C512,244.683,511.256,233.539,509.833,222.609z"
                ></path>
                <path
                    style="fill: #d80027"
                    d="M322.783,322.784L322.783,322.784L437.019,437.02c5.254-5.252,10.266-10.743,15.048-16.435   l-97.802-97.802h-31.482V322.784z"
                ></path>
                <path
                    style="fill: #d80027"
                    d="M189.217,322.784h-0.002L74.98,437.019c5.252,5.254,10.743,10.266,16.435,15.048l97.802-97.804   V322.784z"
                ></path>
                <path
                    style="fill: #d80027"
                    d="M189.217,189.219v-0.002L74.981,74.98c-5.254,5.252-10.266,10.743-15.048,16.435l97.803,97.803   H189.217z"
                ></path>
                <path
                    style="fill: #d80027"
                    d="M322.783,189.219L322.783,189.219L437.02,74.981c-5.252-5.254-10.743-10.266-16.435-15.047   l-97.802,97.803V189.219z"
                ></path>
                </g></svg
            >`,
        lang: "En",
        language: "english",
      },
      {
        icon: `<svg xmlns="http://www.w3.org/2000/svg" style="enable-background: new 0 0 512 512; width: 20px;height: 20px;margin-top:5px" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" width="256" height="256" viewBox="0 0 256 256" xml:space="preserve">
              <defs>
              </defs>
              <g style="stroke: none; stroke-width: 0; stroke-dasharray: none; stroke-linecap: butt; stroke-linejoin: miter; stroke-miterlimit: 10; fill: none; fill-rule: nonzero; opacity: 1;" transform="translate(1.4065934065934016 1.4065934065934016) scale(2.81 2.81)" >
                <path d="M 59.999 2.571 l 0 84.859 c 17.466 -6.175 29.985 -22.818 30 -42.396 v -0.068 C 89.985 25.389 77.465 8.745 59.999 2.571 z" style="stroke: none; stroke-width: 1; stroke-dasharray: none; stroke-linecap: butt; stroke-linejoin: miter; stroke-miterlimit: 10; fill: rgb(243,24,48); fill-rule: nonzero; opacity: 1;" transform=" matrix(1 0 0 1 0 0) " stroke-linecap="round" />
                <path d="M 30 87.429 l 0 -84.858 C 12.524 8.75 0 25.408 0 45 S 12.524 81.25 30 87.429 z" style="stroke: none; stroke-width: 1; stroke-dasharray: none; stroke-linecap: butt; stroke-linejoin: miter; stroke-miterlimit: 10; fill: rgb(0,38,127); fill-rule: nonzero; opacity: 1;" transform=" matrix(1 0 0 1 0 0) " stroke-linecap="round" />
                <path d="M 30 87.429 C 34.693 89.088 39.739 90 45 90 c 5.261 0 10.307 -0.911 15 -2.571 l 0 -84.859 C 55.307 0.911 50.261 0 45 0 c -5.261 0 -10.307 0.912 -15 2.571 L 30 87.429 z" style="stroke: none; stroke-width: 1; stroke-dasharray: none; stroke-linecap: butt; stroke-linejoin: miter; stroke-miterlimit: 10; fill: rgb(243,244,245); fill-rule: nonzero; opacity: 1;" transform=" matrix(1 0 0 1 0 0) " stroke-linecap="round" />
              </g>
              </svg>`,
        lang: "Fr",
        language: "frensh",
      },
    ]);

    const logout = async () => {
      try {
        await axios.get("/auth/logout");
        window.location.href = "/";
        localStorage.removeItem("href-path");
      } catch (error) {
        console.error("Error during logout:", error);
      }
    };

    return {
      state,
      langs,
      selectedLang,
      logout,
    };
  },

  watch: {
    selectedLang(val) {
      if (val.length) {
        let lang = JSON.stringify(val);
        localStorage.setItem("lang", lang);
        localStorage.setItem("lang-slug", val[0].lang);
        let choosedLang = val[0].lang;
        this.changeLang(choosedLang);
      } else {
        let getLang = localStorage.getItem("lang");
        if (getLang) this.selectedLang = JSON.parse(getLang);
      }
    },
  },
  methods: {
    changeLang(lang) {
      this.$i18n.locale = lang.toLowerCase();
    },
  },
};
</script>

<style scoped>
.userInfo {
  display: flex;
  flex-direction: column;
  margin-right: 10px;
  margin-left: 10px;
}

.white-color {
  color: white;
}

.v-toolbar {
  background-color: #193286;
  color: white;
  font-size: 18.16px;
  font-family: Nunito;
  font-weight: 400;
  word-wrap: break-word;
}
</style>
