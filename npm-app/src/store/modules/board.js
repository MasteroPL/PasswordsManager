import ERRORS from '@/consts/standardErrors'
import axios from 'axios';
import { handleStandardRequestResponses, encodeEntities } from '..';

const API_BOARD = "api/v1/board/%%BOARD_ID%%";
const API_BOARD_USER_SEARCH = "api/v1/board/%%BOARD_ID%%/assignments/search-user/";
const API_BOARD_ASSIGNMENTS = "api/v1/board/%%BOARD_ID%%/assignments/";
const API_BOARD_ASSIGNMENT = "api/v1/board/%%BOARD_ID%%/assignment/%%ASSIGNMENT_ID%%";
const API_BOARD_TABS = "api/v1/board/%%BOARD_ID%%/tabs/";
const API_BOARD_TAB = "api/v1/board/%%BOARD_ID%%/tab/%%TAB_ID%%";
const API_BOARD_PASSWORDS = "api/v1/board/%%BOARD_ID%%/passwords/";
const API_BOARD_PASSWORD = "api/v1/board/%%BOARD_ID%%/password/%%PASSWORD_CODE%%";

function adaptBoardTabPasswordsResponseData(response){
    let item = null;
    let result = [];
    let obj = null;
    for(let i = 0; i < response.length; i++){
        item = response[i].password;
        obj = {
            title: item.title,
            description: item.description,
            url: item.url,
            username: item.username,
            code: item.code
        };
        result.push(obj);
    }

    return result;
}

function adaptBoardTabsResponseData(response){
    let tabs = [];
    let item = null;
    let tab = null;
    for(let i = 0; i < response.length; i++){
        item = response[i];
        tab = {
            id: item.id,
            name: item.name,
            isDefault: item.is_default,
            passwords: adaptBoardTabPasswordsResponseData(item.tab_passwords)
        };
        tabs.push(tab);
    }

    return tabs;
}

function adaptBoardResponseData(response){
    let item;
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
        tabs: null,
    };
    result.board.tabs = adaptBoardTabsResponseData(response.tabs);

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
                assignmentId: item.id,
                userId: item.user.id,
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



