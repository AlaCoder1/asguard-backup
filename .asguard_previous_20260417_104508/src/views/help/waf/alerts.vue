<template>
    <div>
        <h3 class="font-weight-bold text-sm pb-2" style="font-size: 20px">
            <span id="dashboard-surveillance-attaques">Dashboard de Surveillance des Attaques</span>
        </h3>

        <p class="py-2">
            Ce dashboard présente une vue d'ensemble des <span id="activites-malveillantes-detectees">activités
                malveillantes
                détectées</span> et bloquées par le pare-feu applicatif Web (WAF). Il est
            divisé en plusieurs sections pour visualiser les données de manière
            claire et exploitable.
        </p>

        <div class="mb-7 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/images_waf/imaged.png" style="width: 100%" />
        </div>

        <h3 class="font-semibold text-sm py-2" style="font-size: 15px">
            <span id="carte-des-localisations">Carte des Localisations </span>
        </h3>

        <p class="py-2">
            La carte indique les <span id="emplacements-geographiques">emplacements géographiques</span> des IP sources
            des
            <span id="requêtes-malveillantes"> requêtes malveillantes</span>.
        </p>

        <p class="py-2">
            Les points rouges représentent les attaques détectées par le WAF. Leur
            taille ou leur concentration peut refléter la fréquence des attaques
            depuis une région donnée.
        </p>

        <p class="py-2">
            Cette visualisation aide à identifier les zones géographiques les plus
            actives en matière de menaces.
        </p>

        <h3 class="font-semibold text-sm py-2" style="font-size: 15px">
            <span>Violations </span>
        </h3>

        <p class="py-2">
            <strong id="tableau-violations"> Tableau des violations : </strong>Liste les types d’attaques
            détectées, avec les colonnes suivantes :
        </p>
        <p class="py-2">
            <strong> Violation : </strong> Code ou catégorie de la règle WAF
            appliquée pour détecter l'attaque.
        </p>

        <h3 class="font-semibold text-sm py-2" style="font-size: 17px">
            <span id="exemples-violations-frequentes">Exemples de violations fréquentes : </span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                <strong id="violation-920510">920510 :</strong> Vérification des protocoles HTTP (souvent pour détecter
                les
                requêtes non conformes).
            </li>
            <li class="mb-2">
                <strong id="violation-941110">941110 :</strong> Détection des attaques XSS (Cross-Site Scripting).
            </li>
            <li class="mb-2">
                <strong id="violation-930130">930130 :</strong> Attaques par inclusion de fichiers (LFI, RFI).
            </li>
        </ul>

        <h3 class="font-semibold text-sm py-2" style="font-size: 15px">
            <span>Top Pays </span>
        </h3>

        <p class="pb-2">
            Classement des pays d'origine des attaques, basé sur les adresses IP
            sources.
        </p>

        <ul class="list-disc ml-7">
            <li class="mb-2"><strong>Country :</strong>Pays d'origine.</li>
            <li class="mb-2">
                <strong>Attacks : </strong>Nombre total d'attaques détectées en
                provenance de chaque pays.
            </li>
        </ul>

        <p class="py-2">
            Cette information permet d'identifier les régions ou pays nécessitant
            une attention particulière.
        </p>

        <h3 class="font-semibold text-sm py-2" style="font-size: 15px">
            <span> Requêtes Bloquées </span>
        </h3>

        <p class="pb-2">
            Ce tableau affiche les détails des <span id="requetes-intercepte-waf">requêtes interceptées par le
                WAF</span>,
            avec les colonnes suivantes :
        </p>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                <strong>Country : </strong>Pays de provenance de la requête
                malveillante.
            </li>
            <li class="mb-2">
                <strong>Timestamp : </strong>Horodatage de l'événement (UTC).
            </li>
            <li class="mb-2">
                <strong>Violation : </strong>Code de la règle appliquée pour bloquer
                l'attaque.
            </li>
            <li class="mb-2">
                <strong>Source IP : </strong>Source de la requête bloquée.
            </li>
            <li class="mb-2">
                <strong>Method : </strong>Méthode HTTP utilisée (GET, POST, etc.).
            </li>
            <li class="mb-2">
                <strong>Message : </strong>Message décrivant le type d'attaque ou de
                violation.
            </li>
            <li class="mb-2">
                <strong>URL : </strong>Message décrivant le type d'attaque ou de
                violation.
            </li>
        </ul>
    </div>
</template>