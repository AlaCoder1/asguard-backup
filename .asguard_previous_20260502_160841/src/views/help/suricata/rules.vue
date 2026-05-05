<template>
    <div>
        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span id="gestion-regles-de-detection">Gestion des règles de détection (IDS/IPS)</span>
        </h3>

        <div class="mb-4 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/ips-ids/image4.png" style="width: 100%" />
        </div>
        <p class="pb-2">
            Les règles définissent les critères pour détecter et, si nécessaire,
            bloquer les intrusions sur le réseau. Chaque règle est associée à des
            protocoles, des flux, et des actions spécifiques à appliquer lorsque les
            conditions sont remplies.
        </p>

        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span>Description des colonnes :</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                <strong>Sid (Signature ID) :</strong>
                Un identifiant unique pour chaque règle. Utilisé pour suivre les
                alertes générées.
            </li>
            <li class="mb-2">
                <strong>Action :</strong>
                Définit l'action à effectuer lorsque la règle est déclenchée. Exemple
                :
            </li>

            <ul class="my-2 ml-4" style="list-style-type: circle">
                <li>
                    <strong>alert : </strong>Génère une alerte en cas de correspondance.
                </li>
            </ul>
            <li class="mb-2">
                <strong>Message :</strong>
                Une description lisible expliquant ce que la règle surveille ou
                détecte.
            </li>
            <li class="mb-2">
                <strong>Protocole :</strong>
                Spécifie le protocole réseau concerné (exemple : ip, tcp, pkthdr).
            </li>
            <li class="mb-2">
                <strong>Source :</strong>
                Décrit la source potentielle du trafic à analyser.
            </li>
            <li class="mb-2">
                <strong>Direction :</strong>
                Indique la direction des flux :
            </li>
            <ul class="my-2 ml-4" style="list-style-type: circle">
                <li><strong>-> : </strong>Du trafic source vers destination.</li>
            </ul>

            <li class="mb-2">
                <strong>Destination :</strong>
                Décrit la cible du trafic analysé.
            </li>
            <li class="mb-2">
                <strong>Révision :</strong>
                La version actuelle de la règle. Cela permet de gérer les mises à jour
                ou les modifications apportées aux règles.
            </li>
            <li class="mb-2">
                <strong>Statut :</strong>
                Active ou désactive une règle.
            </li>
        </ul>

        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span id="modification-regles-tableau">Modification des règles directement dans le tableau
            </span>
        </h3>

        <p class="pb-2">
            L'interface permet une modification directe de certaines colonnes dans
            le tableau des règles. Cette méthode est rapide et intuitive, sans
            nécessiter de formulaire distinct.
        </p>

        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span>Fonctionnalités disponibles : </span>
        </h3>
        <ul class="list-disc ml-7">
            <li class="mb-2">
                <strong>Recherche :</strong>
                Une barre de recherche permet de trouver des règles spécifiques en
                fonction de leurs IDs, messages, protocoles, etc.
            </li>
            <li class="mb-2">
                <strong>Pagination :</strong>
                Permet de naviguer parmi les nombreuses règles disponibles, organisées
                par pages.
            </li>
            <li class="mb-2">
                <strong>Sauvegarde des modifications :</strong>
                Après avoir modifié des règles, cliquez sur le bouton Sauvegarder pour
                enregistrer les changements.
            </li>
        </ul>
    </div>
</template>