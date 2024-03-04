<template>
    <v-app id="inspire">
        <base-layout title="Monitoring">
            <template #content>
                <div>testMo</div>

            </template>
        </base-layout>
    </v-app>
</template>

<script>
import BaseLayout from "@/layouts/layout.vue";

export default {
    components: {
        BaseLayout
    },
    mounted() {
        this.initializeWebSocket()
    },
    data() {
        return {
            socket: null
        }
    },



    methods: {
        initializeWebSocket() {
            this.socket = new WebSocket(
                "ws://" + window.location.host + "/ws/vpnmonitoring/"
            );

            this.socket.onopen = () => {
                console.log("WebSocket connection opened.");
                this.socket.send(JSON.stringify({
                    'id': 1
                }));
            };
            this.socket.onmessage = (event) => {
                // console.log('event', event.data)
                const data = JSON.parse(event.data);
                 console.log("aaaaaaaaaaaaaa",data)


            };

        }

    }
}
</script>