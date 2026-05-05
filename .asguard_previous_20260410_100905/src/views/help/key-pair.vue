<template>
    <div class="container">
        <p id="interface-description" class="py-3">
            L'interface permet de gérer facilement les paires de clés RSA,
            essentielles pour la sécurité des communications et l'authentification.
            Voici les principales fonctionnalités disponibles :
        </p>

        <h3 id="liste-cles" class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            1. Liste des Clés
        </h3>

        <ul id="list-cles" class="list-disc ml-7">
            <li id="liste-informations-clé" class="mb-2">
                Les clés sont affichées dans une liste avec les informations suivantes
                :
            </li>
            <ul class="mt-2 ml-4 mb-2" style="list-style-type: circle">
                <li id="nom-cle">
                    <span class="text-md text-gray-500">Nom de la clé</span>
                </li>
                <li id="utilite-cle">
                    <span class="text-md text-gray-500">Utilité (Privée ou Publique)</span>
                </li>
                <li id="taille-cle">
                    <span class="text-md text-gray-500">Taille de la clé</span>
                </li>
                <li id="empreinte-numerique">
                    <span class="text-md text-gray-500">Empreinte numérique (si applicable)</span>
                </li>
            </ul>

            <li id="actions-possibles" class="mb-2">
                Actions possibles :
                <ul class="mt-2 ml-4 mb-2" style="list-style-type: circle">
                    <li id="actions-cles-publiques">
                        <span class="text-md text-gray-500">Pour les clés publiques : Copier, Télécharger ou
                            Supprimer.</span>
                    </li>

                    <li id="actions-cles-privees">
                        <span class="text-md text-gray-500">Pour les clés privées : Supprimer ou les utiliser
                            directement
                            dans des fonctionnalités comme le pare-feu</span>
                    </li>
                </ul>
            </li>
        </ul>

        <div id="image-rsa-1" class="mb-3 d-flex justify-center align-center py-2">
            <img class="rounded-md" src="@/assets/images/rsa/rsa1.png" style="width: 100%" />

        </div>

        <h3 id="creation-cles" class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            2. Création de Clés
        </h3>

        <ul id="list-creation-cles" class="list-disc ml-7">
            <li id="generer-cles" class="mb-2">
                L'utilisateur peut générer différents types de clés RSA selon ses
                besoins :
            </li>
            <ul class="mt-2 ml-4 mb-2" style="list-style-type: circle">
                <li id="cle-privee">
                    <span class="text-md text-gray-500"><strong>Clé Privée :</strong> Choisir le nom, le type (RSA) et
                        la
                        taille (par ex. 2048 bits).</span>
                </li>
                <li id="cle-publique">
                    <span class="text-md text-gray-500"><strong>Clé Publique :</strong> Générée à partir d'une clé
                        privée
                        existante.</span>
                </li>
                <li id="importation-cle-publique">
                    <span class="text-md text-gray-500"><strong>Importation de Clé Publique :</strong> Possibilité
                        d’importer une clé publique externe en la saisissant dans le champ
                        dédié.</span>
                </li>
            </ul>
        </ul>

        <div id="image-rsa-2" class="flex justify-between gap-10">
            <div class="mb-7 d-flex justify-center align-center py-2">
                <img class="rounded-md" src="@/assets/images/rsa/rsa2.png" style="width: 100%; height: 100%" />

            </div>
            <div class="mb-7 d-flex justify-center align-center py-2">
                <img class="rounded-md" src="@/assets/images/rsa/rsa3.png" style="width: 100%; height: 100%" />

            </div>
            <div class="mb-7 d-flex justify-center align-center py-2">
                <img class="rounded-md" src="@/assets/images/rsa/rsa4.png" style="width: 100%; height: 100%" />

            </div>
        </div>

        <h3 id="gestion-cles" class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            3. Gestion des Clés
        </h3>

        <ul id="list-gestion-cles" class="list-disc ml-7">
            <li id="utilisation-cles" class="mb-2">
                <strong>Utilisation :</strong> Les clés privées générées peuvent être
                intégrées dans les services du pare-feu ou autres composants de
                sécurité.
            </li>
            <li id="securite-cles" class="mb-2">
                <strong>Sécurité :</strong> Les clés privées ne peuvent pas être
                copiées ni téléchargées pour garantir leur confidentialité.
            </li>
        </ul>

        <div id="image-rsa-5" class="mb-7 d-flex justify-center align-center py-2">
            <img class="rounded-md" src="@/assets/images/rsa/rsa5.png" />

        </div>
    </div>

</template>