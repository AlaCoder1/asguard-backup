<template>
    <div class="container">
        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="SNAT"> Qu'est-ce que le SNAT ?</span>
        </h3>

        <p class="pb-2 mt-1">
            Le SNAT (Source Network Address Translation) est une technique utilisée
            pour modifier l'adresse source d'un paquet réseau lorsque celui-ci
            traverse un routeur ou un pare-feu. Cette méthode est souvent utilisée
            pour permettre à plusieurs appareils d'un réseau privé d'accéder à
            Internet en utilisant une seule adresse IP publique.
        </p>

        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="Interface-SNAT"> Interface SNAT</span>
        </h3>

        <p class="pb-3">
            L'interface affichée permet de :
        </p>

        <ol class="list-decimal ml-8">
            <li class="mb-2">
                Créer de nouvelles règles SNAT pour gérer la translation des adresses
                réseau.
            </li>
            <li class="mb-2">
                Lister les règles existantes avec des détails tels que l'adresse
                source, l'adresse de traduction, le protocole utilisé, et l'état des
                règles (activé/désactivé).
            </li>
            <li class="mb-2">
                Modifier ou supprimer des règles existantes via les actions associées.
            </li>
        </ol>

        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="Nouvelle-Règle-SNAT">Créer une Nouvelle Règle SNAT</span>
        </h3>

        <h3 class="font-semibold text-sm py-2" style="font-size: 17px">
            <span>1. Accéder à l'interface SNAT</span>
        </h3>
        <p class="py-2">
            Naviguez vers la section <strong>NAT -> SNAT</strong> dans l'interface
            de gestion du routeur/pare-feu.
        </p>

        <h3 class="font-semibold text-sm py-2" style="font-size: 17px">
            <span id="Paramètres-disponibles">2. Paramètres disponibles</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                <strong>Interface : </strong>Sélectionnez l'interface réseau concernée
                par la règle SNAT (ex. WAN pour le trafic sortant vers Internet).
            </li>
            <li class="mb-2">
                <strong>TCP/IP Version : </strong>Spécifiez la version du protocole IP
                (IPv4 ou IPv6).
            </li>
            <li class="mb-2">
                <strong>Protocole : </strong>Choisissez le protocole à appliquer (TCP,
                UDP, ou les deux).
            </li>
            <li class="mb-2">
                <strong>Adresse Source : </strong>Indiquez l'adresse ou le sous-réseau
                source à transformer (par exemple, 192.168.20.0/24).
            </li>
            <li class="mb-2">
                <strong>Port Source (optionnel) : </strong>Spécifiez le port source si
                nécessaire.
            </li>
            <li class="mb-2">
                <strong>Adresse Destination (optionnel) : </strong>Indiquez une
                adresse de destination spécifique pour limiter l'application de la
                règle.
            </li>
            <li class="mb-2">
                <strong>Port Destination (optionnel) : </strong>Indiquez un port de
                destination spécifique si besoin.
            </li>
            <li class="mb-2">
                <strong>Mode de Traduction : </strong>

                <ul class="mt-2 ml-4 mb-2" style="list-style-type: circle">
                    <li>
                        <span class="text-md text-gray-700">MASQ (Masquerade) : </span>
                        Utilise automatiquement l'adresse IP publique de l'interface
                        sélectionnée.
                    </li>
                    <li>
                        <span class="text-md text-gray-700">Statique : </span>
                        Permet de spécifier une adresse IP publique statique pour la
                        translation.
                    </li>
                </ul>
            </li>
            <li class="mb-2">
                <strong>Description : </strong>Fournissez une description claire de la
                règle pour une identification future.
            </li>
        </ul>

        <h3 class="font-semibold text-sm py-2" style="font-size: 17px">
            <span id="Création-règle">3. Création de la règle</span>
        </h3>

        <p class="pb-2">
            Une fois tous les champs renseignés, cliquez sur
            <strong>CREATE</strong> pour ajouter la règle SNAT.
        </p>

        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="Exemple-Règle-SNAT">Exemple d'une Règle SNAT</span>
        </h3>

        <p class="pb-2">
            Voici un exemple basé sur l'image fournie :
        </p>

        <ul class="list-disc ml-7">
            <li class="mb-2"><strong>Interface : </strong>WAN</li>
            <li class="mb-2"><strong>TCP/IP Version : </strong>IPv4</li>
            <li class="mb-2"><strong>Protocole : </strong>Tous</li>
            <li class="mb-2"><strong>Adresse Source : </strong>192.168.20.0/24</li>
            <li class="mb-2"><strong>Mode de Traduction : </strong>MASQ</li>
            <li class="mb-2">
                <strong>Description : </strong> Translation SNAT pour le réseau
                "192.168.20.0/24"
            </li>
        </ul>
        <p class="py-2">
            Cette règle permet à tout le sous-réseau
            <strong>192.168.20.0/24</strong> de traduire ses adresses IP sources
            vers l'adresse publique de l'interface WAN.
        </p>

        <div class="mb-7 d-flex justify-center align-center py-2">
            <img class="rounded-md" src="@/assets/images/firewall/nat1.png" style="width: 800px" />
        </div>

        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="Gestion-Règles-Existantes">Gestion des Règles Existantes</span>
        </h3>
        <p class="pb-2">
            Les règles déjà créées sont listées dans la table située en
            arrière-plan, avec les colonnes suivantes :
        </p>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                <strong>Interface : </strong>Interface réseau concernée.
            </li>
            <li class="mb-2">
                <strong>Protocole : </strong>Protocole appliqué par la règle.
            </li>
            <li class="mb-2">
                <strong>Adresse Source : </strong>Adresse ou sous-réseau source
                configuré.
            </li>
            <li class="mb-2">
                <strong>Adresse de Traduction : </strong>Adresse IP publique utilisée
                pour la traduction.
            </li>
            <li class="mb-2">
                <strong>Port de Traduction : </strong>Port utilisé pour la
                translation.
            </li>
            <li class="mb-2">
                <strong>Description : </strong> Description fournie pour la règle.
            </li>
            <li class="mb-2">
                <strong>État : </strong> Case à cocher pour activer/désactiver une
                règle.
            </li>
            <li class="mb-2">
                <strong>Actions : </strong> Boutons pour modifier ou supprimer une
                règle.
            </li>
        </ul>

        <!--  -->
    </div>
</template>