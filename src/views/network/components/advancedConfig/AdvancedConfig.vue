<template>
  <div>
    
          <div v-if="ipv6SetupType === 'DHCP'">
            <v-card-title class="title-text"
              >Configuring the DHCPv6 client</v-card-title
            >
            <v-divider
              class="ml-3"
              style="height: 39px; width: 425px"
            ></v-divider>
            <v-row class="ml-3 mt-3">
              <v-tabs
                v-tabs
                v-model="activeTabIPV6"
                fixed-tabs
                background-color="#fff"
                color="#FFC300"
                dark
              >
                <span
                  style="color: #020202; background-color: #fff; height: "
                  class="mt-4"
                >
                  Setup mode</span
                >
                <v-tab v-for="tab in tabsIPV6" :key="tab.label" class="ml-2">
                  <span style="color: #020202">{{ tab.label }}</span>
                </v-tab>
              </v-tabs>

              <v-window v-model="activeTabIPV6">
                <v-window-item
                  v-for="tab in tabsIPV6"
                  :key="tab.label"
                  :value="tab.label"
                >
                  <BasicConfigDHCPv6 />
                </v-window-item>
                <v-window-item
                  v-for="tab in tabs"
                  :key="tab.label"
                  :value="tab.label"
                >
                  <AdvancedConfigDHCPv6 />
                </v-window-item>
              </v-window>
            </v-row>
            <v-card-title class="title-text">Interface status</v-card-title>
            <v-row class="ml-3 mt-9">
              <div style="color: black" class="ml-3">Use IPV4 connectivity</div>
              <input type="checkbox" class="ml-5" />
              <div style="color: black" class="ml-3">IPV4 Connectivity</div>
            </v-row>
            <div class="ml-3">
              <div style="color: black" class="ml-3 inline-input">
                Use VLAN Priority
              </div>
              <v-select class="ml-3 inline-input"></v-select>
            </div>
            <v-card-title class="title-text">Interface status</v-card-title>
            <v-divider class="ml-3"></v-divider>
            <div class="ml-3 mt-2">
              <div style="color: black" class="ml-3 inline-input">
                Informations
              </div>
              <input type="checkbox" class="ml-5 inline-input" />
              <div style="color: black" class="ml-3 inline-input">
                Information only
              </div>
            </div>
            <div class="ml-3">
              <div style="color: black" class="ml-3 inline-input">
                Send options
              </div>
              <v-text-field
                label="Send options"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3">
              <div style="color: black" class="ml-3 inline-input">
                Request options
              </div>
              <v-text-field
                label="Request options"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3">
              <div style="color: black" class="ml-3 inline-input">Script</div>
              <v-text-field
                label="Script"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <v-row class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                Identity association
              </div>
              <div class="ml-16">
                <input
                  type="checkbox"
                  class="inline-input"
                  v-model="isTemporaryAddressAllocation"
                />
                <div style="color: black" class="ml-2 inline-input">
                  Temporary address allocation
                </div>
                <br />
                <div v-if="isTemporaryAddressAllocation">
                  <br />
                  <div style="color: black" class="ml-3">id-assoc na ID</div>
                  <v-text-field class="ml-3 mb-10"></v-text-field>

                  <div style="color: black" class="ml-3">
                    Address IPv6-address
                  </div>
                  <v-text-field class="ml-3 mb-10"></v-text-field>

                  <div style="color: black" class="ml-3">
                    Preferred Lifetime
                  </div>
                  <v-text-field class="ml-3 mb-10"></v-text-field>

                  <div style="color: black" class="ml-3">Valid time</div>
                  <v-text-field class="ml-3 mb-10"></v-text-field>
                </div>
                <input
                  type="checkbox"
                  class="inline-input"
                  v-model="isPrefixDelegation"
                />
                <div style="color: black" class="ml-2 inline-input">
                  Prefix delegation
                </div>
                <div v-if="isPrefixDelegation">
                  <br />
                  <div style="color: black" class="ml-3">id-assoc na ID</div>
                  <v-text-field class="ml-3 mb-10"></v-text-field>

                  <div style="color: black" class="ml-3">
                    Address IPv6-address
                  </div>
                  <v-text-field class="ml-3 mb-10"></v-text-field>

                  <div style="color: black" class="ml-3">
                    Preferred Lifetime
                  </div>
                  <v-text-field class="ml-3 mb-10"></v-text-field>

                  <div style="color: black" class="ml-3">Valid time</div>
                  <v-text-field class="ml-3 mb-10"></v-text-field>
                </div>
              </div>
            </v-row>
          </div>
          <div v-if="false">
            <v-card-title class="title-text">Authentication</v-card-title>
            <v-divider class="ml-3"></v-divider>
            <div class="ml-3">
              <div style="color: black" class="ml-3 inline-input">Authname</div>
              <v-text-field
                label="Authname"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3">
              <div style="color: black" class="ml-3 inline-input">Protocol</div>
              <v-text-field
                label="Protocol"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3">
              <div style="color: black" class="ml-3 inline-input">
                Algorithm
              </div>
              <v-text-field
                label="Algorithm"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3">
              <div style="color: black" class="ml-3 inline-input">rdm</div>
              <v-text-field
                label="rdm"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <v-card-title class="title-text">Key info</v-card-title>
            <v-divider class="ml-3"></v-divider>
            <div class="ml-3">
              <div style="color: black" class="ml-3 inline-input">Keyname</div>
              <v-text-field
                label="Keyname"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3">
              <div style="color: black" class="ml-3 inline-input">Royaume</div>
              <v-text-field
                label="royaume"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3">
              <div style="color: black" class="ml-3 inline-input">Keyid</div>
              <v-text-field
                label="keyid"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3">
              <div style="color: black" class="ml-3 inline-input">Secret</div>
              <v-text-field
                label="secret"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3">
              <div style="color: black" class="ml-3 inline-input">Expire</div>
              <v-text-field
                label="expire"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
          </div>
          
          <div v-if="false">
            <v-card-title class="title-text">Protocol Timing</v-card-title>
            <v-divider class="ml-3"></v-divider>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">Timeout</div>
              <input type="checkbox" class="ml-5 inline-input" />
              <div style="color: black" class="ml-2 inline-input">
                information only
              </div>
            </div>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                Try again
              </div>
              <v-text-field
                label="Hostname"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                Select expiration
              </div>
              <v-text-field
                label="Select expiration"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">restart</div>
              <v-text-field
                label="restart"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                Backoff Cutoff
              </div>
              <v-text-field
                label="Backoff Cutoff"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                Initial Interval
              </div>
              <v-text-field
                label="Initial Interval"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <v-card-title class="title-text">Lease Requirements</v-card-title>
            <v-divider class="ml-3"></v-divider>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                Send options DHCP Client
              </div>
              <v-text-field
                label="Send options DHCP Client"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                Send Options lease time
              </div>
              <v-text-field
                label="Send Options lease time"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                Request Options
              </div>
              <v-text-field
                label="Request Options"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                Required Options
              </div>
              <v-text-field
                label="Required Options"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                Supersede domaine name
              </div>
              <v-text-field
                label="Supersede domaine name"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                Prepend domain server
              </div>
              <v-text-field
                label="Prepend domain server"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
          </div>
          <div v-if="setuptypeip4 === 'PPP'">
            <v-card-title class="title-text">Configuration PPP</v-card-title>
            <v-divider class="ml-3"></v-divider>
            <v-card
              elevation="9"
              class="ml-3 mt-3 mr-3"
              title="Service provider (FAI)"
            >
              <v-card-title
                class="headline grey lighten-2 text-center title-text"
                primary-title
              >
                <v-row justify="center">
                  <h5>Service provider(FAI)</h5>
                </v-row>
              </v-card-title>
              <v-card-text>
                <v-container class="grey lighten-5">
                  <v-row no-gutters>
                    <v-col sm="5" md="6" class="mt-7"> Country </v-col>
                    <v-col sm="5" offset-sm="2" md="6" offset-md="0">
                      <v-select
                        :items="items"
                        label="Country"
                        class="inline-input"
                      ></v-select>
                    </v-col>
                  </v-row>
                  <v-row no-gutters>
                    <v-col sm="5" md="6" class="mt-7"> Access provider </v-col>
                    <v-col sm="5" offset-sm="2" md="6" offset-md="0">
                      <v-select
                        :items="items"
                        label="Access provider"
                        class="inline-input"
                      ></v-select>
                    </v-col>
                  </v-row>
                  <v-row no-gutters>
                    <v-col sm="5" md="6" class="mt-7"> Plan </v-col>
                    <v-col sm="5" offset-sm="2" md="6" offset-md="0">
                      <v-select
                        :items="items"
                        label="Plan"
                        class="inline-input"
                      ></v-select>
                    </v-col>
                  </v-row>
                </v-container>
              </v-card-text>
            </v-card>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">Username</div>
              <v-text-field
                label="Username"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">Password</div>
              <v-text-field
                label="Password"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                Local IP @
              </div>
              <v-text-field
                label="Local IP @"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                Distant IP @
              </div>
              <v-text-field
                label="Distant IP @"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                Host-uniq
              </div>
              <v-text-field
                label="Host-uniq"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                Connection on demand
              </div>
              <input type="checkbox" class="ml-5 inline-input" />
              <div style="color: black" class="ml-2 inline-input">
                Enable dial-on-demand mode
              </div>
            </div>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                Inactivity timeout
              </div>
              <v-text-field
                label="Inactivity timeout"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
          </div>
          <div v-if="ipv6SetupType === 'static'">
            <v-card-title class="title-text"
              >Static IPv6 address configuration</v-card-title
            >
            <v-divider class="ml-3"></v-divider>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">Username</div>
              <v-text-field
                label="Username"
                class="ml-3 inline-input"
              ></v-text-field>
              <v-select class="ml-3 inline-input"></v-select>
            </div>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                IPv6 gateway
              </div>
              <v-btn class="ml-3 mt-2" color="primary" text>
                <v-icon>mdi-plus</v-icon>
                <span class="ml-2">Add</span>
              </v-btn>
              <v-text-field
                label="IPv6 gateway"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                USE ipv4 connectivity
              </div>
              <input type="checkbox" class="ml-5 inline-input" />
              <div style="color: black" class="ml-2 inline-input">
                USE ipv4 connectivity
              </div>
            </div>
          </div>
          <div v-if="false">
            <v-card-title class="title-text">6RD Rapid Deployment</v-card-title>
            <v-divider class="ml-3"></v-divider>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                Préfix 6RD
              </div>
              <v-text-field
                label="Préfix 6RD"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                6RD Edge Relay
              </div>
              <v-text-field
                label="6RD Edge Relay"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                Préfixe length IPv4 6RD
              </div>
              <v-select class="ml-3 inline-input"></v-select>
            </div>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                6RD IPv4 Prefix address
              </div>
              <v-text-field
                label="6RD IPv4 Prefix address"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
          </div>
          <div v-if="false">
            <v-card-title class="title-text">Track IPv6 interface</v-card-title>
            <v-divider class="ml-3"></v-divider>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                IPv6 interface
              </div>
              <v-select class="ml-3 inline-input"></v-select>
            </div>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                Prefix ID IPv6
              </div>
              <v-text-field
                label="Prefix ID IPv6"
                class="ml-3 inline-input"
              ></v-text-field>
            </div>
            <div class="ml-3 mt-3">
              <div style="color: black" class="ml-3 inline-input">
                Manual configuration
              </div>
              <input type="checkbox" class="ml-2 inline-input" />
              <v-col lg="4" style="color: black" class="inline-input"
                >Alow manual adjustment of DHCPv6 and Router Advertisements
              </v-col>
            </div>
          </div>
  </div>
</template>

<script>
export default {
  name: 'AdvancedConfig',
  // Your JavaScript code here
}
</script>

<style>
/* Your CSS code here */
</style>
