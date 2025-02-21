<template>
    <div class="container">
        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span>1. Introduction</span>
        </h3>

        <p class="py-2">
            Le <span id="proxy">proxy</span> sur un <span id="firewall">firewall</span> joue un rôle essentiel en tant
            qu'intermédiaire
            entre les <span id="utilisateurs">utilisateurs</span> et les <span id="ressources">ressources</span>
            extérieures. Il contribue à
            renforcer la <span id="sécurité">sécurité</span>, contrôler les <span id="accès">accès</span>, et surveiller
            le
            <span id="trafic">trafic</span>
            <span id="réseau">réseau</span>. Cette documentation explique comment configurer les différents
            aspects du <span id="proxy-config">proxy</span> : modification du <span id="port">port</span>,
            activation/désactivation de
            l'<span id="authentification">authentification</span>, gestion des <span
                id="gestion-utilisateurs">utilisateurs</span>, création de <span id="règles">règles</span> et
            activation des <span id="acl-prédéfinis">ACL prédéfinis</span>.
        </p>

        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span id="configuration-du-proxy">2. Configuration du Proxy</span>
        </h3>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 17px">
            <span id="modification-du-port-du-proxy">2.1 Modification du Port du Proxy
            </span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                <span id="acceder-interface-administration-firewall">Accédez à l'interface d'administration du
                    firewall.</span>
            </li>
            <li class="mb-2">
                <span id="naviguer-configuration-proxy">Naviguez vers la section Configuration du Proxy. Identifiez le
                    champ
                    <strong>Port</strong>.</span>
            </li>
            <li class="mb-2">
                <span id="saisir-nouveau-numero-port">Saisissez le nouveau numéro de port souhaité (par exemple, de 8080
                    à
                    3128).</span>
            </li>
            <li class="mb-2">
                <span id="cliquer-enregistrer-appliquer">Cliquez sur <strong>Enregistrer ou Appliquer</strong>.</span>
            </li>
            <li class="mb-2">
                <span id="redemarrer-service-proxy">Redémarrez le service proxy pour appliquer les changements.</span>
            </li>
        </ul>

        <div class="mb-7 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/proxy1.png" style="width: 100%" />
        </div>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 17px">
            <span id="activation-ou-desactivation">2.2 Activation ou Désactivation de l'Authentification
            </span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                <span id="localiser-option-authentification">Dans la section <strong>Configuration du Proxy</strong>,
                    localisez l’option <strong>Authentification</strong>.</span>
            </li>
            <li class="mb-2">
                <span id="activer-ou-desactiver-authentification">Activez ou désactivez l’authentification via une case
                    à
                    cocher ou un bouton bascule.</span>
            </li>
            <li class="mb-2">
                <span id="cliquer-enregistrer-valider">Cliquez sur <strong>Enregistrer</strong> pour valider.</span>
            </li>
        </ul>

        <div class="mb-2 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/proxy2.png" style="width: 100%" />
        </div>

        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span id="gestion-des-utilisateurs">3. Gestion des Utilisateurs</span>
        </h3>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 17px">
            <span id="ajout-utilisateurs">3.1 Ajout d’Utilisateurs </span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                Accédez à la section <strong>Gestion des Utilisateurs</strong> dans le
                menu du proxy.
            </li>
            <li class="mb-2">
                Cliquez sur <strong>Ajouter un utilisateur</strong>.
            </li>
            <li class="mb-2">Remplissez les champs requis :</li>
            <ul class="my-2 ml-4" style="list-style-type: circle">
                <li>Nom d'utilisateur</li>
                <li>Mot de passe</li>
                <li>Email</li>
            </ul>
            <li class="mb-2">Cliquez sur <strong>Enregistrer</strong>.</li>
        </ul>

        <div class="mb-2 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/proxy3.png" style="width: 100%" />
        </div>
        <div class="mb-2 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/proxy4.png" style="width: 100%" />
        </div>

        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span id="creation-regles-proxy">4. Création des Règles de Proxy</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                Naviguez vers la section <strong>Règles de Proxy</strong>.
            </li>
            <li class="mb-2">Cliquez sur <strong>Ajouter une règle</strong>.</li>
            <li class="mb-2">Définissez les paramètres de la règle :</li>
            <ul class="my-2 ml-4" style="list-style-type: circle">
                <li>Nom de la règle (ex. : “Blocage des sites non autorisés”).</li>
                <li>Critères (Domaine, adresse IP, plage d'adresses, URL, heure).</li>
                <li>Action (autoriser, bloquer).</li>
            </ul>
            <li class="mb-2">Priorisez la règle si nécessaire.</li>
            <li class="mb-2">
                Cliquez sur <strong>Create</strong> ou <strong>Créer</strong>.
            </li>
        </ul>

        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span id="creation-regles-nouvelles">Interface création de nouvelles règles :</span>
        </h3>

        <div class="mb-2 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/proxy5.png" style="width: 100%" />
        </div>

        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span id="bloquer-avec-regle-simple">Bloquer avec une règle simple :</span>
        </h3>

        <div class="mb-2 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/proxy6.png" style="width: 100%" />
        </div>

        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span id="bloquer-avec-authentification">Bloquer avec authentification :</span>
        </h3>

        <div class="mb-2 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/proxy7.png" style="width: 100%" />
        </div>

        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span id="bloquer-par-temps">Bloquer par temps (Jours de la semaine, Heures et minutes) :</span>
        </h3>

        <div class="mb-2 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/proxy8.png" style="width: 100%" />
        </div>

        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span id="interface-regles-modification">Interface des règles après modification :</span>
        </h3>

        <div class="mb-2 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/proxy9.png" style="width: 100%" />
        </div>

        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span id="activation-acl-predéfinis">5. Activation des ACL Prédéfinis</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                Accédez à la section <strong id="controle">Contrôle d'Accès (ACL)</strong>.
            </li>
            <li class="mb-2">
                Identifiez les ACL prédéfinis (par exemple : "Adult", "bitcoin").
            </li>
            <li class="mb-2">
                Activez les ACL nécessaires en bloquant les cases correspondantes.
            </li>
            <li class="mb-2">Cliquez sur <strong>Appliquer</strong>.</li>
        </ul>

        <div class="mb-2 mt-4 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/proxy10.png" style="width: 100%" />
        </div>

        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span id="bonnes-pratiques">6. Bonnes Pratiques</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2" id="changer-regular-port">Changer régulièrement le port pour éviter les attaques
                prévisibles.
            </li>
            <li class="mb-2" id="activer-authentification">Activer l’authentification pour protéger les accès.</li>
            <li class="mb-2" id="documenter-regles">Documenter les règles afin de maintenir une vue claire sur les
                configurations appliquées.</li>
            <li class="mb-2" id="tester-configurations">Tester les configurations dans un environnement contrôlé avant
                de
                les appliquer en production.</li>
        </ul>


        <!--  -->
    </div>
</template>