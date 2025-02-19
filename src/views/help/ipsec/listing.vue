<template>
    <div>
        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="Gestion-des-Tunnels">1. Gestion des Tunnels IPSec</span>
        </h3>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 17px">
            <span id="Liste-des-Tunnels">1.1 Liste des Tunnels</span>
        </h3>

        <p class="pb-2 mt-1">
            L’onglet <strong id="IPSec-Peers">IPSec Peers</strong> affiche tous les
            <span id="tunnels-configurés">tunnels configurés</span>
            avec les informations suivantes :
        </p>

        <ul class="list-disc ml-7 mt-2">
            <li class="mb-2">
                <strong>Type : </strong>Le type de tunnel (ex. IPv4 V2).
            </li>
            <li class="mb-2">
                <strong>Remote Gateway : </strong>Adresse IP de la passerelle
                distante.
            </li>
            <li class="mb-2">
                <strong>Mode : </strong>Mode du tunnel (ex. Tunnel).
            </li>
            <li class="mb-2">
                <strong>Phase 1 Proposal : </strong>Algorithmes de la phase 1 (ex.
                AES256, SHA256, DH Group 16).
            </li>
            <li class="mb-2">
                <strong>Authentication : </strong> Méthode d’authentification utilisée
                (ex. Mutual PSK).
            </li>
            <li class="mb-2">
                <strong>Local Subnet : </strong> Sous-réseau local configuré.
            </li>
            <li class="mb-2">
                <strong>Remote Subnet : </strong> Sous-réseau distant configuré.
            </li>
            <li class="mb-2">
                <strong>Phase 2 Proposal : </strong> Algorithmes de la phase 2 (ex.
                AES256, SHA256, DH Group 16).
            </li>
            <li class="mb-2">
                <strong>Enable : </strong> Statut d’activation du tunnel.
            </li>
            <li class="mb-2">
                <strong>Action : </strong> Options pour modifier (⚙️),
                activer/désactiver (Boutton UP), ou supprimer (🗑️) un tunnel.
            </li>
        </ul>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 17px">
            <span id="Modifier-un-Tunnel">1.2 Modifier un Tunnel</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                Dans la liste, cliquez sur l’icône ⚙️ pour modifier un tunnel.
            </li>
            <li class="mb-2">Apportez les changements nécessaires :</li>

            <ul class="mt-2 ml-4 mb-2" style="list-style-type: circle">
                <li class="mb-2">Algorithmes</li>
                <li class="mb-2">Sous-réseaux</li>
                <li class="mb-2">Durée de vie</li>
            </ul>
            <li class="mb-2">
                Cliquez sur <strong>Enregistrer</strong> pour appliquer les
                modifications.
            </li>
        </ul>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 17px">
            <span id="activer-desactiver">1.3 Activer ou Désactiver un Tunnel</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                Dans la colonne <strong id="Enable">Enable</strong>, cochez ou
                décochez la case correspondant au tunnel souhaité.
            </li>
            <li class="mb-2">L’état du tunnel sera mis à jour immédiatement.</li>
        </ul>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 17px">
            <span id="Supprimer-un-Tunnel">1.4 Supprimer un Tunnel</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">Cliquez sur l’icône 🗑️ à droite du tunnel.</li>
            <li class="mb-2">
                Confirmez la suppression dans la boîte de dialogue..
            </li>
        </ul>
        <div class="mb-7 mt-4  d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/ipsec/ipsec4.png" style="width: 100%" />
        </div>

    </div>
</template>