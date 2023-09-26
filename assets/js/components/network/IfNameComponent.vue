<template>
    <v-card>
        <v-row class="fill-height ml-3">
            <v-col cols="12" sm="6">
                <v-card-title style="color: #020202;
font-family: Nunito;
font-size: 18px;
font-style: normal;
font-weight: 700;
line-height: normal;">{{ $t('PageNetwork.BasicConfiguration') }}</v-card-title>
                <v-divider class="ml-3"></v-divider>
                <v-row class="ml-3 mt-3">
                    <div style="color: black;">Interface</div>
                    <input type="checkbox" class="ml-5" v-model="activate">
                    <label class="ml-2">Activate</label>
                </v-row>
                <div style="background-color: #F6F6F6;" class="ml-3">
                    <v-row class="ml-3 mt-5">
                        <div style="color: #838383;
                                    font-family: Nunito;
                                    font-size: 16px;
                                    font-style: normal;
                                    font-weight: 400;
                                    line-height: normal;">Device</div>
                    </v-row>
                    <v-text-field label="Enter device name" class="ml-3 mt-2" v-model="device"></v-text-field>
                </div>
                <div style="background-color: #F6F6F6;" class="ml-3">

                    <v-row class="ml-3 mt-2">
                        <div style="color: #838383;
                                font-family: Nunito;
                                font-size: 16px;
                                font-style: normal;
                                font-weight: 400;
                                line-height: normal;">Description</div>
                    </v-row>
                    <v-text-field label="Enter Description" class="ml-3 mt-2" v-model="description"></v-text-field>
                </div>
                <v-card-title style="color: #020202;
font-family: Nunito;
font-size: 18px;
font-style: normal;
font-weight: 700;
line-height: normal;">Generic configuration</v-card-title>
                <v-divider class="ml-3 mb-5"></v-divider>
                <table class="ml-3">
                    <tbody>
                        <tr>
                            <td>
                                <div>Block networks</div>
                            </td>
                            <td><input type="checkbox" v-model="private_aux" class="ml-5">
                                <label>Private</label>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <div class="mt-5">Block Bogon addresses</div>
                            </td>
                            <td><input type="checkbox" v-model="bogon_aux" class="ml-5">
                                <label>Not assigned by IANA</label>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <div class="mt-5 mt-3">IPV4 Setup Type</div>
                            </td>
                            <td> <select class="ml-3" v-model="setuptypeIP4" style=" height: 39px;
                    width: 100%;
                    border-radius: 4px;
                    border: 1px solid #F6F6F6;
                    background-color: #F6F6F6;
                    color: #020202;
                    font-family: Nunito;
                    font-size: 16px;
                    font-style: normal;
                    font-weight: 400;
                    line-height: normal;
                    padding-left: 10px;
                    padding-right: 10px;
                    padding-top: 5px;
                    padding-bottom: 5px;
                    border-color: #F6F6F6;
                    box-shadow: none;
                    outline: none;
                    -webkit-appearance: none;
                    -moz-appearance: none;
                    appearance: none;
                    align-items: center;
                    justify-content: center;
                    ">
                                    <option v-for="item in items" :value="item.value">{{ item.text }}</option>
                                    <v-icon>mdi-chevron-down</v-icon>
                                </select></td>
                        </tr>
                        <tr>
                            <td>
                                <div class="mt-5 mt-6">IPV6 Setup Type</div>
                            </td>
                            <td><select class="ml-3 mt-5" v-model="ipv6SetupType" style=" height: 39px;
                    width: 100%;
                    border-radius: 4px;
                    border: 1px solid #F6F6F6;
                    background-color: #F6F6F6;
                    color: #020202;
                    font-family: Nunito;
                    font-size: 16px;
                    font-style: normal;
                    font-weight: 400;
                    line-height: normal;
                    padding-left: 10px;
                    padding-right: 10px;
                    padding-top: 5px;
                    padding-bottom: 5px;
                    border-color: #F6F6F6;
                    box-shadow: none;
                    outline: none;
                    -webkit-appearance: none;
                    -moz-appearance: none;
                    appearance: none;
                    align-items: center;
                    justify-content: center;

                    ">
                                    <option v-for="item in ipv6Items" :value="item">{{ item }}</option>
                                    <v-icon>mdi-chevron-down</v-icon>
                                </select></td>
                        </tr>
                        <tr>
                            <td>
                                <div style="color: #020202;
