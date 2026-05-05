<template>
    <div class="container">
        <p class="py-2">
            L'interface <span id="sd-wan">SD-WAN</span> permet de configurer des
            zones (areas) et des règles
            <span id="regles-sd-wan">SD-WAN</span> associées. Ces règles incluent
            des algorithmes tels que le <span id="round-robin">round-robin</span> ou
            le <span id="failover">failover</span> pour gérer le routage et la haute
            disponibilité.
        </p>

        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="creation-gestion-zones">1. Création et gestion des zones (Areas)</span>
        </h3>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 17px">
            <span id="liste-zones">Liste des zones</span>
        </h3>

        <p class="pb-2">
            Chaque zone correspond à un regroupement d’interfaces réseau (<span id="wan">WAN</span>, <span
                id="lan">LAN</span>, etc.).
            <span id="liste-zones-2">liste des zones</span> affiche les colonnes
            suivantes :
        </p>

        <ul class="list-disc ml-7">
            <li class="mb-3">
                <strong id="area-name">Area Name :</strong> Nom de la zone.
            </li>
            <li class="mb-3">
                <strong id="members">Members :</strong> Interfaces incluses dans cette
                zone.
            </li>
            <li class="mb-3">
                <strong id="actions">Actions :</strong> Interfaces incluses dans cette
                zone.
            </li>

            <ul class="mt-2 ml-4" style="list-style-type: circle">
                <li>
                    <span id="modifier" class="text-md text-gray-700">Modifier (icône crayon) :</span>
                    Permet d'éditer la zone.
                </li>
                <li>
                    <span id="supprimer" class="text-md text-gray-700">Supprimer (icône corbeille) :</span>
                    Supprime la zone.
                </li>
            </ul>
        </ul>

        <h3 class="font-semibold text-sm py-2" style="font-size: 17px">
            <span id="ajouter-zone">Ajouter une zone</span>
        </h3>

        <ol class="list-decimal ml-8">
            <li class="mb-2">
                Cliquez sur le bouton <strong id="add-area">Add Area</strong>.
            </li>
            <li class="mb-2">Dans la fenêtre de création :</li>

            <ul class="list-disc ml-7">
                <li class="mb-3">
                    <strong id="enter-area-name">Enter Area Name :</strong> Donnez un
                    nom à la zone.
                </li>
                <li class="mb-3">
                    <strong id="list-wan">List WAN :</strong> Sélectionnez les
                    interfaces à inclure dans cette zone.
                </li>
            </ul>
            <li class="mb-2">
                Cliquez sur <strong id="create">Create</strong> pour sauvegarder la
                zone.
            </li>
        </ol>
        <!--  -->
        <div class="mb-7 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/sdwan1.png" style="width: 100%" />
        </div>
        <h3 id="creation-gestion-regles-sdwan" class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span>2. Création et gestion des règles SD-WAN</span>
        </h3>

        <h3 id="liste-regles-sdwan" class="font-semibold text-sm pb-2" style="font-size: 17px">
            <span>Liste des règles SD-WAN</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-3">
                Cette section affiche les règles configurées avec les colonnes
                suivantes :
            </li>
            <li id="rule-name" class="mb-3">
                <strong>Rule Name :</strong> Nom de la règle.
            </li>
            <li id="algorithm-type" class="mb-3">
                <strong>Algorithm Type :</strong> Type d’algorithme utilisé
                (round-robin, failover, etc.).
            </li>
            <li id="actions" class="mb-3"><strong>Actions :</strong></li>

            <ul class="mt-2 ml-4" style="list-style-type: circle">
                <li id="modifier">
                    <span class="text-md text-gray-700">Modifier (icône crayon) :</span>
                    Permet d’éditer une règle.
                </li>
                <li id="supprimer">
                    <span class="text-md text-gray-700">Supprimer (icône corbeille) :</span>
                    Supprime la règle.
                </li>
                <li id="activer">
                    <span class="text-md text-gray-700">Activer (icône verte) :</span>
                    Active la règle.
                </li>
            </ul>
        </ul>

        <h3 id="ajouter-regle" class="font-semibold text-sm py-2" style="font-size: 17px">
            <span>Ajouter une règle</span>
        </h3>

        <ol class="list-decimal ml-8">
            <li id="add-rule" class="mb-2">
                Cliquez sur le bouton <strong>Add Rule</strong>.
            </li>
            <li class="mb-2">Dans la fenêtre de création :</li>

            <ul class="list-disc ml-7">
                <li id="enter-rule-name" class="mb-3">
                    <strong>Rule Name : </strong>Entrez un nom pour la règle.
                </li>
                <li id="source" class="mb-3">
                    <strong>Source : </strong>Spécifiez l’adresse IP source et le
                    préfixe.
                </li>
                <li id="algo" class="mb-3">
                    <strong>Algo : </strong>Choisissez l’algorithme (round-robin,
                    failover, etc.).
                </li>
                <li id="area" class="mb-3">
                    <strong>Area : </strong>Associez cette règle à une zone existante.
                </li>
                <li id="health-check-ms" class="mb-3">
                    <strong>Health check milliseconds : </strong>Configurez l’intervalle
                    de vérification en millisecondes.
                </li>
                <li id="health-check-target" class="mb-3">
                    <strong>Health check target : </strong>Entrez une adresse IP de
                    cible pour les vérifications (par exemple, une passerelle ou un
                    serveur distant comme 8.8.8.8).
                </li>
            </ul>
            <li id="create-rule" class="mb-2">
                Cliquez sur <strong>Create</strong> pour enregistrer la règle.
            </li>
        </ol>

        <div id="sdwan-image" class="mb-7 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/sdwan2.png" style="width: 100%" />
        </div>

        <h3 id="description-algorithmes" class="font-weight-bold text-sm py-2" style="font-size: 20px">
            <span>Description des algorithmes disponibles</span>
        </h3>

        <ul class="list-disc ml-7">
            <li id="round-robin" class="mb-3">
                <strong>Round-robin : </strong>Ce type d'algorithme distribue les
                connexions de manière égale entre les interfaces ou les chemins
                disponibles.
            </li>
            <li id="failover" class="mb-3">
                <strong>Failover : </strong>Ce type d'algorithme bascule
                automatiquement vers une interface de secours en cas de défaillance de
                l'interface principale.
            </li>
        </ul>

        <div class="flex gap-2 py-2">
            <hr class="w-full h-[0.1rem] bg-[#ffcc19] border-1 rounded" />
        </div>

        <h3 id="notes-importantes" class="font-weight-bold text-sm py-2" style="font-size: 20px">
            <span>Notes importantes</span>
        </h3>
        <!--  -->

        <ul class="list-disc ml-7">
            <li id="configuration-zones-regles" class="mb-3">
                <strong>Configuration des zones et règles :</strong>
            </li>
            <ul class="mt-2 ml-4" style="list-style-type: circle">
                <li id="interfaces-zones-configurees" class="mb-2">
                    Assurez-vous que les interfaces assignées à une zone sont
                    correctement configurées dans votre réseau.
                </li>
                <li id="choix-algorithmes-besoins">
                    Le choix des algorithmes dépend des besoins de votre organisation
                    (distribution équilibrée vs haute disponibilité).
                </li>
            </ul>
            <li id="tests-regles" class="mb-3 mt-3">
                <strong>Tests des règles :</strong> Après la création de règles,
                effectuez des tests de connectivité pour vous assurer que le
                comportement attendu est respecté.
            </li>
            <li id="sante-interfaces" class="mb-3 mt-3">
                <strong>Santé des interfaces :</strong> Utilisez des adresses fiables
                pour les vérifications de santé (comme 8.8.8.8 de Google).
            </li>
        </ul>

        <!--  -->
    </div>
</template>