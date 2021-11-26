import Vue from 'vue'
import Vuex from 'vuex'
import BoardsModule from './modules/boardsList';
import BoardModule from './modules/board';
import appConfig from '@/config.js'
import ERRORS from '@/consts/standardErrors'

Vue.use(Vuex);

export const handleStandardRequestResponses = (payload) => {
    let error = payload;
    if (typeof(error.response) === 'undefined'){
        throw {
            type: ERRORS.NETWORK_ERROR,
            errors: []
        };
    }

    switch(error.response.status){
        case 401:
            throw {
                type: ERRORS.UNAUTHORIZED,
                errors: []
            };
        case 404:
            throw {
                type: ERRORS.NOT_FOUND,
                errors: []
            };
        case 403:
            throw {
                type: ERRORS.FORBIDDEN,
                errors: []
            };
        case 429:
            throw {
                type: ERRORS.THROTTLING,
                errors: []
            };
        case 500:
            throw {
                type: ERRORS.INTERNAL_SERVER_ERROR,
                errors: []
            }
    }
}

const store = new Vuex.Store({
    modules: {
        boardsList: BoardsModule,
        board: BoardModule
    },

    state: {
        accessToken: null,
        refreshToken: null,
        userPayload: null,
        apiUrl: appConfig.apiUrl
    },

    mutations: {
        /**
         * Assigns new access and refresh tokens
         * @param {*} state Provided by Vuex
         * @param {Object} payload  Required format of the object: 
         * {
         *      accessToken: {String},
         *      refreshToken: {String}
         * }
         */
        setTokens (state, payload) {
            state.accessToken = payload.accessToken;
            state.refreshToken = payload.refreshToken;
        },

        /**
         * Assigns new user payload (data obtained during user authorization/login)
         * @param {*} state Provided by Vuex
         * @param {Object} payload Just put the whole payload here
         */
        setUserPayload (state, payload){
            state.userPayload = payload;
        }
    },

    getters: {
        standardRequestHeaders: (state) => {
            let jwt = state.accessToken;

			let headers = null;

			if(jwt == null){
				headers = {
					"Content-Type": "application/json"
				}
			}
			else{
				headers = {
					"Content-Type": "application/json",
					"Authorization": "Bearer " + jwt
				}
			}

            return headers;
        }
    }
});


export default store;