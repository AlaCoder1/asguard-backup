import axios from 'axios';

/**
 *
 * Login with username & password.
 *
 * @param  params
 * @returns
 */
 export async function loginAndGetToken(params) {
    return axios.post('/auth/authentification_JWT', params);
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