function adaptBoardUserSearchData(response){
    let result = [];
    let obj;
    let item;

    for(let i = 0; i < response.length; i++){
        item = response[i];
        obj = {
            id: item.id,
            username: item.username,
            firstName: item.first_name,
            lastName: item.last_name,
            searchValue: item.search_value
        };

        result.push(obj);
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

function sortByUsernameCompare(a, b){
	if(a.username < b.username){
		return -1;
	}
	else if(a.username > b.username){
		return 1;
	}
	return 0;
}

function sortByTitleCompare(a, b){
	if(a.title < b.title){
		return -1;
	}
	else if(a.title > b.title){
		return 1;
	}
	return 0;
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
        //                     code: {String},
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
        //             assignmentId: {Number},
        //             userId: {Number},
        //             username: {String},
        //             firstName: {String},
        //             lastName: {String},
    //                 admin: response.permissions.admin,
    //                 create: response.permissions.create,
    //                 read: response.permissions.read,
    //                 update: response.permissions.update,
    //                 delete: response.permissions.delete
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

        getTabs: (state) => {
            return state.board.tabs.sort(sortByTitleCompare);
        },

        getSortedUsers: (state) => {
            if(state.admin == null){
                return null;
            }

            return state.admin.users.sort(sortByUsernameCompare);
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
        },
        /**
         * Adds user assignment to board cache if cache exists
         * @param {*} state Provided by Vuex
         * @param {Object} payload Required format:
         * {
         *      boardId: {Number},
         *      user: Object following format of admin.users items
         * }
         */
        addBoardAssignment(state, payload){
            if(state.board != null && state.admin != null && state.board.id == payload.boardId){
                state.admin.users.push(payload.user);
            }
        },
        /**
         * Edits assignment in cache if cache exists
         * @param {*} state Provided by Vuex
         * @param {*} payload Required format:
         * {
         *      boardId: {Number},
         *      assignment: {Object}
         * }
         */
        editBoardAssignment(state, payload){
            if(state.board != null && state.admin != null && state.board.id == payload.boardId){
                let assignmentId = payload.assignment.assignmentId;
                let data = payload.assignment;

                for(let i = 0; i < state.admin.users.length; i++){
                    if(state.admin.users[i].assignmentId == assignmentId){
                        state.admin.users[i].admin = data.admin;
                        state.admin.users[i].create = data.create;
                        state.admin.users[i].read = data.read;
                        state.admin.users[i].update = data.update;
                        state.admin.users[i].delete = data.delete;

                        return;
                    }
                }
            }
        },
        removeBoardAssignment(state, payload){
            if(state.board != null && state.admin != null && state.board.id == payload.boardId){
                let assignmentId = payload.assignmentId;

                for(let i = 0; i < state.admin.users.length; i++){
                    if(state.admin.users[i].assignmentId == assignmentId){
                        state.admin.users.splice(i, 1);
                        return;
                    }
                }
            }
        },
        newTabsCache(state, payload){
            if(state.board != null && state.board.id == payload.boardId){
                state.board.tabs = payload.tabs;
            }
        },
        addPasswordToTab(state, payload){
            if(state.board != null && state.board.id == payload.boardId){
                let id = payload.tabId;
                for(let i = 0; i < state.board.tabs.length; i++){
                    if(state.board.tabs[i].id == id){
                        state.board.tabs[i].passwords.push(payload.password);
                        break;
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
        async getData({state, commit, rootState, rootGetters}, payload){
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
            if(typeof(payload.allowCache) !== 'undefined' && payload.allowCache && state.board != null){
                return {
                    board: state.board,
                    admin: state.admin
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
        async getAdminData({state, getters, dispatch}, payload){
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
                    admin: {
                        owner: state.admin.owner,
                        users: getters.getSortedUsers
                    },
                    board: state.board
                };
            }

            await dispatch('getData', {
                id: payload.id
            });

            return {
                admin: {
                    owner: state.admin.owner,
                    users: getters.getSortedUsers
                },
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
        },
        /**
         * Searches for users available to assign the the provided board
         * @param {*} param0 Provided by Vuex
         * @param {*} payload Required format
         * {
         *      boardId: {Number},
         *      searchValue: {String},
         *      [abortControllerSignal]: AbortController().signal
         * }
         */
        async searchAddUser({rootState, rootGetters}, payload){
            if(typeof(payload.boardId) === 'undefined'){
                throw {
                    type: ERRORS.VALIDATION,
                    errors: {
                        boardId: {
                            string: "This field is required",
                            code: "required"
                        }
                    }
                };
            }
            if(typeof(payload.searchValue) === 'undefined'){
                throw {
                    type: ERRORS.VALIDATION,
                    errors: {
                        searchValue: {
                            string: "This field is required",
                            code: "required"
                        }
                    }
                };
            }

            let id = payload.boardId;
            let queryParams = {
                search_text: payload.searchValue
            };
            if(payload.searchValue == null) payload.searchValue = "";
            if(payload.searchValue.length > 256){
                throw {
                    type: ERRORS.VALIDATION,
                    errors: {
                        searchValue: {
                            string: "Maximum length of search string is 256 characters",
                            code: "max_length"
                        }
                    }
                };
            }

            let headers = rootGetters.standardRequestHeaders;
            let response = null;

            let requestBody = {
                params: queryParams,
                headers: headers
            };

            if (typeof(payload.abortControllerSignal) !== 'undefined'){
                requestBody.signal = payload.abortControllerSignal
            }

            try {
                response = await axios.get(
                    rootState.apiUrl + API_BOARD_USER_SEARCH.replace("%%BOARD_ID%%", id),
                    requestBody
                );
            } catch(error){
                handleStandardRequestResponses(error);

                throw {
                    type: ERRORS.UNKNOWN,
                    errors: []
                }
            }

            let result = adaptBoardUserSearchData(response.data);
            return result;
        },

        /**
         * Adds new user to board
         * @param {*} param0 Provided Vuex
         * @param {*} payload Required format:
         * {
         *      boardId: {Number},
         *      userId: {Number},
         *      [admin]: {Boolean},
         *      [create]: {Boolean},
         *      [read]: {Boolean},
         *      [update]: {Boolean},
         *      [delete]: {Boolean}
         * }
         */
        async assignUser({commit, rootState, rootGetters}, payload){
            let requiredFields = [
                "boardId", "userId"
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

            let requestData = {
                user_id: payload.userId
            };

            // Mapping optional data
            let dataArray = [
                [ "admin", "perm_admin" ],
                [ "create", "perm_create" ],
                [ "read", "perm_read" ],
                [ "update", "perm_update" ],
                [ "delete", "perm_delete" ]
            ];

            for(let i = 0; i < dataArray.length; i++){
                if(typeof(payload[dataArray[i][0]]) !== 'undefined'){
                    requestData[dataArray[i][1]] = payload[dataArray[i][0]];
                }
            }

            let response = null;
            let headers = rootGetters.standardRequestHeaders;
            try {
                response = await axios({
                    method: "POST",
                    url: rootState.apiUrl + API_BOARD_ASSIGNMENTS.replace("%%BOARD_ID%%", payload.boardId),
                    headers: headers,
                    data: requestData
                });
            } catch(error){
                handleStandardRequestResponses(error);

                throw {
                    type: ERRORS.UNKNOWN,
                    errors: []
                };
            }

            let result = {
                assignmentId: response.data.id,
                userId: response.data.user.id,
                username: response.data.user.username,
                firstName: response.data.user.first_name,
                lastName: response.data.user.last_name,
                admin: response.data.perm_admin,
                create: response.data.perm_create,
                read: response.data.perm_read,
                update: response.data.perm_update,
                delete: response.data.perm_delete
            };

            commit("addBoardAssignment", {
                boardId: payload.boardId,
                user: result
            });

            return result;
        },
        /**
         * Edits existing user assignment
         * @param {*} param0 Provided by Vuex
         * @param {Object} payload Required format:
         * {
         *      boardId: {Number},
         *      assignmentId: {Number},
         *      [admin]: {Boolean},
         *      [create]: {Boolean},
         *      [read]: {Boolean},
         *      [update]: {Boolean},
         *      [delete]: {Boolean}
         * }
         */
        async editUserAssignment({commit, rootState, rootGetters}, payload){
            let requiredFields = [
                "boardId", "assignmentId"
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

            let requestData = {};
            let any = false;
            let dataArray = [
                ["admin", "perm_admin"],
                ["create", "perm_create"],
                ["read", "perm_read"],
                ["update", "perm_update"],
                ["delete", "perm_delete"]
            ];

            for(let i = 0; i < dataArray.length; i++){
                if(typeof(payload[dataArray[i][0]]) !== 'undefined'){
                    requestData[dataArray[i][1]] = payload[dataArray[i][0]];
                    any = true;
                }
            }

            if(!any){
                return null;
            }

            let response = null;
            let headers = rootGetters.standardRequestHeaders;
            try {
                response = await axios({
                    method: "PATCH",
                    url: rootState.apiUrl + API_BOARD_ASSIGNMENT.replace("%%BOARD_ID%%", payload.boardId).replace("%%ASSIGNMENT_ID%%", payload.assignmentId),
                    headers: headers,
                    data: requestData
                });
            } catch(error){
                handleStandardRequestResponses(error);

                throw {
                    type: ERRORS.UNKNOWN,
                    errors: []
                };
            }

            let result = {
                assignmentId: response.data.id,
                userId: response.data.user_id,
                admin: response.data.perm_admin,
                create: response.data.perm_create,
                read: response.data.perm_read,
                update: response.data.perm_update,
                delete: response.data.perm_delete
            };

            commit("editBoardAssignment", {
                boardId: payload.boardId,
                assignment: result
            });

            return result;
        },
        /**
         * Removes existing user assignment from the board
         * @param {*} param0 Provided by Vuex
         * @param {*} payload Required format:
         * {
         *      boardId: {Number},
         *      assignmentId: {Number}
         * }
         */
        async removeUserAssignment({commit, rootState, rootGetters}, payload){
            let requiredFields = [
                "boardId", "assignmentId"
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

            let headers = rootGetters.standardRequestHeaders;
            try {
                await axios({
                    method: "DELETE",
                    url: rootState.apiUrl + API_BOARD_ASSIGNMENT.replace("%%BOARD_ID%%", payload.boardId).replace("%%ASSIGNMENT_ID%%", payload.assignmentId),
                    headers: headers
                });
            } catch(error){
                handleStandardRequestResponses(error);

                throw {
                    type: ERRORS.UNKNOWN,
                    errors: []
                };
            }

            commit("removeBoardAssignment", {
                boardId: payload.boardId,
                assignmentId: payload.assignmentId
            });
        },

        /**
         * Adds a new tab to the list
         * @param {*} param0 Provided by Vuex
         * @param {Object} payload Required format:
         * {
         *      boardId: {Number},
         *      tabName: {String},
         *      [addAfter]: {Number}
         * }
         */
        async addTab({commit, rootState, rootGetters}, payload) {
            let requiredFields = [
                "boardId", "tabName"
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

            let addAfter = null;
            if(typeof(payload.addAfter) !== 'undefined'){
                addAfter = payload.addAfter;
            }

            let headers = rootGetters.standardRequestHeaders;
            let response = null;
            try {
                response = await axios({
                    method: "POST",
                    url: rootState.apiUrl + API_BOARD_TABS.replace("%%BOARD_ID%%", payload.boardId),
                    headers: headers,
                    data: {
                        name: payload.tabName,
                        add_after: addAfter
                    }
                });
            } catch(error) {
                handleStandardRequestResponses(error);

                throw {
                    type: ERRORS.UNKNOWN,
                    errors: []
                };
            }

            let newCache = adaptBoardTabsResponseData(response.data);

            commit("newTabsCache", {
                boardId: payload.boardId,
                tabs: newCache
            });

            return newCache;
        },
        /**
         * Edits an existing tab in the list
         * @param {*} param0 Provided by Vuex
         * @param {Object} payload Required format:
         * {
         *      boardId: {Number},
         *      tabId: {Number},
         *      tabName: {String},
         *      [putAfter]: {Number}
         * }
         */
        async editTab({commit, rootState, rootGetters}, payload) {
            let requiredFields = [
                "boardId", "tabId", "tabName"
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

            let putAfter = null;
            if(typeof(payload.putAfter) !== 'undefined'){
                putAfter = payload.putAfter;
            }

            let headers = rootGetters.standardRequestHeaders;
            let response = null;
            try {
                response = await axios({
                    method: "PATCH",
                    url: rootState.apiUrl + API_BOARD_TAB.replace("%%BOARD_ID%%", payload.boardId).replace("%%TAB_ID%%", payload.tabId),
                    headers: headers,
                    data: {
                        name: payload.tabName,
                        put_after: putAfter
                    }
                });
            } catch(error) {
                handleStandardRequestResponses(error);

                throw {
                    type: ERRORS.UNKNOWN,
                    errors: []
                };
            }

            let newCache = adaptBoardTabsResponseData(response.data);

            commit("newTabsCache", {
                boardId: payload.boardId,
                tabs: newCache
            });

            return newCache;
        },
        /**
         * Removes an existing tab
         * @param {*} param0 Provided by Vuex
         * @param {Object} payload Required format:
         * {
         *      boardId: {Number},
         *      tabId: {Number},
         *      removePasswords: {Boolean},
         *      [movePasswordsTo]: {Number}
         * }
         */
        async removeTab({commit, rootState, rootGetters}, payload) {
            let requiredFields = [
                "boardId", "tabId", "removePasswords"
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

            let movePasswordsTo = null;
            if(!payload.removePasswords && typeof(payload.movePasswordsTo) == 'undefined'){
                throw {
                    type: ERRORS.VALIDATION,
                    errors: {
                        "movePasswordsTo": {
                            string: "This field is required if removePasswords is set to true",
                            errors: "conditionally_required"
                        }
                    }
                };
            }
            else if(!payload.removePasswords){
                movePasswordsTo = payload.movePasswordsTo;
            }

            let headers = rootGetters.standardRequestHeaders;
            let response = null;
            try {
                response = await axios({
                    method: "DELETE",
                    url: rootState.apiUrl + API_BOARD_TAB.replace("%%BOARD_ID%%", payload.boardId).replace("%%TAB_ID%%", payload.tabId),
                    headers: headers,
                    data: {
                        remove_passwords: payload.removePasswords,
                        move_passwords_to_tab_id: movePasswordsTo
                    }
                });
            } catch(error) {
                handleStandardRequestResponses(error);

                throw {
                    type: ERRORS.UNKNOWN,
                    errors: []
                };
            }
            
            let newCache = adaptBoardTabsResponseData(response.data);

            commit("newTabsCache", {
                boardId: payload.boardId,
                tabs: newCache
            });

            return newCache;
        },
        /**
         * Retrieves data about password from cache. If cache is not available, requests new cache
         * @param {*} param0 
         * @param {Object} payload Required format:
         * {
         *      boardId: {Number},
         *      passwordCode: {String}
         * }
         */
        async getPasswordData({state, dispatch}, payload){
            let requiredFields = [
                "boardId", "passwordCode"
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

            let reloadedBoard = false;
            if(state.board == null || state.board.id != payload.boardId){
                await dispatch("getData", {
                    id: payload.boardId
                });
                reloadedBoard = true;
            }

            let item = null;
            for(let x = 0; x < 2; x++){
                for(let i = 0; i < state.board.tabs.length; i++){
                    for(let j = 0; j < state.board.tabs[i].passwords.length; j++){
                        item = state.board.tabs[i].passwords[j];

                        if(item.code == payload.passwordCode){
                            return {
                                ...item,
                                tabId: state.board.tabs[i].id
                            };
                        }
                    }
                }

                if(!reloadedBoard){
                    // Attempt to find password again after reloading the board, just to be sure it doesn't exist
                    await dispatch("getData", {
                        id: payload.boardId
                    });
                    reloadedBoard = true;
                }
                else{
                    break;
                }
            }

            return null;
        },
        /**
         * Adds new password to the database and updates cache if boardId matches with cached board
         * @param {*} param0 Provided by Vuex
         * @param {*} payload Required format:
         * {
         *      boardId: {Number},
         *      boardTabId: {Number},
         *      password: {String},
         *      title: {String},
         *      [description]: {String},
         *      [url]: {String},
         *      [username]: {String}
         * }
         */
        async addPassword({commit, rootState, rootGetters}, payload){
            let requiredFields = [
                "boardId", "boardTabId", "password", "title"
            ];
            let optionalFields = [
                "description", "url", "username"
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

            // Filling optional fields with nulls if undefined
            for(let i = 0; i < optionalFields.length; i++){
                if(typeof(payload[optionalFields[i]]) === 'undefined'){
                    payload[optionalFields[i]] = null;
                }
                else if(payload[optionalFields[i]] == ""){
                    payload[optionalFields[i]] = null;
                }
            }

            let headers = rootGetters.standardRequestHeaders;
            let response = null;
            try {
                response = await axios({
                    method: "POST",
                    url: rootState.apiUrl + API_BOARD_PASSWORDS.replace("%%BOARD_ID%%", payload.boardId),
                    headers: headers,
                    data: {
                        board_tab_id: payload.boardTabId,
                        password: payload.password,
                        title: payload.title,
                        description: payload.description,
                        url: payload.url,
                        username: payload.username
                    }
                });
            } catch(error){
                handleStandardRequestResponses(error);

                throw {
                    type: ERRORS.UNKNOWN,
                    errors: []
                };
            }

            let newPassword = adaptBoardTabPasswordsResponseData([ response.data ])[0];

            commit("addPasswordToTab", {
                boardId: payload.boardId,
                tabId: payload.boardTabId,
                password: newPassword
            });

            return newPassword;
        },
        /**
         * Updates password in the database and updates cache if boardId matches with cached board
         * @param {*} param0 Provided by Vuex
         * @param {*} payload Required format:
         * {
         *      boardId: {Number},
         *      passwordCode: {String},
         *      [boardTabId]: {Number},
         *      [password]: {String},
         *      [title]: {String},
         *      [description]: {String},
         *      [url]: {String},
         *      [username]: {String}
         * }
         */
         async updatePassword({rootState, rootGetters}, payload){
            let requiredFields = [
                "boardId", "passwordCode"
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

            let data = {};
            let optionalData = [
                ["password", "password"], ["title", "title"], ["description", "description"], ["username", "username"], ["url", "url"], ["boardTabId", "board_tab_id"]
            ];

            for(let i = 0; i < optionalData.length; i++){
                if(typeof(payload[optionalData[i][0]]) !== 'undefined'){
                    data[optionalData[i][1]] = payload[optionalData[i][0]];
                }
            }

            let headers = rootGetters.standardRequestHeaders;
            let response = null;
            try {
                response = await axios({
                    method: "PATCH",
                    url: rootState.apiUrl + API_BOARD_PASSWORD.replace("%%BOARD_ID%%", payload.boardId).replace("%%PASSWORD_CODE%%", payload.passwordCode),
                    headers: headers,
                    data: data
                });
            } catch(error){
                handleStandardRequestResponses(error);

                throw {
                    type: ERRORS.UNKNOWN,
                    errors: []
                };
            }

            let updatedPassword = adaptBoardTabPasswordsResponseData([ response.data ])[0];

            return updatedPassword;
        }
    }

}