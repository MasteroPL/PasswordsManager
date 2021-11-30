import ERRORS from '@/consts/standardErrors'
import axios from 'axios';
import { handleStandardRequestResponses, encodeEntities } from '..';

const API_BOARD = "api/v1/board/%%BOARD_ID%%";

function adaptBoardResponseData(response){
    let item;
    let tab;
    let result = {
        board: null,
        admin: null
    };
    let descHTML = null;
    if(response.description != null){
        descHTML = encodeEntities(response.description);
        descHTML = descHTML.replace(/&#10;/g, "<br />");
    }

    result.board = {
        id: response.id,
        name: response.name,
        description: response.description,
        descriptionHTML: descHTML,
        permissions: {
            admin: response.permissions.admin,
            create: response.permissions.create,
            read: response.permissions.read,
            update: response.permissions.update,
            delete: response.permissions.delete
        },
        tabs: [],
    };
    for(let i = 0; i < response.tabs.length; i++){
        item = response.tabs[i];
        tab = {
            id: item.id,
            name: item.name,
            isDefault: item.is_default,
            passwords: [] // TODO
        };
        result.board.tabs.push(tab);
    }

    if(typeof(response.owner) !== 'undefined' && response.owner != null && typeof(response.users) !== 'undefined' && response.users != null){
        let user;
        result.admin = {
            owner: {
                id: response.owner.id,
                username: response.owner.username,
                firstName: response.owner.first_name,
                lastName: response.owner.last_name
            },
            users: []
        };

        for(let i = 0; i < response.users.length; i++){
            item = response.users[i];
            user = {
                id: item.id,
                username: item.user.username,
                firstName: item.user.first_name,
                lastName: item.user.last_name,
                admin: item.perm_admin,
                create: item.perm_admin || item.perm_create,
                read: item.perm_admin || item.perm_read,
                update: item.perm_admin || item.perm_update,
                delete: item.perm_admin || item.perm_delete
            };
            result.admin.users.push(user);
        }
    }

    return result;
}

function validateUpdateBoardData(data){
    let errors = {};
    let anyErrors = false;
    if(typeof(data.name) !== 'undefined'){
        if(data.name.length > 50){
            errors.name = {
                string: "Board name is too long",
                code: "too_long"
            };
            anyErrors = true;
        }
    }   

    if(typeof(data.description) !== 'undefined'){
        if(data.description.length > 1024){
            errors.description = {
                string: "Board description is too long",
                code: "too_long"
            };
            anyErrors = true;
        }
    }

    if(anyErrors){
        throw {
            type: ERRORS.VALIDATION,
            errors: errors
        };
    }

    return data;
}

export default {
    namespaced: true,

    state: {
        
        board: null, // {
        //     id: {Number},
        //     name: {String},
        //     description: {String},
        //     descriptionHTML: {String},
        //     permissions: {
        //          admin: {Boolean},
        //          create: {Boolean},
        //          read: {Boolean},
        //          update: {Boolean},
        //          delete: {Boolean},
        //     }
        //     tabs: [
        //         {
        //             id: {Number},
        //             name: {String},
        //             isDefault: {Boolean},
        //             passwords: [
        //                 {
        //                     id: {Number},
        //                     title: {String},
        //                     username: {String},
        //                     url: {String},
        //                     notes: {String},
        //                     notesHTML: {String}
        //                 }
        //             ]
        //         }
        //     ],
        //
        // }
        admin: null // {
        //     users: [
        //         {
        //             id: {Number},
        //             username: {String},
        //             firstName: {String},
        //             lastName: {String}
        //         }
        //     ],
        //     owner: {
        //         id: {Number},
        //         username: {String},
        //         firstName: {String},
        //         lastName: {String}
        //     }
        // }
    },
    getters: {
        getBoard: (state) => {
            return state.board;
        },

        defaultTab: (state) => {
            for(let i = 0; i < state.board.tabs.length; i++){
                if(state.board.tabs[i].isDefault){
                    return state.board.tabs[i];
                }
            }
        },
        defaultTabId: (state) => {
            for(let i = 0; i < state.board.tabs.length; i++){
                if(state.board.tabs[i].isDefault){
                    return state.board.tabs[i].id;
                }
            }
        },
        defaultTabIndex: (state) => {
            for(let i = 0; i < state.board.tabs.length; i++){
                if(state.board.tabs[i].isDefault){
                    return i;
                }
            }
        },
        getTabById: (state) => (id) => {
            for(let i = 0; i < state.board.tabs.length; i++){
                if(state.board.tabs[i].id == id){
                    return state.board.tabs[i];
                }
            }

            return null;
        }
    },
    mutations: {
        /**
         * Assigns new board cache
         * @param {*} state Provided by Vuex
         * @param {Object} payload Required format of the object:
         * {
         *      board: {adapted API response},
         *      admin: {adapted API response}
         * }
         */
        newCache (state, payload) {
            console.log("newCache");
            console.log(payload);
            state.board = payload.board;
            state.admin = payload.admin;
        },
        /**
         * Updates board cache if it exists and the cached board has the same ID as the payload
         * @param {*} state Provided by Vuex
         * @param {Object} payload Required format:
         * {
         *      id: {Number},
         *      [owner]: {
         *          id: {Number},
         *          username: {String},
         *          firstName: {String},
         *          lastName: {String}
         *      },
         *      [name]: {String},
         *      [description]: {String}
         * }
         */
        updateBoardCache(state, payload){
            if(state.board != null){
                if(payload.id == state.board.id){
                    if(typeof(payload.name) !== 'undefined'){
                        state.board.name = payload.name;
                    }

                    if(typeof(payload.description) !== 'undefined'){
                        state.board.description = payload.description;
                    }

                    if(typeof(payload.owner) !== 'undefined' && state.admin != null){
                        state.admin.owner = payload.owner;
                    }
                }
            }
        }
    },
    actions: {
        /**
         * Retrieves board data from the server
         * @param {*} param0 Provided by Vuex
         * @param {*} payload Required format: 
         * {
         *      id: {Number}, // board id
         * }
         */
        async getData({commit, rootState, rootGetters}, payload){
            if(typeof(payload.id) === 'undefined'){
                throw {
                    type: ERRORS.VALIDATION,
                    errors: {
                        id: {
                            string: "This field is required",
                            code: "required"
                        }
                    }
                };
            }

            let headers = rootGetters.standardRequestHeaders;
            let response = null;
            try {
                response = await axios({
                    method: 'get',
                    url: rootState.apiUrl + API_BOARD.replace("%%BOARD_ID%%", payload.id),
                    headers: headers,
                    params: {
                        include_users: true,
                        include_owner: true
                    }
                });
            } catch(error) {
                handleStandardRequestResponses(error);

                throw {
                    type: ERRORS.UNKNOWN,
                    errors: []
                };
            }

            let adapted = adaptBoardResponseData(response.data);

            commit({
                type: 'newCache',
                board: adapted.board,
                admin: adapted.admin
            });

            return adapted;
        },
        /**
         * Retrieves board data from the server
         * @param {*} param0 Provided by Vuex
         * @param {*} payload Required format: 
         * {
         *      id: {Number}, // board id
         *      [allowCache]: {Boolean} // Use cache if data present?
         * }
         */
        async getAdminData({state, dispatch}, payload){
            if(typeof(payload.id) === 'undefined'){
                throw {
                    type: ERRORS.VALIDATION,
                    errors: {
                        id: {
                            string: "This field is required",
                            code: "required"
                        }
                    }
                };
            }

            if(typeof(payload.allowCache) !== 'undefined'
                && state.admin != null
                && payload.allowCache
                && state.board != null
                && state.board.id == payload.id
            ) {
                return {
                    admin: state.admin,
                    board: state.board
                };
            }

            await dispatch('getData', {
                id: payload.id
            });

            return {
                admin: state.admin,
                board: state.board
            };
        },
        
        /**
         * Updates board based on the provided payload
         * If board id is the same as cached board id, the cache will be updated automatically
         * @param {*} param0 Provided by Vuex
         * @param {*} payload Required format:
         * {
         *      id: {Number},
         *      [name]: {String},
         *      [description]: {String},
         *      [ownerId]: {Number}
         * }
         */
        async updateBoard({commit, rootState, rootGetters}, payload){
            if(typeof(payload.id) === 'undefined'){
                throw {
                    type: ERRORS.VALIDATION,
                    errors: {
                        id: {
                            string: "This field is required",
                            code: "required"
                        }
                    }
                };
            }

            let id = payload.id;
            let data = {};
            let anyData = false;

            if (typeof(payload.name) !== 'undefined'){
                data.name = payload.name;
                anyData = true;
            }
            if(typeof(payload.description) !== 'undefined'){
                data.description = payload.description;
                anyData = true;
            }
            if(typeof(payload.ownerId) !== 'undefined'){
                data.owner_id = payload.ownerId;
                anyData = true;
            }

            if(!anyData){
                throw {
                    type: ERRORS.VALIDATION,
                    errors: {
                        id: {
                            string: "No changes",
                            code: "no_changes"
                        }
                    }
                };
            }

            let validatedData = validateUpdateBoardData(data);

            let headers = rootGetters.standardRequestHeaders;
            let response = null;
            try {
                response = await axios({
                    method: 'patch',
                    url: rootState.apiUrl + API_BOARD.replace("%%BOARD_ID%%", id),
                    headers: headers,
                    data: validatedData
                });
            } catch(error) {
                handleStandardRequestResponses(error);

                throw {
                    type: ERRORS.UNKNOWN,
                    errors: []
                };
            }

            let d = response.data;
            commit('updateBoardCache', {
                id: id,
                name: d.name,
                description: d.description,
                owner: {
                    id: d.owner.id,
                    username: d.owner.username,
                    firstName: d.owner.first_name,
                    lastName: d.owner.last_name
                }
            });

            return response;
        }
    }

}