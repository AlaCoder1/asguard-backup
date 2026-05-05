<template>
    <div>
        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span id="Création-service">Création du service </span>
        </h3>

        <p class="pb-2">
            Après avoir créé les configurations, il faut les connecter à travers un
            service. Pour cela, dans la page du service, cliquez sur "Ajouter un
            service" et remplissez les champs.
        </p>

        <div class="d-flex justify-center align-center mb-2">
            <img class="rounded-md" src="@/assets/images/services/ztna/service.png" style="width: 100%" />
        </div>

        <p class="py-2">
            Description des paramètres.
        </p>

        <div class="relative overflow-x-auto py-2">
            <v-table density="comfortable">
                <tbody>
                    <tr>
                        <th class="font-weight-medium text-left">Nom du service</th>
                        <td>Ajouter un nom au choix</td>
                    </tr>
                    <tr>
                        <th class="font-weight-medium text-left">Attribut du service</th>
                        <td>Ajouter un attribut au choix (nécessaire pour définir les politiques d’accès)</td>
                    </tr>
                    <tr>
                        <th class="font-weight-medium text-left">Cryptage</th>
                        <td>
                            Case à cocher
                        </td>
                    </tr>
                    <tr>
                        <th class="font-weight-medium text-left">Config hôte</th>
                        <td>Configuration hôte créée précédemment</td>
                    </tr>
                    <tr>
                        <th class="font-weight-medium text-left">Config intercept</th>
                        <td>Configuration intercept créée précédemment</td>
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