" class="mt-5 mt-6">MAC address</div>
                            </td>
                            <td><v-text-field style=" height: 39px;
                    width: 100%;
                    border-radius: 4px;
                    border: 1px solid #F6F6F6;
                    background-color: #F6F6F6;
                    color: #020202;
                    font-family: Nunito;
                    font-size: 16px;
                    font-style: normal;
                    font-weight: 400;
                    line-height: normal;
                    padding-left: 10px;
                    padding-right: 10px;
                    padding-top: 5px;
                    padding-bottom: 5px;
                    border-color: #F6F6F6;
                    box-shadow: none;
                    outline: none;
                    -webkit-appearance: none;
                    -moz-appearance: none;
                    appearance: none;
                    align-items: center;
                    justify-content: center;

                    " label="Enter MAC address" class="ml-3 mt-2" v-model="addmac"></v-text-field></td>
                        </tr>
                        <tr>
                            <td>
                                <div class="mt-5 mt-6">MTU (Maximum Transmission Unit)</div>
                            </td>
                            <td> <v-text-field label="Enter MTU" class="ml-3 mt-2" v-model="mtuV"></v-text-field>
                            </td>
                        </tr>
                        <tr>
                            <td> <span style="color: #020202;" class="mt-5 mt-6">Speed and Duplex</span>
                            </td>
                            <td>
                                <select class="ml-3" v-model="speed_duplex" style=" height: 39px;
                    width: 100%;
                    border-radius: 4px;
                    border: 1px solid #F6F6F6;
                    background-color: #F6F6F6;
                    color: #020202;
                    font-family: Nunito;
                    font-size: 16px;
                    font-style: normal;
                    font-weight: 400;
                    line-height: normal;
                    padding-left: 10px;
                    padding-right: 10px;
                    padding-top: 5px;
                    padding-bottom: 5px;
                    border-color: #F6F6F6;
                    box-shadow: none;
                    outline: none;
                    -webkit-appearance: none;
                    -moz-appearance: none;
                    appearance: none;
                    align-items: center;
                    justify-content: center;

                    ">
                                    <option style=" height: 39px;
                    width: 100%;
                    border-radius: 4px;
                    border: 1px solid #F6F6F6;
                    border-color: #F6F6F6;
                    background-color: #F6F6F6;
                    color: #020202;
                    font-family: Nunito;
                    font-size: 16px;
                    font-style: normal;
                    font-weight: 400;
                    line-height: normal;
                    padding-left: 10px;
                    padding-right: 10px;
                    padding-top: 5px;
                    padding-bottom: 5px;
                    border-color: #F6F6F6;
                    box-shadow: none;
                    outline: none;
                    -webkit-appearance: none;
                    -moz-appearance: none;
                    appearance: none;
                    align-items: center;
                    justify-content: center;
                    " v-for="item in speedDuplexItems" :value="item">{{ item }}</option>
                                    <v-icon>mdi-chevron-down</v-icon>
                                </select>
                            </td>
                        </tr>
                        <tr>
                            <td><span style="color: #020202;" class="mt-5 inline-input">Dynamic gateway policy</span></td>
                            <td>
                                <div style="display: flex;">
                                    <input type="checkbox" class="mb-5" v-model="dynamicGatewayPolicy">
                                    <label class="">The interface does not require an intermediate system to act
                                        as a gateway.</label>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>

            </v-col>
            <v-col cols="12" sm="6" v-if="value_setup_Ipv4.ip_address4 != null || value_setup_Ipv4.ip_address4 != null">
                <div v-if="setuptypeIP4 === 'static'">
                    <v-card-title style="color: #020202;
