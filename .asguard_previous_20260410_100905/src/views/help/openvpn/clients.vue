<template>
    <div>
        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="add-client"> 1. Formulaire de creation d'un client </span>
        </h3>

        <div class="mb-3 d-flex justify-center align-center py-2">
            <img class="rounded-md" src="@/assets/images/openVpn/image44.png" style="width: 100%" />
        </div>

        <p class="pb-2 mt-1">
            Vous pouvez maintenant créer un
            <span id="client-VPN">client VPN</span> à l'aide du formulaire "Ajouter
            Client".
        </p>

        <div class="mb-3 d-flex justify-center align-center py-2">
            <img class="rounded-md" src="@/assets/images/openVpn/image2.png" style="width: 100%" />
        </div>
        <div class="mb-3 d-flex justify-center align-center py-2">
            <img class="rounded-md" src="@/assets/images/openVpn/image3.png" style="width: 100%" />
        </div>
        <div class="mb-3 d-flex justify-center align-center py-2">
            <img class="rounded-md" src="@/assets/images/openVpn/image4.png" style="width: 100%" />
        </div>
        <div class="mb-3 d-flex justify-center align-center py-2">
            <img class="rounded-md" src="@/assets/images/openVpn/image5.png" style="width: 100%" />
        </div>

        <p class="pb-2 mt-1">
            <strong>Nom du client : </strong>
            Identifiant unique du <span id="client-VPN">client VPN</span>, utilisé
            pour la gestion et l’organisation.
        </p>
        <p class="pb-2 mt-1">
            <strong>Description : </strong>
            Une brève description pour identifier l’usage ou l’utilisateur du
            client.
        </p>
        <p class="pb-2 mt-1">
            <strong>Mode serveur : </strong>
            Définit le mode d'accès. "Remote access" permet aux utilisateurs
            distants de se connecter au VPN.
        </p>

        <p class="pb-2 mt-1">
            <strong>Protocole : </strong>
            Protocole de communication utilisé pour établir la connexion (ex : UDP
            ou TCP).
        </p>
        <p class="pb-2 mt-1">
            <strong>Mode du dispositif : </strong>
            Définit le mode de connexion du VPN, "TUN" pour un tunnel réseau virtuel
            ou "TAP" pour un pont réseau.
        </p>
        <p class="pb-2 mt-1">
            <strong> Interface : </strong>
            Indique l’interface réseau par laquelle le VPN sera accessible (ex :
            WAN).
        </p>
        <p class="pb-2 mt-1">
            <strong id="Port-serveur"> Port de serveur : </strong>
            Numéro de port utilisé pour la connexion VPN.
        </p>
        <p class="pb-2 mt-1">
            <strong id="Clé"> Clé partagée : </strong>
            Option permettant d’utiliser une clé pré-partagée pour
            l’authentification.
        </p>
        <p class="pb-2 mt-1">
            <strong id="Certificat-autorité"> Certificat d’autorité : </strong>
            Certificat utilisé pour valider l’identité du serveur VPN.
        </p>
        <p class="pb-2 mt-1">
            <strong id="Certificat-serveur"> Certificat de serveur : </strong>
            Certificat SSL utilisé par le serveur VPN pour sécuriser la connexion.
        </p>
        <p class="pb-2 mt-1">
            <strong> Longueur du paramètre DH : </strong>
            Définit la taille des clés Diffie-Hellman utilisées pour l’échange
            sécurisé.
        </p>
        <p class="pb-2 mt-1">
            <strong id="Algorithme-chiffrement">
                Algorithme de chiffrement :
            </strong>
            Méthode de chiffrement utilisée pour sécuriser les communications VPN.
        </p>
        <p class="pb-2 mt-1">
            <strong> Empreinte de l'Algorithme d'Authentification : </strong>
            Algorithme de hachage utilisé pour vérifier l'intégrité des données
            transmises.
        </p>
        <p class="pb-2 mt-1">
            <strong> Réseau de tunnels IPv4 : </strong>
            Plage d’adresses IP attribuées aux clients VPN.
        </p>
        <p class="pb-2 mt-1">
            <strong> Réseau distant IPv4 : </strong>
            Adresse réseau du serveur auquel le
            <span id="client-VPN">client VPN</span> accède.
        </p>
        <p class="pb-2 mt-1">
            <strong> Compression : </strong>
            Active la compression des données pour améliorer la performance du VPN.
        </p>
        <p class="pb-2 mt-1">
            <strong> Adresse et port de l'hôte ou du serveur : </strong>
            Adresse IP ou nom de domaine du serveur VPN.
        </p>

        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="exporter"> 2. Exporter un client à partir d'un serveur </span>
        </h3>

        <div class="mb-3 d-flex justify-center align-center py-2">
            <img class="rounded-md" src="@/assets/images/openVpn/image33.png" style="width: 100%" />

        </div>

        <p class="pb-2 mt-1">
            Depuis la liste des serveurs, l'utilisateur peut exporter la
            configuration des clients en cliquant sur l'icône utilisateur. Cela
            permet de créer un nouveau <span id="client-VPN">client VPN</span> avec
            les certificats client appropriés.
        </p>

    </div>
</template>