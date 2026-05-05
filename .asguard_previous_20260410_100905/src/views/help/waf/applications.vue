<template>
    <div>
        <h3 class="font-weight-bold text-sm py-2" style="font-size: 20px">
            <span id="liste-applications">Liste des Applications</span>
        </h3>

        <p class=" pb-2">
            L'onglet "APPLICATION" affiche une liste des applications déjà
            protégées. Les colonnes principales sont :
        </p>

        <div class="mb-7 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/images_waf/image6.png" style="width: 100%" />
        </div>

        <p class=" pb-2">
            Pour ajouter une nouvelle application à protéger, cliquez sur "Ajouter".
            Un formulaire modal s'affiche avec les paramètres suivants :
        </p>

        <p class=" pb-2">
            <strong> Nom de l'application : </strong> Identifiant unique de
            l'application.
        </p>
        <p class=" pb-2">
            <strong>Type : </strong> Définit si l'application est identifiée par une
            adresse IP ou un domaine.
        </p>
        <p class=" pb-2">
            <strong>Protocole : </strong>Définit le protocole web utilisé.
        </p>
        <p class=" pb-2">
            <strong>Description : </strong>Informations supplémentaires sur
            l'application.
        </p>
        <p class=" pb-2">
            <strong>Actions : </strong>Permet de modifier ou de supprimer une
            application.
        </p>
        <p class=" pb-2">
            <strong>Actions Disponibles : </strong>
        </p>
        <ul class="list-disc ml-7">
            <li class="mb-2">
                Modifier les paramètre d'une application existante.
            </li>
            <li>
                Supprimer l'application du WAF.
            </li>
        </ul>
        <h3 class="font-weight-bold text-sm py-2" style="font-size: 20px">
            <span id="creation-nouvelle-application">Création d'une Nouvelle Application</span>
        </h3>

        <div class="mb-7 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/images_waf/image9.png" style="width: 100%" />
        </div>
        <h3 class="font-semibold text-sm pb-3" style="font-size: 17px">
            <span>Champs du Formulaire :</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2"><strong>Nom de l'application :</strong></li>

            <ul class="mt-2 ml-4 mb-2" style="list-style-type: circle">
                <li class="mb-2">Nom unique pour identifier l'application.</li>
            </ul>
            <li class="mb-2"><strong>Type :</strong></li>

            <p class=" pb-2">
                Sélectionnez le type de l'application parmi :
            </p>
            <ul class="mt-2 ml-4 mb-2" style="list-style-type: circle">
                <li class="mb-2">
                    <strong>ip :</strong> Application identifiée par une adresse IP.
                </li>
                <li class="mb-2">
                    <strong> domain :</strong> Application identifiée par un nom de
                    domaine.
                </li>
            </ul>

            <li class="mb-2"><strong>Protocole :</strong></li>
            <p class=" pb-2">
                Protocole utilisé par l'application (HTTP, HTTPS, etc.).
            </p>
            <li class="mb-2"><strong>Valeur :</strong></li>
            <p class=" pb-2">
                Adresse IP ou nom de domaine de l'application selon le type
                sélectionné.
            </p>
            <li class="mb-2"><strong>Port :</strong></li>
            <p class=" pb-2">
                Numéro du port sur lequel l'application est accessible (par exemple :
                80 pour HTTP ou 443 pour HTTPS).
            </p>
            <li class="mb-2"><strong>Description :</strong></li>
            <p class=" pb-2">
                Fournissez une description pour mieux comprendre l'objectif de
                l'application.
            </p>
            <li class="mb-2"><strong>Pays :</strong></li>
            <p class=" pb-2">
                (Optionnel) Sélectionnez un pays spécifique le blocage des pays par
                requête.
            </p>
        </ul>

        <p class=" py-2">
            Dans l'interface de configuration des règles du WAF, vous pouvez choisir
            quelles règles activer ou désactiver pour protéger vos applications.
            Voici une description des principales catégories et des règles visibles
            sur l'image :
        </p>

        <div class="mb-7 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/images_waf/imagea.png" style="width: 100%" />
        </div>

        <p class=" py-2">
            Dans l'interface de création, vous pouvez choisir les paramètres
            convenables pour chaque application :
        </p>

        <div class="mb-7 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/images_waf/imageb.png" style="width: 100%" />
        </div>
        <div class="mb-7 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/images_waf/imagec.png" style="width: 100%" />
        </div>
    </div>
</template>