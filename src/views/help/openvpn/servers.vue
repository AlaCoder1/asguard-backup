<template>
    <div>
        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="add-server"> 1. Ajouter un serveur SSL </span>
        </h3>

        <p class="pb-2 mt-1">
            Le Service <span id="Open-VPN">OpenVPN</span> permet aux utilisateurs
            distants d'accéder l'infrastructure de l'entreprise d'une façon
            sécurisé.
        </p>

        <div class="mb-3 d-flex justify-center align-center py-2">
                <img class="rounded-md" src="@/assets/images/openVpn/imageee.png" style="width: 100%" />
        </div>

        <p class="pb-2 mt-1">
            Accédez à <strong>Services -> OpenVPN -></strong> et cliquez sur
            <strong>Ajouter Serveur</strong> dans le coin supérieur droit du
            formulaire.
        </p>

        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="formulaire-add-server">
                Formulaire de création de serveur VPN
            </span>
        </h3>

        <div class="mb-3  d-flex justify-center align-center py-2">
                <img class="rounded-md" src="@/assets/images/openVpn/imagea.png" style="width: 100%" />
        </div>

        <div class="mb-3  d-flex justify-center align-center py-2">
                <img class="rounded-md" src="@/assets/images/openVpn/imageb.png" style="width: 100%" />
        </div>
        <div class="mb-3  d-flex justify-center align-center py-2">
                <img class="rounded-md" src="@/assets/images/openVpn/imagec.png" style="width: 100%" />
        </div>
        <div class="mb-3  d-flex justify-center align-center py-2">
                <img class="rounded-md" src="@/assets/images/openVpn/imaged.png" style="width: 100%" />
        </div>

        <p class="pb-2 mt-1">
            <strong>Description du serveur : </strong>Le champ "Description" permet
            de donner un nom ou une description au serveur VPN.
        </p>
        <p class="pb-2 mt-1">
            <strong>Mode serveur : </strong>Ce champ permet de sélectionner le mode
            de fonctionnement du serveur VPN. Le mode "Remote access" permet
            d'autoriser l'accès à distance.
        </p>
        <p class="pb-2 mt-1">
            <strong>Protocole : </strong>Ce champ permet de sélectionner le
            protocole de communication utilisé par le serveur VPN. "UDP" est
            couramment utilisé.
        </p>
        <p class="pb-2 mt-1">
            <strong>Interface en mode : </strong>Permet de choisir le type
            d'interface virtuelle. Le mode "TUN" est utilisé pour les tunnels de
            réseau de niveau 3.
        </p>
        <p class="pb-2 mt-1">
            <strong>Interface : </strong> Choisissez l'interface réseau qui sera
            utilisée pour le serveur VPN, typiquement "WAN".
        </p>
        <p class="pb-2 mt-1">
            <strong>Port local : </strong> Définissez le port local sur lequel le
            serveur VPN va écouter les connexions entrantes. Le port par défaut est
            souvent "1194".
        </p>
        <p class="pb-2 mt-1">
            <strong id="Authentification-TLS">Authentification TLS : </strong> Ce
            champ permet d'activer l'authentification TLS, une méthode de
            sécurisation des connexions entre le client et le serveur.
        </p>
        <p class="pb-2 mt-1">
            <strong>Peer Certificate Authority : </strong> Sélectionnez le
            certificat de l'autorité de certification (CA) utilisée pour valider les
            certificats clients.
        </p>
        <p class="pb-2 mt-1">
            <strong>Certificat serveur : </strong> Ce champ permet de choisir le
            certificat SSL du serveur pour sécuriser les connexions.
        </p>
        <p class="pb-2 mt-1">
            <strong>Longueur des paramètres DH : </strong> Ce champ définit la
            longueur des paramètres Diffie-Hellman (DH) utilisés pour l'échange de
            clés. Une longueur de "4096 bits" est recommandée pour une meilleure
            sécurité.
        </p>
        <p class="pb-2 mt-1">
            <strong>Algorithme de chiffrement : </strong> Choisissez l'algorithme de
            chiffrement utilisé pour sécuriser les données transmises sur le VPN.
            "AES-256-CBC" est une option sécurisée avec une clé de 256 bits.
        </p>
        <p class="pb-2 mt-1">
            <strong>Empreinte de l'Algorithme d'Authentification : </strong> Ce
            champ définit l'algorithme d'authentification utilisé pour garantir
            l'intégrité des données échangées. "SHA256" est une option courante.
        </p>

        <p class="pb-2 mt-1">
            <strong>Réseau de tunnels IPv4 : </strong> Spécifie le sous-réseau IPv4
            utilisé pour le tunnel VPN. Cela détermine les adresses IP attribuées
            aux clients VPN.
        </p>
        <p class="pb-2 mt-1">
            <strong>Réseau de tunnels IPv6 : </strong> Si vous souhaitez utiliser
            IPv6, vous pouvez définir un sous-réseau pour les tunnels IPv6.
        </p>
        <p class="pb-2 mt-1">
            <strong>Rediriger la passerelle : </strong> Permet de rediriger tout le
            trafic réseau vers la passerelle VPN. Ce champ est généralement laissé
            non sélectionné si ce n'est pas nécessaire.
        </p>

        <p class="pb-2 mt-1">
            <strong>Réseau local IPv4 : </strong> Définissez l'adresse du réseau
            local IPv4 pour déterminer la plage d'adresses IP à utiliser sur le
            réseau local du serveur.
        </p>
        <p class="pb-2 mt-1">
            <strong>Réseau local IPv6 : </strong> Si vous utilisez IPv6, spécifiez
            l'adresse du réseau local IPv6.
        </p>
        <p class="pb-2 mt-1">
            <strong>Connexions simultanées : </strong> Ce champ permet de spécifier
            le nombre maximum de connexions simultanées autorisées pour un client
            VPN.
        </p>

        <p class="pb-2 mt-1">
            <strong>Compression : </strong> Activez cette option pour activer la
            compression des données échangées sur le tunnel VPN, ce qui peut
            améliorer les performances.
        </p>
        <p class="pb-2 mt-1">
            <strong>Type de service </strong> : Ce champ permet de configurer un
            type de service réseau spécifique, généralement laissé non sélectionné.
        </p>
        <p class="pb-2 mt-1">
            <strong>Dupliquer les connexions : </strong> Si activé, permet de
            permettre des connexions dupliquées pour un même client.
        </p>
        <p class="pb-2 mt-1">
            <strong>Désactiver IPv6 : </strong> Cochez cette option si vous
            souhaitez désactiver la prise en charge de l'IPv6 sur ce serveur VPN.
        </p>
        <p class="pb-2 mt-1">
            <strong>IP dynamique : </strong> Ce champ permet d'activer ou désactiver
            l'utilisation d'adresses IP dynamiques pour les clients VPN.
        </p>
        <p class="pb-2 mt-1">
            <strong>Ensemble d'adresse : </strong> Cochez cette option si vous
            souhaitez configurer un ensemble d'adresses IP pour les clients VPN.
        </p>
        <p class="pb-2 mt-1">
            <strong>Topologie : </strong> Ce champ permet de définir la topologie
            réseau du VPN, généralement laissé non sélectionné.
        </p>
        <p class="pb-2 mt-1">
            <strong>Domaine DNS par défaut : </strong> Définissez le domaine DNS par
            défaut pour les clients VPN si nécessaire.
        </p>
        <p class="pb-2 mt-1">
            <strong>Serveurs DNS : </strong> Spécifiez un ou plusieurs serveurs DNS
            à utiliser pour les clients VPN.
        </p>
        <p class="pb-2 mt-1">
            <strong>Forcer la mise à jour du cache DNS : </strong> Activez cette
            option pour forcer la mise à jour du cache DNS sur les clients VPN.
        </p>
        <p class="pb-2 mt-1">
            <strong id="Serveurs-NTP">Serveurs NTP : </strong> Configurez les
            serveurs NTP pour la synchronisation horaire sur les clients VPN.
        </p>
        <p class="pb-2 mt-1">
            <strong>Options NetBIOS : </strong> Activez cette option pour permettre
            l'utilisation de NetBIOS sur le réseau VPN.
        </p>
        <p class="pb-2 mt-1">
            <strong>Port de management client : </strong> Si nécessaire, configurez
            un port spécifique pour le management du
            <span id="client-VPN">client VPN</span>.
        </p>

        <p class="pb-2 mt-1">
            Cliquez sur <strong>Sauvegarder</strong> pour ajouter le serveur VPN
            avec ces paramètres.
        </p>
        <!--  -->

        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span>
                Si <span id="tap">"TAP"</span> est sélectionné dans le champ Interface
            </span>
        </h3>

        <div class="mb-3  d-flex justify-center align-center py-2">
                <img class="rounded-md" src="@/assets/images/openVpn/imagev.png" style="width: 100%" />
        </div>

        <p class="pb-2 mt-1">
            Lorsque vous choisissez <strong>"TAP"</strong>, certains champs
            supplémentaires s'affichent :
        </p>

        <p class="pb-2 mt-1">
            <strong>Mode serveur : </strong> Choisissez "Remote access".
        </p>
        <p class="pb-2 mt-1">
            <strong>Protocole : </strong> Sélectionnez "UDP".
        </p>
        <p class="pb-2 mt-1">
            <strong>Interface en mode : </strong> Choisissez "Tap".
        </p>
        <p class="pb-2 mt-1">
            <strong>Interface : </strong> Sélectionnez "WAN".
        </p>
        <p class="pb-2 mt-1">
            <strong>Port local : </strong> Le port à utiliser pour la connexion est
            "1194".
        </p>
        <p class="pb-2 mt-1">
            <strong>Authentification TLS : </strong> Activez l'authentification TLS
            pour sécuriser la communication.
        </p>
        <p class="pb-2 mt-1">
            <strong>Peer Certificate Authority : </strong> Sélectionnez le
            certificat d’autorité pour valider les certificats clients.
        </p>
        <p class="pb-2 mt-1">
            <strong>Certificat serveur : </strong> Sélectionnez le certificat
            serveur SSLVPN (CA: SSL VPN CA).
        </p>
        <p class="pb-2 mt-1">
            <strong>Longueur des paramètres DH : </strong> Choisissez "4096 bits"
            pour une sécurité renforcée.
        </p>
        <p class="pb-2 mt-1">
            <strong>Algorithme de chiffrement : </strong> Sélectionnez "AES-256-CBC"
            pour un chiffrement sécurisé avec une clé de 256 bits.
        </p>
        <p class="pb-2 mt-1">
            <strong>Empreinte de l'Algorithme d'Authentification : </strong>
            Choisissez "SHA256" pour l'authentification des données.
        </p>
        <p class="pb-2 mt-1">
            <strong>Pont : </strong>
            Cochez cette option pour permettre le pontage entre les réseaux locaux
            et VPN.
        </p>
        <p class="pb-2 mt-1">
            <strong>Pont d’interface : </strong>
            Sélectionnez l'interface à utiliser pour le pont réseau, souvent "LAN"
            si vous souhaitez intégrer le VPN avec le réseau local.
        </p>
        <p class="pb-2 mt-1">
            <strong>Démarrer le pont DHCP : </strong>
            Ce champ permet de définir la plage d'adresses IP attribuées par DHCP
            aux clients du pont VPN.
        </p>
        <p class="pb-2 mt-1">
            <strong>Fin du pont DHCP : </strong>
            Spécifie l'adresse de fin pour la plage DHCP des clients VPN.
        </p>

        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="verification-état">
                2. Vérification de l'état d'activation de serveur
            </span>
        </h3>

        <p class="pb-2 mt-1">
            L'état de la connexion peut être visualisé dans
            <strong>VPN -> Services -> OpenVPN</strong> => liste.
        </p>
    </div>
</template>