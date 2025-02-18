<template>
    <div class="container">
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


        <!--  -->
    </div>
</template>