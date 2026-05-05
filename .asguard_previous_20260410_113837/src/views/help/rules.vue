<template>
    <div class="container">
        <p class=" pb-4 mt-1">
            Cette interface permet de gérer les règles de pare-feu en fonction des
            interfaces réseau, telles que WAN et LAN. Les règles sont divisées en
            deux catégories :
        </p>

        <ol class="list-decimal ml-8">
            <li class="mb-2">
                <strong id="regles-entrantes">Règles entrantes (Inbound rules) :</strong>
                Gèrent les connexions provenant de l'extérieur vers le réseau.
            </li>
            <li class="mb-2">
                <strong id="regles-sortantes">Règles sortantes (Outbound rules) :</strong>
                Gèrent les connexions initiées depuis le réseau local vers
                l'extérieur.
            </li>
        </ol>

        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="navigation-interface">Navigation dans l'interface</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                <strong id="onglets-wan-lan">Onglets WAN/LAN : </strong>
                <ul class="mt-2 ml-4 mb-2" style="list-style-type: circle">
                    <li>
                        <span class="text-md text-gray-500" id="wan">
                            <strong>WAN : </strong>Pour les connexions entrant/sortant par
                            l'interface WAN.
                        </span>
                    </li>
                    <li>
                        <span class="text-md text-gray-500" id="lan">
                            <strong>LAN : </strong> Pour les connexions entrant/sortant par
                            l'interface LAN.
                        </span>
                    </li>
                </ul>
            </li>

            <li class="mb-2">
                <strong id="bouton-add">Bouton ADD : </strong>
                Permet d'ajouter une nouvelle règle au pare-feu.
            </li>
            <li class="mb-2">
                <strong id="tableau-regles">Tableau des règles : </strong>
                Permet d'ajouter une nouvelle règle au pare-feu.
            </li>

            <ul class="mt-2 ml-4 mb-2" style="list-style-type: circle">
                <li>
                    <span class="text-md text-gray-500" id="policy">
                        <strong>Policy : </strong>Type d'action (ex. : accept, drop).
                    </span>
                </li>
                <li>
                    <span class="text-md text-gray-500" id="rule-description">
                        <strong>Rule Description : </strong> Description de la règle pour
                        identifier son objectif.
                    </span>
                </li>
                <li>
                    <span class="text-md text-gray-500" id="protocol">
                        <strong>Protocol : </strong> Protocole réseau (ex. : TCP, UDP,
                        ALL).
                    </span>
                </li>
                <li>
                    <span class="text-md text-gray-500" id="source-address">
                        <strong>Source Address / Source Port : </strong> Adresse/Port
                        source de la connexion.
                    </span>
                </li>
                <li>
                    <span class="text-md text-gray-500" id="destination-address">
                        <strong>Destination Address / Destination Port : </strong>
                        Adresse/Port de destination de la connexion.
                    </span>
                </li>
                <li>
                    <span class="text-md text-gray-500" id="action">
                        <strong>Action : </strong> Adresse/Port de destination de la
                        connexion.
                    </span>
                </li>
                <ul class="list-disc ml-7">
                    <li class="mb-2" id="edition">
                        <strong>Édition (icône crayon) : </strong>Modifier la règle
                        existante.
                    </li>
                    <li class="mb-2" id="suppression">
                        <strong>Suppression (icône corbeille) : </strong>Supprimer la
                        règle.
                    </li>
                </ul>
            </ul>
            <li class="mb-2" id="bouton-save">
                <strong>Bouton Save : </strong>
                Enregistrez les modifications apportées aux règles.
            </li>
        </ul>

        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="ajout-regle">Ajout d'une règle</span>
        </h3>

        <ol class="list-decimal ml-8 mt-3">
            <li class="mb-2">
                Cliquez sur le bouton <strong id="add-button">ADD</strong>.
            </li>
            <li class="mb-2">
                Configurez les paramètres suivants dans la fenêtre de création de
                règle :
            </li>
            <ul class="list-disc ml-7">
                <li class="mb-2" id="policy-selection">
                    <strong>Policy : </strong>Choisissez entre accept, drop, ou d'autres
                    politiques disponibles.
                </li>
                <li class="mb-2" id="rule-description-input">
                    <strong>Rule Description : </strong>Entrez une description claire
                    pour la règle.
                </li>
                <li class="mb-2" id="protocol-selection">
                    <strong>Protocol : </strong>Spécifiez le protocole (TCP, UDP, ALL).
                </li>
                <li class="mb-2" id="source-address-input">
                    <strong>Source Address / Source Port : </strong>Définissez les
                    paramètres sources (ALL pour tout accepter).
                </li>
                <li class="mb-2" id="destination-address-input">
                    <strong>Destination Address / Destination Port : </strong>
                    Définissez les paramètres de destination (ALL pour tout accepter).
                </li>
            </ul>
            <li class="mb-2" id="create-button">
                Cliquez sur <strong>Create</strong> pour ajouter la règle.
            </li>
        </ol>

        <div class=" d-flex justify-center align-center py-5">
            <img class="rounded-md" src="@/assets/images/firewall/fw1.png" style="width: 100%" />
        </div>

        <h3 class="font-weight-bold text-1xl pb-2" style="font-size: 20px">
            <span id="ajout-regle-specifique">Ajout d'une règle spécifique</span>
        </h3>

        <div class="mb-4  d-flex justify-center align-center py-3">
            <img class="rounded-md" src="@/assets/images/firewall/fw2.png" style="width: 100%" />
        </div>

        <h3 class="font-weight-bold text-1xl pb-2" style="font-size: 20px">
            <span id="modification-regle">Modification d'une règle</span>
        </h3>

        <ol class="list-decimal ml-8 mt-1">
            <li class="mb-2" id="icône-crayon">
                Cliquez sur l'icône de crayon à droite de la règle.
            </li>
            <li class="mb-2" id="modification-parametres">
                Modifiez les paramètres souhaités.
            </li>
            <li class="mb-2" id="save-modification">
                Cliquez sur <strong>Save</strong> pour enregistrer les changements.
            </li>
        </ol>

        <h3 class="font-weight-bold text-1xl pb-2" style="font-size: 20px">
            <span id="suppression-regle">Suppression d'une règle</span>
        </h3>

        <ol class="list-decimal ml-8 mt-1">
            <li class="mb-2" id="icone-corbeille">
                Cliquez sur l'icône corbeille à droite de la règle.
            </li>
            <li class="mb-2" id="confirmation-suppression">
                Confirmez la suppression.
            </li>
        </ol>

        <h3 class="font-weight-bold text-1xl pb-2" style="font-size: 20px">
            <span id="exemple-configuration">Exemple de configuration</span>
        </h3>
        <h3 class="font-weight-bold text-1xl pb-2" style="font-size: 18px">
            <span id="rule-inbound">Règle entrante (Inbound)</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                <strong>Description : </strong> Accepter tout le trafic entrant sur le
                WAN.
            </li>
            <li class="mb-2"><strong>Policy : </strong> accept</li>
            <li class="mb-2"><strong>Protocol : </strong> ALL</li>
            <li class="mb-2"><strong>Source Address/Port : </strong> ALL</li>
            <li class="mb-2"><strong>Destination Address/Port : </strong> ALL</li>
        </ul>

        <h3 class="font-weight-bold text-1xl pb-2 mt-2" style="font-size: 18px">
            <span id="rule-outbound">Règle sortante (Outbound)</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                <strong>Description : </strong> Accepter tout le trafic sortant vers
                le WAN.
            </li>
            <li class="mb-2"><strong>Policy : </strong> accept</li>
            <li class="mb-2"><strong>Protocol : </strong> ALL</li>
            <li class="mb-2"><strong>Source Address/Port : </strong> ALL</li>
            <li class="mb-2"><strong>Destination Address/Port : </strong> ALL</li>
        </ul>
    </div>
</template>