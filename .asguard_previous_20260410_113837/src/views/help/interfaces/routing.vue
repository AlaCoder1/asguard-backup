<template>
    <div>
        <h3 class="font-weight-bold  text-1xl pt-2" style="font-size: 20px" id="routing">
            <span id="routage"> Routage </span>
        </h3>

        <p class=" py-2" id="routing-description">
            Le routage statique permet de configurer manuellement des chemins
            spécifiques pour le trafic réseau.
        </p>

        <div class="mb-6 d-flex justify-center align-center" id="routing-image">
            <img style="width: 100%;" class="rounded-md" src="@/assets/images/interfaces/interfaces11.png" />

        </div>

        <h3 class="font-weight-bold  text-1xl pt-2 pb-4" style="font-size: 20px" id="routing-actions">
            <span> Actions disponibles : </span>
        </h3>

        <ul class="list-disc ml-7" id="routing-actions-list">
            <li class="mb-2" id="add-route">
                <strong>Ajouter : </strong> Créer une nouvelle route.
            </li>
            <li class="mb-2" id="modify-or-delete-route">
                <strong>Modifier ou Supprimer : </strong> une route existante.
            </li>
        </ul>

        <h3 class="font-weight-bold  text-1xl pt-2 pb-4" style="font-size: 20px" id="new-route-parameters">
            <span> Paramètres pour une nouvelle route : </span>
        </h3>
        <div class="mb-6 d-flex justify-center align-center" id="new-route-image">
            <img style="width: 100%;" class="rounded-md" src="@/assets/images/interfaces/interfaces12.png" />

        </div>

        <p class=" py-2" id="new-route-description">
            Lorsque vous cliquez sur Ajouter, une fenêtre s'ouvre avec les champs
            suivants :
        </p>

        <h3 class="font-semibold text-sm pt-2 pb-4" style="font-size: 18px" id="network-field">
            <span> Réseau : </span>
        </h3>

        <ul class="list-disc ml-7" id="network-definition">
            <li class="mb-2" id="network-definition-1">
                <strong>Définition : </strong> Spécifie le réseau cible au format CIDR
                (exemple : 192.168.1.0/24).
            </li>
            <li class="mb-2" id="network-purpose">
                <strong>But : </strong> Identifier le segment réseau auquel la route
                s'applique.
            </li>
        </ul>

        <!--  -->
        <h3 class="font-semibold text-sm pt-2 pb-4" style="font-size: 18px" id="gateway-header">
            <span id="gateway-span">Gateway (Passerelle) :</span>
        </h3>

        <ul class="list-disc ml-7" id="gateway-ul">
            <li class="mb-2" id="gateway-li-definition">
                <strong>Définition : </strong> Définit la passerelle utilisée pour
                acheminer le trafic.
            </li>
            <li class="mb-2" id="gateway-li-purpose">
                <strong>But : </strong> Indique la passerelle par laquelle les paquets
                seront envoyés pour atteindre le réseau cible.
            </li>
            <li class="mb-2" id="gateway-li-options">
                <strong>Options disponibles :</strong> Sélectionner une passerelle
                prédéfinie dans la liste déroulante. Choisir l'option "Other" pour
                définir une passerelle personnalisée.
            </li>
        </ul>

        <!-- Description Section -->
        <h3 class="font-semibold text-sm pt-2 pb-4" style="font-size: 18px" id="description-header">
            <span id="description-span">Description :</span>
        </h3>

        <ul class="list-disc ml-7" id="description-ul">
            <li class="mb-2" id="description-li-definition">
                <strong>Définition : </strong> Champ facultatif pour fournir des
                informations supplémentaires sur la route.
            </li>
            <li class="mb-2" id="description-li-purpose">
                <strong>But : </strong> Aider à la documentation ou à l'identification
                des routes.
            </li>
        </ul>

        <!-- Image for the Description (Gateway) -->
        <div class="mb-6 d-flex justify-center align-center" id="gateway-image-container">
            <img style="width: 100%;" class="rounded-md" src="@/assets/images/interfaces/interfaces13.png" id="gateway-image"
                alt="Image illustrating gateway configuration" />

        </div>

        <!-- Additional Info When "Other" is Selected -->
        <p class=" py-2" id="other-option-message">
            Lorsque l'option "Other" est sélectionnée dans le champ Gateway, des
            champs supplémentaires apparaissent :
        </p>

        <!-- Gateway Address Section -->
        <h3 class="font-semibold text-sm pt-2 pb-4" style="font-size: 18px" id="gateway-address-header">
            <span id="gateway-address-span">Adresse de passerelle :</span>
        </h3>

        <ul class="list-disc ml-7" id="gateway-address-ul">
            <li class="mb-2" id="gateway-address-li-definition">
                <strong>Définition : </strong> Adresse IP de la passerelle
                personnalisée.
            </li>
            <li class="mb-2" id="gateway-address-li-purpose">
                <strong>But : </strong> Permet de définir une passerelle spécifique
                qui n'est pas listée dans les options par défaut.
            </li>
        </ul>

        <!-- Parent Interface Section -->
        <h3 class="font-semibold text-sm pt-2 pb-4" style="font-size: 18px" id="parent-interface-header">
            <span id="parent-interface-span">Interface parentale :</span>
        </h3>

        <ul class="list-disc ml-7" id="parent-interface-ul">
            <li class="mb-2" id="parent-interface-li-definition">
                <strong>Définition : </strong>Interface réseau à utiliser pour la
                route (par exemple : eth0, wlan0).
            </li>
            <li class="mb-2" id="parent-interface-li-purpose">
                <strong>But : </strong> Détermine par quelle interface les paquets
                seront transmis.
            </li>
        </ul>

        <!-- Metric Section -->
        <h3 class="font-semibold text-sm pt-2 pb-4" style="font-size: 18px" id="metric-header">
            <span id="metric-span">Metric :</span>
        </h3>

        <ul class="list-disc ml-7" id="metric-ul">
            <li class="mb-2" id="metric-li-definition">
                <strong>Définition : </strong>Poids ou priorité de la route. Une
                valeur plus basse signifie une priorité plus élevée.
            </li>
            <li class="mb-2" id="metric-li-purpose">
                <strong>But : </strong> Permet de définir la préférence lorsqu'il
                existe plusieurs routes vers un même réseau.
            </li>
        </ul>
    </div>
</template>