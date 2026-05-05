<template>
  <div >
    <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
      1. Introduction
    </h3>

    <p class="pb-3 mt-2">
      Les paramètres généraux définissent les configurations essentielles du
      système, comme le nom d’hôte, le domaine, le fuseau horaire et les
      serveurs DNS. Ce guide explique les étapes et champs à configurer.
    </p>

    <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
      <span id="configurer-parametres"
        >2. Étapes pour configurer les paramètres généraux</span
      >
    </h3>
    <h3 class="font-semibold text-sm pb-1" style="font-size: 17px">
      <span>2.1 Accéder à l’interface des paramètres généraux : </span>
    </h3>
    <p class="pb-3">
      Ouvrez l’onglet "Système -> Paramètre" dans notre produit de sécurité.
    </p>

    <div class="mb-3 d-flex justify-center align-center py-2">
      <img
        class="rounded-md"
        src="@/assets/images/settings/image.png"
        style="width: 100%"
      />
    </div>

    <h3 class="font-semibold text-sm pb-1" style="font-size: 17px">
      <span>2.2 Remplir les champs système : </span>
    </h3>
    <p class="pb-3">
      Saisissez ou modifiez les informations essentielles, comme le nom d’hôte,
      le domaine, et le fuseau horaire.
    </p>

    <h3 class="font-semibold text-sm pb-1" style="font-size: 17px">
      <span id="configurer-réseau">2.3 Configurer le réseau : </span>
    </h3>
    <p class="pb-3">Ajouter et définir les serveurs DNS nécessaires.</p>

    <div class="mb-3 d-flex justify-center align-center py-2">
      <img
        class="rounded-md"
        src="@/assets/images/settings/image2.png"
        style="width: 100%"
      />
    </div>

    <h3 class="font-semibold text-sm pb-1" style="font-size: 17px">
      <span id="sauvegarder">2.4 Sauvegarder les modifications : </span>
    </h3>
    <p class="pb-3">Cliquez sur "Ajouter" pour enregistrer vos paramètres.</p>

    <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
      3. Description des champs d’entrée
    </h3>
    <h3 class="font-semibold text-sm pb-1" style="font-size: 17px">
      <span>3.1 Section Système : </span>
    </h3>

    <ul class="list-disc ml-7">
      <li class="mb-2">Nom d’hôte :</li>
      <ul class="mt-2 ml-4 mb-2" style="list-style-type: circle">
        <li>
          <span class="text-md">Description : </span>Identifiant unique de votre
          système.
        </li>
        <li>
          <span class="text-md">Exemple :</span>
          "Asguard" ou tout autre nom représentant votre appareil ou service.
        </li>
        <li>
          <span class="text-md">Format attendu :</span>
          Texte simple, sans espaces.
        </li>
      </ul>

      <li class="mb-2">Domaine :</li>
      <ul class="mt-2 ml-4 mb-2" style="list-style-type: circle">
        <li>
          <span class="text-md">Description : </span>Le domaine réseau auquel
          appartient le système.
        </li>
        <li>
          <span class="text-md">Exemple :</span>
          "localdomain" ou un nom de domaine personnalisé.
        </li>
        <li>
          <span class="text-md">Format attendu :</span>
          Nom valide respectant les conventions des domaines.
        </li>
      </ul>

      <li class="mb-2">Fuseau horaire :</li>
      <ul class="mt-2 ml-4 mb-2" style="list-style-type: circle">
        <li>
          <span class="text-md">Description : </span>Sélectionnez le fuseau
          horaire correspondant à votre emplacement géographique ou à celui du
          système.
        </li>
        <li>
          <span class="text-md">Exemple :</span>
          "Africa/Tunis".
        </li>
        <li>
          <span class="text-md">Format attendu :</span>
          Sélection via une liste déroulante.
        </li>
      </ul>
    </ul>

    <h3 class="font-semibold text-sm pb-1" style="font-size: 17px">
      <span id="section-réseau">3.2 Section Réseau : </span>
    </h3>
    <ul class="list-disc ml-7">
      <li class="mb-2">Serveur DNS (Obligatoire) :</li>
      <ul class="mt-2 ml-4 mb-2" style="list-style-type: circle">
        <li>
          <span class="text-md">Description : </span> Adresse IP du serveur DNS
          à utiliser pour la résolution de noms.
        </li>
        <li>
          <span class="text-md">Format attendu :</span>
          Une adresse IP valide (exemple : "8.8.8.8").
        </li>
      </ul>

      <li class="mb-2">Passerelle (Obligatoire) :</li>
      <ul class="mt-2 ml-4 mb-2" style="list-style-type: circle">
        <li>
          <span class="text-md">Description : </span>Choisissez la passerelle
          réseau via une liste déroulante pour connecter le DNS.
        </li>
        <li>
          <span class="text-md">Exemple :</span>
          Sélectionnez une passerelle prédéfinie ou active dans le réseau.
        </li>
      </ul>
    </ul>
  </div>
</template>
