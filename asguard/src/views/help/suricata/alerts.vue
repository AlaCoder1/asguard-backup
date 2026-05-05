<template>
    <div>
        <p class="pb-2">
            Cette interface affiche les alertes générées par le système IDS/IPS pour
            surveiller et <span id="détecter-les-activités">détecter les activités réseau suspectes ou
                malveillantes</span>.
            Elle offre également des options de filtrage pour faciliter l'analyse
            des données.
        </p>

        <div class="mb-4 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/ips-ids/image5.png" style="width: 100%" />
        </div>

        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span>Description des Champs </span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                <strong>Horodatage LINUX :</strong>
                Affiche la date et l'heure précises de l'alerte selon le format Linux.
            </li>
            <li class="mb-2">
                <strong>SID (Signature ID) :</strong>
                Identifiant unique associé à la règle ou signature ayant déclenché
                l'alerte.
            </li>
            <li class="mb-2">
                <strong>Message :</strong>
                Décrit la nature de l'alerte.
            </li>
            <li class="mb-2">
                <strong>Protocole :</strong>
                Protocole réseau impliqué dans l'alerte, tel que TCP ou UDP
            </li>
            <li class="mb-2">
                <strong>Source :</strong>
                Adresse IP et port de la source ayant généré le trafic suspect.
            </li>
            <li class="mb-2">
                <strong>Destination :</strong>
                Adresse IP et port de la destination cible du trafic suspect.
            </li>
        </ul>

        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span>Fonctionnalités Clés </span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                <strong>Filtrage par Colonne :</strong>
                Appliquez un filtre spécifique à chaque colonne en cliquant sur son
                nom.
            </li>
            <li class="mb-2">
                <strong>Recherche Globale :</strong>
                Une barre de recherche située en haut de l'interface permet de
                rechercher des alertes en fonction de mots-clés, de SID, ou d'autres
                critères.
            </li>
            <li class="mb-2">
                <strong>Pagination :</strong>
                Les alertes sont paginées pour simplifier la navigation.
            </li>
        </ul>

        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span>Cas d'Utilisation </span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                <strong>Analyse Rapide :</strong>
                Utiliser le filtrage pour identifier rapidement des anomalies
                spécifiques.
            </li>
            <li class="mb-2">
                <strong>Priorisation :</strong>
                Trier ou filtrer les alertes par niveau de gravité pour traiter les
                événements critiques en premier.
            </li>
            <li class="mb-2">
                <strong>Investigation Détaillée :</strong>
                Explorer les alertes par adresse IP, protocole ou message pour
                détecter les tentatives d'intrusion ou les comportements suspects.
            </li>
        </ul>
    </div>
</template>