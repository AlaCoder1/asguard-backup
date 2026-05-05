<template>
    <div class="container">

        <div class="flex items-center mt-2">
            <span class="mdi mdi-file-document mr-2" style="font-size: 24px; color: #ffcb26"></span>
            <span id="gestion-Serveurs" style="font-weight: 400; font-size: 20px">Gestion des Serveurs</span>
        </div>

        <div class="flex gap-2 py-2">
            <hr class="w-full h-[0.1rem] bg-[#ffcc19] border-1 rounded" />
        </div>

        <h3 class="font-weight-bold pt-3" style="font-size: 20px">
            <span> 1. Introduction</span>
        </h3>
        <p class=" py-3">
            <span id="ldap">LDAP</span> (Lightweight Directory Access Protocol) est
            un protocole de communication utilisé pour accéder et gérer les services
            d'annuaires distribués. Il permet d'interroger et de modifier des
            informations dans des répertoires, tels que les informations sur les
            <span id="utilisateurs">utilisateurs</span>, les groupes et les
            ressources d'un réseau. <span id="ldap-usage">LDAP</span> est couramment
            utilisé par des solutions comme
            <span id="active-directory">Microsoft Active Directory</span>,
            <span id="openldap">OpenLDAP</span> et
            <span id="novell-edirectory">Novell eDirectory</span>, pour faciliter
            l'<span id="authentification">authentification</span>, l'autorisation et
            la gestion des ressources au sein d'un environnement informatique. Ce
            protocole est dit <span id="leger">"léger"</span> car il a été conçu
            pour être plus simple et plus rapide que les protocoles d'annuaires plus
            anciens, tout en restant efficace pour des besoins complexes de gestion
            d'informations d'annuaire. <span id="asguard">ASGUARD</span> peut
            utiliser un serveur <span id="ldap-server">LDAP</span> en tant que
            serveur d'<span id="authentification-server">authentification</span> et
            lier les <span id="users-link">utilisateurs</span> à ce serveur pour
            permettre l'option d'utilisation d'une adresse mail à l'<span id="initial-auth">authentification</span>
            initiale à l'interface graphique du pare-feu. Dans ce didacticiel, nous
            allons montrer comment configurer la connexion à un serveur d'<span
                id="auth-connection">authentification</span>
            <span id="ldap-auth">LDAP</span> (que ce soit
            <span id="ad">Active Directory</span>,
            <span id="openldap-auth">OpenLDAP</span>, etc.) et expliquer les
            différents champs à remplir pour établir une connexion réussie.
        </p>
        <h3 class="text-md font-semibold" id="prerequis">
            <span> Prérequis</span>
        </h3>
        <p class=" py-3" id="connexion-description">
            Pour procéder à la connexion, nous avons besoin de :
        </p>

        <section id="pre-requis-list">
            <ul class="list-disc ml-7 mt-3">
                <li class="mb-3" id="firewall-asguard">
                    <strong>Firewall ASGUARD : </strong>Permettant l'accès à l'interface
                    utilisateur web.
                </li>
                <li class="mb-3" id="serveur-ldap">
                    <strong>Un serveur LDAP (ex. : Active Directory, OpenLDAP, etc.) : </strong>accessible depuis la
                    machine firewall (les ports nécessaires au
                    service doivent être accessibles et le service sur le serveur doit
                    être disponible et fonctionnel).
                </li>
            </ul>
        </section>

        <h3 class="font-weight-bold py-2" style="font-size: 20px" id="etapes-ajout-serveur">
            <span> 2. Les étapes d'ajout d'un serveur d'authentification</span>
        </h3>

        <section id="ajout-serveur-list">
            <ul class="list-disc ml-7 mt-3">
                <li class="mb-3" id="ajout-serveur">
                    Pour ajouter un nouveau serveur comme source d'authentification,
                    accédez à : « Système -> Utilisateurs -> Serveur d'authentification
                    ».
                </li>
                <li class="mb-3" id="cliquer-ajouter-serveur">
                    Dans le coin inférieur droit, cliquez sur « Ajouter serveur ».
                </li>
                <div class="mb-5 d-flex justify-center align-center" id="image-serveur-auth">
                    <img class="rounded-md" src="@/assets/images/system/serveur_authentification.png"
                        style="width: 100%" />
                </div>
                <li class="mb-5" id="formulaire-ldap">
                    On y reçoit un formulaire à remplir avec les champs nécessaires à la
                    connexion d'un serveur LDAP d'authentification.
                </li>
                <div class="mb-5 d-flex justify-center align-center" id="image-formulaire-ldap">
                    <img class="rounded-md" src="@/assets/images/system/formulaire_ldap.png" />
                </div>
                <div class="mb-5 d-flex justify-center align-center" id="image-champs-ldap">
                    <img class="rounded-md" src="@/assets/images/system/champs_ldap.png" />
                </div>
            </ul>
        </section>

        <!--  -->
        <h3 class="font-weight-bold pb-1" style="font-size: 20px">
            <span id="liaison-utilisateur-serveur-ldap">
                3. La liaison d’un utilisateur à un serveur LDAP
            </span>
        </h3>

        <p class=" py-3">
            <span id="creation-liaison-utilisateur-ldap">À la création d'un nouvel utilisateur système ou à la
                modification
                d'un utilisateur existant, on peut le lier à un serveur LDAP,
                c'est-à-dire le lier à un utilisateur existant dans le serveur Par le
                choix de l'option "Enregistrer sur LDAP" L'utilisateur choisit le
                serveur LDAP auquel il va se connecter à partir de la liste des
                serveurs enregistrés. Ensuite, il devra réécrire le mot de passe de
                l'utilisateur qui a été enregistré lors du premier ajout du
                serveur.</span>
        </p>

        <div class="mb-3 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/system/enregistrer_ldap.png" style="width: 100%" />
        </div>

        <p class=" py-3">
            <span id="activation-enregistrer-ldap">L'ors de l'activation d'option "Enregistrer sur LDAP", le champ
                adresse e-mail doit être compatible avec l'adresse e-mail de
                l'utilisateur présent dans le serveur avec lequel on va établir la
                liaison.</span>
        </p>

        <div class="mb-3 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/system/email_auth_ldap.png" style="width: 100%" />
        </div>

        <div class="flex items-center mt-7">
            <span class="mdi mdi-file-document mr-2" style="font-size: 24px; color: #ffcb26"></span>
            <span id="gestion-utilisateurs" style="font-weight: 400; font-size: 20px">Gestion des utilisateurs</span>
        </div>

        <div class="flex gap-2 py-2">
            <hr class="w-full h-[0.1rem] bg-[#ffcc19] border-1 rounded" />
        </div>

        <h3 class="font-weight-bold py-3" style="font-size: 20px">
            <span id="introduction-creation-utilisateur"> 1. Introduction</span>
        </h3>

        <p class=" py-3">
            <span id="creation-utilisateur-essentielle">La création d’un utilisateur est essentielle pour gérer les
                accès et
                permissions dans votre produit de sécurité. Ce guide explique les
                étapes et options du formulaire pour configurer rapidement des profils
                utilisateur conformes aux politiques de sécurité.</span>
        </p>

        <h3 class="font-weight-bold py-3" style="font-size: 20px">
            <span id="etapes-creation-utilisateur">
                2. Étapes pour créer un utilisateur
            </span>
        </h3>

        <h3 class="text-md font-semibold">
            <span id="acceder-interface-utilisateur">
                2.1 Accéder à l’interface utilisateur :</span>
        </h3>

        <p class=" py-3">
            <span id="navigation-gestion-utilisateurs">Naviguez vers la section de gestion des utilisateurs dans
                l’application.</span>
        </p>

        <div class="mb-3 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/system/gestion_des_utilisateurs.png" style="width: 100%" />
        </div>

        <!--  -->
        <h3 class="text-md font-semibold">
            <span id="cliquer-ajouter-utilisateur">
                2.2 Cliquer sur "Ajouter un Utilisateur" :</span>
        </h3>

        <p class=" py-3">
            <span id="ouvrir-formulaire-creation-utilisateur">Ouvrez le formulaire de création d’un nouvel
                utilisateur.</span>
        </p>

        <h3 class="text-md font-semibold">
            <span id="remplir-champs-formulaire">
                2.3 Remplir les champs du formulaire :</span>
        </h3>

        <p class=" py-3">
            <span id="completer-champs-obligatoires">Complétez les informations nécessaires dans les champs d’entrée
                obligatoires et facultatifs.</span>
        </p>
        <div class="mb-3 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/system/formulaire_ajouter_utilisateur.png"
                style="width: 100%" />
        </div>

        <h3 class="text-md font-semibold mt-5">
            <span id="configurer-options"> 2.4 Configurer les options : </span>
        </h3>

        <p class=" py-3">
            <span id="activer-desactiver-options">Activez ou désactivez les options selon vos besoins (ex. :
                Enregistrement sur LDAP, désactivation de l’utilisateur).</span>
        </p>

        <h3 class="text-md font-semibold mt-2">
            <span id="sauvegarder-utilisateur">
                2.5 Sauvegarder l’utilisateur :
            </span>
        </h3>

        <p class=" py-3">
            <span id="cliquer-creer-sauvegarder">Cliquez sur le bouton "Créer" pour sauvegarder les informations de
                l’utilisateur.</span>
        </p>

        <h3 class="font-weight-bold py-3" style="font-size: 20px">
            <span id="description-champs-entrer">
                3. Description des champs d’entrée
            </span>
        </h3>

        <section>
            <ul class="list-disc ml-10 mt-2">
                <li class="mb-3">
                    <strong id="champ-nom-utilisateur">Nom d'utilisateur</strong>(Obligatoire).
                    <ul class="mt-2 ml-4" style="list-style-type: circle">
                        <li>
                            <span class="text-md" id="description-nom-utilisateur">Description : </span>Identifiant
                            unique pour l’utilisateur.
                        </li>
                    </ul>
                </li>
                <li class="mb-3">
                    <strong id="champ-mot-de-passe">Mot de passe</strong>(Obligatoire).
                    <ul class="mt-2 ml-4" style="list-style-type: circle">
                        <li>
                            <span class="text-md" id="description-mot-de-passe">Description : </span>:Mot de passe
                            utilisé pour sécuriser l’accès de l’utilisateur.
                        </li>
                        <li>
                            <span class="text-md" id="format-mot-de-passe">Format attendu : </span>Minimum 20
                            caractères, peut contenir des lettres, chiffres, et
                            certains caractères spéciaux (selon les règles de votre
                            système).
                        </li>
                    </ul>
                </li>
                <li class="mb-3">
                    <strong id="champ-confirmer-mot-de-passe">Confirmer le mot de passe</strong>(Obligatoire).
                    <ul class="mt-2 ml-4" style="list-style-type: circle">
                        <li>
                            <span class="text-md" id="description-confirmer-mot-de-passe">Description : </span>Champ
                            permettant de confirmer que le mot de passe saisi est
                            correct.
                        </li>
                    </ul>
                </li>
                <li class="mb-3">
                    <strong id="champ-nom-complet">Nom complet</strong>(Obligatoire).
                    <ul class="mt-2 ml-4" style="list-style-type: circle">
                        <li>
                            <span class="text-md" id="description-nom-complet">Description : </span>Nom complet de
                            l’utilisateur (prénom et nom).
                        </li>
                        <li>
                            <span class="text-md" id="format-nom-complet">Format attendu : </span>Texte libre.
                        </li>
                    </ul>
                </li>
                <li class="mb-3">
                    <strong id="champ-email">E-mail</strong>(Obligatoire).
                    <ul class="mt-2 ml-4" style="list-style-type: circle">
                        <li>
                            <span class="text-md" id="description-email">Description : </span>Adresse e-mail unique
                            associée à l’utilisateur.
                        </li>
                        <li>
                            <span class="text-md" id="format-email">Format attendu : </span>Adresse e-mail valide
                            (exemple : utilisateur@domaine.com).
                        </li>
                    </ul>
                </li>
                <li class="mb-3">
                    <strong id="champ-role-utilisateur">Rôle de l'utilisateur</strong>(Obligatoire).
                    <ul class="mt-2 ml-4" style="list-style-type: circle">
                        <li>
                            <span class="text-md" id="description-role-utilisateur">Description : </span>Sélectionnez le
                            rôle ou les permissions attribuées à
                            l’utilisateur dans le système (exemple : administrateur,
                            utilisateur standard).
                        </li>
                    </ul>
                </li>
                <li class="mb-3">
                    <strong id="champ-groupe-utilisateur">Affecter à un groupe</strong>(Optionnel).
                    <ul class="mt-2 ml-4" style="list-style-type: circle">
                        <li>
                            <span class="text-md" id="description-groupe-utilisateur">Description : </span>Associez
                            l’utilisateur à un groupe spécifique pour la gestion
                            des permissions ou des accès
                        </li>
                    </ul>
                </li>
                <li class="mb-3">
                    <strong id="champ-desactiver-utilisateur">Désactiver l’utilisateur</strong>(Optionnel).
                    <ul class="mt-2 ml-4" style="list-style-type: circle">
                        <li>
                            <span class="text-md" id="description-desactiver-utilisateur">Description : </span>Cochez
                            cette case si vous souhaitez créer l’utilisateur mais le
                            garder inactif.
                        </li>
                    </ul>
                </li>
            </ul>
        </section>

        <!--  -->
        <div class="flex items-center mt-7" id="gestion-des-groups">
            <span class="mdi mdi-file-document mr-2" style="font-size: 24px; color: #ffcb26"></span>
            <span style="font-weight: 400; font-size: 20px">Gestion des groupes</span>
        </div>

        <div class="flex gap-2 py-2">
            <hr class="w-full h-[0.1rem] bg-[#ffcc19] border-1 rounded" />
        </div>

        <h3 class="font-weight-bold py-3" style="font-size: 20px" id="introduction-group">
            <span> 1. Introduction</span>
        </h3>

        <p class=" mb-3" id="intro-group-description">
            La création de groupes simplifie la gestion des utilisateurs en
            centralisant les permissions et rôles. Ce guide décrit les étapes et
            champs nécessaires pour créer un groupe.
        </p>

        <h3 class="font-weight-bold py-3" style="font-size: 20px" id="etapes-pour-creation-group">
            <span> 2. Étapes pour créer un group </span>
        </h3>

        <h3 class="text-md font-semibold" id="accéder-interface-group">
            <span> 2.1 Accéder à l’interface utilisateur :</span>
        </h3>

        <p class=" py-3" id="access-group-interface">
            Rendez-vous dans la section de gestion des groupes.
        </p>

        <div class="mb-3 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/system/gestion_des_utilisateurs.png" style="width: 100%"
                id="gestion-utilisateurs-image" />
        </div>

        <h3 class="text-md font-semibold" id="cliquer-ajouter-group">
            <span> 2.2 Cliquer sur "Ajouter un groupe" :</span>
        </h3>
        <p class=" py-3" id="ouvrir-formulaire-group">
            Ouvrez le formulaire de création d’un nouveau groupe.
        </p>

        <h3 class="text-md font-semibold" id="remplir-champs-group">
            <span> 2.3 Remplir les champs requis :</span>
        </h3>
        <p class=" py-3" id="completer-champs-group">
            Complétez les informations demandées pour le groupe.
        </p>

        <div class="mb-3 mt-3 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/system/formulaire_group.png" style="width: 100%"
                id="formulaire-group-image" />
        </div>

        <h3 class="text-md font-semibold mt-3" id="sauvegarder-group">
            <span> 2.4 Sauvegarder le groupe :</span>
        </h3>
        <p class=" py-3" id="sauvegarder-button-group">
            Cliquez sur le bouton "Créer" pour finaliser la création.
        </p>

        <h3 class="font-weight-bold pb-1" style="font-size: 20px" id="description-champs-group">
            <span> 3. Description des champs d’entrée </span>
        </h3>

        <section id="champs-group">
            <ul class="list-disc ml-10 mt-2">
                <li class="mb-3" id="nom-groupe">
                    <strong>Nom de groupe</strong>(Obligatoire).
                    <ul class="mt-2 ml-4" style="list-style-type: circle">
                        <li>
                            <span class="text-md">Description : </span>Le nom unique du
                            groupe permettant de l’identifier.
                        </li>
                    </ul>
                </li>
                <li class="mb-3" id="description-groupe">
                    <strong>Description</strong>(Obligatoire).
                    <ul class="mt-2 ml-4" style="list-style-type: circle">
                        <li>
                            <span class="text-md">Description : </span>Texte libre pour
                            décrire la fonction du groupe.
                        </li>
                    </ul>
                </li>
            </ul>
        </section>

        <div class="flex items-center mt-7" id="gestion-des-roles">
            <span class="mdi mdi-file-document mr-2" style="font-size: 24px; color: #ffcb26"></span>
            <span style="font-weight: 400; font-size: 20px">Gestion des rôles</span>
        </div>

        <div class="flex gap-2 py-2">
            <hr class="w-full h-[0.1rem] bg-[#ffcc19] border-1 rounded" />
        </div>

        <h3 class="font-weight-bold py-3" style="font-size: 20px" id="introduction-role">
            <span> 1. Introduction</span>
        </h3>

        <p class=" mb-3" id="intro-role-description">
            La création de rôles définit des privilèges spécifiques pour gérer les
            autorisations des utilisateurs. Ce guide explique les étapes et les
            champs du formulaire pour créer un rôle.
        </p>

        <h3 class="font-weight-bold py-3" style="font-size: 20px" id="etapes-ajouter-role">
            <span> 2. Étapes pour ajouter un rôle </span>
        </h3>

        <h3 class="text-md font-semibold" id="accéder-interface-role">
            <span> 2.1 Accéder à l’interface utilisateur :</span>
        </h3>
        <p class=" py-3" id="access-role-interface">
            Naviguez vers la section des rôles dans l’application.
        </p>

        <div class="mb-3 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/system/gestion_des_utilisateurs.png" style="width: 100%"
                id="gestion-role-image" />
        </div>

        <h3 class="text-md font-semibold" id="cliquer-ajouter-role">
            <span> 2.2 Cliquer sur "Ajouter un rôle" :</span>
        </h3>
        <p class=" py-3" id="ouvrir-formulaire-role">
            Ouvrez le formulaire dédié.
        </p>

        <h3 class="text-md font-semibold" id="completer-champs-role">
            <span> 2.3 Compléter les champs : </span>
        </h3>
        <p class=" py-3" id="completer-champs-role-description">
            Saisissez les informations nécessaires pour définir le rôle.
        </p>

        <div class="mb-5 mt-3 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/system/ajouter_role.png" style="width: 100%"
                id="formulaire-role-image" />
        </div>

        <h3 class="text-md font-semibold" id="valider-creation-role">
            <span> 2.4 Valider la création : </span>
        </h3>
        <p class=" py-3" id="sauvegarder-role">
            Cliquez sur "Créer" pour enregistrer le rôle.
        </p>

        <h3 class="font-weight-bold pb-1" style="font-size: 20px" id="description-champs-role">
            <span> 3. Description des champs d’entrée </span>
        </h3>

        <section id="champs-role">
            <ul class="list-disc ml-10 mt-2">
                <li class="mb-3" id="nom-role">
                    <strong>Nom</strong>(Obligatoire).
                    <ul class="mt-2 ml-4" style="list-style-type: circle">
                        <li>
                            <span class="text-md">Description : </span>Le nom unique du
                            rôle.
                        </li>
                        <li>
                            <span class="text-md">Format attendu : </span> Texte simple,
                            représentant clairement le rôle (ex. : Administrateur,
                            Modérateur)
                        </li>
                    </ul>
                </li>
                <li class="mb-3" id="privileges-role">
                    <strong>Privilèges</strong>(Obligatoire).
                    <ul class="mt-2 ml-4" style="list-style-type: circle">
                        <li>
                            <span class="text-md">Description : </span>Une liste déroulante
                            pour sélectionner les autorisations spécifiques attribuées au
                            rôle.
                        </li>
                        <li>
                            <span class="text-md">Exemples : </span> Accès aux rapports,
                            gestion des utilisateurs, modification des paramètres.
                        </li>
                    </ul>
                </li>
            </ul>
        </section>
    </div>
</template>