<template>
  <div class="container">
    <h3
      class="font-weight-bold text-1xl py-2"
      style="font-size: 20px"
      id="type-des-interfaces-heading"
    >
      <span id="type-des-interfaces"> Type des interfaces </span>
    </h3>

    <p class="py-3" id="interface-type-description">
      Pour créer une nouvelle interface virtuelle, on peut accéder à
      <strong> Interfaces -> Type d’interfaces. </strong>.
    </p>

    <h3
      class="font-weight-bold text-1xl py-2"
      style="font-size: 20px"
      id="create-vlan-heading"
    >
      <span id="create-vlan"> Création d’une interface VLAN :</span>
    </h3>

    <p class="py-2" id="vlan-description">
      Un VLAN (Virtual Local Area Network) est une technologie permettant de
      créer des réseaux logiques séparés au sein d'une même infrastructure
      physique. Il permet de segmenter un réseau en sous-réseaux virtuels pour
      améliorer la sécurité, la gestion du trafic et l'efficacité.
    </p>

    <p class="py-2" id="vlan-button">
      Sous le champ de création de VLANs, on trouve un bouton intitulé
      <strong>"Ajouter un VLAN"</strong>.
    </p>

    <div
      class="mb-7 d-flex justify-center align-center py-2"
      id="image4-container"
    >
      <img
        class="rounded-md"
        src="@/assets/images/interfaces/interfaces6.png"
        style="width: 100%"
        id="image4"
      />
    </div>

    <p class="py-2" id="vlan-parameters">Les paramètres à remplir incluent :</p>

    <div
      class="mb-4 d-flex justify-center align-center py-2"
      id="image5-container"
    >
      <img
        class="rounded-md"
        src="@/assets/images/interfaces/interfaces5.png"
        style="width: 180px"
        id="image5"
      />
    </div>

    <ul class="list-disc ml-7" id="vlan-configuration-options">
      <li class="mb-2" id="vlan-interface-parent">
        <strong>Interface parent : </strong>Interface physique ou principale sur
        laquelle le VLAN sera créé.
      </li>
      <li class="mb-2" id="vlan-tag">
        <strong>Tag VLAN : </strong>Identifiant unique du VLAN (1 à 4094).
      </li>
      <li class="mb-2" id="vlan-priority">
        <strong>Priorité VLAN : </strong>Niveau de priorité (0 à 7).
      </li>
      <li class="mb-2" id="vlan-description">
        <strong>Description : </strong>Note ou texte descriptif pour identifier
        le VLAN.
      </li>
    </ul>
    <!--  -->
    <h3
      class="font-weight-bold text-1xl py-2"
      style="font-size: 20px"
      id="vxlan-creation"
    >
      <span> Création d’une interface VXLAN : </span>
    </h3>

    <p class="pb-3" id="vxlan-description">
      Un VXLAN (Virtual Extensible LAN) est une technologie de virtualisation de
      réseau qui permet de créer des réseaux locaux virtuels sur des réseaux
      physiques étendus. Il utilise des tunnels encapsulés pour transporter des
      paquets Ethernet à travers des réseaux IP, facilitant ainsi la mise en
      réseau à grande échelle dans des environnements virtualisés.
    </p>

    <p class="pb-2" id="vxlan-button-description">
      Sous le champ de création de VXLANs, on trouve un bouton intitulé
      <strong>"Ajouter un VXLAN"</strong>.
    </p>

    <div class="mb-4 d-flex justify-center align-center py-2" id="vxlan-image">
      <img
        class="rounded-md"
        src="@/assets/images/interfaces/interfaces8.png"
        style="width: 100%"
      />
    </div>

    <p class="pb-4" id="vxlan-params-description">
      Les paramètres à remplir incluent :
    </p>

    <ul class="list-disc ml-7" id="vxlan-params-list">
      <li class="mb-2" id="vxlan-name">
        <strong>Nom de l'interface : </strong>Identifiant unique pour
        l'interface VXLAN.
      </li>
      <li class="mb-2" id="vxlan-id">
        <strong>Identificateur de réseau VXLAN : </strong> ID unique (1 à
        16777215).
      </li>
      <li class="mb-2" id="vxlan-source-address">
        <strong>Adresse source : </strong> IP source d'envoi des paquets VXLAN.
      </li>
      <li class="mb-2" id="vxlan-destination-address">
        <strong>Adresse de destination : </strong> IP de réception des paquets
        VXLAN.
      </li>
      <li class="mb-2" id="vxlan-port">
        <strong>Port de destination : </strong> Port UDP à utiliser, compris
        entre 1 et 65535 (par défaut : 4789).
      </li>
      <li class="mb-2" id="vxlan-parent-device">
        <strong>Dispositif parent : </strong> Interface physique ou logique
        utilisée.
      </li>
      <li class="mb-2" id="vxlan-connection-name">
        <strong>Nom de la connexion : </strong> Identifiant de la connexion
        VXLAN.
      </li>
    </ul>

    <!--  -->
    <h3
      class="font-weight-bold text-1xl pt-5 pb-3"
      style="font-size: 20px"
      id="interface-assignment"
    >
      <span> Assignement d’interface </span>
    </h3>

    <p class="pb-4" id="interface-assignment-description">
      Permet d'assigner une interface réseau à un VLAN ou VXLAN. L'interface ne
      sera pas configurable et activée tant qu'elle n'aura pas été assignée via
      ce champ.
    </p>

    <div
      class="mb-4 d-flex justify-center align-center py-2"
      id="interface-assignment-image"
    >
      <img
        class="rounded-md"
        src="@/assets/images/interfaces/interfaces14.png"
        style="width: 100%"
      />
    </div>

    <p class="pb-4" id="interface-assignment-section">
      Dans la section dédiée :
    </p>

    <ul class="list-disc ml-7" id="interface-assignment-params">
      <li class="mb-2" id="interface-vlan-vxlan">
        <strong>Sélectionner le type VLAN/VXLAN : </strong>Choisir entre "VXLAN"
        ou "VLAN".
      </li>
      <li class="mb-2" id="interface-select">
        <strong>Nouvelle interface : </strong>Sélectionner l'interface à
        associer.
      </li>
    </ul>

    <p class="py-3" id="interface-assignment-finalize">
      Après avoir sélectionné l'interface souhaitée, cliquez sur "Créer" pour
      finaliser l'assignation.
    </p>

    <h3
      class="font-weight-bold text-1xl pt-5 pb-2"
      style="font-size: 20px"
      id="vlan-configuration-header"
    >
      <span> Configuration d'une interface VLAN </span>
    </h3>

    <h3 class="text-md font-semibold" id="basic-configuration-header">
      <span> Configuration de base</span>
    </h3>

    <div
      class="mb-4 d-flex justify-center align-center py-4"
      id="vlan-configuration-image"
    >
      <img
        class="rounded-md"
        src="@/assets/images/interfaces/interfaces15.png"
        style="width: 100%"
      />
    </div>

    <ul class="list-disc ml-7" id="vlan-configuration-params">
      <li class="mb-2" id="vlan-name">
        <strong>Dispositif : </strong>Nom ou identifiant du VLAN à configurer
        (obligatoire).
      </li>
      <li class="mb-2" id="vlan-description">
        <strong>Description : </strong> Informations supplémentaires ou notes
        sur le VLAN (facultatif).
      </li>
    </ul>

    <h3
      class="font-weight-bold text-1xl py-2"
      style="font-size: 20px"
      id="generic-configuration-header"
    >
      <span> Configuration Générique </span>
    </h3>

    <ul class="list-disc ml-7" id="generic-configuration-params">
      <li class="mb-2" id="network-blocks">
        <strong>Blocs de réseaux : </strong>Cochez "Privé" si le réseau est
        privé, ou "Non assigné par l'IANA" pour éviter les blocs réservés.
      </li>
      <li class="mb-2" id="bogon-addresses">
        <strong>Bloquer les adresses bogon : </strong>Activez pour empêcher le
        trafic provenant d'adresses non routables.
      </li>
      <li class="mb-2" id="ipv4-configuration-type">
        <strong>Type de configuration IPv4 : </strong>Sélectionnez le mode de
        configuration IPv4 (statique, DHCP, etc.).
      </li>
      <li class="mb-2" id="mac-address">
        <strong>Adresse MAC : </strong>Adresse MAC associée à l'interface VLAN
        (facultatif).
      </li>
      <li class="mb-2" id="mtu">
        <strong>MTU : </strong>Taille maximale des paquets transmis (en octets).
      </li>
      <li class="mb-2" id="mss">
        <strong>MSS : </strong>Taille maximale de segment TCP pour le VLAN (en
        octets).
      </li>
      <li class="mb-2" id="speed-duplex">
        <strong>Vitesse et duplex : </strong>Configurez la vitesse et le mode
        duplex pour l'interface réseau.
      </li>
    </ul>

    <h3
      class="font-weight-bold text-1xl py-2"
      style="font-size: 20px"
      id="ipv4-static-configuration-header"
    >
      <span> Configuration de l’adresse IPV4 statique </span>
    </h3>

    <div
      class="mb-4 d-flex justify-center align-center py-4"
      id="ipv4-static-image"
    >
      <img
        class="rounded-md"
        src="@/assets/images/interfaces/interfaces16.png"
        style="width: 100%"
      />
    </div>

    <ul class="list-disc ml-7" id="ipv4-static-params">
      <li class="mb-2" id="ipv4-address">
        <strong>Adresse IPv4 : </strong>Spécifiez l'adresse IPv4 statique pour
        le VLAN (obligatoire).
      </li>
      <li class="mb-2" id="ipv4-prefix">
        <strong>Préfixe : </strong>Indiquez la longueur du masque de
        sous-réseau.
      </li>
      <li class="mb-2" id="ipv4-gateway">
        <strong>IPv4 Gateway : </strong>Sélectionnez ou ajoutez une passerelle
        IPv4 pour acheminer le trafic réseau (obligatoire).
      </li>
    </ul>

    <!--  -->
    <h3
      class="font-weight-bold text-1xl pt-2"
      style="font-size: 20px"
      id="vxlan-configuration"
    >
      <span> Configuration d'une interface VXLAN </span>
    </h3>

    <p class="py-2" id="vxlan-description">
      Pour le VXLAN, la configuration est identique à celle du VLAN, mais seule
      l'option d'adressage statique est disponible pour définir l'adresse IPv4.
    </p>

    <div class="mb-3 d-flex justify-center align-center py-4" id="vxlan-image">
      <img
        class="rounded-md h-full w-full"
        src="@/assets/images/interfaces/interfaces17.png"
        style="width: 100%"
      />
    </div>
  </div>
</template>
