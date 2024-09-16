<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="text-h5"> {{ $t("ztna.createNewIdentity") }}</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12">
                  <v-text-field v-model="date" label="Date" prepend-icon="mdi-calendar" type="date"></v-text-field>
                </v-col>
                <v-col cols="12">
                  <v-text-field v-model="time" label="Time" prepend-icon="mdi-clock" type="time"
                    class="ml-1"></v-text-field>
                </v-col>

                <v-col cols="12">
                  <div class="d-flex align-center">
                    <label class="ml-1" for="Type">Type</label>
                    <div class="ml-5 mt-1">
                      <v-menu open-on-hover>
                        <template v-slot:activator="{ props }">
                          <v-btn color="#FAFAFA" v-bind="props">
                            {{ selectedTitle }}
                          </v-btn>
                        </template>

                        <v-list>
                          <v-list-item v-for="(item, index) in items" :key="index" @click="selectItem(item)">
                            <v-list-item-title>{{
                              item.title
                            }}</v-list-item-title>
                          </v-list-item>
                        </v-list>
                      </v-menu>
                    </div>
                  </div>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="indigo-darken-3" :rounded="true" large rounded outlined label-color="#213E9F" variant="flat"
              class="mt-3 btn-add" text @click="cancel">{{ $t("buttons.close") }}</v-btn>
            <!-- <VBtn
              color="red"
              :rounded="true"
              large
              rounded
              outlined
              label-color="#213E9F"
              variant="flat"
              class="mt-3 btn-add"
              type="reset"
            >
              Reset
            </VBtn> -->
            <VBtn large rounded outlined label-color="#213E9F" color="indigo-darken-3" :rounded="true" variant="flat"
              class="mt-3 ml-2 btn-add" type="submit">
              {{ $t("buttons.create") }}
            </VBtn>
          </v-card-actions>
        </v-card>
      </form>
    </v-dialog>
  </v-row>
</template>

<script>
import axios from "axios";
import { getCookie } from "@/mixins/csrftoken.js";
import { toRefs, ref, watch, reactive, inject } from "vue";

export default {
  props: {
    isOpen: {
      type: Boolean,
      required: true,
    },
    selectedId: {
      type: [String, Number],
      required: true,
    },
  },

  setup(props) {
    const date = ref(null);
    const time = ref(null);
    const selectedTitle = ref("ott");
    const jwtToken = ref("");
    const showJwtToken = ref(false);
    const EnrollementId = ref("");
    const items = [{ title: "ott" }, { title: "updb" }, { title: "ottca" }];
    const rules = [(value) => !!value || "You must enter a value."];

    const emitter = inject("emitter");

    const { isOpen, selectedId } = toRefs(props);

    const state = reactive({
      openModal: false,
      itemId: null,
    });

    watch(
      () => isOpen.value,
      (val) => {
        state.openModal = val;
      }
    );

    watch(
      () => selectedId.value,
      (val) => {
        console.log(val);
        state.itemId = val;
      }
    );

    const submitForm = async () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      let token = document.getElementById("app").getAttribute("token");

      let payload = {
        expiresAt: dateTime,
        method: selectedTitle.value,
        identityId: state.itemId,
      }
      axios
        .post("/ztna/add_enrollment", payload, {
          headers: {
            "zt-session": token,
            "Content-Type": "application/json",
          },
        })
        .then((response) => {
          console.log('response', response)
          if (response.status == "201") {
            // state.openModal = false;
            // state.snackbar = true;
            // state.color = "success";
            // state.textAlert = response.data.msg;

            setTimeout(() => {
              // location.reload();
            }, 1000);
          }
        })
        .catch((i) => {
          console.log('r', i.response)
          // state.snackbar = true;
          // state.color = "red";
          // state.textAlert = i.response.data.error;
        });
    };

    const selectItem = (item) => {
      selectedTitle.value = item.title;
    };

    const cancel = () => {
      console.log("test");
      emitter.emit("closeEnrollmentModal");
    };

    return {
      state,
      cancel,
      emitter,
      rules,
      submitForm,
      selectedTitle,
      selectItem,
      items,
      date,
      time,
      jwtToken,
      showJwtToken,
      EnrollementId,
    };
  },
};
</script>
<style>
.error-feedback {
  color: red;
  font-size: 0.85em;
}

.actionBtn {
  justify-content: center;
}

.red-asterisk {
  color: rgb(147, 3, 3);
  font-size: 1.6em;
}

.v-application--is-ltr .v-menu__content {
  display: flex;
  justify-content: center;
  left: 50% !important;
  transform: translateX(-50%) !important;
}
</style>