font-family: Nunito;
font-size: 18px;
font-style: normal;
font-weight: 700;
line-height: normal;">Static IPV4 address configuration</v-card-title>
                    <v-divider class="ml-3" style="height: 39px;
                    width: 425px;"></v-divider>
                    <table class="ml-3 mt-3">
                        <tbody>
                            <tr>
                                <td><span style="color: black;" class="inline-input">IPV4 address</span></td>
                                <td></td>
                                <td>
                                    <div style="display: flex">
                                        <v-text-field label="Enter IP address" class="ml-3 mt-2 inline-input"
                                            v-model="value_setup_Ipv4.ip_address4"></v-text-field>
                                        <select v-model="value_setup_Ipv4.netmask4" class="ml-3 mt-5 inline-input" style="height: 39px;
                    width: 111px;
                    border-radius: 4px;
                    border: 1px solid #F6F6F6;
                    background-color: #F6F6F6;
                    color: #020202;
                    font-family: Nunito;
                    font-size: 16px;
                    font-style: normal;
                    font-weight: 400;
                    line-height: normal;
                    padding-left: 10px;
                    padding-right: 10px;
                    padding-top: 5px;
                    padding-bottom: 5px;
                    border-color: #F6F6F6;
                    box-shadow: none;
                    outline: none;">
                                            <option style=" height: 39px;
                    border-radius: 4px;
                    border: 1px solid #F6F6F6;
                    border-color: #F6F6F6;
                    background-color: #F6F6F6;
                    color: #020202;
                    font-family: Nunito;
                    font-size: 16px;
                    font-style: normal;
                    font-weight: 400;
                    line-height: normal;" v-for="item in netmaskItems" :value="item">{{ item }}</option>
                                            <v-icon>mdi-chevron-down</v-icon>
                                        </select>
                                    </div>
                                </td>

                            </tr>
                            <tr>
                                <td><span style="color: black;" class="inline-input">IPV4 gateway</span></td>
                                <td><v-btn class="ml-3 mt-2 " color="primary" text @click="openModal">
                                        <i class="fas fa-plus"></i>
                                        <span class="ml-2">Add</span>
                                    </v-btn></td>
                                <td> <select class="ml-3" v-model="value_setup_Ipv4.gateway" style="height: 39px;
                    width: 312px;
                    margin-bottom: 5px;
                    border-radius: 4px;
                    border: 1px solid #F6F6F6;
                    background-color: #F6F6F6;
                    color: #020202;
                    font-family: Nunito;
                    font-size: 16px;
                    font-style: normal;
                    font-weight: 400;
                    line-height: normal;
                    padding-left: 10px;
                    padding-right: 10px;
                    padding-top: 5px;
                    padding-bottom: 5px;
                    border-color: #F6F6F6;
                    box-shadow: none;
                    outline: none;
                    -webkit-appearance: none;
                    -moz-appearance: none;
                    appearance: none;
                    align-items: center;
                    justify-content: center;

                    ">
                                        <option style=" height: 39px;
                    width: 100%;
                    border-radius: 4px;
                    border: 1px solid #F6F6F6;
                    border-color: #F6F6F6;
                    background-color: #F6F6F6;
                    color: #020202;
                    font-family: Nunito;
                    font-size: 16px;
                    font-style: normal;
                    font-weight: 400;
                    line-height: normal;
                    padding-left: 10px;
                    padding-right: 10px;
                    padding-top: 5px;
                    padding-bottom: 5px;
                    border-color: #F6F6F6;
                    box-shadow: none;
                    outline: none;
                    -webkit-appearance: none;
                    -moz-appearance: none;
                    appearance: none;
                    align-items: center;
                    justify-content: center;
                    " v-for="item in allStaticGatewaysAddresses" :value="item">{{ item }}</option>
                                        <v-icon>mdi-chevron-down</v-icon>
                                    </select></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div v-if="ipv6SetupType === 'DHCP'">
                    <v-card-title style="color: #020202;
font-family: Nunito;
font-size: 18px;
font-style: normal;
font-weight: 700;
line-height: normal;">Configuring the DHCPv6 client</v-card-title>
                    <v-divider class="ml-3"></v-divider>
                    <v-row class="ml-3 mt-3">
                        <v-tabs v-model="activeTabIPV6" fixed-tabs background-color="#fff" color="#FFC300" dark>
                            <span style="color: #020202; background-color: #fff; height: ;" class="mt-4">
                                Setup mode</span>
                            <v-tab v-for="tab in tabsIPV6" :key="tab.id" class="ml-2">
                                <span style="color: #020202;">{{ tab.label }}</span>
                            </v-tab>
                            <v-tab-item v-for="tab in tabsIPV6" :key="tab.id">
                                <BasicConfigDHCPv6 v-if="tab.id == 1" />
                                <AdvancedConfigDHCPv6 v-if="tab.id == 2" />
                            </v-tab-item>
                        </v-tabs>
                    </v-row>
                    <v-card-title style="color: #020202;
