<template>
    <div>
        <h3 class="font-weight-bold text-1xl pt-2" style="font-size: 20px" id="dhcp-v4">
            <span id="DHCP"> DHCP V4 </span>
        </h3>

        <p class="py-2" id="dhcp-description">
            Le protocole DHCPv4 permet d'attribuer automatiquement des adresses IP
            et d'autres paramètres réseau essentiels à des appareils connectés à un
            réseau.
        </p>

        <div class="mb-3 d-flex justify-center align-center py-4" id="dhcp-image">
            <img class="rounded-md" src="@/assets/images/interfaces/interfaces18.png" style="width: 100%" />
        </div>

        <h3 class="font-weight-bold text-1xl pt-2 mb-4" style="font-size: 20px" id="dhcp-options">
            <span> Options disponibles :</span>
        </h3>

        <ul class="list-disc ml-7" id="dhcp-options-list">
            <li class="mb-2" id="dhcp-enable">
                <strong>Activer le serveur DHCP sur cette interface : </strong> Permet
                d'activer ou de désactiver le service DHCP sur l'interface réseau
                configurée.
            </li>
            <li class="mb-2" id="subnet-address">
                <strong>Adresse de sous-réseau : </strong> Spécifie l'adresse réseau
                principale pour laquelle le DHCP gérera les adresses. Par exemple,
                192.168.20.0.
            </li>
            <li class="mb-2" id="subnet-mask">
                <strong>Masque de sous-réseau : </strong>Définit le masque de
                sous-réseau pour l'adresse réseau. Par exemple, 255.255.255.0.
            </li>
            <li class="mb-2" id="dhcp-range">
                <strong>Plage disponible : </strong>
                <ul class="mt-2 ml-4 mb-2" style="list-style-type: circle" id="dhcp-range-list">
                    <li id="range-from">
                        <span class="text-md text-gray-500">Plage de : Adresse IP de début pour la plage d’adresses
                            attribuables par le serveur DHCP.
                        </span>
                    </li>
                    <li id="range-to">
                        <span class="text-md text-gray-500">Plage à : Adresse IP de fin pour la plage d’adresses
                            attribuables par le serveur DHCP.
                        </span>
                    </li>
                </ul>
            </li>
            <li class="mb-2" id="dhcp-table">
                <strong>Tableau des plages : </strong>Affiche les plages configurées
                avec leurs adresses de début et de fin.
            </li>
        </ul>

        <div class="mb-4 d-flex justify-center align-center" id="dhcp-table-image">
            <img class="rounded-md" src="@/assets/images/interfaces/interfaces19.png" style="width: 100%" />

        </div>

        <ul class="list-disc ml-7" id="dhcp-button">
            <li class="mb-4" id="add-button">
                <strong>Bouton "Ajouter" : </strong>Permet de configurer une nouvelle
                plage. Lorsqu'on clique dessus, une fenêtre s'affiche pour saisir la
                plage de début et de fin d’adresses IP (voir capture "Fenêtre d’ajout
                de plage").
            </li>
        </ul>

        <div class="mb-6 d-flex justify-center align-center" id="dhcp-button-image">
            <img class="rounded-md" src="@/assets/images/interfaces/interfaces10.png" style="width: 500px" />

        </div>

        <ul class="list-disc ml-7" id="dhcp-parameters">
            <li class="mb-2" id="dns-server">
                <strong>Serveur DNS : </strong>Champ permettant de spécifier les
                serveurs DNS à utiliser pour la résolution des noms de domaine.
                Plusieurs entrées peuvent être ajoutées (par exemple, 8.8.8.8,
                1.1.1.1).
            </li>
            <li class="mb-2" id="gateway">
                <strong>Passerelle : </strong>Adresse IP de la passerelle par défaut,
                utilisée pour router le trafic vers l’extérieur du réseau local.
            </li>
            <li class="mb-2" id="domain-name">
                <strong>Nom de domaine : </strong>Permet de spécifier un nom de
                domaine local ou personnalisé, utilisé pour la résolution interne des
                noms.
            </li>
        </ul>

    </div>
</template>