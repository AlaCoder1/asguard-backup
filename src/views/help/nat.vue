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

        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="One-to-One">Qu'est-ce que le One-to-One NAT ?</span>
        </h3>
        <p class="pb-2">
            Le One-to-One NAT (Network Address Translation) est une technique qui
            associe une adresse IP privée à une adresse IP publique unique. Cette
            méthode est idéale pour les serveurs nécessitant une adresse IP dédiée,
            permettant ainsi un routage direct entre une IP publique et une IP
            privée.
        </p>

        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="Interface-One-to-One">Interface One-to-One NAT</span>
        </h3>
        <p class="pb-2">
            L'interface affichée permet de :
        </p>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                Créer une règle One-to-One pour une correspondance directe entre une
                adresse IP source privée et une adresse IP de traduction publique.
            </li>
            <li class="mb-2">
                Lister les règles existantes avec des détails tels que l'adresse
                source, l'adresse de traduction, et l'adresse de destination.
            </li>
            <li class="mb-2">
                Activer, désactiver ou supprimer des règles selon les besoins.
            </li>
        </ul>

        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="Créer-Nouvelle-Règle">Créer une Nouvelle Règle One-to-One NAT</span>
        </h3>

        <h3 class="font-semibold text-sm py-2" style="font-size: 17px">
            <span>1. Accéder à l'interface One-to-One NAT</span>
        </h3>

        <p class="pb-2">
            Naviguez vers <strong>NAT -> One-to-One </strong>dans l'interface de
            gestion de votre routeur/pare-feu.
        </p>
        <h3 class="font-semibold text-sm py-2" style="font-size: 17px">
            <span>2. Paramètres disponibles</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                <strong>Interface : </strong>Sélectionnez l'interface réseau concernée
                par la règle NAT (par exemple, WAN pour le trafic entrant ou sortant).
            </li>
            <li class="mb-2">
                <strong>Source Address : </strong>Indiquez l'adresse ou le sous-réseau
                source à mapper (par exemple, 192.168.1.100).
            </li>
            <ul class="mt-2 ml-4 mb-2" style="list-style-type: circle">
                <li>
                    <span class="text-md text-gray-500"><strong>Prefix : </strong>Sélectionnez le préfixe CIDR de
                        l'adresse source (par exemple, /32 pour une adresse unique ou /24
                        pour un sous-réseau entier).
                    </span>
                </li>
            </ul>

            <li class="mb-2">
                <strong>Translation Address : </strong>Spécifiez l'adresse IP publique
                à utiliser pour la translation.
            </li>

            <ul class="mt-2 ml-4 mb-2" style="list-style-type: circle">
                <li>
                    <span class="text-md text-gray-500"><strong>Prefix : </strong>Sélectionnez le préfixe CIDR
                        correspondant à l'adresse de traduction.
                    </span>
                </li>
            </ul>

            <li class="mb-2">
                <strong>Destination Address (optionnel) : </strong>Définissez une
                adresse de destination spécifique si la règle NAT ne doit s'appliquer
                qu'à un hôte ou une plage d'adresses particuliers.
            </li>
            <ul class="mt-2 ml-4 mb-2" style="list-style-type: circle">
                <li>
                    <span class="text-md text-gray-500"><strong>Prefix : </strong>Sélectionnez le préfixe CIDR de
                        l'adresse de destination.
                    </span>
                </li>
            </ul>

            <li class="mb-2">
                <strong>Description : </strong>Fournissez une description claire et
                concise de la règle pour une identification facile (par exemple,
                "Mapping serveur web 192.168.1.100 vers 203.0.113.10").
            </li>
        </ul>

        <h3 class="font-semibold text-sm py-2" style="font-size: 17px">
            <span>3. Création de la règle</span>
        </h3>

        <p class="pb-2">
            Après avoir complété les champs obligatoires, cliquez sur
            <strong>CREATE</strong> pour ajouter la règle.
        </p>

        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="exemple-regle-one-to-one">Exemple d'une Règle One-to-One NAT</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2"><strong>Interface : </strong>WAN</li>
            <li class="mb-2"><strong>Source Address : </strong>192.168.1.100</li>
            <li class="mb-2"><strong>Prefix : </strong>/32</li>
            <li class="mb-2">
                <strong>Translation Address : </strong>203.0.113.10
            </li>
            <li class="mb-2">
                <strong>Description : </strong>"Mapping serveur web interne vers IP
                publique"
            </li>
        </ul>

        <div class="mb-7 d-flex justify-center align-center py-2">
            <img class="rounded-md" src="@/assets/images/firewall/nat2.png" style="width: 800px" />

        </div>

        <p class="pb-2">
            Cette règle associera l'adresse privée 192.168.1.100 à l'adresse
            publique 203.0.113.10. Tout trafic provenant ou destiné à l'adresse
            publique sera automatiquement redirigé vers l'adresse privée
            correspondante.
        </p>

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