<template>
    <div class="container">
        <h3 class="font-weight-bold  py-3" style="font-size: 20px">
            <span id="titre-interface">1. Interface de gestion des certificats</span>
        </h3>

        <div class="mb-7 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/certif/image.png" style="width: 100%" />

        </div>

        <p class=" py-3">
            Cette capture d'écran représente une
            <span id="motcle-interface">interface</span> de gestion des
            <span id="motcle-certificats">certificats</span>, divisée en trois
            <span id="motcle-sections">sections</span> principales :
        </p>

        <h3 class="font-weight-bold  pb-3" style="font-size: 20px">
            <span id="titre-autorites">Autorités de certification</span>
        </h3>

        <section>
            <ul class="list-disc ml-7">
                <li class="mb-3">
                    <span id="motcle-liste">Liste</span> des
                    <span id="motcle-autorite">autorités</span> de certification
                    existantes.
                </li>
                <li class="mb-3">
                    <span id="motcle-details">Affichage des détails</span> de chaque
                    <span id="motcle-autorite">autorité</span>, notamment son
                    <span id="motcle-nom">nom</span>, le nombre de
                    <span id="motcle-certificats2">certificats</span> associés et les
                    informations de l'<span id="motcle-identite">identité</span>
                    (adresse e-mail, <span id="motcle-organisation">organisation</span>,
                    <span id="motcle-localisation">localisation</span>, durée de
                    validité, etc.).
                </li>
                <li class="mb-3">
                    Possibilité d'effectuer des
                    <span id="motcle-actions">actions</span> sur chaque
                    <span id="motcle-autorite">autorité</span> via des
                    <span id="motcle-icones">icônes</span> (visualisation, modification,
                    suppression).
                </li>
                <li class="mb-3">
                    Un bouton "<span id="motcle-ajouter">Ajouter autorités</span>"
                    permet d'ajouter une nouvelle
                    <span id="motcle-autorite">autorité</span> de certification.
                </li>
            </ul>
        </section>

        <!--  -->
        <h3 class="font-weight-bold  pb-3" style="font-size: 20px">
            <span id="titre-certificats">Certificats</span>
        </h3>

        <section>
            <ul class="list-disc ml-7">
                <li class="mb-3">
                    <span id="motcle-liste">Liste</span> des
                    <span id="motcle-certificats">certificats</span> créés avec leur
                    <span id="motcle-nom">nom</span> et leur
                    <span id="motcle-identite">identité</span> distinguée.
                </li>
                <li class="mb-3">
                    Chaque
                    <span id="motcle-certificat">certificat</span> affiche des
                    <span id="motcle-infos">informations détaillées</span> comme l'
                    <span id="motcle-email">adresse e-mail</span>, le
                    <span id="motcle-cn">nom commun (CN)</span>, la
                    <span id="motcle-localisation">localisation</span> et la
                    <span id="motcle-validite">période de validité</span>.
                </li>
                <li class="mb-3">
                    Des
                    <span id="motcle-icones">icônes</span> permettent d'effectuer des
                    <span id="motcle-actions">actions</span> sur chaque
                    <span id="motcle-certificat2">certificat</span> (
                    <span id="motcle-visualisation">visualisation</span>,
                    <span id="motcle-modification">modification</span>,
                    <span id="motcle-suppression">suppression</span>, etc.).
                </li>
                <li class="mb-3">
                    Un bouton "<span id="motcle-ajouter">Ajouter certificats</span>"
                    permet d'ajouter un
                    <span id="motcle-nouveau-certificat">nouveau certificat</span>.
                </li>
            </ul>
        </section>

        <h3 class="font-weight-bold  pb-3" style="font-size: 20px">
            <span id="titre-liste-revocation">Liste de révocation par autorité</span>
        </h3>

        <section>
            <ul class="list-disc ml-7">
                <li class="mb-3">
                    Affichage des
                    <span id="motcle-certificats-revoques">certificats révoqués</span>
                    pour chaque
                    <span id="motcle-autorite-certification">autorité de certification</span>.
                </li>
                <li class="mb-3">
                    Présente la
                    <span id="motcle-liste-certificats">liste des certificats</span> qui
                    ne sont plus <span id="motcle-plus-valides">valides</span> et
                    <span id="motcle-empeches">empêchés d’utilisation</span>.
                </li>
                <li class="mb-3">
                    Possibilité de
                    <span id="motcle-consulter">consulter</span> les
                    <span id="motcle-certificats-revoques2">certificats révoqués</span>
                    associés à une
                    <span id="motcle-autorite-specifique">autorité spécifique</span>.
                </li>
            </ul>
        </section>

        <h3 class="font-weight-bold  py-3" style="font-size: 20px">
            <span id="etapes-creation-certificat-autorite">2. Étapes pour créer un certificat d'autorité</span>
        </h3>

        <!--  -->
        <p class="mb-3 ">
            Un
            <span id="motcle-certificat-authorite">certificat d'autorité</span>
            (<span id="motcle-ca">CA</span>) est utilisé pour
            <span id="motcle-signer">signer</span> et
            <span id="motcle-valider">valider</span> d'autres
            <span id="motcle-certificats">certificats</span>. Suivez ces
            <span id="motcle-etapes">étapes</span> pour
            <span id="motcle-creer">créer</span> un
            <span id="motcle-certificat-authorite">certificat d'autorité</span>.
        </p>

        <section>
            <ul class="list-disc ml-7">
                <li class="mb-5">
                    <strong id="motcle-acceder-autorites">
                        Accéder à la section "Autorités" :
                    </strong>
                    Dans l'interface de gestion des
                    <span id="motcle-certificats2">certificats</span>, localisez et
                    accédez à la section <span id="motcle-autorites">"Autorités"</span>.
                </li>

                <div class="mb-6 d-flex justify-center align-center">
                    <img class="rounded-md" src="@/assets/images/certif/image3.png" style="width: 100%"
                        id="motcle-image3" />

                </div>

                <li class="mb-2">
                    <strong id="motcle-ajouter-autorite">
                        Ajouter une nouvelle autorité :
                    </strong>
                    Cliquez sur le bouton
                    <span id="motcle-ajouter-bouton">"Ajouter autorités"</span>.
                </li>

                <li class="mb-2">
                    <strong id="motcle-fournir-infos">
                        Fournir les informations nécessaires :
                    </strong>
                    <ul class="mt-2 ml-4" style="list-style-type: circle">
                        <li>
                            <span class="text-md text-gray-500" id="motcle-nom-label">Nom :</span>
                            Entrez le <span id="motcle-nom">nom</span> de l'autorité de
                            certification.
                        </li>
                        <li>
                            <span class="text-md text-gray-500" id="motcle-infos-certificat-label">
                                Informations du certificat :
                            </span>
                            Renseignez l'<span id="motcle-email">adresse e-mail</span>, le
                            <span id="motcle-organisation">nom de l'organisation (O)</span>,
                            la <span id="motcle-localisation">localisation (L)</span>,
                            l'<span id="motcle-etat">état (ST)</span>, et le
                            <span id="motcle-pays">pays (C)</span>.
                        </li>
                        <li>
                            <span class="text-md text-gray-500" id="motcle-duree-validite-label">
                                Durée de validité :
                            </span>
                            Spécifiez la
                            <span id="motcle-duree-validite">durée</span> pendant laquelle
                            le
                            <span id="motcle-certificat-authorite">certificat d'autorité</span>
                            sera valide.
                        </li>
                    </ul>
                </li>

                <li class="mb-2">
                    <strong id="motcle-generer-certificat">
                        Générer le certificat d'autorité :
                    </strong>
                    Vérifiez les
                    <span id="motcle-infos-fournies">informations fournies</span> et
                    confirmez la <span id="motcle-creation">création</span>. L'autorité
                    apparaîtra alors dans la liste des
                    <span id="motcle-autorites2">"Autorités"</span>.
                </li>
            </ul>
        </section>

        <h3 class="font-weight-bold  py-3" style="font-size: 20px">
            <span id="motcle-formulaire-importation">
                Formulaire d'importation d'une autorité de certification existante :
            </span>
        </h3>

        <!--  -->

        <div class="py-5 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/certif/image4.png" style="width: 100%" />

        </div>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                <strong>
                    <span id="motcle-nom-certificat">Nom du certificat :</span>
                </strong>
                Nom descriptif pour l'autorité.
            </li>
            <li class="mb-2">
                <strong>
                    <span id="motcle-methode">Méthode :</span>
                </strong>
                Sélectionner Importer une autorité de certification existante.
            </li>
            <li class="mb-2">
                <strong>
                    <span id="motcle-donnees-certificat">Données du certificat :</span>
                </strong>
                Collez le contenu du clé public.
            </li>
            <li class="mb-2">
                <strong>
                    <span id="motcle-certificat-cle-privee">Certificat de clé privée :</span>
                </strong>
                Collez le contenu du clé privé.
            </li>
            <li class="mb-2">
                <strong>
                    <span id="motcle-boutons">Boutons :</span>
                </strong>
                <ul class="mt-2 ml-4" style="list-style-type: circle">
                    <li>
                        <span class="text-md text-gray-500" id="motcle-creer">Créer :</span>
                        Valide l'importation.
                    </li>
                    <li>
                        <span class="text-md text-gray-500" id="motcle-fermer">Fermer :</span>
                        Annule l'importation.
                    </li>
                </ul>
            </li>
        </ul>

        <h3 class="font-weight-bold  py-3" style="font-size: 20px">
            <span id="titre-creation-certificat-utilisateur">3. Création d'un certificat utilisateur</span>
        </h3>

        <p class=" pb-3">
            Les <span id="motcle-certificats-usage">certificats</span> sont utilisés
            pour diverses fonctions, telles que sécuriser une
            <span id="motcle-communication-vpn">communication VPN</span> ou
            identifier des <span id="motcle-utilisateurs">utilisateurs</span> ou
            <span id="motcle-serveurs">serveurs</span>.
        </p>

        <!--  -->
        <div class="py-6 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/certif/image5.png" style="width: 100%" />

        </div>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                <strong>
                    <span id="motcle-acceder">Accéder</span> à la
                    <span id="motcle-section">section</span> "<span id="motcle-certificats">Certificats</span>" :
                </strong>
                Localisez la <span id="motcle-section-2">section</span> "<span
                    id="motcle-certificats-2">Certificats</span>" dans l'interface.
            </li>
            <li class="mb-2">
                <strong>
                    <span id="motcle-ajouter-nouveau">Ajouter</span> un nouveau
                    <span id="motcle-certificat">certificat</span> :
                </strong>
                Cliquez sur le bouton "<span id="motcle-ajouter-certificats">Ajouter certificats</span>".
            </li>
            <li class="mb-2">
                <strong>
                    <span id="motcle-selectionner">Sélectionner</span> une
                    <span id="motcle-autorite-existante">autorité de certification existante</span>
                    :
                </strong>
                Choisissez l'autorité (par exemple :
                <span id="motcle-numeryx_auth">numeryx_auth</span>) qui signera le
                <span id="motcle-certificat">certificat</span>.
            </li>
            <li class="mb-2">
                <strong>
                    <span id="motcle-fournir">Fournir</span> les
                    <span id="motcle-infos-necessaires">informations nécessaires</span>
                    :
                </strong>
                <ul class="mt-2 ml-4" style="list-style-type: circle">
                    <li>
                        <span class="text-md text-gray-500" id="motcle-nom-label">Nom :</span>
                        Nom du certificat (ex. :
                        <span id="motcle-vpn_server_test">VPN_server_test</span>).
                    </li>
                    <li>
                        <span class="text-md text-gray-500" id="motcle-infos-certificat-label">
                            Informations du certificat :
                        </span>
                        Adresse e-mail, nom du serveur ou client (<span id="motcle-cn">CN</span>), <span
                            id="motcle-organisation">organisation</span>.
                    </li>
                    <li>
                        <span class="text-md text-gray-500" id="motcle-duree-validite-label">Durée de validité :</span>
                        Période de validité du certificat.
                    </li>
                </ul>
            </li>
            <li class="mb-2">
                <strong>
                    <span id="motcle-valider">Valider</span> la
                    <span id="motcle-creation">création</span> :
                </strong>
                Après avoir rempli les informations, validez la création du
                <span id="motcle-certificat">certificat</span>. Il apparaîtra dans
                la <span id="motcle-liste-certificats">liste des certificats</span>.
            </li>
        </ul>
        <!--  -->
        <h3 class="font-weight-bold  py-3" style="font-size: 20px">
            <span id="titre-importation">Importation</span> d'un
            <span id="motcle-certificat">certificat</span>
            <span id="motcle-utilisateur">utilisateur</span> :
        </h3>

        <p class=" pb-3">
            Cette <span id="motcle-section">section</span>
            <span id="motcle-decrit">décrit</span> comment
            <span id="motcle-importer">importer</span> un
            <span id="motcle-certificat2">certificat</span>
            <span id="motcle-utilisateur2">utilisateur</span> existant.
        </p>
        <!--  -->

        <div class="py-6 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/certif/image6.png" style="width: 100%" />

        </div>

        <h3 class="font-weight-bold  py-3" style="font-size: 20px" id="formulaire-import-certificat">
            <span>Formulaire pour importer un certificat utilisateur :</span>
        </h3>

        <ul class="list-disc ml-7" id="list-import-certificat">
            <li class="mb-2" id="nom-certificat">
                <strong>Nom du certificat (obligatoire) : </strong>Champ où
                l'utilisateur doit saisir le nom du certificat.
            </li>
            <li class="mb-2" id="methode-import">
                <strong>Méthode : </strong>Une liste déroulante avec l'option
                sélectionnée "Importer un certificat existant".
            </li>
            <li class="mb-2" id="certificat-existant">
                <strong>Certificat existant : </strong>
                <ul class="mt-2 ml-4" style="list-style-type: circle" id="certificat-existant-options">
                    <li id="donnees-certificat">
                        <span class="text-md text-gray-500">Données du certificat (obligatoire) :
                        </span>
                        Zone pour coller les données PEM ou DER du certificat.
                    </li>
                    <li id="cle-privee">
                        <span class="text-md text-gray-500">Certificat de clé privée (facultatif) :
                        </span>
                        Option pour ajouter une clé privée si nécessaire.
                    </li>
                    <li id="num-serial">
                        <span class="text-md text-gray-500">Certificat de numéro de série :
                        </span>
                        Option pour inclure un certificat avec un numéro de série
                        spécifique.
                    </li>
                </ul>
            </li>

            <li class="mb-2" id="actions-disponibles">
                <strong>Actions disponibles : </strong>
                <ul class="mt-2 ml-4" style="list-style-type: circle" id="actions-list">
                    <li id="action-creer">
                        <span class="text-md text-gray-500">Créer : </span>Bouton pour
                        importer le certificat.
                    </li>
                    <li id="action-fermer">
                        <span class="text-md text-gray-500">Fermer : </span>Bouton pour
                        annuler l'opération.
                    </li>
                </ul>
            </li>
        </ul>

        <h3 class="font-weight-bold  py-3" style="font-size: 20px" id="revocation-certificats">
            <span> 4. Révocation des certificats par autorité</span>
        </h3>

        <p class=" pb-3" id="revocation-definition">
            La révocation d'un certificat invalide celui-ci avant sa date
            d'expiration, nécessaire en cas de compromission ou de modification des
            conditions d'utilisation.
        </p>

        <h3 class="font-weight-bold  py-3" style="font-size: 20px" id="etapes-revocation">
            <span> Étapes pour révoquer un certificat :</span>
        </h3>
        <div class="pb-5 d-flex justify-center align-center" id="image-revocation">
            <img class="rounded-md" src="@/assets/images/certif/image7.png" style="width: 100%"
                id="image-revocation-step" />

        </div>

        <ul class="list-disc ml-7" id="steps-revocation">
            <li class="mb-2" id="step-acceder-liste-revocation">
                <strong>Accéder à la section "Liste de révocation par autorité" :
                </strong>
                Localisez cette section dans l'interface.
            </li>
            <li class="mb-2" id="step-selectionner-autorite">
                <strong>Sélectionner l'autorité de certification : </strong>
                Choisissez l'autorité ayant signé le certificat à révoquer.
            </li>
            <li class="mb-2" id="step-revoquer-certificat">
                <strong>Révoquer le certificat : </strong>
                Cliquez sur l'icône en face du certificat et confirmez la révocation.
            </li>
        </ul>

        <h3 class="font-weight-bold  py-3" style="font-size: 20px" id="actions-supplementaires">
            <span> Actions supplémentaires :</span>
        </h3>
        <ul class="list-disc ml-7" id="additional-actions">
            <li class="mb-2" id="action-consulter-details">
                <strong>Consultation des détails : </strong>
                Cliquez sur l'icône en forme d'œil pour consulter les informations du
                certificat.
            </li>
            <li class="mb-2" id="action-telechargement-suppression">
                <strong>Téléchargement ou suppression :</strong>
                Utilisez les icônes associées pour télécharger ou supprimer le
                certificat.
            </li>
        </ul>

        <h3 class="font-weight-bold  py-3" style="font-size: 20px" id="annuler-revocation">
            <span> 5. Annuler la révocation d’un certificat</span>
        </h3>
        <h3 class="font-bold text-sm pb-3" style="font-size: 20px" id="consultation-certificats-revoques">
            <span> Consulter la liste des certificats révoqués</span>
        </h3>

        <ul class="list-disc ml-7" id="consultation-revocation-list">
            <li class="mb-2" id="consultation-liste-revocation">
                Consultez la section "Liste de revocation par autorité".
            </li>
            <li class="mb-2" id="consultation-selectionner-autorite">
                Sélectionnez l'autorité et consultez les certificats révoqués avec
                leurs détails.
            </li>
        </ul>

        <h3 class="font-bold text-sm pb-3" style="font-size: 20px" id="annuler-revocation-certificat">
            <span> Annuler la révocation d’un certificat</span>
        </h3>

        <div class="pb-3 d-flex justify-center align-center" id="image-annuler-revocation">
            <img class="rounded-md" src="@/assets/images/certif/image8.png" style="width: 100%"
                id="image-annuler-revocation-step" />

        </div>

        <ul class="list-disc ml-7 mt-3" id="steps-annuler-revocation">
            <li class="mb-2" id="step-consulter-certificats-revoques">
                Consultez la liste des certificats révoqués.
            </li>
            <li class="mb-2" id="step-selectionner-certificat-annuler">
                Sélectionnez un certificat et annulez la révocation via l'icône du
                cadenas.
            </li>
            <li class="mb-2" id="step-confirmer-annulation">Confirmez l’action.</li>
        </ul>

        <!--  -->
    </div>
</template>