font-family: Nunito;
font-size: 18px;
font-style: normal;
font-weight: 700;
line-height: normal;">Interface status</v-card-title>
                    <v-row class="ml-3 mt-9">
                        <div style="color: black;" class="ml-3">Use IPV4 connectivity</div>
                        <input type="checkbox" class="ml-5">
                        <div style="color: black;" class="ml-3">IPV4 Connectivity</div>
                    </v-row>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Use VLAN Priority</div>
                        <v-select class="ml-3 inline-input"></v-select>
                    </div>
                    <v-card-title>Interface status</v-card-title>
                    <v-divider class="ml-3"></v-divider>
                    <div class="ml-3 mt-2">
                        <div style="color: black;" class="ml-3 inline-input">Informations</div>
                        <input type="checkbox" class="ml-5 inline-input">
                        <div style="color: black;" class="ml-3 inline-input">Information only</div>
                    </div>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Send options</div>
                        <v-text-field label="Send options" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Request options</div>
                        <v-text-field label="Request options" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Script</div>
                        <v-text-field label="Script" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <v-row class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Identity association</div>
                        <div class="ml-16">
                            <input type="checkbox" class="inline-input" v-model="isTemporaryAddressAllocation">
                            <div style="color: black;" class="ml-2 inline-input">Temporary address allocation</div>
                            <br />
                            <!-- bloc to show when Non-temporary address allocation is checked -->
                            <div v-if="isTemporaryAddressAllocation">
                                <br />
                                <div style="color: black;" class="ml-3">id-assoc na ID</div>
                                <v-text-field class="ml-3 mb-10"></v-text-field>

                                <div style="color: black;" class="ml-3">Address IPv6-address</div>
                                <v-text-field class="ml-3  mb-10"></v-text-field>

                                <div style="color: black;" class="ml-3">Preferred Lifetime</div>
                                <v-text-field class="ml-3  mb-10"></v-text-field>

                                <div style="color: black;" class="ml-3">Valid time</div>
                                <v-text-field class="ml-3  mb-10"></v-text-field>
                            </div>
                            <input type="checkbox" class="inline-input" v-model="isPrefixDelegation">
                            <div style="color: black;" class="ml-2 inline-input">Prefix delegation</div>
                            <!-- bloc to show when prefix deligation is checked -->
                            <div v-if="isPrefixDelegation">
                                <br />
                                <div style="color: black;" class="ml-3">id-assoc na ID</div>
                                <v-text-field class="ml-3  mb-10"></v-text-field>

                                <div style="color: black;" class="ml-3">Address IPv6-address</div>
                                <v-text-field class="ml-3  mb-10"></v-text-field>

                                <div style="color: black;" class="ml-3">Preferred Lifetime</div>
                                <v-text-field class="ml-3  mb-10"></v-text-field>

                                <div style="color: black;" class="ml-3">Valid time</div>
                                <v-text-field class="ml-3  mb-10"></v-text-field>
                            </div>
                        </div>
                    </v-row>
                </div>
                <div v-if="false">
                    <v-card-title style="color: #020202;
font-family: Nunito;
font-size: 18px;
font-style: normal;
font-weight: 700;
line-height: normal;">Authentication</v-card-title>
                    <v-divider class="ml-3"></v-divider>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Authname</div>
                        <v-text-field label="Authname" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Protocol</div>
                        <v-text-field label="Protocol" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Algorithm</div>
                        <v-text-field label="Algorithm" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">rdm</div>
                        <v-text-field label="rdm" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <v-card-title style="color: #020202;
font-family: Nunito;
font-size: 18px;
font-style: normal;
font-weight: 700;
line-height: normal;">Key info</v-card-title>
                    <v-divider class="ml-3"></v-divider>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Keyname</div>
                        <v-text-field label="Keyname" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Royaume</div>
                        <v-text-field label="royaume" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Keyid</div>
                        <v-text-field label="keyid" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Secret</div>
                        <v-text-field label="secret" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3">
                        <div style="color: black;" class="ml-3 inline-input">Expire</div>
                        <v-text-field label="expire" class="ml-3 inline-input"></v-text-field>
                    </div>
                </div>
                <div v-if="setuptypeIP4 === 'DHCP'">
                    <v-card-title style="color: #020202;
font-family: Nunito;
font-size: 18px;
font-style: normal;
font-weight: 700;
line-height: normal;">Configuring the DHCP Client</v-card-title>
                    <v-divider class="ml-3"></v-divider>
                    <v-row class="ml-3 mt-3">
                        <v-tabs v-model="activeTab" fixed-tabs background-color="#fff" color="#FFC300" dark>
                            <span style="color: #020202; background-color: #fff;
                            height: ;" class="mt-4">
                                Setup mode</span>
                            <v-tab v-for="tab in tabs" :key="tab.id" class="ml-2">
                                <span style="color: #020202;">{{ tab.label }}</span>

                            </v-tab>
                            <v-tab-item v-for="tab in tabs" :key="tab.id">
                                <BasicConfigDHCPv4 v-if="tab.id == 1" />
                                <AdvancedConfigDHCPv4 v-if="tab.id == 2" />
                            </v-tab-item>
                        </v-tabs>
                    </v-row>
                </div>
                <div v-if="false">
                    <v-card-title style="color: #020202;
