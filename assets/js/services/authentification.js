import axios from 'axios';

/**
 *
 * Login with username & password.
 *
 * @param  params
 * @returns
 */
 export async function login(params) {
    return axios.post('/auth/authentification', params);
}

/**
 * update.
 * @returns
 
export function updateTest(id, params) {
    const config = {
        headers: {
            'Content-Type': 'application/ld+json',
            Accept: 'application/ld+json',
        },
    };
    return axios.put(`/test/${id}`, params, config);
}*/