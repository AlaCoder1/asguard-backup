<template>
    <div>
        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span> 1. Introduction </span>
        </h3>

        <p class="pb-2 mt-1">
            <span id="Strongswan-IPSEC">Strongswan IPSec</span> est une solution
            puissante pour la mise en place de tunnels VPN sécurisés. Cette
            documentation explique comment utiliser les trois interfaces principales
            de configuration :
        </p>

        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="création-Tunnel-IPSec">2. Création d'un Tunnel IPSec</span>
        </h3>
        <h3 class="font-semibold text-sm pb-2" style="font-size: 17px">
            <span id="interface-creation-tunnel">2.1 Accéder à l'Interface de Création de Tunnel</span>
        </h3>

        <ul class="list-disc ml-7 mt-2">
            <li class="mb-2">
                Connectez-vous à l'interface d'administration de Site on site VPN.
            </li>
            <li class="mb-2">
                Accédez à la section
                <strong id="Tunnel-Configuration">Tunnel Configuration</strong>.
            </li>
        </ul>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 17px">
            <span id="Configuration-Phase-1">2.2 Configuration de la Phase 1</span>
        </h3>

        <ul class="list-disc ml-7 mt-2">
            <li class="mb-2">
                Dans l'onglet <strong>Phase 1</strong> de l'interface :
            </li>

            <ul class="mt-2 ml-4 mb-2" style="list-style-type: circle">
                <li>
                    Remplissez le champ <strong>Tunnel settings name</strong> avec un
                    nom significatif pour votre tunnel.
                </li>
                <li>
                    Sélectionnez la <strong> Connection method</strong> appropriée (par
                    défaut).
                </li>
                <li>
                    Choisissez la <strong>Key Exchange Version</strong> (par ex. v2).
                </li>
                <li>Indiquez le protocole internet (IPv4 ou autre).</li>
                <li>
                    Configurez l'interface locale et le
                    <strong>Remote Gateway</strong> (adresse IP distante).
                </li>
                <li>
                    Si nécessaire, activez l'option
                    <strong>Dynamic Gateway</strong> pour accepter des adresses
                    dynamiques.
                </li>
                <li>
                    Sélectionnez une méthode d'authentification (par ex. Mutual RSA) et
                    ajoutez les certificats locaux et distants, ou ajoutez la clé PSK ou
                    <strong>Mutual Public Key</strong>.
                </li>
            </ul>
        </ul>

        <div class="mb-7 d-flex justify-center align-center py-2">
            <img class="rounded-md" src="@/assets/images/ipsec/ipsec1.png" style="width: 100%" />
        </div>

        <ul class="list-disc ml-7 mt-2">
            <li class="mb-2">
                Configurez les
                <span id="algorithmes-chiffrement">algorithmes de chiffrement</span>
            </li>

            <ul class="mt-2 ml-4 mb-2" style="list-style-type: circle">
                <li><strong>Encryption Algorithm</strong> (ex. AES-256).</li>
                <li><strong>Hash Algorithm</strong> (ex. SHA-256).</li>
                <li>Définissez une durée de vie pour la clé.</li>
            </ul>

            <li class="mb-2">
                Activez les options avancées si nécessaire, telles que
                <strong id="NAT-Traversal">NAT Traversal</strong> ou
                <strong id="Dead-Peer">Dead Peer Detection</strong>.
            </li>
            <li class="mb-2">
                Cliquez sur <strong>Enregistrer</strong> pour valider la phase 1.
            </li>
        </ul>

        <div class="mb-7 d-flex justify-center align-center py-2">
            <img class="rounded-md" src="@/assets/images/ipsec/ipsec2.png" style="width: 100%" />
        </div>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 17px">
            <span id="Configuration-Phase-2">2.3 Configuration de la Phase 2</span>
        </h3>

        <ul class="list-disc ml-7 mt-2">
            <li class="mb-2">Accédez à l'onglet <strong>Phase 2</strong> :</li>

            <ul class="mt-2 ml-4 mb-2" style="list-style-type: circle">
                <li class="mb-2">
                    Remplissez les champs nécessaires, tels que le Mode (par ex. Tunnel
                    IPv4).
                </li>
                <li class="mb-2">
                    Configurez les réseaux locaux et distants (adresses et
                    sous-réseaux).
                </li>
                <li class="mb-2">Sélectionnez les protocoles et algorithmes.</li>

                <ul class="list-disc ml-7 mt-2">
                    <li class="mb-2"><strong>Protocol : </strong>ESP.</li>
                    <li class="mb-2">
                        <strong>Encryption Algorithm : </strong> AES-GCM.
                    </li>
                    <li class="mb-3"><strong>Hash Algorithm : </strong> SHA-256.</li>
                </ul>
                <li class="mb-2">
                    Définissez une <span id="durée-de-vie">durée de vie</span> pour la
                    phase 2.
                </li>

                <div class="mb-7 d-flex justify-center align-center py-2">
                    <img class="rounded-md" src="@/assets/images/ipsec/ipsec3.png" style="width: 100%" />
                </div>
            </ul>
            <li class="mb-2">
                Une fois les paramètres configurés, cliquez sur
                <strong>Créer</strong> pour finaliser le tunnel.
            </li>
        </ul>
    </div>

</template>