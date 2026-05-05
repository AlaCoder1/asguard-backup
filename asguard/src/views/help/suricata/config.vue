<template>
    <div>
        <p class="py-2">
            Le service <span id="ips-ids">IPS/IDS</span> est conçu pour
            <span id="surveillance-trafic">surveiller le trafic réseau</span>,
            <span id="détection-intrusions">détecter les intrusions</span> et
            <span id="protection-attaques">protéger contre les attaques malveillantes</span> :
        </p>

        <p class="py-2">
            <strong id="ids-intrusion-detection-system">IDS (Intrusion Detection System) :</strong>
            Surveille le <span id="trafic-reseau">trafic réseau</span> à la recherche d'
            <span id="activités-suspectes">activités suspectes</span> ou
            <span id="activités-malveillantes">malveillantes</span> et génère des
            <span id="alertes">alertes</span>.
        </p>
        <p class="py-2">
            <strong id="ips-intrusion-prevention-system">IPS (Intrusion Prevention System) :</strong>
            Non seulement détecte, mais empêche également les
            <span id="menaces">menaces</span> en bloquant le
            <span id="trafic-suspect">trafic suspect</span> en
            <span id="temps-réel">temps réel</span>.
        </p>

        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span id="configuration-service">Configuration du service</span>
        </h3>

        <p class="pb-2">
            Cette section de l'interface permet de configurer les fonctionnalités du
            service :
        </p>

        <div class="mb-4 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/ips-ids/image.png" style="width: 100%" />
        </div>

        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span id="parametres-generaux">Paramètres généraux</span>
        </h3>

        <ul class="list-disc ml-7">
            <li id="activer-ids" class="mb-2">
                Activer le système IDS : Permet d'activer la détection des intrusions sur le réseau.
            </li>
            <li id="activer-ips" class="mb-2">
                Activer l'IPS : Active la prévention des intrusions pour bloquer activement les menaces détectées.
            </li>
            <li id="mode-promiscuous" class="mb-2">
                Activer le mode Promiscuous : Capture tout le trafic réseau, même celui qui n'est pas destiné au
                système, pour
                une analyse complète.
            </li>
            <li id="alertes-syslog" class="mb-2">
                Activer les alertes syslog : Envoie les alertes générées par IDS/IPS à un serveur Syslog pour
                centralisation
                et analyse.
            </li>
            <li id="sortie-syslog-eve" class="mb-2">
                Activer la sortie syslog d’eve : Active la sortie des données détaillées au format JSON (eve-log).
            </li>
        </ul>

        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span id="options-avancées">Options avancées</span>
        </h3>

        <ul class="list-disc ml-7">
            <li id="correspondance-motifs" class="mb-2">
                Correspondance de motifs : Configure la méthode de détection des motifs dans le trafic réseau. Par
                exemple,
                Aho-Corasick est un algorithme rapide pour la détection.
            </li>
            <li id="profil-détection" class="mb-2">
                Profil de détection : Permet de sélectionner un niveau de sensibilité pour la détection (faible, moyen
                ou
                élevé)
            </li>
        </ul>


        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span id="configuration-interfaces">Configuration des interfaces</span>
        </h3>

        <div class="mb-4 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/ips-ids/image2.png" style="width: 100%" />
        </div>

        <p class="py-2">
            L’interface utilisateur liste les interfaces réseau disponibles et leurs
            paramètres associés. Lorsque vous cliquez sur le bouton "Ajouter" dans
            l'interface (coin supérieur droit du tableau), une fenêtre apparaît pour
            configurer une nouvelle règle ou un nouveau flux de capture réseau.
        </p>

        <div class="mb-4 d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/services/ips-ids/image3.png" />
        </div>
        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span>Champs disponibles dans l'ajout :</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                <strong id="interface-obligatoire">Interface (Obligatoire) :</strong>
                Sélectionnez l'interface réseau à surveiller (exemple : WAN pour le trafic entrant ou LAN pour le trafic
                interne).
            </li>
            <li class="mb-2">
                <strong id="fil-optionnel">Fil (Optionnel) :</strong>
                Spécifie le filtre appliqué sur le trafic réseau. Par défaut, il est défini sur auto.
            </li>
            <li class="mb-2">
                <strong id="defrag-obligatoire">Defrag (Obligatoire) :</strong>
                Active ou désactive la défragmentation des paquets réseau pour permettre une meilleure analyse des flux
                fragmentés.
            </li>
            <li class="mb-2">
                <strong id="id-cluster-obligatoire">ID de cluster (Obligatoire) :</strong>
                Un identifiant unique pour la configuration. Utilisé pour distinguer et gérer différentes règles ou
                instances.
            </li>
            <li class="mb-2">
                <strong id="type-cluster">Type de cluster :</strong>
                Définit la méthode de gestion des flux réseau, comme cluster_flow pour regrouper les paquets par flux.
            </li>
            <li class="mb-2">
                <strong id="mode-copie">Mode Copie :</strong>
                Indique la manière dont le trafic est copié pour analyse. Par exemple :
            </li>
            <ul class="my-2 ml-4" style="list-style-type: circle">
                <li><strong>tap : </strong>Le trafic est copié sans modification.</li>
                <li>
                    <strong>mirror : </strong>Une copie exacte du trafic est envoyée à une interface.
                </li>
            </ul>
            <li class="mb-2">
                <strong id="copie-iface-obligatoire">Copie Iface (Obligatoire) :</strong>
                L’interface cible où les paquets copiés seront envoyés (utile pour des analyses externes ou
                supplémentaires).
            </li>
            <li class="mb-2">
                <strong id="taille-buffer-obligatoire">Taille du buffer (Obligatoire) :</strong>
                Spécifie la taille du tampon utilisé pour stocker temporairement les paquets capturés. Une taille
                adaptée
                évite la perte de paquets.
            </li>
            <li class="mb-2">
                <strong id="utiliser-mmap">Utiliser Mmap :</strong>
                Active ou désactive l'utilisation de la mémoire partagée (mmap) pour optimiser les performances de
                capture et
                de traitement des paquets.
            </li>
        </ul>


        <h3 class="font-weight-bold  text-1xl py-2" style="font-size: 20px">
            <span>Actions :</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                <strong>Créer :</strong>
                Enregistre la configuration et l'ajoute à la liste des règles dans
                l'interface principale.
            </li>
            <li class="mb-2">
                <strong>Fermer :</strong>
                Annule la configuration et retourne à la vue principale sans appliquer
                de changements.
            </li>
        </ul>
    </div>
</template>