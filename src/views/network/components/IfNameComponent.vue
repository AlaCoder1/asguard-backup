<template>
  <v-dialog v-model="deleteDialog" max-width="500px">
    <v-card>
      <v-card-title class="headline">{{
        $t("delete.DeleteConfirmation")
      }}</v-card-title>
      <v-card-text>{{ $t("delete.deleteRow") }} ?</v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="cancelDelete">{{
          $t("buttons.cancel")
        }}</v-btn>
        <v-btn color="blue darken-1" text @click="confirmDelete">{{
          $t("buttons.delete")
        }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-overlay v-model="viewModal">
    <v-dialog v-model="isviewModal" :scrim="false" width="auto">
      <v-card color="#193286" class="alert-box">
        <v-card-title class="img-containter">
          <img
            src="@/assets/images/view.png"
            alt="logo"
            class="img-view"
            width="100"
            height="100"
        /></v-card-title>
        <v-card-text>
          {{ $t("profil.NoPermission") }}
          <br />
          {{ $t("profil.ContactAdmin") }}
        </v-card-text>

        <div class="mr-3 mb-5 d-flex justify-end">
          <VButton
            rounded
            outlined
            color="#ffffff"
            label-color="#213E9F"
            :label="$t('buttons.close')"
            :isLarge="true"
            @click="close"
          />
        </div>
      </v-card>
    </v-dialog>
  </v-overlay>
  <v-card class="mt-5">
    <v-overlay v-model="loading">
      <v-dialog
        v-model="isLoadingDialogue"
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

    <v-form @submit.prevent="handleSubmit(onSubmit)">
      <v-row class="fill-height ml-3">
        <v-col cols="12" sm="6">
          <v-card-title class="title-text" style="margin-left: -5px">{{
            $t("interface.basicConfiguration")
          }}</v-card-title>
          <v-divider class="ml-3"></v-divider>
          <v-row class="px-0 mx-0 mt-3">
            <!-- <div style="color: black">Interface</div>
            <input type="checkbox" class="ml-5" v-model="activate" />
            <label class="ml-5">{{ $t("interface.activate") }}</label> -->

            <!-- <v-col cols="4">
              <label>Interface</label>
            </v-col>
            <v-col cols="4" class="mb-n6">
              <input type="checkbox" disabled v-model="activate" />
              <label class="ml-2">{{ $t("interface.activate") }}</label>
            </v-col> -->
          </v-row>

          <div class="px-0 mx-0">
            <v-row class="px-0 mx-0 mt-5">
              <v-col class="device-style"
                >{{ $t("interface.device")
                }}<span style="color: red">*</span></v-col
              >
            </v-row>
            <v-row class="ml-2 mr-3 mb-n6">
              <v-text-field :model-value="device" readonly></v-text-field>
            </v-row>
          </div>
          <div class="">
            <v-row class="px-0 mx-0 mt-5">
              <v-col class="device-style">Description </v-col>
            </v-row>
            <v-row class="ml-2 mr-3">
              <v-text-field v-model="description"></v-text-field>
            </v-row>
          </div>
          <v-card-title class="title-text mt-5" style="margin-left: -5px">{{
            $t("interface.genericConfiguration")
          }}</v-card-title>
          <v-divider class="ml-3 mb-5"></v-divider>

          <v-row class="px-0 mb-2">
            <v-col cols="4" class="ml-3">
              <label>{{ $t("interface.blockNetworks") }}</label>
            </v-col>
            <v-col cols="4" class="mb-n6">
              <input type="checkbox" v-model="private_aux" />
              <label class="ml-2">{{ $t("interface.private") }}</label>
            </v-col>
            <v-col cols="4" class="ml-3">
              <label>{{ $t("interface.blockBogonAddresses") }}</label>
            </v-col>
            <v-col cols="4" class="mb-n6">
              <input type="checkbox" v-model="bogon_aux" />
              <label class="ml-2">{{
                $t("interface.notAssignedByIANA")
              }}</label>
            </v-col>
          </v-row>
          <table class="ml-3">
            <tbody>
              <!-- <tr>
                <td>
                  <div>{{ $t("interface.blockNetworks") }}</div>
                </td>
                <td>
                  <input type="checkbox" v-model="private_aux" class="ml-5" />
                  <label>{{ $t("interface.private") }}</label>
                </td>
              </tr>
              <tr>
                <td>
                  <div class="mt-5">
                    {{ $t("interface.blockBogonAddresses") }}
                  </div>
                </td>
                <td>
                  <input type="checkbox" v-model="bogon_aux" class="ml-5" />
                  <label>{{ $t("interface.notAssignedByIANA") }}</label>
                </td>
              </tr> -->
              <tr>
                <td>
                  <div class="mt-n4">
                    {{ $t("interface.IPV4SetupType") }}
                    <span style="color: red">*</span>
                  </div>
                </td>
                <td class="new-style">
                  <v-select
                    :readonly="is_main"
                    :label="$t('interface.IPV4SetupType')"
                    background-color="#f6f6f6"
                    v-model="setuptypeip4"
                    :items="items"
                    item-value="id"
                    item-title="value"
                    return-object
                    class="ml-3"
                    :rules="[(v) => !!v || $t('interface.IPV4Required')]"
                    :no-data-text="$t('certificat.certificatlist')"
                  ></v-select>
                </td>
              </tr>
              <tr>
                <td>
                  <div style="color: #020202" class="mt-n4">
                    {{ $t("interface.MACAddress") }}
                  </div>
                </td>
                <td>
                  <v-text-field
                    :readonly="is_vxlan_vlan"
                    :label="$t('interface.MACAddress')"
                    class="ml-3"
                    v-model="addmac"
                  ></v-text-field>
                </td>
              </tr>
              <tr>
                <td></td>
                <td>
                  <p
                    style="margin-top: -10px; margin-left: 12px"
                    class="error-feedback ml-4"
                    v-if="!isValidAddmac"
                  >
                    {{ $t("errors.validAddmac") }}
                  </p>
                </td>
              </tr>
              <tr>
                <td>
                  <div class="mt-n4">{{ $t("interface.MTU") }}</div>
                </td>
                <td>
                  <v-text-field
                    :readonly="is_vxlan_vlan"
                    :label="$t('interface.MTU')"
                    class="ml-3"
                    v-model="mtuv"
                  ></v-text-field>
                </td>
              </tr>

              <tr>
                <td></td>
                <td>
                  <p
                    style="margin-top: -10px; margin-left: 12px"
                    class="error-feedback ml-4"
                    v-if="!isValidMTU"
                  >
                    {{ $t("errors.validMTU") }}
                  </p>
                </td>
              </tr>

              <tr>
                <td>
                  <div class="mt-n4">{{ $t("interface.MSS") }}</div>
                </td>
                <td>
                  <v-text-field
                    :readonly="is_vxlan_vlan"
                    :label="$t('interface.MSS')"
                    class="ml-3"
                    v-model="mssv"
                  ></v-text-field>
                </td>
              </tr>

              <tr>
                <td></td>
                <td>
                  <p
                    style="margin-top: -10px; margin-left: 12px"
                    class="error-feedback ml-4"
                    v-if="!isValidMSS"
                  >
                    {{ $t("errors.validMSS") }}
                  </p>
                </td>
              </tr>

              <tr>
                <td>
                  <div style="color: #020202" class="mt-n4">
                    {{ $t("interface.speedAndDuplex") }}
                  </div>
                </td>
                <td>
                  <v-select
                    :readonly="is_vxlan_vlan"
                    :label="$t('interface.speedAndDuplex')"
                    v-model="speed_duplex"
                    :items="speedDuplexItems.map((item) => item)"
                    class="ml-3 speed-duplex-style"
                    :no-data-text="$t('certificat.certificatlist')"
                  ></v-select>
                </td>
              </tr>
            </tbody>
          </table>
        </v-col>
        <v-col cols="12" sm="6">
          <div v-if="setuptypeip4?.slug === 'static'">
            <v-card-title class="title-text" style="margin-left: -5px">{{
              $t("interface.staticIPV4AddressConfiguration")
            }}</v-card-title>
            <v-divider class="ml-3 mr-3"></v-divider>
            <div class="mr-2 ml-2">
              <v-row class="mt-2">
                <v-col align-self="center" cols="3">
                  <label>{{ $t("interface.IPV4Address") }}</label>
                  <small style="color: red">*</small>
                </v-col>
                <v-col cols="4" class="mb-n6">
                  <v-text-field
                    :readonly="is_main"
                    :label="$t('interface.IPV4Address')"
                    v-model="value_setup_Ipv4.ip_address4"
                    class="ip-address-style"
                    :rules="[
                      (v) => !!v || $t('interface.IPV4AddressRequired'),
                      () => ipAddressValidation(value_setup_Ipv4.ip_address4),
                    ]"
                  ></v-text-field>
                </v-col>
                <v-col cols="4" class="mb-n6">
                  <v-select
                    :readonly="is_main"
                    :label="$t('sdwan.prefix')"
                    v-model="value_setup_Ipv4.netmask4"
                    :items="netmaskItems"
                    class="ml-3 netmask-select-style"
                    :rules="[(v) => !!v || $t('interface.netmaskRequired')]"
                    :no-data-text="$t('certificat.certificatlist')"
                  ></v-select>
                </v-col>
                <v-col align-self="center" cols="3">
                  <label>{{ $t("interface.iPv4gateway") }}</label>
                  <small style="color: red">*</small>
                </v-col>
                <v-col cols="3" class="mb-n6 ml-3 mt-3">
                  <v-btn
                    :disabled="is_main"
                    color="#F6F6F6"
                    class="text-none"
                    variant="flat"
                    @click="openGatewayDialog"
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
                    <span class="ml-1" style="color: #086eae">{{
                      $t("interface.add")
                    }}</span>
                  </v-btn>
                </v-col>
                <v-col cols="5" class="mb-n6">
                  <v-select
                    :readonly="is_main"
                    v-model="value_setup_Ipv4.gateway4.value"
                    :items="allStaticGateways"
                    item-title="gwaddress"
                    item-value="id"
                    return-object
                    :rules="[(v) => !!v || $t('interface.IPV4GatewayRequired')]"
                    :no-data-text="$t('certificat.certificatlist')"
                    label="Select Item"
                  >
                    <template v-slot:item="{ props, index, item }">
                      <v-list-item v-bind="props">
                        <template v-slot:prepend>
                          <v-text-item :v-html="item?.raw?.gwaddress">
                          </v-text-item>
                        </template>
                        <template v-slot:append>
                          <v-btn
                            v-if="item?.raw?.gwaddress != 'Auto Detect'"
                            icon
                            color="red"
                            class="mr-3 d-flex align-center text-center"
                            style="width: 26px; height: 26px"
                            @click.stop="deleteGateway(item?.raw?.id)"
                          >
                            <v-icon
                              style="width: 16px; height: 16px; font-size: 16px"
                              small
                              >mdi-delete</v-icon
                            >
                          </v-btn>
                        </template>
                      </v-list-item>
                    </template>
                  </v-select>
                </v-col>
              </v-row>
            </div>
          </div>
          <div v-if="setuptypeip4?.slug === 'dhcp'">
            <v-card-title class="title-text">{{
              $t("interface.configuringDHCP")
            }}</v-card-title>
            <v-divider class="ml-3"></v-divider>
            <!-- <ConfigDHCPv4
              :ipAddress="value_setup_Ipv4.ip_address4"
              v-model:alias_add="interface.alias_add"
              v-model:alias_mask="interface.alias_mask"
              v-model:rejectLeases="interface.rejectLeases"
              v-model:hostname="interface.hostname"
              v-model:overrideMTU="interface.overrideMTU"
            /> -->
            <!--  -->
            <v-row>
              <v-col cols="12">
                <div class="mr-2 ml-2">
                  <v-row class="mt-2">
                    <v-col cols="12">
                      <v-text-field
                        v-model="value_setup_Ipv4.ip_address4"
                        :label="$t('interface.IPV4Address')"
                        variant="outlined"
                        readonly
                      ></v-text-field>
                    </v-col>
                    <v-col align-self="center" cols="4">
                      <label class="ml-2">{{
                        $t("interface.IPV4Address")
                      }}</label>
                    </v-col>
                    <v-col cols="4" class="mb-n6">
                      <v-text-field
                        :label="$t('interface.IPV4Address')"
                        v-model="interface.alias_add"
                      />
                    </v-col>
                    <v-col cols="4" class="mb-n6">
                      <v-select
                        :label="$t('sdwan.prefix')"
                        v-model="interface.alias_mask"
                        :items="netmaskItems"
                        :no-data-text="$t('certificat.certificatlist')"
                        class="ml-3"
                      ></v-select>
                    </v-col>
                    <v-col cols="12" class="mb-n6" v-if="!isValidIPV4Address">
                      <p
                        class="error-feedback"
                        style="margin-top: -10px; margin-left: 35%"
                      >
                        {{ messageValidIPV4Address }}
                      </p>
                    </v-col>
                    <v-col
                      cols="12"
                      class="mb-n6"
                      v-if="
                        isValidIPV4Address &&
                        interface.alias_add &&
                        !interface.alias_mask
                      "
                    >
                      <p
                        class="error-feedback"
                        style="margin-top: -10px; margin-left: 70%"
                      >
                        {{ $t("errors.valueRequired") }}
                      </p>
                    </v-col>
                    <v-col align-self="center" cols="4">
                      <label class="ml-2">{{
                        $t("interface.rejectLeasesFrom")
                      }}</label>
                    </v-col>
                    <v-col cols="8" class="mb-n6">
                      <v-text-field
                        :label="$t('interface.rejectLeasesFrom')"
                        v-model="interface.rejectLeases"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12" class="mb-n6" v-if="!isValidRejectAddress">
                      <p
                        class="error-feedback"
                        style="margin-top: -10px; margin-left: 35%"
                      >
                        {{ messageRejectAddress }}
                      </p>
                    </v-col>
                    <v-col align-self="center" cols="4">
                      <label class="ml-2">{{ $t("interface.hostname") }}</label>
                    </v-col>
                    <v-col cols="8" class="mb-n6">
                      <v-text-field
                        :label="$t('interface.hostname')"
                        v-model="interface.hostname"
                      ></v-text-field>
                    </v-col>

                    <v-col cols="12" class="mb-n6" v-if="!isValidHostname">
                      <p
                        class="error-feedback"
                        style="margin-top: -10px; margin-left: 35%"
                      >
                        {{ messageValidHostnameAddress }}
                      </p>
                    </v-col>
                  </v-row>
                </div>
              </v-col>
            </v-row>
            <!--  -->
            <v-row class="advanced-parameters-style">
              <label class="ml-3">{{
                $t("interface.advancedParameters")
              }}</label>
              <input
                type="checkbox"
                id="advancedParameters"
                name="advancedParameters"
                value="true"
                v-model="advancedParameters"
                class="ml-3"
              />
            </v-row>
            <!-- advanced -->

            <div v-if="advancedParameters">
              <v-card-title class="title-text">{{
                $t("interface.protocolTiming")
              }}</v-card-title>
              <v-divider class="ml-3"></v-divider>
              <table class="ml-3 mt-3 mr-5">
                <tbody>
                  <tr>
                    <td class="">
                      <span style="color: black" class="">{{
                        $t("interface.timeout")
                      }}</span>
                    </td>
                    <td>
                      <v-text-field
                        :label="$t('interface.timeout')"
                        class="ml-3 mt-1"
                        v-model="AdvancedConfigDHCPv4.timeout"
                      ></v-text-field>
                    </td>
                  </tr>
                  <tr>
                    <td></td>
                    <td>
                      <p
                        style="margin-top: -10px; margin-left: 12px"
                        class="error-feedback ml-4"
                        v-if="!isValidTimeout"
                      >
                        {{ $t("errors.ChampIncludeOnlyNumbersOrFloat") }}
                      </p>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <span style="color: black">{{
                        $t("interface.tryAgain")
                      }}</span>
                    </td>
                    <td style="width: 80%">
                      <v-text-field
                        :label="$t('interface.tryAgain')"
                        class="ml-3 mt-1"
                        v-model="AdvancedConfigDHCPv4.retry"
                      ></v-text-field>
                    </td>
                  </tr>
                  <tr>
                    <td></td>
                    <td>
                      <p
                        style="margin-top: -10px; margin-left: 12px"
                        class="error-feedback ml-4"
                        v-if="!isValidRetry"
                      >
                        {{ $t("errors.ChampIncludeOnlyNumbersOrFloat") }}
                      </p>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <span style="color: black; width: 50%" class="">{{
                        $t("interface.selectExpiration")
                      }}</span>
                    </td>
                    <td style="width: 50%">
                      <v-text-field
                        :label="$t('interface.selectExpiration')"
                        class="ml-3 mt-1"
                        v-model="AdvancedConfigDHCPv4.select_timeout"
                      ></v-text-field>
                    </td>
                  </tr>
                  <tr>
                    <td></td>
                    <td>
                      <p
                        style="margin-top: -10px; margin-left: 12px"
                        class="error-feedback ml-4"
                        v-if="!isValidSelectTimeout"
                      >
                        {{ $t("errors.ChampIncludeOnlyNumbersOrFloat") }}
                      </p>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <span style="color: black" class="">{{
                        $t("interface.restart")
                      }}</span>
                    </td>
                    <td style="width: 80%">
                      <v-text-field
                        :label="$t('interface.restart')"
                        class="ml-3 mt-1"
                        v-model="AdvancedConfigDHCPv4.reboot"
                      ></v-text-field>
                    </td>
                  </tr>
                  <tr>
                    <td></td>
                    <td>
                      <p
                        style="margin-top: -10px; margin-left: 12px"
                        class="error-feedback ml-4"
                        v-if="!isValidReboot"
                      >
                        {{ $t("errors.ChampIncludeOnlyNumbersOrFloat") }}
                      </p>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <span style="color: black" class="">{{
                        $t("interface.backoffCutoff")
                      }}</span>
                    </td>
                    <td style="width: 80%">
                      <v-text-field
                        :label="$t('interface.backoffCutoff')"
                        class="ml-3 mt-1"
                        v-model="AdvancedConfigDHCPv4.backoff"
                      ></v-text-field>
                    </td>
                  </tr>
                  <tr>
                    <td></td>
                    <td>
                      <p
                        style="margin-top: -10px; margin-left: 12px"
                        class="error-feedback ml-4"
                        v-if="!isValidBackoff"
                      >
                        {{ $t("errors.ChampIncludeOnlyNumbersOrFloat") }}
                      </p>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <span style="color: black" class="">{{
                        $t("interface.initialInterval")
                      }}</span>
                    </td>
                    <td style="width: 80%">
                      <v-text-field
                        :label="$t('interface.initialInterval')"
                        class="ml-3 mt-1"
                        v-model="AdvancedConfigDHCPv4.initial_interval"
                      ></v-text-field>
                    </td>
                  </tr>
                  <tr>
                    <td></td>
                    <td>
                      <p
                        style="margin-top: -10px; margin-left: 12px"
                        class="error-feedback ml-4"
                        v-if="!isValidInitialInterval"
                      >
                        {{ $t("errors.ChampIncludeOnlyNumbersOrFloat") }}
                      </p>
                    </td>
                  </tr>
                </tbody>
              </table>
              <v-card-title class="title-text">{{
                $t("interface.leaseRequirements")
              }}</v-card-title>
              <v-divider class="ml-3"></v-divider>
              <table class="ml-3 mt-3 mr-5">
                <tbody>
                  <tr>
                    <td>
                      <span style="color: black" class="">{{
                        $t("interface.sendOptions")
                      }}</span>
                    </td>
                    <td style="width: 70%">
                      <v-text-field
                        class="ml-3 mt-1"
                        :label="$t('interface.sendOptions')"
                        v-model="AdvancedConfigDHCPv4.dhcp_client"
                      ></v-text-field>
                    </td>
                  </tr>
                  <tr>
                    <td></td>
                    <td>
                      <p
                        style="margin-top: -10px; margin-left: 12px"
                        class="error-feedback ml-4"
                        v-if="!isValidDhcp_client"
                      >
                        {{ $t("errors.validAddmac") }}
                      </p>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <span style="color: black" class="">{{
                        $t("interface.sendOptionsLeaseTime")
                      }}</span>
                    </td>
                    <td style="width: 70%">
                      <v-text-field
                        class="ml-3 mt-1"
                        :label="$t('interface.sendOptionsLeaseTime')"
                        v-model="AdvancedConfigDHCPv4.lease_time"
                      ></v-text-field>
                    </td>
                  </tr>
                  <tr>
                    <td></td>
                    <td>
                      <p
                        style="margin-top: -10px; margin-left: 12px"
                        class="error-feedback ml-4"
                        v-if="!isValidLease_time"
                      >
                        {{ $t("errors.ChampIncludeOnlyNumbersOrFloat") }}
                      </p>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <span style="color: black" class="">{{
                        $t("interface.requestOptions")
                      }}</span>
                    </td>
                    <td style="width: 70%">
                      <v-text-field
                        class="ml-3 mt-1"
                        :label="$t('interface.requestOptions')"
                        v-model="AdvancedConfigDHCPv4.request"
                      ></v-text-field>
                    </td>
                  </tr>
                  <tr>
                    <td></td>
                    <td>
                      <p
                        style="margin-top: -10px; margin-left: 12px"
                        class="error-feedback ml-4"
                        v-if="!isValidRequest"
                      >
                        {{ $t("champs.champletter") }}
                      </p>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <span style="color: black" class="">{{
                        $t("interface.requiredOptions")
                      }}</span>
                    </td>
                    <td style="width: 70%">
                      <v-text-field
                        class="ml-3 mt-1"
                        :label="$t('interface.requiredOptions')"
                        v-model="AdvancedConfigDHCPv4.require"
                      ></v-text-field>
                    </td>
                  </tr>
                  <tr>
                    <td></td>
                    <td>
                      <p
                        style="margin-top: -10px; margin-left: 12px"
                        class="error-feedback ml-4"
                        v-if="!isValidRequire"
                      >
                        {{ $t("champs.champletter") }}
                      </p>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <span style="color: black" class="">{{
                        $t("interface.supersedeDomaineName")
                      }}</span>
                    </td>
                    <td style="width: 70%">
                      <v-text-field
                        class="ml-3 mt-1"
                        :label="$t('interface.supersedeDomaineName')"
                        v-model="AdvancedConfigDHCPv4.domain_name"
                      ></v-text-field>
                    </td>
                  </tr>
                  <tr>
                    <td></td>
                    <td>
                      <p
                        style="margin-top: -10px; margin-left: 12px"
                        class="error-feedback ml-4"
                        v-if="!isValidDomain_name"
                      >
                        {{ $t("errors.validHostname") }}
                      </p>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <span style="color: black" class="">{{
                        $t("interface.prependDomainServer")
                      }}</span>
                    </td>
                    <td style="width: 70%">
                      <v-text-field
                        class="ml-3 mt-1"
                        :label="$t('interface.prependDomainServer')"
                        v-model="AdvancedConfigDHCPv4.domain_server"
                      ></v-text-field>
                    </td>
                  </tr>
                  <tr>
                    <td></td>
                    <td>
                      <p
                        style="margin-top: -10px; margin-left: 12px"
                        class="error-feedback ml-4"
                        v-if="!isValidDomain_server"
                      >
                        {{ $t("errors.formatMustBeLikeAdresseIP") }}
                      </p>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <!--  -->
            <!-- <AdvancedConfigDHCPv4
              v-if="advancedParameters"
              v-model:typeDHCP4="typeDHCP4"
              v-model:timeout="AdvancedConfigDHCPv4.timeout"
              v-model:retry="AdvancedConfigDHCPv4.retry"
              v-model:select_timeout="AdvancedConfigDHCPv4.select_timeout"
              v-model:reboot="AdvancedConfigDHCPv4.reboot"
              v-model:backoff="AdvancedConfigDHCPv4.backoff"
              v-model:initial_interval="AdvancedConfigDHCPv4.initial_interval"
              v-model:dhcp_client="AdvancedConfigDHCPv4.dhcp_client"
              v-model:lease_time="AdvancedConfigDHCPv4.lease_time"
              v-model:request="AdvancedConfigDHCPv4.request"
              v-model:require="AdvancedConfigDHCPv4.require"
              v-model:domain_name="AdvancedConfigDHCPv4.domain_name"
              v-model:domain_server="AdvancedConfigDHCPv4.domain_server"
            /> -->
          </div>
        </v-col>
      </v-row>
      <div class="text-start ml-8 mt-10">
        <span class="text-sm">
          <span class="text-red text-lg">*</span>
          {{ $t("errors.oblig") }}</span
        >
      </div>
      <v-spacer></v-spacer><v-spacer></v-spacer>
      <div class="text-center">
        <VButton
          large
          rounded
          outlined
          color="#FFFF"
          label-color="#213E9F"
          :label="$t('interface.cancel')"
          :isLarge="true"
          @click="cancel"
        />
        <VButton
          large
          rounded
          outlined
          color="#213E9F"
          label-color="#ffff"
          :label="$t('interface.save')"
          :isLarge="true"
          type="submit"
          class="ml-2"
        />
      </div>
      <br /><br /><br />
      <v-alert
        type="success"
        class="d-flex mt-3"
        style="align-self: flex-end"
        elevation="2"
        icon="mdi-check-circle-outline"
        border="top"
        v-if="showAlertGateway"
        :style="alertStyle"
      >
        {{ message }}
      </v-alert>
      <v-alert
        type="success"
        class="d-flex mt-3"
        style="align-self: flex-end"
        elevation="2"
        icon="mdi-check-circle-outline"
        border="top"
        v-if="showAlert"
        :style="alertStyle"
      >
        {{ message }}
      </v-alert>
      <v-dialog
        v-model="showGatewayDialog"
        max-width="600px"
        class="gateway-dialog"
      >
        <v-card class="ml-3 mr-3">
          <v-card-title class="title-text">
            <span class="headline font-weight-bold">
              {{ $t("interface.addIPv4Gateway") }}
            </span>
          </v-card-title>
          <v-card-text>
            <v-form>
              <v-container>
                <v-row>
                  <v-text-field
                    :label="`${$t('interface.gatewayName')} *`"
                    v-model="gateway.gwname"
                  ></v-text-field>
                </v-row>
                <p class="error-feedback mb-5 px-0 mx-0" v-if="!isNameGateway">
                  {{ messageNameGateway }}
                </p>
                <v-row>
                  <v-text-field
                    :label="`${$t('interface.iPv4gateway')} *`"
                    clsas="w-100"
                    v-model="gateway.gwaddress"
                  ></v-text-field>
                </v-row>
                <p
                  class="error-feedback mb-5 px-0 mx-0"
                  v-if="!isGatewayAddress"
                >
                  {{ messageGatewayAddress }}
                </p>
                <p class="error-feedback mb-5 px-0 mx-0" v-if="!isValidAddress">
                  {{ messageValidAddress }}
                </p>
                <p
                  class="error-feedback mb-5 px-0 mx-0"
                  v-if="messageExistGateway"
                >
                  {{ messageExistGateway }}
                </p>
                <v-row>
                  <v-text-field
                    label="Description"
                    v-model="gateway.description"
                  ></v-text-field
                ></v-row>
                <v-row>
                  <input
                    type="checkbox"
                    disabled
                    v-model="gateway.default_aux"
                  />
                  <label class="ml-3">{{
                    $t("interface.GatewayDefault")
                  }}</label>
                </v-row>
                <v-row>
                  <input type="checkbox" v-model="gateway.far_aux" />
                  <label class="ml-3">{{ $t("interface.farGateway") }}</label>
                </v-row>
                <v-row>
                  <input type="checkbox" v-model="gateway.multiwan_aux" />
                  <label class="ml-3">{{
                    $t("interface.multiWANGateway")
                  }}</label>
                </v-row>
              </v-container>
            </v-form>
          </v-card-text>
          <div class="text-start ml-6 mt-3 mb-8">
            <span class="text-sm">
              <span class="text-red text-lg">*</span>
              {{ $t("errors.oblig") }}</span
            >
          </div>

          <div class="text-center">
            <VButton
              large
              rounded
              outlined
              color="#FFFF"
              label-color="#213E9F"
              :label="$t('interface.cancel')"
              :isLarge="true"
              @click="cancelGateway"
            />
            <VButton
              large
              rounded
              outlined
              color="#213E9F"
              label-color="#ffff"
              :label="$t('interface.save')"
              :isLarge="true"
              type="submit"
              class="ml-2"
              @click="addGateway"
            />
          </div>
          <br />
        </v-card>
      </v-dialog>
    </v-form>
    <v-snackbar
      :timeout="2000"
      v-model="snackbar"
      location="bottom right"
      :color="color"
    >
      {{ textAlert }}
    </v-snackbar>
  </v-card>
