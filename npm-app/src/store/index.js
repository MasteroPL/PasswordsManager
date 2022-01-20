import Vue from 'vue';
import Vuex from 'vuex';
import BoardsModule from './modules/boardsList';
import BoardModule from './modules/board';
import UserPasswordsModule from './modules/userPasswords';
import appConfig from '@/config.js';
import ERRORS from '@/consts/standardErrors';
import axios from 'axios';

Vue.use(Vuex);

const API_CHANGE_PASSWORD = "api/change-password/";

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
};

const SURROGATE_PAIR_REGEXP = /[\uD800-\uDBFF][\uDC00-\uDFFF]/g,
    // Match everything outside of normal chars and " (quote character)
    NON_ALPHANUMERIC_REGEXP = /([^#-~| |!])/g;

/**
* Escapes all potentially dangerous characters, so that the
* resulting string can be safely inserted into attribute or
* element text.
* @param value
* @returns {string} escaped text
*/
export const encodeEntities = (value) => {
    return value.
        replace(/&/g, '&amp;').
        replace(SURROGATE_PAIR_REGEXP, function(value) {
            var hi = value.charCodeAt(0);
            var low = value.charCodeAt(1);
            return '&#' + (((hi - 0xD800) * 0x400) + (low - 0xDC00) + 0x10000) + ';';
        }).
        replace(NON_ALPHANUMERIC_REGEXP, function(value) {
            return '&#' + value.charCodeAt(0) + ';';
        }).
        replace(/</g, '&lt;').
        replace(/>/g, '&gt;');
};

const store = new Vuex.Store({
    modules: {
        boardsList: BoardsModule,
        board: BoardModule,
        userPasswords: UserPasswordsModule
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

            localStorage.setItem("jwtAccess", payload.accessToken);
            localStorage.setItem("jwtRefresh", payload.refreshToken);
        },

        /**
         * Assigns new user payload (data obtained during user authorization/login)
         * @param {*} state Provided by Vuex
         * @param {Object} payload Just put the whole payload here
         */
        setUserPayload (state, payload){
            state.userPayload = payload;

            localStorage.setItem("userPayload", JSON.stringify(payload));
        },

        loadLocalStorage (state) {
            state.accessToken = localStorage.getItem("jwtAccess");
            state.refreshToken = localStorage.getItem("jwtRefresh");
            state.userPayload = JSON.parse(localStorage.getItem("userPayload"));
        },

        clearCaches (state) {
            localStorage.removeItem("jwtAccess");
            localStorage.removeItem("jwtRefresh");
            localStorage.removeItem("userPayload");

            state.accessToken = null;
            state.refreshToken = null;
            state.userPayload = null;
        },
    },

    getters: {
        userPayload: (state) => {
            return state.userPayload;
        },
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
    },

    actions: {
        resetAll({commit}){
            commit("clearCaches");

            commit("boardsList/reset");
            commit("board/reset");
            commit("userPasswords/reset");
        },

        async changePassword({state, getters}, payload){
            let requiredFields = [
                "oldPassword", "newPassword"
            ];
            let errors = {};
            let valid = true;

            for(let i = 0; i < requiredFields.length; i++){
                if (typeof(payload[requiredFields[i]]) === 'undefined'){
                    valid = false;
                    errors[requiredFields[i]] = {
                        string: "This field is required",
                        code: "required"
                    };
                }
            }
            if(!valid){
                throw {
                    type: ERRORS.VALIDATION,
                    errors: errors
                };
            }            

            let headers = getters.standardRequestHeaders;

            try {
                await axios({
                    method: "POST",
                    url: state.apiUrl + API_CHANGE_PASSWORD,
                    headers: headers,
                    data: {
                        old_password: payload.oldPassword,
                        new_password: payload.newPassword
                    }
                });
            } catch(error) {
                handleStandardRequestResponses(error);

                throw {
                    type: ERRORS.UNKNOWN,
                    errors: []
                };
            }
        }
    }
});


export default store;