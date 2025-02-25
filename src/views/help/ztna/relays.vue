<template>
    <div>
        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="Création-relais">Création du relais </span>
        </h3>

        <p class=" pb-2">
            Les relais sont des éléments qui garantissent la connexion à distance à
            travers l'internet. Cliquez sur ajouter un relais et remplissez les
            champs.
        </p>
        <div class="d-flex justify-center align-center my-2">
            <img class="rounded-md" src="@/assets/images/services/ztna/relay.png" style="width: 100%" />
        </div>
        <p class=" py-2">
            Description des paramètres.
        </p>

        <div class="relative overflow-x-auto py-2">
            <v-table density="comfortable">
                <tbody>
                    <tr>
                        <th class="font-weight-medium text-left">Nom du relais</th>
                        <td>Ajouter un nom au choix</td>
                    </tr>
                    <tr>
                        <th class="font-weight-medium text-left">Attribut du relais</th>
                        <td>Ajouter un attribut au choix (nécessaire pour définir les politiques d’accès)</td>
                    </tr>
                    <tr>
                        <th class="font-weight-medium text-left">Traversée</th>
                        <td>
                            Case à cocher
                        </td>
                    </tr>
                    <tr>
                        <th class="font-weight-medium text-left">Description</th>
                        <td>Champs optionnel</td>
                    </tr>
                </tbody>
            </v-table>
        </div>

        <p class=" py-3">
            Après la création, cliquez sur le bouton "Play".
        </p>

        <div class="d-flex justify-center align-center py-2">
            <img class="rounded-md" src="@/assets/images/services/ztna/relayplay.png" style="width: 100%" />
        </div>
    </div>
</template>