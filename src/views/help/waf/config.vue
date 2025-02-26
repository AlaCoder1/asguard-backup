<template>
    <div>
        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span>Introduction</span>
        </h3>

        <p id="web-application-firewall" class=" pb-2">
            Le <strong>Web Application Firewall (WAF)</strong> <span id="modsecurity">ModSecurity</span> est une
            solution
            puissante
            permettant de protéger les applications web contre diverses attaques.
            Basée sur les captures fournies, cette documentation explique les
            <span id="configurations">configurations</span>, les <span id="parametres">paramètres</span> et les <span
                id="fonctionnalites">fonctionnalités</span> disponibles dans
            l'interface <span id="modsecurity-interface">ModSecurity</span>.
        </p>

        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="configuration-generale">Configuration Générale</span>
        </h3>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 17px">
            <span id="parametres-principaux">Paramètres principaux </span>
        </h3>

        <p class=" pb-3">
            Dans l’onglet paramètres dans la section configuration vous trouverez
            les paramètres principaux :
        </p>

        <div class="mb-7 d-flex justify-center align-center">
                <img class="rounded-md" src="@/assets/images/services/images_waf/imagef.png" style="width: 100%" />
        </div>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 17px">
            <span id="initialisation-moteur-regles">Initialisation du moteur de règles :</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">Le moteur de règles est activé.</li>
            <li class="mb-2">Paramètre : On.</li>
        </ul>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 17px">
            <span id="acces-corps-requetes">Accès aux corps des requêtes :</span>
        </h3>

        <p class=" pb-2">Options activées :</p>
        <ul class="list-disc ml-7">
            <li class="mb-2">
                <span id="analyseur-corps-xml">Analyseur de corps de requête XML.</span>
            </li>
            <li class="mb-2">
                <span id="analyseur-corps-json">Analyseur de corps de requête JSON.</span>
            </li>
        </ul>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 17px">
            <span id="taille-maximale-corps">Taille maximale des corps :</span>
        </h3>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 15px">
            <span id="corps-requete">Corps de la requête :</span>
        </h3>
        <ul class="list-disc ml-7">
            <li class="mb-2">Taille maximale : 13107202 bytes.</li>
        </ul>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 15px">
            <span id="excluant-fichiers">Excluant les fichiers :</span>
        </h3>
        <ul class="list-disc ml-7">
            <li class="mb-2">Taille maximale : 131072 bytes.</li>
        </ul>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 15px">
            <span id="initialisation-moteur-regles">Initialisation du moteur de règles :</span>
        </h3>
        <ul class="list-disc ml-7">
            <li class="mb-2">Le moteur de règles est activé.</li>
        </ul>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 15px">
            <span id="profondeur-maximale-json">Profondeur maximale pour JSON :</span>
        </h3>
        <ul class="list-disc ml-7">
            <li class="mb-2">Analyse maximale : 511.</li>
        </ul>
        <h3 class="font-semibold text-sm pb-2" style="font-size: 15px">
            <span id="limite-arguments">Limite des arguments :</span>
        </h3>
        <ul class="list-disc ml-7">
            <li class="mb-2">Nombre maximum d'arguments par requête : 909.</li>
        </ul>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 15px">
            <span id="limites-pcre">Limites PCRE (Expressions régulières) :</span>
        </h3>
        <ul class="list-disc ml-7">
            <li id="limite-correspondance" class="mb-2">Limite de correspondance : 1000.</li>
            <li id="limite-recursion" class="mb-2">Limite de récursion : 1000.</li>
        </ul>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 15px">
            <span>Accès aux corps des réponses</span>
        </h3>
        <h3 class="font-semibold text-sm pb-2" style="font-size: 15px">
            <span>Activation :</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">Permet d'examiner les réponses HTTP.</li>
        </ul>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 15px">
            <span id="type-mime-analyse">Type MIME analysé</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">text/html.</li>
        </ul>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 15px">
            <span id="taille-maximale-corps">Taille maximale des corps :</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">524288 bytes.</li>
        </ul>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 15px">
            <span id="action-limitation">Action de limitation</span>
        </h3>
        <h3 class="font-semibold text-sm pb-2" style="font-size: 15px">
            <span>Pour les corps de requêtes et réponses :</span>
        </h3>

        <p class=" pb-2">
            Action définie: <span id="ProcessPartial">ProcessPartial</span> (traitement partiel si limite atteinte).
        </p>
    </div>
</template>