<template>
  <v-row justify="center">
    <v-overlay v-model="state.loading">
      <v-dialog
        v-model="state.isLoadingDialogue"
        :scrim="false"
        persistent
        width="auto"
      >
        <v-card color="#193286">
          <v-card-text>
            {{ $t("sdwan.pleaseWait") }}
            <v-progress-linear
              indeterminate
              color="white"
              class="mb-0"
            ></v-progress-linear>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-overlay>

    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm" class="scroller">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              {{ $t("sdwan.createNewRule") }}</span
            >
            <span class="headline" v-if="modalMode === 'edit'">
              {{ $t("sdwan.updateRule") }}</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="`${$t('sdwan.ruleName')} *`"
                    v-model="state.ruleName"
                  ></v-text-field>
                  <p class="error-feedback mb-5" v-if="v$.ruleName.$error">
                    {{ v$.ruleName.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-textarea
                    rows="1"
                    row-height="15"
                    v-model="state.description"
                    :label="$t('firewall.description')"
                    variant="outlined"
                  ></v-textarea>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    multiple
                    v-model="state.variable"
                    label="Variable *"
                    item-title="name"
                    item-value="slug"
                    :items="state.listVariable"
                    return-object
                    :no-data-text="$t('certificat.certificatlist')"
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.variable.$error">
                    {{ v$.variable.$errors[0].$message }}
                  </p>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-select
                    multiple
                    clearable
                    v-model="state.operator"
                    :label="$t('Waf.operator')"
                    item-title="type"
                    item-value="slug"
                    :items="state.listOperator"
                    return-object
                    :no-data-text="$t('certificat.certificatlist')"
                  ></v-select>
                  <!-- <p class="error-feedback mb-5" v-if="v$.operator.$error">
                    {{ v$.operator.$errors[0].$message }}
                  </p> -->
                </v-col>

                <v-col cols="12" class="d-flex justify-end mb-n6">
                  <v-btn
                    color="#F6F6F6"
                    class="text-none"
                    variant="flat"
                    @click="addNewRow"
                  >
                    <svg
                      width="17"
                      height="17"
                      viewBox="0 0 17 17"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <mask
                        id="mask0_50_190"
                        style="mask-type: luminance"
                        maskUnits="userSpaceOnUse"
                        x="0"
                        y="0"
                        width="17"
                        height="17"
                      >
                        <path d="M17 0H0V17H17V0Z" fill="white" />
                      </mask>
                      <g mask="url(#mask0_50_190)">
                        <path
                          d="M8.70871 0.219971C10.3463 0.219971 11.9472 0.705584 13.3088 1.6154C14.6705 2.52522 15.7317 3.81838 16.3584 5.33135C16.9851 6.84432 17.1491 8.50916 16.8296 10.1153C16.5101 11.7215 15.7215 13.1968 14.5636 14.3548C13.4056 15.5128 11.9302 16.3014 10.3241 16.6209C8.7179 16.9404 7.05306 16.7764 5.54009 16.1497C4.02712 15.523 2.73396 14.4617 1.82414 13.1001C0.914324 11.7385 0.428711 10.1376 0.428711 8.49997C0.428976 6.30406 1.30142 4.19816 2.85416 2.64542C4.4069 1.09268 6.5128 0.220236 8.70871 0.219971Z"
                          fill="#086EAE"
                        />
                        <path
                          d="M13.6689 8.03597C13.7332 8.09478 13.7842 8.16654 13.8187 8.24652C13.8531 8.32651 13.8703 8.41289 13.8689 8.49997C13.8703 8.58779 13.8542 8.675 13.8216 8.75654C13.789 8.83808 13.7405 8.91233 13.6789 8.97497C13.6167 9.04086 13.5412 9.09277 13.4574 9.12725C13.3736 9.16173 13.2835 9.178 13.1929 9.17497H9.36591V12.981C9.36918 13.0709 9.35391 13.1606 9.32105 13.2443C9.28819 13.3281 9.23845 13.4042 9.17491 13.468C9.11435 13.5295 9.04187 13.578 8.96191 13.6105C8.88195 13.643 8.7962 13.6588 8.70991 13.657C8.62268 13.6583 8.53614 13.6412 8.45599 13.6068C8.37585 13.5723 8.30391 13.5212 8.24491 13.457C8.18336 13.3943 8.13487 13.3201 8.10225 13.2385C8.06963 13.157 8.05354 13.0698 8.05491 12.982V9.17697H4.22791C4.04915 9.17414 3.87848 9.10194 3.75197 8.97562C3.62546 8.84929 3.553 8.67873 3.54991 8.49997C3.54829 8.41285 3.5653 8.32639 3.59979 8.24637C3.63428 8.16635 3.68546 8.09462 3.74991 8.03597C3.81266 7.97421 3.88704 7.92552 3.96876 7.89274C4.05047 7.85995 4.13788 7.84371 4.22591 7.84497H8.05491V4.03797C8.04956 3.85273 8.11789 3.67292 8.24491 3.53797C8.30487 3.47498 8.37701 3.42483 8.45694 3.39056C8.53688 3.35629 8.62294 3.33862 8.70991 3.33862C8.79688 3.33862 8.88294 3.35629 8.96288 3.39056C9.04281 3.42483 9.11495 3.47498 9.17491 3.53797C9.3023 3.67276 9.37099 3.85259 9.36591 4.03797V7.84497H13.1929C13.2809 7.84377 13.3683 7.86003 13.45 7.89281C13.5317 7.9256 13.6061 7.97426 13.6689 8.03597Z"
                          fill="white"
                        />
                      </g>
                    </svg>
                    <span class="ml-2" style="color: #086eae">{{
                      $t("buttons.Add")
                    }}</span>
                  </v-btn>
                </v-col>
                <v-col cols="12" class="mb-1 mt-0">
                  <ag-grid-vue
                    id="grid-wrapper"
                    domLayout="autoHeight"
                    class="ag-theme-alpine mt-3"
                    :columnDefs="columnWafOperator"
                    :alwaysShowHorizontalScroll="false"
                    :alwaysShowVarticalScroll="false"
                    :rowData="rowDataOperator.value"
                    style="width: 100%; height: 100%"
                    :overlayNoRowsTemplate="overlayTemplate"
                    @grid-ready="onGridReadyOperator"
                    :pagination="true"
                    :paginationPageSize="4"
                    :localeText="paginationLocalization"
                  />
                </v-col>

                <!-- <v-col cols="12" class="mb-n6" v-if="!state.isActivated">
                  <v-select
                    multiple
                    v-model="state.transformationFun"
                    :label="$t('Waf.transformations')"
                    :items="state.listTrans"
                    item-title="name"
                    item-value="slug"
                    return-object
                    :no-data-text="$t('certificat.certificatlist')"
                  ></v-select>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.transformationFun.$error"
                  >
                    {{ v$.transformationFun.$errors[0].$message }}
                  </p>
                </v-col> -->

                <!-- <v-col cols="4">
                  <label>{{ $t("Waf.activate") }}</label>
                </v-col>
                <v-col cols="8" class="mb-n6">
                  <input
                    type="checkbox"
                    hide-details
                    v-model="state.isActivated"
                  />
                  <label class="ml-2">{{ $t("Waf.useTransformation") }}</label>
                </v-col> -->

                <template v-if="!state.isActivated">
                  <v-col size="6" class="mt-2">
                    <label for="">{{ $t("Waf.transformations") }}</label>
                  </v-col>
                  <v-col cols="6" class="d-flex justify-end mb-n6">
                    <v-btn
                      color="#F6F6F6"
                      class="text-none"
                      variant="flat"
                      @click="addNewRowTransform"
                    >
                      <svg
                        width="17"
                        height="17"
                        viewBox="0 0 17 17"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <mask
                          id="mask0_50_190"
                          style="mask-type: luminance"
                          maskUnits="userSpaceOnUse"
                          x="0"
                          y="0"
                          width="17"
                          height="17"
                        >
                          <path d="M17 0H0V17H17V0Z" fill="white" />
                        </mask>
                        <g mask="url(#mask0_50_190)">
                          <path
                            d="M8.70871 0.219971C10.3463 0.219971 11.9472 0.705584 13.3088 1.6154C14.6705 2.52522 15.7317 3.81838 16.3584 5.33135C16.9851 6.84432 17.1491 8.50916 16.8296 10.1153C16.5101 11.7215 15.7215 13.1968 14.5636 14.3548C13.4056 15.5128 11.9302 16.3014 10.3241 16.6209C8.7179 16.9404 7.05306 16.7764 5.54009 16.1497C4.02712 15.523 2.73396 14.4617 1.82414 13.1001C0.914324 11.7385 0.428711 10.1376 0.428711 8.49997C0.428976 6.30406 1.30142 4.19816 2.85416 2.64542C4.4069 1.09268 6.5128 0.220236 8.70871 0.219971Z"
                            fill="#086EAE"
                          />
                          <path
                            d="M13.6689 8.03597C13.7332 8.09478 13.7842 8.16654 13.8187 8.24652C13.8531 8.32651 13.8703 8.41289 13.8689 8.49997C13.8703 8.58779 13.8542 8.675 13.8216 8.75654C13.789 8.83808 13.7405 8.91233 13.6789 8.97497C13.6167 9.04086 13.5412 9.09277 13.4574 9.12725C13.3736 9.16173 13.2835 9.178 13.1929 9.17497H9.36591V12.981C9.36918 13.0709 9.35391 13.1606 9.32105 13.2443C9.28819 13.3281 9.23845 13.4042 9.17491 13.468C9.11435 13.5295 9.04187 13.578 8.96191 13.6105C8.88195 13.643 8.7962 13.6588 8.70991 13.657C8.62268 13.6583 8.53614 13.6412 8.45599 13.6068C8.37585 13.5723 8.30391 13.5212 8.24491 13.457C8.18336 13.3943 8.13487 13.3201 8.10225 13.2385C8.06963 13.157 8.05354 13.0698 8.05491 12.982V9.17697H4.22791C4.04915 9.17414 3.87848 9.10194 3.75197 8.97562C3.62546 8.84929 3.553 8.67873 3.54991 8.49997C3.54829 8.41285 3.5653 8.32639 3.59979 8.24637C3.63428 8.16635 3.68546 8.09462 3.74991 8.03597C3.81266 7.97421 3.88704 7.92552 3.96876 7.89274C4.05047 7.85995 4.13788 7.84371 4.22591 7.84497H8.05491V4.03797C8.04956 3.85273 8.11789 3.67292 8.24491 3.53797C8.30487 3.47498 8.37701 3.42483 8.45694 3.39056C8.53688 3.35629 8.62294 3.33862 8.70991 3.33862C8.79688 3.33862 8.88294 3.35629 8.96288 3.39056C9.04281 3.42483 9.11495 3.47498 9.17491 3.53797C9.3023 3.67276 9.37099 3.85259 9.36591 4.03797V7.84497H13.1929C13.2809 7.84377 13.3683 7.86003 13.45 7.89281C13.5317 7.9256 13.6061 7.97426 13.6689 8.03597Z"
                            fill="white"
                          />
                        </g>
                      </svg>
                      <span class="ml-2" style="color: #086eae">{{
                        $t("buttons.Add")
                      }}</span>
                    </v-btn>
                  </v-col>
                  <v-col cols="12" class="mb-1 mt-0">
                    <ag-grid-vue
                      id="grid-wrapper"
                      domLayout="autoHeight"
                      class="ag-theme-alpine mt-3"
                      :columnDefs="columnWafTransform"
                      :alwaysShowHorizontalScroll="false"
                      :alwaysShowVarticalScroll="false"
                      :rowData="rowDataTransform.value"
                      style="width: 100%; height: 100%"
                      :overlayNoRowsTemplate="overlayTemplate"
                      @grid-ready="onGridReadyTransform"
                      :pagination="true"
                      :paginationPageSize="4"
                      :localeText="paginationLocalization"
                    />
                  </v-col>
                </template>

                <v-col cols="12" class="mb-n6">
                  <v-select
                    multiple
                    v-model="state.actions"
                    label="Actions *"
                    item-title="type"
                    item-value="slug"
                    return-object
                    :items="state.listActions"
                    :no-data-text="$t('certificat.certificatlist')"
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.actions.$error">
                    {{ v$.actions.$errors[0].$message }}
                  </p>
                </v-col>
                <!-- <v-col cols="12" class="d-flex justify-end mb-n6">
                  <v-btn
                    color="#F6F6F6"
                    class="text-none"
                    variant="flat"
                    @click="addNewRow"
                  >
                    <svg
                      width="17"
                      height="17"
                      viewBox="0 0 17 17"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <mask
                        id="mask0_50_190"
                        style="mask-type: luminance"
                        maskUnits="userSpaceOnUse"
                        x="0"
                        y="0"
                        width="17"
                        height="17"
                      >
                        <path d="M17 0H0V17H17V0Z" fill="white" />
                      </mask>
                      <g mask="url(#mask0_50_190)">
                        <path
                          d="M8.70871 0.219971C10.3463 0.219971 11.9472 0.705584 13.3088 1.6154C14.6705 2.52522 15.7317 3.81838 16.3584 5.33135C16.9851 6.84432 17.1491 8.50916 16.8296 10.1153C16.5101 11.7215 15.7215 13.1968 14.5636 14.3548C13.4056 15.5128 11.9302 16.3014 10.3241 16.6209C8.7179 16.9404 7.05306 16.7764 5.54009 16.1497C4.02712 15.523 2.73396 14.4617 1.82414 13.1001C0.914324 11.7385 0.428711 10.1376 0.428711 8.49997C0.428976 6.30406 1.30142 4.19816 2.85416 2.64542C4.4069 1.09268 6.5128 0.220236 8.70871 0.219971Z"
                          fill="#086EAE"
                        />
                        <path
                          d="M13.6689 8.03597C13.7332 8.09478 13.7842 8.16654 13.8187 8.24652C13.8531 8.32651 13.8703 8.41289 13.8689 8.49997C13.8703 8.58779 13.8542 8.675 13.8216 8.75654C13.789 8.83808 13.7405 8.91233 13.6789 8.97497C13.6167 9.04086 13.5412 9.09277 13.4574 9.12725C13.3736 9.16173 13.2835 9.178 13.1929 9.17497H9.36591V12.981C9.36918 13.0709 9.35391 13.1606 9.32105 13.2443C9.28819 13.3281 9.23845 13.4042 9.17491 13.468C9.11435 13.5295 9.04187 13.578 8.96191 13.6105C8.88195 13.643 8.7962 13.6588 8.70991 13.657C8.62268 13.6583 8.53614 13.6412 8.45599 13.6068C8.37585 13.5723 8.30391 13.5212 8.24491 13.457C8.18336 13.3943 8.13487 13.3201 8.10225 13.2385C8.06963 13.157 8.05354 13.0698 8.05491 12.982V9.17697H4.22791C4.04915 9.17414 3.87848 9.10194 3.75197 8.97562C3.62546 8.84929 3.553 8.67873 3.54991 8.49997C3.54829 8.41285 3.5653 8.32639 3.59979 8.24637C3.63428 8.16635 3.68546 8.09462 3.74991 8.03597C3.81266 7.97421 3.88704 7.92552 3.96876 7.89274C4.05047 7.85995 4.13788 7.84371 4.22591 7.84497H8.05491V4.03797C8.04956 3.85273 8.11789 3.67292 8.24491 3.53797C8.30487 3.47498 8.37701 3.42483 8.45694 3.39056C8.53688 3.35629 8.62294 3.33862 8.70991 3.33862C8.79688 3.33862 8.88294 3.35629 8.96288 3.39056C9.04281 3.42483 9.11495 3.47498 9.17491 3.53797C9.3023 3.67276 9.37099 3.85259 9.36591 4.03797V7.84497H13.1929C13.2809 7.84377 13.3683 7.86003 13.45 7.89281C13.5317 7.9256 13.6061 7.97426 13.6689 8.03597Z"
                          fill="white"
                        />
                      </g>
                    </svg>
                    <span class="ml-2" style="color: #086eae">{{
                      $t("buttons.Add")
                    }}</span>
                  </v-btn>
                </v-col> -->
                <v-col cols="12" class="mb-n5 mb-1 mt-0">
                  <ag-grid-vue
                    id="grid-wrapper"
                    domLayout="autoHeight"
                    class="ag-theme-alpine mt-3"
                    :columnDefs="columnWaf"
                    :alwaysShowHorizontalScroll="false"
                    :alwaysShowVarticalScroll="false"
                    :rowData="rowDataWaf.value"
                    style="width: 100%; height: 100%"
                    :overlayNoRowsTemplate="overlayTemplate"
                    @grid-ready="onGridReady"
                    :pagination="true"
                    :paginationPageSize="4"
                    :localeText="paginationLocalization"
                  />
                </v-col>

                <!-- <button @click="show">test</button> -->
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
            <span></span>
            <v-spacer></v-spacer>
            <v-btn
              color="indigo-darken-3"
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
              type="submit"
              color="indigo-darken-3"
              variant="flat"
              class="mt-3 btn-add"
            >
              <span class="text-white pr-3 pl-3" v-if="modalMode === 'create'">
                {{ $t("buttons.create") }}</span
              >
              <span class="text-white pr-3 pl-3" v-if="modalMode === 'edit'">
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
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import { useI18n } from "vue-i18n";
import axios from "axios";
import useValidate from "@vuelidate/core";
import { toRefs, ref, watch, onMounted, reactive, computed, inject } from "vue";
import { required, helpers, requiredIf } from "@vuelidate/validators";
import { getCookie } from "@/mixins/csrftoken.js";
import MultiSelectRenderVue from "../../views/waf/agGridSelectType/MultiSelectRenderVue.vue";

export default {
  components: {
    AgGridVue,
    MultiSelectRenderVue,
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
    modalMode: {
      required: true,
    },
  },

  setup(props) {
    const emitter = inject("emitter");
    onMounted(() => {
      overlayTemplate.value = `
      <span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
     </svg></span>`;
    });
    const { t } = useI18n();

    const { isOpen, editRow, modalMode } = toRefs(props);

    const rowDataWaf = ref([]);
    const rowDataTransform = ref([]);
    const rowDataOperator = ref([]);
    const paginationLocalization = reactive({
      of: "/",
    });
    const overlayTemplate = ref("");
    const gridApi = ref(null);
    const gridApiOperator = ref(null);
    const gridApiTransform = ref(null);
    const gridColumnApi = ref(null);

    const state = reactive({
      listVariable: [
        "ARGS",
        "ARGS_GET",
        "ARGS_POST",
        "FILES",
        "FULL_REQUEST",
        "QUERY_STRING",
        "REQUEST_BODY",
        "REQUEST_HEADERS",
        "REQUEST_METHOD",
        "REQUEST_URI",
      ],
      listOperator: [
        { type: "lt", value: "", slug: "lt" },
        { type: "detectSQLi", value: "", slug: "detectSQLi" },
        { type: "geoLookup", value: "", slug: "geoLookup" },
        { type: "noMatch", value: "", slug: "noMatch" },
        { type: "pm", value: "", slug: "pm" },
        { type: "pmf", value: "", slug: "pmf" },
        { type: "pmFromFile", value: "", slug: "pmFromFile" },
        { type: "rbl", value: "", slug: "rbl" },
        { type: "rx", value: "", slug: "rx" },
        { type: "rxGlobal", value: "", slug: "rxGlobal" },
        { type: "streq", value: "", slug: "streq" },
        { type: "strmatch", value: "", slug: "strmatch" },
        { type: "unconditionalMatch", value: "", slug: "unconditionalMatch" },
        { type: "validateByteRange", value: "", slug: "validateByteRange" },
        { type: "validateDTD", value: "", slug: "validateDTD" },
        { type: "validateHash", value: "", slug: "validateHash" },
        { type: "validateSchema", value: "", slug: "validateSchema" },
        { type: "validateUrlEncoding", value: "", slug: "validateUrlEncoding" },
        {
          type: "validateUtf8Encoding",
          value: "",
          slug: "validateUtf8Encoding",
        },
        { type: "verifyCC", value: "", slug: "verifyCC" },
        { type: "verifyCPF", value: "", slug: "verifyCPF" },
        { type: "verifySSN", value: "", slug: "verifySSN" },
        { type: "within", value: "", slug: "within" },
        { type: "beginsWith", value: "", slug: "beginsWith" },
        { type: "contains", value: "", slug: "contains" },
        { type: "containsWord", value: "", slug: "containsWord" },
        { type: "detectXSS", value: "", slug: "detectXSS" },
        { type: "endsWith", value: "", slug: "endsWith" },
        { type: "fuzzyHash", value: "", slug: "fuzzyHash" },
        { type: "eq", value: "", slug: "eq" },
        { type: "ge", value: "", slug: "ge" },
        { type: "gsbLookup", value: "", slug: "gsbLookup" },
        { type: "gt", value: "", slug: "gt" },
        { type: "inspectFile", value: "", slug: "inspectFile" },
        { type: "ipMatch", value: "", slug: "ipMatch" },
        { type: "ipMatchF", value: "", slug: "ipMatchF" },
        { type: "ipMatchFromFile", value: "", slug: "ipMatchFromFile" },
        { type: "le", value: "", slug: "le" },
        { type: "rsub", value: "", slug: "rsub" },
      ],

      listTrans: [
        { name: "base64Decode", slug: "t:base64Decode" },
        { name: "sqlHexDecode", slug: "t:sqlHexDecode" },
        { name: "base64DecodeExt", slug: "t:base64DecodeExt" },
        { name: "base64Encode", slug: "t:base64Encode" },
        { name: "cmdLine", slug: "t:cmdLine" },
        { name: "compressWhitespace", slug: "t:compressWhitespace" },
        { name: "cssDecode", slug: "t:cssDecode" },
        { name: "escapeSeqDecode", slug: "t:escapeSeqDecode" },
        { name: "hexDecode", slug: "t:hexDecode" },
        { name: "hexEncode", slug: "t:hexEncode" },
        { name: "htmlEntityDecode", slug: "t:htmlEntityDecode" },
        { name: "jsDecode", slug: "t:jsDecode" },
        { name: "length", slug: "t:length" },
        { name: "lowercase", slug: "t:lowercase" },
        { name: "md5", slug: "t:md5" },
        { name: "none", slug: "t:none" },
        { name: "normalisePath", slug: "t:normalisePath" },
        { name: "normalizePath", slug: "t:normalizePath" },
        { name: "normalisePathWin", slug: "t:normalisePathWin" },
        {
          name: "normalizePathWinparityEven7bit",
          slug: "t:normalizePathWinparityEven7bit",
        },
        { name: "parityOdd7bit", slug: "t:parityOdd7bit" },
        { name: "ParityZero7bit", slug: "t:ParityZero7bit" },
      ],
      listActions: [
        { type: "accuracy", value: "", slug: "accuracy" },
        { type: "allow", value: "", slug: "allow" },
        { type: "auditlog", value: "", slug: "auditlog" },
        { type: "block", value: "", slug: "block" },
        { type: "capture", value: "", slug: "capture" },
        { type: "chain", value: "", slug: "chain" },
        { type: "ctl", value: "", slug: "ctl" },
        { type: "deny", value: "", slug: "deny" },
        { type: "drop", value: "", slug: "drop" },
        { type: "exec", value: "", slug: "exec" },
        { type: "expirevar", value: "", slug: "expirevar" },
        { type: "id", value: "", slug: "id" },
        { type: "initcol", value: "", slug: "initcol" },
        { type: "log", value: "", slug: "log" },
        { type: "logdata", value: "", slug: "logdata" },
        { type: "maturity", value: "", slug: "maturity" },
        { type: "msg", value: "", slug: "msg" },
        { type: "multiMatch", value: "", slug: "multiMatch" },
        { type: "noauditlog", value: "", slug: "noauditlog" },
        { type: "nolog", value: "", slug: "nolog" },
        { type: "pass", value: "", slug: "pass" },
        { type: "phase", value: "", slug: "phase" },
        { type: "redirect", value: "", slug: "redirect" },
        { type: "rev", value: "", slug: "rev" },
        { type: "severity", value: "", slug: "severity" },
        { type: "setuslug", value: "", slug: "setuslug" },
        { type: "setrsc", value: "", slug: "setrsc" },
        { type: "setsslug", value: "", slug: "setsslug" },
        { type: "setenv", value: "", slug: "setenv" },
        { type: "setvar", value: "", slug: "setvar" },
        { type: "skip", value: "", slug: "skip" },
        { type: "skipAfter", value: "", slug: "skipAfter" },
        { type: "status", value: "", slug: "status" },
        { type: "t", value: "", slug: "t" },
        { type: "tag", value: "", slug: "tag" },
        { type: "ver", value: "", slug: "ver" },
        { type: "xmlns", value: "", slug: "xmlns" },
      ],
      loading: false,
      isLoadingDialogue: false,
      id: null,
      //
      snackbar: false,
      color: "",
      textAlert: "",
      openModal: false,

      variable: [],
      operator: [],
      transformationFun: [],
      description: "",
      ruleName: "",
      typeTransf: "",
      actions: [{ type: "id", value: "", slug: "id" }],
      existType: false,
      existTypeOperator: false,
      isActivated: false,
      description: "",
    });

    watch(
      () => isOpen.value,
      (val) => {
        state.openModal = val;
      }
    );
    watch(
      () => editRow.value,
      (val) => {
        populate(val);
      }
    );
    watch(
      () => modalMode.value,
      () => {
        if (modalMode.value === "create") {
          state.variable = [];
          state.ruleName = "";
          state.operator = [];
          state.transformationFun = [];
          state.isActivated = false;
          rowDataWaf.value = [];
          rowDataOperator.value = [];
          rowDataTransform.value = [];
          state.actions = [{ type: "id", value: "", slug: "id" }];
        }
      }
    );

    watch(
      () => state.actions,
      (val) => {
        if (val) {
          rowDataWaf.value = val;
          if (gridApi.value) {
            gridApi.value.setRowData(rowDataWaf.value);
          }
        }
      },
      { immediate: true }
    );
    watch(
      () => state.operator,
      (val) => {
        if (val) {
          rowDataOperator.value = val;
          if (gridApiOperator.value) {
            gridApiOperator.value.setRowData(rowDataOperator.value);
          }
        }
      },
      { immediate: true }
    );
    const value = computed(() => {
      return t("squid.value");
    });

    const columnWafTransform = ref([
      {
        headerName: value,
        field: "value",
        width: 90,
        minWidth: 50,
        flex: 1,
        editable: true,
      },
      {
        headerName: "Actions",
        cellRenderer: actionCellRendererTransform,
        width: 150,
      },
    ]);
    const columnWafOperator = ref([
      {
        headerName: "Type",
        field: "type",
        width: 90,
        minWidth: 50,
        flex: 1,
        editable: true,
      },
      {
        headerName: value,
        field: "value",
        width: 90,
        minWidth: 50,
        flex: 1,
        editable: true,
      },
      {
        headerName: "Actions",
        cellRenderer: actionCellRendererOperator,
        width: 150,
      },
    ]);
    const columnWaf = ref([
      {
        headerName: "Type",
        // cellEditor: MultiSelectRenderVue,
        field: "type",
        width: 90,
        minWidth: 50,
        flex: 1,
        // editable: true,
        // cellEditorParams: {
        // values: [

        // ],
        // formatValue: (value) => value.toUpperCase(),
        // cellRenderer: (params) => params.value.toUpperCase(),
        // searchDebounceDelay: 200,
        // onProtocolsSelected: (event) => {
        //   params.setValue(event);
        // },
        // },
      },
      {
        headerName: value,
        field: "value",
        width: 90,
        minWidth: 50,
        flex: 1,
        editable: true,
      },
      {
        headerName: "Actions",
        cellRenderer: actionCellRenderer,
        width: 150,
      },
    ]);

    const populate = (data) => {
      if (modalMode.value === "edit") {
        state.id = data.id;

        let mapedAction = data.actions.map((e) => {
          return {
            type: e.type,
            value: e.value,
            slug: e.type,
          };
        });
        let mapedOperator = data.operators.map((e) => {
          return {
            type: e.type,
            value: e.value,
            slug: e.type,
          };
        });
        state.operator = mapedOperator;
        state.actions = mapedAction;
        state.ruleName = data.name;
        state.description = data.description;
        state.variable = data.variables;
        if (data.transformations.length === 0) return;
        else {
          const index = state.listTrans.findIndex(
            (item) => item.name === data.transformations[0]
          );

          if (index !== -1) {
            state.isActivated = false;
            let filtredTrans = [];
            data?.transformations.forEach((e) => {
              filtredTrans = [
                ...filtredTrans,
                ...state.listTrans.filter((i) => i.name === e),
              ];
            });

            state.transformationFun = filtredTrans ?? [];
          } else {
            state.isActivated = true;
            let mappedTrans = data.transformations.map((e) => {
              return {
                value: e,
              };
            });
            rowDataTransform.value = mappedTrans;
          }
        }
      }
    };

    // function checkForDuplicateTypes(array) {
    //   const typesSet = new Set();

    //   for (const item of array) {
    //     if (typesSet.has(item.type)) {
    //       state.isTrueType = true;

    //       return `Error: Duplicate type found - ${item.type}`;
    //     } else {
    //       state.isTrueType = false;
    //     }
    //     typesSet.add(item.type);
    //   }

    //   return "No duplicate types found";
    // }

    function checkForEmptyProperties(arr) {
      for (let obj of arr) {
        if (
          (obj.type === "nolog" && obj.value === "") ||
          (obj.type === "allow" && obj.value === "") ||
          (obj.type === "auditlog" && obj.value === "") ||
          (obj.type === "block" && obj.value === "") ||
          (obj.type === "capture" && obj.value === "") ||
          (obj.type === "chain" && obj.value === "") ||
          (obj.type === "log" && obj.value === "") ||
          (obj.type === "noauditlog" && obj.value === "") ||
          (obj.type === "pass" && obj.value === "")
        ) {
          continue;
        }
        if (obj.type === "" || obj.value === "") {
          state.existType = obj.type;
          return true;
        }
      }
      return false;
    }
    const hasEmptyProperty = (obj) => {
      return obj.value === "";
    };
    function checkForEmptyPropertiesOperators(arr) {
      for (let obj of arr) {
        if (
          (obj.type === "detectSQLi" && obj.value === "") ||
          (obj.type === "geoLookup" && obj.value === "") ||
          (obj.type === "unconditionalMatch" && obj.value === "") ||
          (obj.type === "validateUtf8Encoding" && obj.value === "")
        ) {
          continue;
        }
        if (obj.type === "" || obj.value === "") {
          state.existTypeOperator = obj.type;
          return true;
        }
      }
      return false;
    }

    const closeModal = () => {
      emitter.emit("closeWafRuleModal");
      if (modalMode.value === "create") {
        state.variable = [];
        state.ruleName = "";
        state.operator = [];
        state.transformationFun = [];
        state.typeTransf = "";
        state.actions = [{ type: "id", value: "", slug: "id" }];
        rowDataTransform.value = [];
        rowDataWaf.value = [];
        rowDataOperator.value = [];
        state.isActivated = false;
      }
    };
    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const champInclude = computed(() => {
      return t("errors.ChampIncludeOnlyNumbers");
    });
    const indication = computed(() => {
      return t("champs.indication");
    });
    const rules = computed(() => {
      return {
        ruleName: {
          required: helpers.withMessage(error, required),
          isValidkeyName: helpers.withMessage(
            indication,
            helpers.regex(/^[A-Za-z0-9_\-]+$/)
          ),
        },

        // operator: {
        //   required: helpers.withMessage(error, required),
        // },

        variable: {
          required: helpers.withMessage(error, required),
        },
        // transformationFun: {
        //   required: helpers.withMessage(error, required),
        // },
        // typeTransf: {
        //   required: helpers.withMessage(error, required),
        // },
        actions: {
          required: helpers.withMessage(error, required),
        },
      };
    });

    const v$ = useValidate(rules, state);

    const show = () => {};

    const onGridReady = (params) => {
      gridApi.value = params.api;
      gridColumnApi.value = params.columnApi;
      if (gridApi.value) {
        gridApi.value.setRowData(rowDataWaf.value);
      }
    };
    const onGridReadyOperator = (params) => {
      gridApiOperator.value = params.api;
      gridColumnApi.value = params.columnApi;
      if (gridApiOperator.value) {
        gridApiOperator.value.setRowData(rowDataOperator.value);
      }
    };
    const onGridReadyTransform = (params) => {
      gridApiTransform.value = params.api;
      gridColumnApi.value = params.columnApi;
      if (gridApiTransform.value) {
        gridApiTransform.value.setRowData(rowDataTransform.value);
      }
    };
    const addNewRow = () => {
      const newRow = { type: "", value: "" };
      rowDataOperator.value.push(newRow);
      if (gridApiOperator.value) {
        gridApiOperator.value.setRowData(rowDataOperator.value);
      }
    };
    const addNewRowTransform = () => {
      const newRow = { value: "" };
      rowDataTransform.value.push(newRow);
      if (gridApiTransform.value) {
        gridApiTransform.value.setRowData(rowDataTransform.value);
      }
    };
    function actionCellRenderer(params) {
      let eGui = document.createElement("div");

      {
        eGui.innerHTML = `
        <button
          class="action-button delete"
          data-action="delete">
            <i class="fas fa-times" style="color: #086eae; font-size: 20px;"></i>
        </button>

            `;
      }
      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          handleAction(action, params.node.data, params.node.rowIndex);
        });
      });

      return eGui;
    }
    const handleAction = (action, rowData, index) => {
      switch (action) {
        case "delete":
          const index = rowDataWaf.value.findIndex(
            (item) => item.type === rowData.type
          );

          if (index !== -1) {
            rowDataWaf.value.splice(index, 1);
            if (gridApi.value) {
              gridApi.value.setRowData(rowDataWaf.value);
            }
          }
          break;
        default:
          break;
      }
    };
    function actionCellRendererOperator(params) {
      let eGui = document.createElement("div");

      {
        eGui.innerHTML = `
        <button
          class="action-button delete"
          data-action="delete">
            <i class="fas fa-times" style="color: #086eae; font-size: 20px;"></i>
        </button>

            `;
      }
      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          handleActionOperator(action, params.node.data, params.node.rowIndex);
        });
      });

      return eGui;
    }
    const handleActionOperator = (action, rowData, index) => {
      switch (action) {
        case "delete":
          const index = rowDataOperator.value.findIndex(
            (item) => item.type === rowData.type
          );

          if (index !== -1) {
            rowDataOperator.value.splice(index, 1);
            if (gridApiOperator.value) {
              gridApiOperator.value.setRowData(rowDataOperator.value);
            }
          }
          break;
        default:
          break;
      }
    };
    function actionCellRendererTransform(params) {
      let eGui = document.createElement("div");

      {
        eGui.innerHTML = `
        <button
          class="action-button delete"
          data-action="delete">
            <i class="fas fa-times" style="color: #086eae; font-size: 20px;"></i>
        </button>

            `;
      }
      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          handleActionTransform(action, params.node.data, params.node.rowIndex);
        });
      });

      return eGui;
    }
    const handleActionTransform = (action, rowData, index) => {
      switch (action) {
        case "delete":
          const index = rowDataTransform.value.findIndex(
            (item) => item.type === rowData.type
          );

          if (index !== -1) {
            rowDataTransform.value.splice(index, 1);
            if (gridApiTransform.value) {
              gridApiTransform.value.setRowData(rowDataTransform.value);
            }
          }
          break;
        default:
          break;
      }
    };

    const restartNginx = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      axios.post("/waf/restartNginx");
    };

    const submitForm = async () => {
      const result = await v$.value.$validate();
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      if (result) {
        var isArrayEmpty = rowDataWaf.value.length === 0;
        if (isArrayEmpty) {
          state.snackbar = true;
          state.color = "red";
          state.textAlert = t("errors.emptyArray");
          return;
        } else if (checkForEmptyProperties(rowDataWaf.value)) {
          state.snackbar = true;
          state.color = "red";
          state.textAlert = `${state.existType} ${t("errors.emptyValue")}`;
          return;
        } else if (checkForEmptyPropertiesOperators(rowDataOperator.value)) {
          state.snackbar = true;
          state.color = "red";
          state.textAlert = `${state.existTypeOperator} ${t(
            "errors.emptyValue"
          )}`;
          return;
        } else {
          var hasEmptyElement = rowDataTransform.value.some(hasEmptyProperty);

          if (hasEmptyElement) {
            state.snackbar = true;
            state.color = "red";
            state.textAlert = t("errors.atLeastemptyValue");
            return;
          }
        }

        let mapedRow = rowDataWaf.value.map((e) => {
          return {
            type: e.type,
            value: e.value,
          };
        });
        let mapedOperator = state.operator.map((e) => {
          return {
            type: e.type,
            value: e.value,
          };
        });

        if (!state.isActivated) {
          var mapedRowTransf = state.transformationFun.map((e) => e.name);
        } else if (state.isActivated) {
          var mapedRowTransfType = rowDataTransform.value.map((e) => e.value);
        }

        let payload = {
          name: state.ruleName,
          variables: state.variable,
          operators: mapedOperator,

          transformations: !state.isActivated
            ? mapedRowTransf
            : mapedRowTransfType,
          actions: mapedRow,
          description: state.description,
        };

        if (modalMode.value === "edit") {
          axios
            .put(`/waf/updateRuleWaf/${state.id}`, payload)
            .then((response) => {
              if (response.status == "201") {
                // state.snackbar = true;
                // state.color = "success";
                // state.textAlert = response.data.msg;
                // setTimeout(() => {
                //   location.reload();
                // }, 1000);
                restartNginx();
                state.loading = true;
                state.isLoadingDialogue = true;
                setTimeout(() => {
                  state.loading = false;
                  state.isLoadingDialogue = false;
                  state.snackbar = true;
                  state.color = "success";
                  state.textAlert = response.data.msg;
                  closeModal();
                }, 10000);
                setTimeout(() => {
                  location.reload();
                }, 10000);
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
          axios
            .post("/waf/createRuleWaf", payload)
            .then((response) => {
              if (response.status == "201") {
                restartNginx();
                state.loading = true;
                state.isLoadingDialogue = true;
                setTimeout(() => {
                  state.loading = false;
                  state.isLoadingDialogue = false;
                  state.snackbar = true;
                  state.color = "success";
                  state.textAlert = response.data.msg;
                  closeModal();
                }, 10000);
                setTimeout(() => {
                  location.reload();
                }, 10000);
                // state.openModal = false;
                // state.snackbar = true;
                // state.color = "success";
                // state.textAlert = response.data.msg;

                // setTimeout(() => {
                //   location.reload();
                // }, 1000);
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
        }
      } else {
        var isArrayEmpty = rowDataWaf.value.length === 0;
        if (isArrayEmpty) {
          state.snackbar = true;
          state.color = "red";
          state.textAlert = t("errors.emptyArray");
          return;
        } else if (checkForEmptyProperties(rowDataWaf.value)) {
          state.snackbar = true;
          state.color = "red";
          state.textAlert = `${state.existType} ${t("errors.emptyValue")}`;
          return;
        } else if (checkForEmptyPropertiesOperators(rowDataOperator.value)) {
          state.snackbar = true;
          state.color = "red";
          state.textAlert = `${state.existTypeOperator} ${t(
            "errors.emptyValue"
          )}`;
          return;
        } else {
          var hasEmptyElement = rowDataTransform.value.some(hasEmptyProperty);

          if (hasEmptyElement) {
            state.snackbar = true;
            state.color = "red";
            state.textAlert = t("errors.atLeastemptyValue");
            return;
          }
        }
      }
    };



    return {
      rowDataOperator,
      gridApiTransform,
      onGridReadyTransform,
      addNewRowTransform,
      rowDataTransform,
      columnWafTransform,
      columnWafOperator,
      state,
      columnWaf,
      rowDataWaf,
      paginationLocalization,
      overlayTemplate,
      gridColumnApi,
      gridApi,
      emitter,
      v$,
      closeModal,
      onGridReady,
      onGridReadyOperator,
      submitForm,
      addNewRow,
      show,
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
.scroller {
  overflow: auto;
}
</style>
