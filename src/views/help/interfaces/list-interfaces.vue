<template>
    <div class="container">

        <h3 class="font-weight-bold py-2" style="font-size: 20px" id="liste-des-interfaces-heading">
            <span id="liste-des-interfaces"> Liste des interfaces </span>
        </h3>

        <p id="interface-list-description">
            Ici, on a la liste des interfaces présentes et activées dans le
            pare-feu, comme par exemple l'interface LAN, WAN, VXLAN5, etc., qui ont
            été créées.
        </p>

        <p class=" py-4" id="interface-subfields">
            Pour chaque interface, on dispose de sous-champs de configuration en
            fonction des paramètres et options choisis, tels que :
        </p>

        <ul class="list-disc ml-7" id="configuration-options">
            <li class="mb-2">Configuration de base</li>
            <li class="mb-2">Configuration générique</li>
            <li class="mb-2">Configuration de l'adresse IPv4 statique</li>
        </ul>

        <div class="mb-7 d-flex justify-center align-center py-4" id="image2-container">
            <img class="rounded-md" src="@/assets/images/interfaces/interfaces2.png" style="width: 100%" id="image2" />

        </div>
        <div class="mb-7 d-flex justify-center align-center py-4" id="image2-container">
            <img class="rounded-md" src="@/assets/images/interfaces/interfaces3.png" style="width: 100%" id="image2" />

        </div>

        <div class="d-flex justify-center align-center pt-4" id="image3-container">
            <img class="rounded-md" src="@/assets/images/interfaces/interfaces4.png" style="width: 100%" id="image3" />

        </div>
    </div>
</template>