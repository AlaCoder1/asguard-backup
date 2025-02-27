<template>
    <div>
        <h3 class="font-weight-bold text-1xl pb-2" style="font-size: 20px">
            <span id="Configuration-connexion">Configuration de la connexion
            </span>
        </h3>

        <p class=" pb-4">
            Passez à la page de configuration, cliquez sur "Ajouter Config
            intercept" et remplissez les champs.
        </p>

        <div class="d-flex justify-center align-center mb-7">
            <img class="rounded-md" src="@/assets/images/services/ztna/boutonintercpt.png" style="width: 100%" />
        </div>
        <div class="d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/ztna/intercept.png" style="width: 100%" />
        </div>

        <p class=" py-2">
            Description des paramètres.
        </p>

        <div class="relative overflow-x-auto py-3">
            <v-table>
                <tbody>
                    <tr>
                        <th class="font-weight-medium">Nom du config</th>
                        <td>Ajouter un nom au choix</td>
                    </tr>
                    <tr>
                        <th class="font-weight-medium">Protocole</th>
                        <td>UDP / TCP</td>
                    </tr>
                    <tr>
                        <th class="font-weight-medium">Adresse</th>
                        <td>Ajouter une adresse à accéder au choix</td>
                    </tr>
                    <tr>
                        <th class="font-weight-medium">Port Low</th>
                        <td>[0, 65535]</td>
                    </tr>
                    <tr>
                        <th class="font-weight-medium">Port High</th>
                        <td>[0, 65535]</td>
                    </tr>
                    <tr>
                        <th class="font-weight-medium">Description</th>
                        <td>Champs optionnel</td>
                    </tr>
                </tbody>
            </v-table>
        </div>

        <p class=" py-2">
            Dans la même page, configurez le <span id="config-hôte">config hôte</span>
        </p>

        <div class="d-flex justify-center align-center mb-7">
            <img class="rounded-md" src="@/assets/images/services/ztna/boutonhost.png" style="width: 100%" />
        </div>
        <div class="d-flex justify-center align-center mb-7">
            <img class="rounded-md" src="@/assets/images/services/ztna/host.png" style="width: 100%" />
        </div>

        <div class="relative overflow-x-auto py-3">
            <v-table density="comfortable">
                <tbody>
                    <tr>
                        <th class="font-weight-medium text-left">Nom du config</th>
                        <td>Ajouter un nom au choix</td>
                    </tr>
                    <tr>
                        <th class="font-weight-medium text-left">Protocole</th>
                        <td>UDP / TCP</td>
                    </tr>
                    <tr>
                        <th class="font-weight-medium text-left">Adresse</th>
                        <td>localhost (adresse serveur)</td>
                    </tr>
                    <tr>
                        <th class="font-weight-medium text-left">Port</th>
                        <td>[0, 65535]</td>
                    </tr>
                    <tr>
                        <th class="font-weight-medium text-left">Description</th>
                        <td>Champs optionnel</td>
                    </tr>
                </tbody>
            </v-table>
        </div>
    </div>
</template>