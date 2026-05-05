<template>
    <div>

        <h3 class="font-weight-bold text-1xl pb-2" style="font-size: 20px">
            <span id="Ajout-identités">Ajout des identités</span>
        </h3>

        <p class=" pb-2">
            Accédez à Services ‣ ZTNA‣ et cliquez sur Play Button dans le coin
            supérieur. Cliquez sur Ajouter une identité et remplissez les champs.
            Ajouter deux identités une pour le client et l’autre pour le serveur.
        </p>

        <div class="mb-5 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/ztna/identity.png" style="width:100%" />

        </div>

        <p class=" pb-2">
            Description des paramètres.
        </p>

        <div class="relative overflow-x-auto py-3">
            <v-table>
                <tbody>
                    <tr>
                        <th class="font-weight-medium">Nom identité</th>
                        <td>Ajouter un nom au choix</td>
                    </tr>
                    <tr>
                        <th class="font-weight-medium">Attribut identité</th>
                        <td>Ajouter un attribut au choix (nécessaire pour définir les politiques d’accès)</td>
                    </tr>
                    <tr>
                        <th class="font-weight-medium">Type OS</th>
                        <td>Windows / Linux (OS du client et serveur)</td>
                    </tr>
                    <tr>
                        <th class="font-weight-medium">Description</th>
                        <td>Champs optionnel</td>
                    </tr>
                </tbody>
            </v-table>
        </div>

        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="Ajout-OTT">Ajout d'un OTT</span>
        </h3>

        <p class=" pb-4">
            Après la création de l'identité, il faut créer un OTT. Cliquez sur le
            bouton rouge dans le champ inscrit de l'identité créée, puis remplissez
            la date d'expiration de cet OTT.
        </p>

        <div class="mb-5 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/ztna/ott.png" style="width:100%" />

        </div>

        <p class=" pb-4">
            Après la création, téléchargez le fichier apparaissant dans le champ
            <span id="token">"token"</span> de l'identité créée.
        </p>

        <div class="d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/ztna/token.png" style="width:100%" />

        </div>

        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="Connexion-identité">Connexion d’identité </span>
        </h3>

        <p class=" pb-4">
            D'abord, téléchargez le script situé à gauche de l'identité créée pour
            assurer la visibilité entre les clients et le pare-feu Asguard. Dans
            l'application cliente, ajoutez l'OTT créé pour se connecter au service
            ZTNA Asguard.
        </p>
        <div class="d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/ztna/os.png" style="width:100%" />

        </div>
    </div>
</template>