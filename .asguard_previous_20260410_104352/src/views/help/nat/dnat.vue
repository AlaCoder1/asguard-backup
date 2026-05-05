<template>
    <div class="container">
        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="DNAT">Qu'est-ce que le DNAT ?</span>
        </h3>

        <p class="pb-5">
            Le DNAT (Destination Network Address Translation) est une méthode de NAT
            utilisée pour rediriger le trafic entrant destiné à une adresse IP
            publique (ou une plage d’adresses IP) vers une adresse IP privée ou
            interne spécifique sur un réseau.
        </p>
        <p class="pb-2">
            Cette technique est principalement utilisée pour :
        </p>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                Permettre l'accès à des serveurs internes depuis l'extérieur (par
                exemple, un serveur web ou FTP).
            </li>
            <li class="mb-2">
                Effectuer des redirections de ports pour des applications spécifiques.
            </li>
        </ul>
        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="Interface-DNAT">Interface DNAT</span>
        </h3>

        <p class="pb-2">
            L'interface affichée permet de :
        </p>

        <ol class="list-decimal ml-8">
            <li class="mb-2">
                Créer des règles DNAT pour rediriger le trafic depuis une IP/port
                externe vers une IP/port interne.
            </li>
            <li class="mb-2">
                Configurer le protocole, plage de ports et IP source/destination pour
                un contrôle précis.
            </li>
            <li class="mb-2">Activer ou désactiver les règles.</li>
        </ol>

        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="Nouvelle-Règle-DNAT">Créer une Nouvelle Règle DNAT</span>
        </h3>

        <h3 class="font-semibold text-sm py-2" style="font-size: 17px">
            <span>1. Accéder à l'interface DNAT</span>
        </h3>

        <p class="pb-2">
            Naviguez vers <strong>NAT -> DNAT</strong> dans l'interface de gestion.
        </p>

        <h3 class="font-semibold text-sm py-2" style="font-size: 17px">
            <span>2. Paramètres disponibles</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                <strong>Interface : </strong>Sélectionnez l'interface réseau où le
                trafic entrant sera capturé (par exemple, WAN pour l'accès externe).
            </li>
            <li class="mb-2">
                <strong>Select Protocol : </strong>Choisissez le protocole à utiliser
                (TCP, UDP, ou les deux).
            </li>
            <li class="mb-2">
                <strong>Source Address (optionnel) : </strong>Indiquez l'adresse IP
                source si vous souhaitez restreindre la règle à des adresses
                spécifiques.
            </li>
            <li class="mb-2">
                <strong>Source Port Range : </strong>Spécifiez la plage de ports
                source si vous souhaitez limiter la règle à certains ports.
            </li>
            <li class="mb-2">
                <strong>External Address : </strong>Indiquez l'adresse IP publique ou
                externe à rediriger (par exemple, 203.0.113.10).
            </li>
            <li class="mb-2">
                <strong>Internal Address : </strong>Spécifiez l'adresse IP privée ou
                interne qui recevra le trafic (par exemple, 192.168.1.100).
            </li>
            <li class="mb-2">
                <strong>Port Forwarding : </strong>Activez cette option si vous
                redirigez des ports spécifiques.
            </li>
            <ul class="mt-2 ml-4 mb-2" style="list-style-type: circle">
                <li>
                    <span class="text-md text-gray-700">Destination Port Range : </span>
                    Indiquez les ports externes (publics) et internes (privés) pour la
                    redirection.
                </li>
            </ul>
            <li class="mb-2">
                <strong>Description : </strong> Fournissez une description claire et
                concise de la règle (par exemple, "Redirection HTTP vers serveur web
                interne").
            </li>
        </ul>

        <h3 class="font-semibold text-sm py-2" style="font-size: 17px">
            <span>3. Création de la règle</span>
        </h3>

        <p class="pb-2">
            Une fois les champs complétés, cliquez sur <strong>CREATE</strong> pour
            sauvegarder la règle.
        </p>

        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="exemple-regle-dnat">Exemple de Règle DNAT</span>
        </h3>

        <p class="pb-2">
            Supposons que vous souhaitiez rediriger tout le trafic HTTP (port 80) de
            l'IP publique 203.0.113.10 vers un serveur interne 192.168.1.100 :
        </p>

        <ul class="list-disc ml-7">
            <li class="mb-2"><strong>Interface : </strong>WAN</li>
            <li class="mb-2"><strong>Select Protocol : </strong>TCP</li>
            <li class="mb-2"><strong>External Address : </strong>203.0.113.10</li>
            <li class="mb-2"><strong>Internal Address : </strong>192.168.1.100</li>
            <li class="mb-2"><strong>Port Forwarding : </strong>Activé</li>
            <li class="mb-2">
                <strong>Destination Port Range : </strong>

                <ul class="mt-2 ml-4 mb-2" style="list-style-type: circle">
                    <li>
                        <span class="text-md text-gray-700">From : </span>
                        80
                    </li>
                    <li>
                        <span class="text-md text-gray-700">To : </span>
                        80
                    </li>
                </ul>
            </li>
            <li class="mb-2">
                <strong>Description : </strong> "Redirection HTTP vers serveur
                interne"
            </li>
        </ul>

        <div class="mb-7 d-flex justify-center align-center py-2">
            <img class="rounded-md" src="@/assets/images/firewall/nat3.png" style="width: 800px" />

        </div>

        <p class="pb-2">
            Cette règle assurera que tout le trafic entrant sur le port 80 de l'IP
            publique sera transmis au serveur interne sur le même port.
        </p>

        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="gestion-des-règles-DNAT">Gestion des Règles DNAT</span>
        </h3>

        <p class="pb-2">
            Les règles existantes sont affichées dans une table avec les colonnes
            suivantes :
        </p>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                <strong>Interface : </strong>L'interface réseau concernée.
            </li>
            <li class="mb-2"><strong>Protocol : </strong>Le protocole utilisé.</li>
            <li class="mb-2">
                <strong>Source Address : </strong>L'adresse ou le sous-réseau source
                autorisé.
            </li>
            <li class="mb-2">
                <strong>External Port : </strong>Le port externe redirigé.
            </li>
            <li class="mb-2">
                <strong>Internal Port : </strong>Le port interne cible.
            </li>
            <li class="mb-2">
                <strong>Description : </strong>La description fournie pour la règle.
            </li>
            <li class="mb-2">
                <strong>Status : </strong>Indique si la règle est activée ou
                désactivée.
            </li>
            <li class="mb-2">
                <strong>Actions : </strong>Permet de modifier ou supprimer une règle.
            </li>
        </ul>

        <!--  -->
    </div>
</template>