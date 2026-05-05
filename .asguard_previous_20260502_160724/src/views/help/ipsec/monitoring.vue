<template>
    <div>
        <h3 class="font-weight-bold text-1xl py-2" style="font-size: 20px">
            <span id="Monitoring">1. Monitoring des Tunnels Actifs</span>
        </h3>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 17px">
            <span>1.1 Vue d’Ensemble</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">Accédez à la section <strong>Monitoring</strong>.</li>
            <li class="mb-2">Consultez les informations en temps réel :</li>

            <ul class="mt-2 ml-4 mb-2" style="list-style-type: circle">
                <li class="mb-2">Tunnels actifs</li>
                <li class="mb-2">Durée d’activité</li>
                <li class="mb-2">Adresse IP distante</li>
            </ul>
        </ul>

        <h3 class="font-semibold text-sm pb-2" style="font-size: 17px">
            <span id="Statistiques">1.2 Statistiques et Graphiques des Tunnels</span>
        </h3>

        <ul class="list-disc ml-7">
            <li class="mb-2">
                Dans cette section, vous pouvez surveiller les
                <span id="indicateurs">indicateurs de performance clés</span> des tunnels actifs :
            </li>
            <li class="mb-2">
                <strong>Disponibilité : </strong> Affiche le pourcentage de
                disponibilité des tunnels (par ex. 100 %).
            </li>
            <li class="mb-2">
                <strong>Perte de paquets : </strong> Permet d’identifier les pertes
                éventuelles (par ex. 0 %).
            </li>
            <li class="mb-4">
                <strong>Sessions actives : </strong> Nombre total de sessions en
                cours.
            </li>
            <li class="mb-2">Des graphiques détaillés montrent :</li>
            <li class="mb-2">
                <strong>Disponibilité : </strong> Sur une période donnée.
            </li>
            <li class="mb-2">
                <strong id="Trafic-total-VPN">Trafic total VPN : </strong> Volume des données échangées.
            </li>
            <li class="mb-2">
                <strong>Paquets envoyés</strong> et <strong>paquets reçus</strong>.
            </li>
        </ul>

        <div class="mb-7 mt-4 flex d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/ipsec/ipsec5.png" style="width:100%" />
        </div>
        <div class="mb-7 mt-4 flex d-flex justify-center align-center">
            <img class="rounded-md" src="@/assets/images/ipsec/ipsec6.png" style="width:100%" />
        </div>

    </div>
</template>