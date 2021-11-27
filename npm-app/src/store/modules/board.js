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
    console.log(response.description);
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

    if(typeof(response.owner) !== 'undefined' && typeof(response.users) !== 'undefined'){
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
                username: item.username,
                firstName: item.first_name,
                lastName: item.last_name
            };
            result.admin.users.push(user);
        }
    }

    return result;
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
         * @param {*} payload Required format of the object:
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
        }
    },
    actions: {
        /**
         * Retrieves board data from the server
         * @param {*} param0 Provided by Vuex
         * @param {*} payload Required format: 
         * {
         *      id: {Number}, // board id
         *      [isAdmin]: {Boolean} // whether to request board as admin or regular user
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
            if(typeof(payload.isAdmin) === 'undefined'){
                payload.isAdmin = false;
            }

            let headers = rootGetters.standardRequestHeaders;
            let response = null;
            try {
                response = await axios({
                    method: 'get',
                    url: rootState.apiUrl + API_BOARD.replace("%%BOARD_ID%%", payload.id),
                    headers: headers,
                    params: {
                        include_users: payload.isAdmin,
                        include_owner: payload.isAdmin
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
        }
    }
}