font-family: Nunito;
font-size: 18px;
font-style: normal;
font-weight: 700;
line-height: normal;">Protocol Timing</v-card-title>
                    <v-divider class="ml-3"></v-divider>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Timeout</div>
                        <input type="checkbox" class="ml-5 inline-input">
                        <div style="color: black;" class="ml-2 inline-input">information only</div>

                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Try again</div>
                        <v-text-field label="Hostname" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Select expiration</div>
                        <v-text-field label="Select expiration" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">restart</div>
                        <v-text-field label="restart" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Backoff Cutoff</div>
                        <v-text-field label="Backoff Cutoff" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Initial Interval</div>
                        <v-text-field label="Initial Interval" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <v-card-title style="color: #020202;
font-family: Nunito;
font-size: 18px;
font-style: normal;
font-weight: 700;
line-height: normal;">Lease Requirements</v-card-title>
                    <v-divider class="ml-3"></v-divider>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Send options DHCP Client</div>
                        <v-text-field label="Send options DHCP Client" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Send Options lease time</div>
                        <v-text-field label="Send Options lease time" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Request Options</div>
                        <v-text-field label="Request Options" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Required Options</div>
                        <v-text-field label="Required Options" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Supersede domaine name</div>
                        <v-text-field label="Supersede domaine name" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Prepend domain server</div>
                        <v-text-field label="Prepend domain server" class="ml-3 inline-input"></v-text-field>
                    </div>
                </div>
                <div v-if="setuptypeIP4 === 'PPP'">
                    <v-card-title style="color: #020202;
font-family: Nunito;
font-size: 18px;
font-style: normal;
font-weight: 700;
line-height: normal;">Configuration PPP</v-card-title>
                    <v-divider class="ml-3"></v-divider>
                    <v-card elevation="9" class="ml-3 mt-3 mr-3" title="Service provider (FAI)">
                        <v-card-title class="headline grey lighten-2 text-center" primary-title>
                            <v-row justify="center">
                                <h5>Service provider(FAI)</h5>
                            </v-row>
                        </v-card-title>
                        <v-card-text>
                            <v-container class="grey lighten-5">
                                <v-row no-gutters>
                                    <v-col sm="5" md="6" class="mt-7">
                                        Country
                                    </v-col>
                                    <v-col sm="5" offset-sm="2" md="6" offset-md="0">
                                        <v-select :items="items" label="Country" class="inline-input"></v-select>
                                    </v-col>
                                </v-row>
                                <v-row no-gutters>
                                    <v-col sm="5" md="6" class="mt-7">
                                        Access provider
                                    </v-col>
                                    <v-col sm="5" offset-sm="2" md="6" offset-md="0">
                                        <v-select :items="items" label="Access provider" class="inline-input"></v-select>
                                    </v-col>
                                </v-row>
                                <v-row no-gutters>
                                    <v-col sm="5" md="6" class="mt-7">
                                        Plan
                                    </v-col>
                                    <v-col sm="5" offset-sm="2" md="6" offset-md="0">
                                        <v-select :items="items" label="Plan" class="inline-input"></v-select>
                                    </v-col>
                                </v-row>
                            </v-container>
                        </v-card-text>
                    </v-card>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Username</div>
                        <v-text-field label="Username" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Password</div>
                        <v-text-field label="Password" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Local IP @</div>
                        <v-text-field label="Local IP @" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Distant IP @</div>
                        <v-text-field label="Distant IP @" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Host-uniq</div>
                        <v-text-field label="Host-uniq" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Connection on demand</div>
                        <input type="checkbox" class="ml-5 inline-input">
                        <div style="color: black;" class="ml-2 inline-input">Enable dial-on-demand mode</div>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Inactivity timeout</div>
                        <v-text-field label="Inactivity timeout" class="ml-3 inline-input"></v-text-field>
                    </div>
                </div>
                <div v-if="ipv6SetupType === 'static'">
                    <v-card-title style="color: #020202;
font-family: Nunito;
font-size: 18px;
font-style: normal;
font-weight: 700;
line-height: normal;">Static IPv6 address configuration</v-card-title>
                    <v-divider class="ml-3"></v-divider>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Username</div>
                        <v-text-field label="Username" class="ml-3 inline-input"></v-text-field>
                        <v-select class="ml-3 inline-input"></v-select>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">IPv6 gateway</div>
                        <v-btn class="ml-3 mt-2 " color="primary" text @click="openModalIPv6">
                            <v-icon>mdi-plus</v-icon>
                            <span class="ml-2">Add</span>
                        </v-btn>
                        <v-text-field label="IPv6 gateway" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">USE ipv4 connectivity</div>
                        <input type="checkbox" class="ml-5 inline-input">
                        <div style="color: black;" class="ml-2 inline-input">USE ipv4 connectivity</div>
                    </div>
                </div>
                <div v-if="false">
                    <v-card-title style="color: #020202;