</template>

<script>
import axios from "axios";
import ConfigDHCPv4 from "./configDHCP/ConfigDHCPv4.vue";
import AdvancedConfigDHCPv4 from "./configDHCP/AdvancedConfigDHCPv4.vue";
import VButton from "../../../components/VButton.vue";
import netmaskItems from "../../../constants/netmask.js";
import { user_privilege } from "@/mixins/user_privilege.js";
import { v4 as uuidv4 } from "uuid";

export default {
  name: "IfNameComponent",
  components: {
    ConfigDHCPv4,
    VButton,
    AdvancedConfigDHCPv4,
  },
  inject: ["emitter"],
  props: {
    activeTab: String,
  },
  data() {
    return {
      is_main: false,
      is_vxlan_vlan: false,
      messageExistGateway: "",
      itemData: [],
      deleteDialog: false,
      isviewModal: false,
      viewModal: false,
      loading: false,
      isLoadingDialogue: false,
      textAlert: "",
      color: "",
      snackbar: false,
      messageGatewayAddress: "",
      messageNameGateway: "",
      messageValidAddress: "",
      messageValidIPV4Address: "",
      messageRejectAddress: "",
      messageValidHostnameAddress: "",
      message: "",
      typeDHCP4: "",
      advancedParameters: false,
      interface: {
        alias_add: "",
        alias_mask: "",
        rejectLeases: "",
        hostname: "",
        overrideMTU: false,
      },
      items: [],
      speedDuplexItems: [
        "100baseTx-FD",
        "100baseTx-HD",
        "10baseT-FD",
        "10baseT-HD",
      ],
      netmaskItems: netmaskItems,
      activate: false,
      device: "",
      description: "",
      private_aux: false,
      bogon_aux: false,
      setuptypeip4: "",
      addmac: "",
      mtuv: "",
      mssv: null,
      rulesNumber: (value) => {
        if (!value) return true;
        const integerRegex = /^[0-9]+$/;
        if (!integerRegex.test(value.trim())) {
          return this.$t("interface.numberValidity");
        }
        return true;
      },
      rulesMTU: (value) => {
        if (!value) return true;
        const integerRegex = /^[0-9]+$/;
        if (!integerRegex.test(value.trim())) {
          return this.$t("interface.numberValidity");
        }
        const num = parseFloat(value);
        if (num < 1500 || num > 9000) {
          return this.$t("interface.NumberMust");
        }
        return true;
      },
      speed_duplex: "",
      dynamicGatewayPolicy: false,
      showAlert: false,
      name_interface: "",
      value_setup_Ipv4: {
        ip_address4: "",
        netmask4: "",
        gateway4: {
          id: "",
          value: "",
        },
      },
      IPV4Config: {},
      allStaticGateways: [],
      showGatewayDialog: false,
      gateway: {
        gwname: "",
        gwaddress: "",
        description: "",
        default_aux: true,
        far_aux: false,
        multiwan_aux: false,
      },
      showAlertGateway: false,
      AdvancedConfigDHCPv4: {
        timeout: "",
        retry: "",
        select_timeout: "",
        reboot: "",
        backoff: "",
        initial_interval: "",
        dhcp_client: "",
        lease_time: "",
        request: "",
        require: "",
        domain_name: "",
        domain_server: "",
      },
    };
  },

  computed: {
    alertStyle() {
      return {
        position: "fixed",
        top: "60px",
        right: "20px",
        width: "20%",
      };
    },
    isNameGateway() {
      return this.gateway.gwname;
    },
    isGatewayAddress() {
      return this.gateway.gwaddress;
    },

    isValidAddress() {
      const ipRegex =
        /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;

      // Validate the input value against the regex
      if (!ipRegex.test(this.gateway.gwaddress)) {
        return false; // Error message for invalid IP address
      }
      return true;
    },
    isValidRejectAddress() {
      const ipRegex =
        /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;

      // Validate the input value against the regex
      if (
        this.interface.rejectLeases &&
        !ipRegex.test(this.interface.rejectLeases)
      ) {
        return false; // Error message for invalid IP address
      }
      return true;
    },

    isValidHostname() {
      const hostnameRegex =
        /^(?!-)(?!.*-$)([A-Za-z0-9-]{1,63}\.)+[A-Za-z0-9-]{1,63}$/;

      if (this.interface.hostname && this.interface.hostname.length > 253) {
        return false;
      }

      if (
        this.interface.hostname &&
        !hostnameRegex.test(this.interface.hostname)
      ) {
        return false;
      }
      return true;
    },

    isValidIPV4Address() {
      const ipRegex =
        /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;

      if (this.interface.alias_add && !ipRegex.test(this.interface.alias_add)) {
        return false;
      }
      return true;
    },

    isValidTimeout() {
      const numberRegex = /^[0-9]*\.?[0-9]+$/;

      if (
        this.AdvancedConfigDHCPv4.timeout &&
        !numberRegex.test(this.AdvancedConfigDHCPv4.timeout)
      ) {
        return false;
      }
      return true;
    },
    isValidRetry() {
      const numberRegex = /^[0-9]*\.?[0-9]+$/;

      if (
        this.AdvancedConfigDHCPv4.retry &&
        !numberRegex.test(this.AdvancedConfigDHCPv4.retry)
      ) {
        return false;
      }
      return true;
    },
    isValidSelectTimeout() {
      const numberRegex = /^[0-9]*\.?[0-9]+$/;

      if (
        this.AdvancedConfigDHCPv4.select_timeout &&
        !numberRegex.test(this.AdvancedConfigDHCPv4.select_timeout)
      ) {
        return false;
      }
      return true;
    },
    isValidReboot() {
      const numberRegex = /^[0-9]*\.?[0-9]+$/;

      if (
        this.AdvancedConfigDHCPv4.reboot &&
        !numberRegex.test(this.AdvancedConfigDHCPv4.reboot)
      ) {
        return false;
      }
      return true;
    },
    isValidBackoff() {
      const numberRegex = /^[0-9]*\.?[0-9]+$/;

      if (
        this.AdvancedConfigDHCPv4.backoff &&
        !numberRegex.test(this.AdvancedConfigDHCPv4.backoff)
      ) {
        return false;
      }
      return true;
    },
    isValidInitialInterval() {
      const numberRegex = /^[0-9]*\.?[0-9]+$/;

      if (
        this.AdvancedConfigDHCPv4.initial_interval &&
        !numberRegex.test(this.AdvancedConfigDHCPv4.initial_interval)
      ) {
        return false;
      }
      return true;
    },
    isValidDhcp_client() {
      const charRegex =
        /^(?:[0-9A-Fa-f]{2}([-:]))(?:[0-9A-Fa-f]{2}\1){4}[0-9A-Fa-f]{2}$/;

      if (
        this.AdvancedConfigDHCPv4.dhcp_client &&
        !charRegex.test(this.AdvancedConfigDHCPv4.dhcp_client)
      ) {
        return false;
      }
      return true;
    },
    isValidAddmac() {
      const charRegex =
        /^(?!([0]{2}[:-]){5}[0]{2}$)([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}$/;

      if (this.addmac && !charRegex.test(this.addmac)) {
        return false;
      }
      return true;
    },
    isValidLease_time() {
      const numberRegex = /^[0-9]*\.?[0-9]+$/;

      if (
        this.AdvancedConfigDHCPv4.lease_time &&
        !numberRegex.test(this.AdvancedConfigDHCPv4.lease_time)
      ) {
        return false;
      }
      return true;
    },
    isValidRequest() {
      const charRegex = /^[a-zA-Z]+$/;

      if (
        this.AdvancedConfigDHCPv4.request &&
        !charRegex.test(this.AdvancedConfigDHCPv4.request)
      ) {
        return false;
      }
      return true;
    },
    isValidRequire() {
      const charRegex = /^[a-zA-Z]+$/;

      if (
        this.AdvancedConfigDHCPv4.require &&
        !charRegex.test(this.AdvancedConfigDHCPv4.require)
      ) {
        return false;
      }
      return true;
    },
    isValidDomain_name() {
      const charRegex =
        /^(?!-)(?!.*-$)([A-Za-z0-9-]{1,63}\.)+[A-Za-z0-9-]{1,63}$/;
      if (
        this.AdvancedConfigDHCPv4.domain_name &&
        !charRegex.test(this.AdvancedConfigDHCPv4.domain_name)
      ) {
        return false;
      }
      return true;
    },
    isValidDomain_server() {
      const charRegex =
        /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;

      if (
        this.AdvancedConfigDHCPv4.domain_server &&
        !charRegex.test(this.AdvancedConfigDHCPv4.domain_server)
      ) {
        return false;
      }
      return true;
    },
    isValidMTU() {
      const charRegex = /^(?:5(?:7[6-9]|[89]\d)|[6-9]\d\d|[1-8]\d{3}|9000)$/;

      if (this.mtuv && !charRegex.test(this.mtuv)) {
        return false;
      }
      return true;
    },
    isValidMSS() {
      const charRegex = /^(?:57[7-9]|5[89]\d|[6-9]\d\d|\d{4,})$/;

      if (this.mssv && !charRegex.test(this.mssv)) {
        return false;
      }
      return true;
    },
  },
  methods: {
    cancelDelete() {
      this.deleteDialog = false;
    },
    deleteGateway(id) {
      this.itemData = id;
      this.deleteDialog = true;
    },
    confirmDelete() {
      const csrfToken = this.getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios
        .delete(`/gateway/deleteGateway/${this.itemData}`)
        .then((response) => {
          this.snackbar = true;
          this.color = "success";
          this.textAlert = response.data.msg;

          setTimeout(() => {
            location.reload();
          }, 1000);
        })
        .catch((i) => {
          if (i.response?.status === 500) {
            this.snackbar = true;
            this.color = "red";
            this.textAlert = this.$t("errors.errorServer");
          } else {
            this.snackbar = true;
            this.color = "red";
            this.textAlert = i.response?.data?.msg;
          }
        });
    },

    close() {
      this.isviewModal = false;
      this.viewModal = false;
    },
    validateRange(value) {
      const num = parseFloat(value); // Parse the value to a number

      if (isNaN(num)) {
        return true; // Return true if the value is not a number
      }

      if (num < 1500 || num > 9000) {
        return this.$t("interface.NumberMust");
      }

      return true; // Return true when the value is within the range
    },
    macAddressValidation(value) {
      // if value is empty, return true
      if (!value) {
        return true;
      }

      // Regular expression for MAC address validation
      const macRegex = /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/;

      // Validate the input value against the regex
      if (!macRegex.test(value)) {
        return this.$t("interface.addressValid"); // Error message for invalid MAC address
      }
      return true; // Return true when the input is valid
    },
    ipAddressValidation(value) {
      if (!value) {
        return true;
      }

      // Regular expression for IP address validation
      const ipRegex =
        /^(?!0\.0\.0\.0$)((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;

      // Validate the input value against the regex
      if (!ipRegex.test(value)) {
        return "Please enter a valid IP address"; // Error message for invalid IP address
      }
      return true; // Return true when the input is valid
    },
    getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === name + "=") {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    },

    addNetwork() {
      if (!this.isValidTimeout && this.setuptypeip4?.slug === "dhcp") return;
      if (!this.isValidRetry && this.setuptypeip4?.slug === "dhcp") return;
      if (!this.isValidSelectTimeout && this.setuptypeip4?.slug === "dhcp")
        return;
      if (!this.isValidReboot && this.setuptypeip4?.slug === "dhcp") return;
      if (!this.isValidBackoff && this.setuptypeip4?.slug === "dhcp") return;
      if (!this.isValidInitialInterval && this.setuptypeip4?.slug === "dhcp")
        return;
      if (!this.isValidDhcp_client && this.setuptypeip4?.slug === "dhcp")
        return;
      if (!this.isValidLease_time && this.setuptypeip4?.slug === "dhcp") return;
      if (!this.isValidRequest && this.setuptypeip4?.slug === "dhcp") return;
      if (!this.isValidRequire && this.setuptypeip4?.slug === "dhcp") return;
      if (!this.isValidDomain_name && this.setuptypeip4?.slug === "dhcp")
        return;
      if (!this.isValidDomain_server && this.setuptypeip4?.slug === "dhcp")
        return;
      if (!this.isValidMTU) return;
      if (!this.isValidMSS) return;
      if (!this.isValidAddmac) return;

      if (
        this.isValidIPV4Address &&
        this.interface.alias_add &&
        !this.interface.alias_mask &&
        this.setuptypeip4?.slug === "dhcp"
      ) {
        return;
      }

      if (!this.isValidHostname && this.setuptypeip4?.slug === "dhcp") {
        this.messageValidHostnameAddress = this.$t("errors.validHostname");
        return;
      }
      if (!this.isValidIPV4Address && this.setuptypeip4?.slug === "dhcp") {
        this.messageValidIPV4Address = this.$t(
          "errors.formatMustBeLikeAdresseIP"
        );
        return;
      }
      if (!this.isValidRejectAddress && this.setuptypeip4?.slug === "dhcp") {
        this.messageRejectAddress = this.$t("errors.formatMustBeLikeAdresseIP");
        return;
      }

      const ipRegex =
        /^(?!0\.0\.0\.0$)((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;

      if (
        this.setuptypeip4?.slug === "static" &&
        !ipRegex.test(this.value_setup_Ipv4.ip_address4)
      ) {
        return;
      }

      const csrfToken = this.getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      if (this.advancedParameters) {
        this.typeDHCP4 = "Advanced";
      } else {
        this.typeDHCP4 = "Base";
      }
      // todo: add network refactoring && optimization needed
      if (
        this.setuptypeip4?.slug === "static" &&
        this.value_setup_Ipv4?.ip_address4 &&
        this.value_setup_Ipv4?.netmask4
      ) {
        const params = {
          name_interface: this.activeTab,
          device: this.device,
          description: this.description,
          private_aux: this.private_aux,
          bogon_aux: this.bogon_aux,
          addmac: this.addmac,
          mtuv: this.mtuv ? +this.mtuv : null,
          mssv: this.mssv ? +this.mssv : null,
          speed_duplex: this.speed_duplex,
          setuptypeIP4: this.setuptypeip4?.slug,
          value_setup_Ipv4: {
            ip_address4: this.value_setup_Ipv4.ip_address4,
            netmask4: this.value_setup_Ipv4.netmask4,
            gateway4: {
              value: this.value_setup_Ipv4.gateway4.value?.gwaddress,
            },
          },
        };

        this.loading = true;
        this.isLoadingDialogue = true;

        axios
          .put("/network/conf/" + this.activeTab, params)
          .then((response) => {
            this.loading = false;
            this.isLoadingDialogue = false;
            this.message = response.data.message;
            this.showAlert = true;
            setTimeout(() => {
              this.showAlert = false;
              location.reload();
            }, 1000);
          })
          .catch((i) => {
            this.loading = false;
            this.isLoadingDialogue = false;

            if (i.response.status === 500) {
              this.snackbar = true;
              this.color = "red";
              this.textAlert = this.$t("errors.errorServer");
            } else {
              this.snackbar = true;
              this.color = "red";
              this.textAlert = i.response.data.message;
            }
          });
      }
      if (this.setuptypeip4?.slug === "dhcp") {
        const params = {
          name_interface: this.activeTab,
          device: this.device,
          description: this.description,
          private_aux: this.private_aux,
          bogon_aux: this.bogon_aux,
          addmac: this.addmac,
          mtuv: this.mtuv,
          mssv: this.mssv,
          speed_duplex: this.speed_duplex,
          setuptypeIP4: this.setuptypeip4?.slug,
          value_setup_Ipv4: {
            typeDHCP4: this.typeDHCP4,
            alias_add: this.interface.alias_add,
            alias_mask: this.interface.alias_mask,
            reject: this.interface.rejectLeases,
            hostname: this.interface.hostname,
            timeout: this.AdvancedConfigDHCPv4.timeout,
            retry: this.AdvancedConfigDHCPv4.retry,
            backoff: this.AdvancedConfigDHCPv4.backoff,
            reboot: this.AdvancedConfigDHCPv4.reboot,
            select_timeout: this.AdvancedConfigDHCPv4.select_timeout,
            initial_interval: this.AdvancedConfigDHCPv4.initial_interval,
            dhcp_client: this.AdvancedConfigDHCPv4.dhcp_client,
            request: this.AdvancedConfigDHCPv4.request,
            require: this.AdvancedConfigDHCPv4.require,
            domain_name: this.AdvancedConfigDHCPv4.domain_name,
            domain_server: this.AdvancedConfigDHCPv4.domain_server,
            lease_time: this.AdvancedConfigDHCPv4.lease_time,
          },
        };

        this.loading = true;
        this.isLoadingDialogue = true;
        axios
          .put("/network/conf/" + this.activeTab, params)
          .then((response) => {
            this.loading = false;
            this.isLoadingDialogue = false;
            this.message = response.data.message;
            this.showAlert = true;
            setTimeout(() => {
              this.showAlert = false;
              location.reload();
            }, 1000);
          })
          .catch((i) => {
            this.loading = false;
            this.isLoadingDialogue = false;

            if (i.response.status === 500) {
              this.snackbar = true;
              this.color = "red";
              this.textAlert = this.$t("errors.errorServer");
            } else {
              this.snackbar = true;
              this.color = "red";
              this.textAlert = i.response.data.message;
            }
          });
      }
    },
    cancel() {
      // todo: reset form values to initial values
    },
    openGatewayDialog() {
      const user = user_privilege();
      if (user === "viewer") {
        this.isviewModal = true;
        this.viewModal = true;
      } else {
        this.showGatewayDialog = true;
      }
    },
    addGateway() {
      const user = user_privilege();
      if (user === "viewer") {
        this.isviewModal = true;
        this.viewModal = true;
      } else {
        if (!this.isNameGateway) {
          this.messageNameGateway = this.$t("errors.valueRequired");
          return;
        }
        if (!this.isGatewayAddress) {
          this.messageGatewayAddress = this.$t("errors.valueRequired");
          return;
        }
        if (!this.isValidAddress) {
          this.messageValidAddress = this.$t(
            "errors.formatMustBeLikeAdresseIP"
          );
          return;
        }
        let mappedGateways = this.allStaticGateways.map(
          (gateway) => gateway.gwaddress
        );

        if (mappedGateways.includes(this.gateway.gwaddress)) {
          this.messageExistGateway = this.$t("champs.existGateway");
          setTimeout(() => {
            this.messageExistGateway = "";
          }, 1000);
          return;
        }

        const params = {
          gwname: this.gateway.gwname,
          gwaddress: this.gateway.gwaddress,
          description: this.gateway.description,
          default_aux: this.gateway.default_aux,
          far_aux: this.gateway.far_aux,
          multiwan_aux: this.gateway.multiwan_aux,
        };

        const csrfToken = this.getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

        axios
          .post("/gateway/addStaticGateway", params)
          .then((response) => {
            if (response.status == "200") {
              this.showGatewayDialog = false;
              this.message = response.data.msg;
              this.gateway = {
                gwname: "",
                gwaddress: "",
                description: "",
                default_aux: true,
                far_aux: false,
                multiwan_aux: false,
              };
              this.messageGatewayAddress = "";
              this.messageNameGateway = "";
              this.messageValidAddress = "";
              this.showAlertGateway = true;
              setTimeout(() => {
                this.showAlertGateway = false;
                this.handleGateway();
              }, 1000);
            } else {
              this.showGatewayDialog = true;
            }
          })
          .catch((i) => {
            if (i.response.status === 500) {
              this.snackbar = true;
              this.color = "red";
              this.textAlert = this.$t("errors.errorServer");
            } else {
              this.snackbar = true;
              this.color = "red";
              this.textAlert = i.response.data.msg;
            }
          });
      }
    },
    cancelGateway() {
      const user = user_privilege();
      if (user === "viewer") {
        this.isviewModal = true;
        this.viewModal = true;
      } else {
        this.showGatewayDialog = false;
        this.gateway = {
          gwname: "",
          gwaddress: "",
          description: "",
          default_aux: true,
          far_aux: false,
          multiwan_aux: false,
        };
        this.messageGatewayAddress = "";
        this.messageNameGateway = "";
        this.messageValidAddress = "";
      }
    },
    updateGateway() {
      const params = {
        gwname: this.gateway.gwname,
        gwaddress: this.gateway.gwaddress,
        description: this.gateway.description,
        default_aux: this.gateway.default_aux,
        far_aux: this.gateway.far_aux,
        multiwan_aux: this.gateway.multiwan_aux,
      };
      const csrfToken = this.getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios
        .put("/gateway/updateStaticGateway", params)
        .then((response) => {
          this.showAlert = true;
          setTimeout(() => {
            this.showAlert = false;
          }, 3000);
        })
        .catch((i) => {
          if (i.response.status === 500) {
            this.snackbar = true;
            this.color = "red";
            this.textAlert = this.$t("errors.errorServer");
          } else {
            this.snackbar = true;
            this.color = "red";
            this.textAlert = i.response.data.message;
          }
        });
    },
    onSubmit() {
      const user = user_privilege();
      if (user === "viewer") {
        this.isviewModal = true;
        this.viewModal = true;
      } else {
        this.addNetwork();
      }
    },
    handleSubmit() {
      this.onSubmit();
    },
    handleGateway() {
      const csrfToken = this.getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/gateway/getStaticGateways").then((response) => {
        let mappedStaticAddress = response.data?.Gateways.map((gateway) => {
          return {
            id: gateway.id,
            gwaddress: gateway.gwaddress,
          };
        });

        let combineArray = [{ id: uuidv4(), gwaddress: "Auto Detect" }];
        this.allStaticGateways = [...mappedStaticAddress, ...combineArray];
      });
    },
  },

  beforeMount: async function () {
    this.handleGateway();

    let interfaces =
      document.getElementById("app").attributes["interfaces"].value;

    let validJsonStringInterface = interfaces
      .replace(/'/g, '"')
      .replace(/True/g, "true")
      .replace(/False/g, "false")
      .replace(/None/g, "null");
    let parsedArrayInterface = JSON.parse(validJsonStringInterface);

    let filtred_main = parsedArrayInterface.filter(
      (i) => i.name_interface === this.activeTab
    );

    this.is_vxlan_vlan =
      this.activeTab.startsWith("VXLAN") || this.activeTab.startsWith("VLAN")
        ? true
        : false;

    this.is_main = filtred_main[0]?.is_main;

    if (
      this.activeTab.startsWith("VXLAN") ||
      this.activeTab.startsWith("VLAN")
    ) {
      this.items.push({ id: 1, value: this.$t("Static"), slug: "static" });
      this.setuptypeip4 = { id: 1, value: this.$t("Static"), slug: "static" };
    } else {
      this.items.push(
        { id: 1, value: this.$t("Static"), slug: "static" },
        { id: 2, value: "dhcp", slug: "dhcp" }
      );
    }

    this.IPV4Config =
      document.getElementById("app").attributes["ipv4config"].value;
    let validJsonString = this.IPV4Config.replace(/'/g, '"')
      .replace(/True/g, "true")
      .replace(/False/g, "false")
      .replace(/None/g, "null");
    let parsedArray = JSON.parse(validJsonString);
    this.IPV4Config = parsedArray[this.activeTab];

    this.activate = this.IPV4Config?.interface !== null ? true : false;
    this.device = this.IPV4Config.interface.ifname;
    this.description = this.IPV4Config.interface.description;

    this.private_aux = this.IPV4Config.interface.private_aux;
    this.bogon_aux = this.IPV4Config.interface.bogon_aux;

    this.addmac = this.IPV4Config.genericConfig.addmac;
    this.mtuv = this.IPV4Config.genericConfig.mtuv;
    this.mssv = this.IPV4Config.genericConfig.mssv;
    this.speed_duplex = this.IPV4Config.genericConfig.speed_duplex;

    setTimeout(() => {
      let filtredType = this.items.filter(
        (i) => i.slug === this.IPV4Config?.IPV4Config?.typeip4?.toLowerCase()
      );
      this.setuptypeip4 = filtredType[0] ? filtredType[0] : { id: 1, value: this.$t("Static"), slug: "static" };
      console.log('filtredType',filtredType[0])
    }, 1000);

    // this.setuptypeip4 = this.IPV4Config
    //   ? this.IPV4Config?.IPV4Config?.typeip4?.toLowerCase()
    //   : "";
    this.value_setup_Ipv4.ip_address4 = this.IPV4Config.IPV4Config.ip_address;
    this.value_setup_Ipv4.netmask4 = this.IPV4Config.IPV4Config.netmask;

    this.name_interface = this.IPV4Config.interface.name_interface;

    setTimeout(() => {
      if (this.IPV4Config.IPV4Config.addrgw) {
        let filtredAddress = this.allStaticGateways.filter(
          (i) => i.gwaddress === this.IPV4Config.IPV4Config.addrgw
        );
        this.value_setup_Ipv4.gateway4.value = filtredAddress[0];
      } else {
        let filtredAutoDetect = this.allStaticGateways.filter(
          (i) => i.gwaddress === "Auto Detect"
        );

        this.value_setup_Ipv4.gateway4.value = filtredAutoDetect[0];
      }
    }, 1000);

    this.advancedParameters =
      this.IPV4Config.IPV4Config.typedhcp === "Advanced" ? true : false;

    this.typeDHCP4 = this.IPV4Config.IPV4Config.typedhcp;
    this.interface.alias_add = this.IPV4Config.IPV4Config.alias_add;
    this.interface.alias_mask = this.IPV4Config.IPV4Config.alias_mask;
    this.interface.rejectLeases = this.IPV4Config.IPV4Config.reject;
    this.interface.hostname = this.IPV4Config.IPV4Config.hostname;
  },
  watch: {
    typeDHCP4: function (val) {
      if (val === "Advanced") {
        // this.advancedParameters = true;
        this.AdvancedConfigDHCPv4.timeout = this.IPV4Config.IPV4Config.timeout;
        this.AdvancedConfigDHCPv4.retry = this.IPV4Config.IPV4Config.retry;
        this.AdvancedConfigDHCPv4.select_timeout =
          this.IPV4Config.IPV4Config.select_timeout;
        this.AdvancedConfigDHCPv4.reboot = this.IPV4Config.IPV4Config.reboot;
        this.AdvancedConfigDHCPv4.backoff = this.IPV4Config.IPV4Config.backoff;
        this.AdvancedConfigDHCPv4.initial_interval =
          this.IPV4Config.IPV4Config.initial_interval;
        this.AdvancedConfigDHCPv4.dhcp_client =
          this.IPV4Config.IPV4Config.dhcp_client;
        this.AdvancedConfigDHCPv4.lease_time =
          this.IPV4Config.IPV4Config.lease_time;
        this.AdvancedConfigDHCPv4.request = this.IPV4Config.IPV4Config.request;
        this.AdvancedConfigDHCPv4.require = this.IPV4Config.IPV4Config.require;
        this.AdvancedConfigDHCPv4.domain_name =
          this.IPV4Config.IPV4Config.domain_name;
        this.AdvancedConfigDHCPv4.domain_server =
          this.IPV4Config.IPV4Config.domain_server;
      }
      //  else {
      //   this.advancedParameters = false;
      // }
    },
  },
};
</script>

<style scoped>
.ip-address-style {
  width: 100%;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  margin-left: 0.5rem;
  margin-right: 0.5rem;
}

.error-feedback {
  color: red;
  font-size: 0.85em;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  margin-left: 0.5rem;
  margin-right: 0.5rem;
  white-space: pre-wrap;
}

.netmask-select-style {
  width: 100%;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  margin-left: 0.5rem;
  margin-right: 0.5rem;
}

.IPV4Setup-type-style {
  /* remove underline  */

  border-bottom: none !important;
  border-top: none !important;
  border-left: none !important;
  border-right: none !important;
  border-radius: 0px !important;
  border-color: #f6f6f6 !important;
  border-width: 0px !important;
  width: 100%;
}

.advanced-parameters-style {
  display: flex;
  margin-top: 1rem;
  margin-bottom: 1rem;
  margin-left: 0.5rem;
  margin-right: 0.5rem;
}

.gateway-dialog {
  position: fixed;
  overflow-x: unset;
  overflow-y: unset;
}

.new-style {
  width: 70%;
}

.title-text {
  color: #020202;
  font-family: Nunito;
  font-size: 18px;
  font-style: normal;
  font-weight: 700;
  line-height: normal;
}

.error-feedback {
  color: red;
  font-size: 0.85em;
}
</style>
