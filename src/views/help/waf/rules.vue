<template>
    <div>
        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="regles">Règles : </span>
        </h3>

        <p class="pb-2">
            Dans l’onglet règles vous trouverez la liste des règles prédéfinies :
        </p>

        <div class="mb-5 d-flex justify-center align-center">
                <img class="rounded-md" src="@/assets/images/services/images_waf/image3.png" style="width: 100%" />
        </div>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 15px">
            <span>Vue d'ensemble des règles</span>
        </h3>

        <p class="pb-2">
            Liste des règles prédéfinies : (ID, règle, description et les
            applications qui utilisent chaque règle).
        </p>

        <p class="py-2">Exemple :</p>
        <ul class="list-disc ml-7">
            <li class="mb-2">951: RESPONSE-951-DATA-LEAKAGES-SQL</li>
            <li class="mb-2">952: RESPONSE-952-DATA-LEAKAGES-JAVA</li>
            <li class="mb-2">953: RESPONSE-955-DATA-LEAKAGES-PHP</li>
        </ul>

        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="creation-nouvelle-regle">Création d'une nouvelle règle</span>
        </h3>

        <p class="py-2">
            Cliquer sur le bouton “ajouter” pour ajouter une regle :
        </p>

        <div class="mb-5 d-flex justify-center align-center">
                <img class="rounded-md" src="@/assets/images/services/images_waf/image4.png" style="width: 100%" />
        </div>

        <div class="mb-7 d-flex justify-center align-center">
                <img class="rounded-md" src="@/assets/images/services/images_waf/image5.png" style="width: 100%" />
        </div>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 15px">
            <span>Informations générales :</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">Nom de la règle.</li>
            <li class="mb-2">Description de la règle.</li>
            <li class="mb-2">
                Variable cible (par exemple : requête, réponse, etc.).
            </li>
            <li class="mb-2">Opérateur (ex : égal, contient, etc.).</li>
        </ul>

        <h3 class="font-semibold text-sm py-2" style="font-size: 15px">
            <span>Conditions :</span>
        </h3>
        <ul class="list-disc ml-7">
            <li class="mb-2">Ajouter des types de conditions :</li>
            <p class="text-gray-500 dark:text-gray-400">
                Type : valeur (avec action).
            </p>
        </ul>

        <h3 class="font-semibold text-sm py-2" style="font-size: 15px">
            <span id="fonctions-transformation">Fonctions de transformation :</span>
        </h3>

        <p id="appliquer-transformations" class="pb-2">
            Appliquer des transformations avant analyse (par exemple : conversion,
            normalisation).
        </p>
        <h3 class="font-semibold text-sm py-2" style="font-size: 15px">
            <span>Actions :</span>
        </h3>
        <p class="pb-2">
            Exécuter des actions en cas de correspondance, par exemple :
        </p>
        <ul class="list-disc ml-7">
            <li class="mb-2">Bloquer.</li>
            <li class="text-gray-500 dark:text-gray-400">Journaliser.</li>
        </ul>
    </div>
</template>