<template>
    <div>
        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span id="politiques-connexion">Définition des politiques de connexion</span>
        </h3>

        <p class=" pb-3">
            L'étape finale consiste à définir des politiques entre les relais et les
            identités (client et serveur) à travers les attributs.
        </p>

        <div class="d-flex justify-center align-center py-2">
            <img class="rounded-md" src="@/assets/images/services/ztna/relaypolicy.png" style="width: 100%" />
        </div>
        <p class=" py-2">
            Description des paramètres.
        </p>

        <div class="relative overflow-x-auto py-2">
            <v-table density="comfortable">
                <tbody>
                    <tr>
                        <th class="font-weight-medium text-left">Nom du politique relais</th>
                        <td>Ajouter un nom au choix</td>
                    </tr>
                    <tr>
                        <th class="font-weight-medium text-left">Sémantique</th>
                        <td>ALLOF / ANYOF</td>
                    </tr>
                    <tr>
                        <th class="font-weight-medium text-left">Attribut relais</th>
                        <td>Attribut relais créé précédemment</td>
                    </tr>
                    <tr>
                        <th class="font-weight-medium text-left">Attribut identité</th>
                        <td>Attribut identité créé précédemment</td>
                    </tr>
                    <tr>
                        <th class="font-weight-medium text-left">Description</th>
                        <td>Champs optionnel</td>
                    </tr>
                </tbody>
            </v-table>
        </div>

        <p class=" py-2">
            Ensuite, on définit la politique entre le service et l'identité (client
            "Dial" et serveur "Bind").
        </p>
        <div class="d-flex justify-center align-center py-2">
            <img class="rounded-md" src="@/assets/images/services/ztna/servicepolicy.png" style="width: 100%" />
        </div>

        <p class=" py-2">
            Description des paramètres.
        </p>

        <div class="relative overflow-x-auto py-2">
            <v-table density="compact">
                <tbody>
                    <tr>
                        <th class="text-left font-weight-medium">Nom du politique relais</th>
                        <td>Ajouter un nom au choix</td>
                    </tr>
                    <tr>
                        <th class="text-left font-weight-medium">Type</th>
                        <td>Bind / Dial</td>
                    </tr>
                    <tr>
                        <th class="text-left font-weight-medium">Sémantique</th>
                        <td>ALLOF / ANYOF</td>
                    </tr>
                    <tr>
                        <th class="text-left font-weight-medium">Attribut service</th>
                        <td>Attribut service crée précédemment</td>
                    </tr>
                    <tr>
                        <th class="text-left font-weight-medium">Attribut identité</th>
                        <td>Attribut identité crée précédemment</td>
                    </tr>
                    <tr>
                        <th class="text-left font-weight-medium">Description</th>
                        <td>Champs optionnel</td>
                    </tr>
                </tbody>
            </v-table>
        </div>

        <p class=" py-2">
            Finalement, on définit la politique entre le service et le relais.
        </p>

        <div class="d-flex justify-center align-center py-2">
            <img class="rounded-md" src="@/assets/images/services/ztna/relser.png" style="width: 100%" />
        </div>

        <p class=" py-2">
            Description des paramètres.
        </p>

        <div class="relative overflow-x-auto py-2">
            <v-table density="compact">
                <tbody>
                    <tr>
                        <th class="text-left font-weight-medium">Nom du politique service-relais</th>
                        <td>Ajouter un nom au choix</td>
                    </tr>
                    <tr>
                        <th class="text-left font-weight-medium">Sémantique</th>
                        <td>ALLOF / ANYOF</td>
                    </tr>
                    <tr>
                        <th class="text-left font-weight-medium">Attribut service</th>
                        <td>Attribut service crée précédemment</td>
                    </tr>
                    <tr>
                        <th class="text-left font-weight-medium">Attribut relais</th>
                        <td>Attribut relais crée précédemment</td>
                    </tr>
                    <tr>
                        <th class="text-left font-weight-medium">Description</th>
                        <td>Champs optionnel</td>
                    </tr>
                </tbody>
            </v-table>
        </div>
    </div>
</template>