font-family: Nunito;
font-size: 18px;
font-style: normal;
font-weight: 700;
line-height: normal;">6RD Rapid Deployment</v-card-title>
                    <v-divider class="ml-3"></v-divider>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Préfix 6RD</div>
                        <v-text-field label="Préfix 6RD" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">6RD Edge Relay</div>
                        <v-text-field label="6RD Edge Relay" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Préfixe length IPv4 6RD</div>
                        <v-select class="ml-3 inline-input"></v-select>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">6RD IPv4 Prefix address</div>
                        <v-text-field label="6RD IPv4 Prefix address" class="ml-3 inline-input"></v-text-field>
                    </div>
                </div>
                <div v-if="false">
                    <v-card-title style="color: #020202;
font-family: Nunito;
font-size: 18px;
font-style: normal;
font-weight: 700;
line-height: normal;">Track IPv6 interface</v-card-title>
                    <v-divider class="ml-3"></v-divider>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">IPv6 interface</div>
                        <v-select class="ml-3 inline-input"></v-select>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Prefix ID IPv6</div>
                        <v-text-field label="Prefix ID IPv6" class="ml-3 inline-input"></v-text-field>
                    </div>
                    <div class="ml-3 mt-3">
                        <div style="color: black;" class="ml-3 inline-input">Manual configuration</div>
                        <input type="checkbox" class="ml-2 inline-input">
                        <v-col lg="4" style="color: black;" class="inline-input">Alow manual adjustment of DHCPv6 and Router
                            Advertisements
                        </v-col>
                    </div>
                </div>
            </v-col>
        </v-row>
        <v-spacer></v-spacer>
        <br />
        <div class="text-center">
            <v-btn large rounded outlined color="#086eae" class="mr-3 trac-cancel" @click="cancel">Cancel</v-btn>
            <v-btn large rounded outlined color="#ffff" class="mr-3 trac-edit" @click="addNetwork">
                Save
            </v-btn>
        </div>
        <br />
        <v-alert type="success" variant="outlined" elevation="2" class="ml-3" icon="mdi-check-circle-outline"
            style="width: 20%;" border="top" v-if="showAlert" :style="alertStyle">
            Configuration saved successfully
        </v-alert>
        <br /><br /><br /><br />
        <v-dialog style="
    position: fixed;
    overflow-x: unset; /* Hide horizontal overflow */
    overflow-y: unset; /* Remove the vertical scroll */
    " max-width="600px" v-model="showModal">
            <v-card class="ml-3 mr-3">
                <v-card-title>
                    <span class="headline font-weight-bold">Add IPv4 Gateway</span>
                </v-card-title>
                <v-card-text>
                    <v-container>
                        <v-row>
                            <v-text-field label="Enter Gateway Name" v-model="gateway.gwname"></v-text-field>
                        </v-row>
                        <v-row>
                            <v-text-field label="Enter Gateway IPV4" v-model="gateway.gwaddress"></v-text-field></v-row>
                        <v-row> <v-text-field label="Enter Description"
                                v-model="gateway.description"></v-text-field></v-row>
                        <v-row>
                            <input type="checkbox" v-model="gateway.default_aux">
                            <label class="ml-3">Default Gateway</label>
                        </v-row>
                        <v-row>
                            <input type="checkbox" v-model="gateway.far_aux">
                            <label class="ml-3">Far Gateway</label>
                        </v-row>
                        <v-row>
                            <input type="checkbox" v-model="gateway.multiwan_aux">
                            <label class="ml-3">Multi-WAN Gateway</label>
                        </v-row>
                    </v-container>
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn large rounded outlined color="#086eae" class="mr-3 trac-cancel" @click="cancelGateway">
                        Cancel
                    </v-btn>
                    <v-btn large rounded outlined color="#ffff" class="mr-3 trac-edit" @click="addGateway">
                        Save
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </v-card>
</template>

<script>
// import { network } from "@/services/network.js";
import axios from 'axios';
import BasicConfigDHCPv4 from '../shared/BasicConfigDHCPv4.vue';
import AdvancedConfigDHCPv4 from '../shared/AdvancedConfigDHCPv4.vue';
import AdvancedConfigDHCPv6 from '../shared/AdvancedConfigDHCPv6.vue';
import BasicConfigDHCPv6 from '../shared/BasicConfigDHCPv6.vue';

