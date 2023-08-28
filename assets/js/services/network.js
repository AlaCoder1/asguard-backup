import axios from 'axios';

export async function createNetwork(params) {
    return axios.put('network/conf/1', params);
}
