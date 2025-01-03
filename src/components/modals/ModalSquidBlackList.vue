<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="text-h5"> {{ $t("squid.editBlackList") }} </span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="$t('squid.aclName')"
                    v-model="state.formData.aclName"
                    :readonly="true"
                  ></v-text-field>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-autocomplete
                    v-model="state.formData.urlList"
                    :items="state.formData.secondAclList"
                    :no-data-text="$t('squid.pleaseType')"
                    :label="`${$t('squid.selectItem')} *`"
                    chips
                    closable-chips
                    item-title="url"
                    item-value="url"
                    return-object
                    multiple
                    @update:search="searchAclItem"
                  >
                    <template v-slot:item="{ props, item }">
                      <!-- :subtitle="item?.raw?.status" -->
                      <!-- <div class="d-flex justify-space-between"> -->
                      <v-list-item
                        color="gray"
                        class="my-hover-color"
                        v-bind="props"
                        :title="item?.raw?.url"
                        :append-icon="
                          item?.raw?.status === true
                            ? 'mdi mdi-lock'
                            : 'mdi mdi-lock-open-outline'
                        "
                      ></v-list-item>
                      <!-- <v-chip
                          v-if="item.raw.status"
                          color="green"
                          class="mt-2"
                          >Blocked</v-chip
                        >
                        <v-chip v-else color="red" class="mt-2"
                          >Unblocked</v-chip
                        > -->
                      <!-- </div> -->
                    </template>
                  </v-autocomplete>

                  <p
                    class="error-feedback mb-5"
                    v-if="v$.formData.urlList.$error"
                  >
                    {{ v$.formData.urlList.$errors[0].$message }}
                  </p>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions class="mt-3 actionBtn">
            <div class="text-start ml-6 mt-3">
              <span class="text-sm">
                <span class="text-red text-lg">*</span>
                {{ $t("errors.oblig") }}</span
              >
            </div>
            <v-spacer></v-spacer>
            <v-btn
              color="indigo-darken-3"
              :rounded="true"
              large
              rounded
              outlined
              label-color="#213E9F"
              variant="flat"
              @click="closeModal"
              class="mt-3 btn-add"
            >
              <span class="text-white pr-3 pl-3">{{
                $t("buttons.close")
              }}</span>
            </v-btn>

            <v-btn
              large
              rounded
              outlined
              label-color="#213E9F"
              @click="saveAcl"
              color="indigo-darken-3"
              :rounded="true"
              variant="flat"
              class="mt-3 btn-add"
            >
              <span class="text-white pr-3 pl-3">
                {{ $t("buttons.update") }}</span
              >
            </v-btn>
          </v-card-actions>
        </v-card>
      </form>
    </v-dialog>
    <v-snackbar
      :timeout="2000"
      v-model="state.snackbar"
      location="bottom right"
      :color="state.color"
    >
      {{ state.textAlert }}
    </v-snackbar>
  </v-row>
</template>

<script>
import axios from "axios";
import useValidate from "@vuelidate/core";
import { required } from "@vuelidate/validators";
import { reactive, computed, toRefs, watch, inject } from "vue";
import VButton from "@/components/VButton.vue";
import { useI18n } from "vue-i18n";

export default {
  name: "Modal_User_Squid",
  components: {
    VButton,
  },
  props: {
    isOpen: {
      type: Boolean,
      required: true,
    },
    editRow: {
      type: Object,
      Array,
      required: true,
    },
  },
  setup(props) {
    const { t } = useI18n();
    const { isOpen, editRow } = toRefs(props);
    const emitter = inject("emitter");
    const state = reactive({
      formData: {
        password: "",
        confirm_password: "",
        aclName: null,
        category: "",
        description: "",
        urlList: [],
        originAclList: [],
        secondAclList: [],
      },
      openModal: false,
      textAlert: "",
      color: "",
      snackbar: false,
    });
    const rules = computed(() => {
      return {
        formData: {
          urlList: { required },
        },
      };
    });

    const v$ = useValidate(rules, state);

    watch(
      () => isOpen.value,
      (val) => {
        state.openModal = val;
      }
    );
    watch(
      () => editRow.value,
      (val) => {
        state.formData.aclName = val.name;

        const csrfToken = getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

        let payload = { file_name: val.name };

        axios
          .post("/proxy/readFromFile", payload)
          .then((response) => {
            state.formData.originAclList = response.data.content;
          })
          .catch((i) => {
            console.log("i : ", i);
          });
      }
    );

    const closeModal = () => {
      emitter.emit("closeAclListModal");
      v$.value.$reset();
      state.formData.secondAclList = [];
      state.formData.urlList = [];
    };
    const getCookie = (name) => {
      let cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === name + "=") {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    };

    const searchAclItem = (event) => {
      if (!event) {
        state.formData.secondAclList = [];
        return;
      } else {
        let filtredItem = state.formData.originAclList.filter((item) =>
          item[0].startsWith(event)
        );

        let mapedItem = filtredItem.map(([url, status]) => ({ url, status }));
        state.formData.secondAclList = mapedItem;
      }
    };
    const saveAcl = async () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      const result = await v$.value.$validate();
      if (result) {
        const changeFormArray = state.formData.urlList.map(
          ({ url, status }) => [url, status]
        );

        let payload = {
          file_name: state.formData.aclName,
          list_elements: changeFormArray,
        };

        axios
          .post("/proxy/changeStausElementsInGroup", payload)
          .then((response) => {
            if (response.status == "200") {
              state.snackbar = true;
              state.color = "success";
              state.textAlert = response.data.msg;
              setTimeout(() => {
                location.reload();
              }, 1000);
            }
          })
          .catch((i) => {
            if (i.response.status === 500) {
              state.snackbar = true;
              state.color = "red";
              state.textAlert = t("errors.errorServer");
            } else {
              state.snackbar = true;
              state.color = "red";
              state.textAlert = i.response.data.error;
            }
          });
      } else {
        console.log("error", v$.value);
      }
    };
    return {
      state,
      v$,
      emitter,
      closeModal,
      searchAclItem,
      saveAcl,
    };
  },
};
</script>
<style>
.error-feedback {
  color: red;
  font-size: 0.85em;
}
.my-hover-color:hover {
  background-color: red; /* Replace with your desired hover color */
}
</style>