export default {
    name: "IfNameComponent",
    components: {
        BasicConfigDHCPv4,
        AdvancedConfigDHCPv4,
        AdvancedConfigDHCPv6,
        BasicConfigDHCPv6
    },
    props: {
        activeTab: {
            type: String,
        },
    },
    data() {
        return {
            activeTabIPV6: 0,
            tabs: [
                { id: 1, label: "Basic" },
                { id: 2, label: "Advanced" },
            ],
            tabsIPV6: [
                { id: 1, label: "Basic" },
                { id: 2, label: "Advanced" },
            ],
            items: [
                { text: "DHCP", value: "DHCP" },
                { text: "Static", value: "static" },
                // { text: "PPP", value: "PPP" },
                // { text: "PPPoE", value: "PPPoE" },
                // { text: "L2TP", value: "L2TP" },
                // { text: "PPTP", value: "PPTP" },
                // { text: "SLIP", value: "SLIP" },
                // { text: "6RD", value: "6RD" },
                // { text: "6to4", value: "6to4" },
                // { text: "Track Interface", value: "Track Interface" },
                // { text: "GRE", value: "GRE" },
                // { text: "IPsec", value: "IPsec" },
            ],
            speedDuplexItems: [
                '100baseTx-FD',
                '100baseTx-HD',
                '10baseT-FD',
                '10baseT-HD',
                '100baseTX',
                '10BaseT/UTP full duplex',
                '10BaseT/UTP',
            ],
            netmaskItems: [
                '1',
                '2',
                '3',
                '4',
                '5',
                '6',
                '7',
                '8',
                '9',
                '10',
                '11',
                '12',
                '13',
                '14',
                '15',
                '16',
                '17',
                '18',
                '19',
                '20',
                '21',
                '22',
                '23',
                '24',
                '25',
                '26',
                '27',
                '28',
                '29',
                '30',
                '31',
                '32',
            ],
            ipv6Items: [
                'DHCPv6',
                'Static',
                'SLAAC',
                '6to4',
                '6RD',
                'Track Interface',
                'PPPoE',
            ],
            activate: false,
            device: "",
            description: "",
            private_aux: false,
            bogon_aux: false,

            setuptypeIP4: "",
            ipv6SetupType: "",

            addmac: "",
            mtuV: "",
            mssV: "",
            speed_duplex: "",

            dynamicGatewayPolicy: false,
            showAlert: false,
            showModal: false,
            gateway: {
                gwname: "",
                gwaddress: "",
                description: "",
                default_aux: false,
                far_aux: false,
                multiwan_aux: false,
            },
            name_interface: "",
            value_setup_Ipv4: {
                ip_address4: "",
                netmask4: "",
                gateway: {
                    id: "",
                    value: ""
                },
            },
            IPV4Config: {},
            allStaticGateways: [],
        };
    },
    computed: {
        alertStyle() {
            return {
                position: "fixed",
                top: "20px",
                right: "20px",
                width: "20%",
            };
        },
        allStaticGatewaysAddresses() {
            return this.allStaticGateways.map((gateway) => gateway.gwaddress);
        },
    },
    methods: {
        addNetwork() {
            const params = {
                name_interface: this.activeTab,
                device: this.device,
                description: this.description,
                private_aux: this.private_aux,
                bogon_aux: this.bogon_aux,
                addmac: this.addmac,
                mtuV: this.mtuV,
                mssV: this.mssV,
                speed_duplex: this.speed_duplex,
                setuptypeIP4: this.setuptypeIP4,
                value_setup_Ipv4: {
                    ip_address4: this.value_setup_Ipv4.ip_address4,
                    netmask4: this.value_setup_Ipv4.netmask4,
                    gateway: {
                        value: this.gateway.value
                    },
                }
            };
            function getCookie(name) {
                let cookieValue = null;
                if (document.cookie && document.cookie !== '') {
                    const cookies = document.cookie.split(';');
                    for (let i = 0; i < cookies.length; i++) {
                        const cookie = cookies[i].trim();
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) === (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            const csrfToken = getCookie('csrftoken')
            axios.defaults.headers.common['X-CSRFToken'] = csrfToken;

            axios.put('/network/conf/' + this.activeTab, params)
                .then((response) => {
                    console.log(response);
                    this.showAlert = true;
                    setTimeout(() => {
                        this.showAlert = false;
                    }, 3000);
                }, (error) => {
                    console.log(error);
                });
        },
        cancel() {
            this.$emit("cancel");
        },
        openModal() {
            this.showModal = true;
        },
        addGateway() {
            const params = {
                gwname: this.gateway.gwname,
                gwaddress: this.gateway.gwaddress,
                description: this.gateway.description,
                default_aux: this.gateway.default_aux,
                far_aux: this.gateway.far_aux,
                multiwan_aux: this.gateway.multiwan_aux,
            };
            function getCookie(name) {
                let cookieValue = null;
                if (document.cookie && document.cookie !== '') {
                    const cookies = document.cookie.split(';');
                    for (let i = 0; i < cookies.length; i++) {
                        const cookie = cookies[i].trim();
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) === (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            const csrfToken = getCookie('csrftoken')
            axios.defaults.headers.common['X-CSRFToken'] = csrfToken;

            axios.post('/gateway/addStaticGateway', params)
                .then((response) => {
                    console.log(response);
                    this.showAlert = true;
                    setTimeout(() => {
                        this.showAlert = false;
                    }, 3000);
                }, (error) => {
                    console.log(error);
                });
        },
        cancelGateway() {
            this.showModal = false;
            this.gateway = {
                gwname: "",
                gwaddress: "",
                description: "",
                default_aux: false,
                far_aux: false,
                multiwan_aux: false,
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
            console.log(params);
            function getCookie(name) {
                let cookieValue = null;
                if (document.cookie && document.cookie !== '') {
                    const cookies = document.cookie.split(';');
                    for (let i = 0; i < cookies.length; i++) {
                        const cookie = cookies[i].trim();
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) === (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            const csrfToken = getCookie('csrftoken')
            axios.defaults.headers.common['X-CSRFToken'] = csrfToken;

            axios.put('/gateway/updateStaticGateway', params)
                .then((response) => {
                    console.log(response);
                    this.showAlert = true;
                    setTimeout(() => {
                        this.showAlert = false;
                    }, 3000);
                }, (error) => {
                    console.log(error);
                });
        }
    },
    mounted() {
        this.IPV4Config = this.$root.$data.IPV4Config;
        let validJsonString = this.IPV4Config
            .replace(/'/g, '"')
            .replace(/True/g, 'true')
            .replace(/False/g, 'false')
            .replace(/None/g, 'null');
        let parsedArray = JSON.parse(validJsonString);
        this.IPV4Config = parsedArray;

        this.allStaticGateways = this.$root.$data.allStaticGateways;
        validJsonString = this.allStaticGateways
            .replace(/'/g, '"')
            .replace(/True/g, 'true')
            .replace(/False/g, 'false')
            .replace(/None/g, 'null');
        parsedArray = JSON.parse(validJsonString);
        this.allStaticGateways = parsedArray;

        this.activate = this.IPV4Config.interface !== null ? true : false;
        this.device = this.IPV4Config.interface.ifname;
        this.description = this.IPV4Config.interface.description;

        this.private_aux = this.IPV4Config.interface.private;
        this.bogon_aux = this.IPV4Config.interface.bogon;

        this.addmac = this.IPV4Config.genericConfig.addmac;
        this.mtuV = this.IPV4Config.genericConfig.mtuV;
        this.mssV = this.IPV4Config.genericConfig.mssV;
        this.speed_duplex = this.IPV4Config.genericConfig.speed_duplex;

        this.setuptypeIP4 = this.IPV4Config.IPV4Config.typeIP4;
        this.value_setup_Ipv4.ip_address4 = this.IPV4Config.IPV4Config.ip_address;
        this.value_setup_Ipv4.netmask4 = this.IPV4Config.IPV4Config.netmask;

        this.name_interface = this.IPV4Config.interface.name_interface;

        this.ipv6SetupType = this.IPV4Config.IPV4Config.typeDHCP;
    },
};
</script>
<style scoped>
.inline-label {
    display: inline-block;
    vertical-align: middle;
}

.inline-input {
    display: inline-block;
    vertical-align: middle;
}

.bold-title {
    font-weight: bold;
}

.v-text-field {
    padding-top: 12px;
    margin-top: -2px;
}

.text-label-title {
    color: #838383;
    font-family: Nunito;
    font-size: 16px;
    font-style: normal;
    font-weight: 400;
    line-height: normal;
}

.action-button:hover {
    color: #086eae;
}

.action-button.update {
    color: #00b300;
}

.action-button.cancel {
    color: #ff0000;
}

.action-button.edit {
    color: #086eae;
}

.action-button.delete {
    color: #086eae;
}


.trac-edit {
    height: 43px;
    width: 183px;
    background-color: #086eae;
    color: #ffffff;
    font-family: "Nunito-Regular", Helvetica;
    left: 0;
    letter-spacing: 0;
    line-height: normal;
    text-align: center;
    text-transform: capitalize;
}

.trac-cancel {
    height: 43px;
    width: 183px;

    font-family: "Nunito-Regular", Helvetica;
    left: 0;
    letter-spacing: 0;
    line-height: normal;
    text-align: center;
    text-transform: capitalize;
}
</style>
