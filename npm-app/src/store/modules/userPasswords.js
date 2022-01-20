import ERRORS from '@/consts/standardErrors'
import axios from 'axios';
import { handleStandardRequestResponses, encodeEntities } from '..';

const API_USER_PASSWORDS = 'api/v1/user-passwords/';
const API_USER_PASSWORD = 'api/v1/user-password/%%PASSWORD_CODE%%';
const API_USER_PASSWORD_COPY = 'api/v1/user-password/%%PASSWORD_CODE%%/copy/';
const API_USER_PASSWORD_SHARE_SEARCH_USER = 'api/v1/user-password/%%PASSWORD_CODE%%/share/search-user/';
const API_USER_PASSWORD_SHARES = 'api/v1/user-password/%%PASSWORD_CODE%%/shares/';
const API_USER_PASSWORD_SHARE = 'api/v1/user-password/%%PASSWORD_CODE%%/share/%%SHARE_ID%%';
// const API_USER_PASSWORD = 'api/v1/user-password/%%PASSWORD_CODE%%';
// const API_USER_PASSWORD_COPY = 'api/v1/user-password/%%PASSWORD_CODE%%/copy/';
// const API_USER_PASSWORD_SHARES = 'api/v1/user-password/%%PASSWORD_CODE%%/shares/';
// const API_USER_PASSWORD_SHARE = 'api/v1/user-password/%%PASSWORD_CODE%%/share/%%SHARE_ID%%';
// const API_USER_PASSWORDS_SHARED_TO_ME = 'api/v1/user-passwords/shared-to-me/';
// const API_USER_PASSWORD_DUPLICATE = 'api/v1/user-password/%%PASSWORD_CODE%%/duplicate/';


//
// STANDARD RESPONSE ADAPTERS
//

function adaptPasswordShareData(passwordShareData){
    let user = passwordShareData.user;
    let obj = {
        shareId: passwordShareData.id,
        userId: user.id,
        username: user.username,
        fullName: user.full_name
    }

    return obj;
}

function adaptPasswordSharesData(passwordSharesData){
    let result = [];

    for(let i = 0; i < passwordSharesData.length; i++){
        result.push(adaptPasswordShareData(passwordSharesData[i]));
    }

    return result;
}

function adaptPasswordData(passwordData, tabId){
    let descHTML = null;
    if(passwordData.password.description != null){
        descHTML = encodeEntities(passwordData.password.description);
        descHTML = descHTML.replace(/&#10;/g, "<br />");
    }

    let password = {
        tabId: tabId,
        code: passwordData.password.code,
        title: passwordData.password.title,
        description: passwordData.password.description,
        descriptionHTML: descHTML,
        url: passwordData.password.url,
        username: passwordData.password.username,

        shares: adaptPasswordSharesData(passwordData.password_shares)
    };

    return password;
}

function adaptTabPasswordsData(tabPasswordsData, tabId){
    let tabPasswords = [];
    for(let i = 0; i < tabPasswordsData.length; i++){
        tabPasswords.push(adaptPasswordData(tabPasswordsData[i], tabId));
    }

    return tabPasswords;
}

function adaptTabData(tabData){
    let tab = {
        id: tabData.id,
        name: tabData.name,
        isDefault: tabData.is_default,
        passwords: adaptTabPasswordsData(tabData.passwords, tabData.id)
    };

    return tab;
}

function adaptTabsData(tabsData){
    let tabs = [];
    let tab = null;

    for(let i = 0; i < tabsData.length; i++){
        tab = adaptTabData(tabsData[i]);

        tabs.push(tab);
    }

    return tabs;
}

function adaptSharedPasswordData(sharedPasswordData){
    let descHTML = null;
    if(sharedPasswordData.password.description != null){
        descHTML = encodeEntities(sharedPasswordData.password.description);
        descHTML = descHTML.replace(/&#10;/g, "<br />");
    }

    let password = {
        tabId: -1,
        code: sharedPasswordData.password.code,
        title: sharedPasswordData.password.title,
        description: sharedPasswordData.password.description,
        descriptionHTML: descHTML,
        url: sharedPasswordData.password.url,
        username: sharedPasswordData.password.username,

        owner: {
            id: sharedPasswordData.user.id,
            username: sharedPasswordData.user.username,
            firstName: sharedPasswordData.user.first_name,
            lastName: sharedPasswordData.user.last_name,
            email: sharedPasswordData.user.email
        }
    };

    return password;
}

function adaptSharedPasswordsData(sharedPasswordsData){
    let passwords = [];
    for(let i = 0; i < sharedPasswordsData.length; i++){
        passwords.push(adaptSharedPasswordData(sharedPasswordsData[i]));
    }
    return passwords;
}

function adaptResponseData(responseData){
    let result = {
        tabs: adaptTabsData(responseData.tabs),
        shared: adaptSharedPasswordsData(responseData.shared)
    };

    return result;
}

function adaptPasswordShareSearchUserData(responseData){
    var result = [];
    var obj;

    for(let i = 0; i < responseData.length; i++){
        obj = responseData[i];

        result.push({
            id: obj.id,
            searchValue: obj.search_value
        });
    }

    return result;
}

//
// END OF STANDARD RESPONSE ADAPTERS
//


export default {
    namespaced: true,

    state: {
        passwords: null, // {
        //     tabs: [
        //         {
        //             id: {Number},
        //             name: {String},
        //             isDefault: {Boolean},
        //             passwords: [
        //                 {
        //                     tabId: {Number},
        //                     code: {String},
        //                     title: {String},
        //                     description: {String},
        //                     descriptionHTML: {String},
        //                     username: {String},
        //                     url: {String},
        //
        //                     shares: [
        //                         {
        //                             shareId: {Number},
        //                             userId: {Number},
        //                             username: {String},
        //                             fullName: {String}
        //                         }
        //                     ]
        //                 }
        //             ]
        //         }
        //     ],
        //     shared: [
        //         {
        //             tabId: -1,
        //             code: {String},
        //             title: {String},
        //             description: {String},
        //             descriptionHTML: {String},
        //             username: {String},
        //             url: {String},

        //             owner: {
        //                 id: {Number},
        //                 username: {String},
        //                 firstName: {String},
        //                 lastName: {String},
        //                 email: {String}
        //             }
        //         }
        //     ]
        // }
    },
    getters: {
        getPasswords: (state) => {
            return state.passwords;
        },

        getPassword: (state) => (code, searchTabs=true, searchShared=false) => {
            if(state.passwords != null){
                if (searchTabs){
                    for(let i = 0; i < state.passwords.tabs.length; i++){
                        for(let j = 0; j < state.passwords.tabs[i].passwords.length; j++){
                            if(state.passwords.tabs[i].passwords[j].code == code){
                                return state.passwords.tabs[i].passwords[j];
                            }
                        }
                    }
                }

                if (searchShared){
                    for(let i = 0; i < state.passwords.shared.length; i++){
                        for(let j = 0; j < state.passwords.shared[i].passwords.length; j++){
                            if(state.passwords.shared[i].passwords[j].code == code){
                                return state.passwords.shared[i].passwords[j];
                            }
                        }
                    }
                }
            }

            return null;
        },

        getTabs: (state) => {
            var tabs = [];
            if (state.passwords != null){
                for(let i = 0; i < state.passwords.tabs.length; i++){
                    tabs.push({
                        id: state.passwords.tabs[i].id,
                        name: state.passwords.tabs[i].name
                    });
                }
            }
            return tabs;
        },

        /**
         * -1 means shared passwords tab
         * @param {*} state Provided by Vuex
         * @returns Found tab or null if not found
         */
        getTabById: (state) => (id) => {
            if(id == -1){
                return state.passwords.shared;
            }

            for(let i = 0; i < state.passwords.tabs.length; i++){
                if(state.passwords.tabs[i].id == id){
                    return state.passwords.tabs[i];
                }
            }
            return null;
        }
    },
    mutations: {
        reset(state){
            state.passwords = null;
        },

        newCache(state, payload) {
            state.passwords = payload.passwords;
        },
        deletePassword(state, payload){
            if(state.passwords != null){
                for(let i = 0; i < state.passwords.tabs.length; i++){
                    for(let j = 0; j < state.passwords.tabs[i].passwords.length; j++){
                        if(state.passwords.tabs[i].passwords[j].code == payload.passwordCode){
                            state.passwords.tabs[i].passwords.splice(j, 1);
                            return;
                        }
                    }
                }
            }
        },
        updatePassword(state, payload){
            if(state.passwords != null){
                for(let i = 0; i < state.passwords.tabs.length; i++){
                    for(let j = 0; j < state.passwords.tabs[i].passwords.length; j++){
                        if(state.passwords.tabs[i].passwords[j].code == payload.code){
                            state.passwords.tabs[i].passwords[j] = payload;
                            return;
                        }
                    }
                }
            }
        },
        addPasswordToTab(state, payload){
            if(state.passwords != null){
                let id = payload.tabId;
                for(let i = 0; i < state.passwords.tabs.length; i++){
                    if(state.passwords.tabs[i].id == id){
                        state.passwords.tabs[i].passwords.push(payload.password);
                        break;
                    }
                }
            }
        },

        addPasswordShare(state, payload){
            if(state.passwords != null){
                for(let i = 0; i < state.passwords.tabs.length; i++){
                    for(let j = 0; j < state.passwords.tabs[i].passwords.length; j++){
                        if(state.passwords.tabs[i].passwords[j].code == payload.code){
                            state.passwords.tabs[i].passwords[j].shares.push(
                                payload.share
                            );
                            return;
                        }
                    }
                }
            }
        },

        deletePasswordShare(state, payload){
            if(state.passwords != null){
                for(let i = 0; i < state.passwords.tabs.length; i++){
                    for(let j = 0; j < state.passwords.tabs[i].passwords.length; j++){
                        if(state.passwords.tabs[i].passwords[j].code == payload.code){
                            for(let k = 0; k < state.passwords.tabs[i].passwords[j].shares.length; k++){
                                if (state.passwords.tabs[i].passwords[j].shares[k].shareId == payload.shareId){
                                    state.passwords.tabs[i].passwords[j].shares.splice(k, 1);
                                    return;
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    actions: {
        /**
         * Retrieves user password data from the server
         * @param {*} param0 Provided by Vuex
         * @param {Object} payload Optional, can be null. Required format:
         * {
         *      allowCache: {Boolean}
         * }
         */
        async getData({state, commit, rootState, rootGetters}, payload){
            if(typeof(payload.allowCache) !== 'undefined' 
                && payload.allowCache != null 
                && payload.allowCache
            ){
                if (state.passwords != null){
                    return state.passwords;
                }
            }

            let headers = rootGetters.standardRequestHeaders;
            let response = null;
            try {
                response = await axios({
                    method: 'get',
                    url: rootState.apiUrl + API_USER_PASSWORDS, 
                    headers: headers
                });
            } catch(error) {
                handleStandardRequestResponses(error);
                throw {
                    type: ERRORS.UNKNOWN,
                    errors: []
                };
            }

            let adapted = adaptResponseData(response.data);

            commit({
                type: 'newCache',
                passwords: adapted
            });

            return adapted;
        },
        /**
         * Retrieves data about password from cache. If cache is not available, requests new cache
         * @param {*} param0 Provided by Vuex
         * @param {*} payload Required format:
         * {
         *      passwordCode: {String}
         * }
         */
        async getPasswordData({state, dispatch}, payload){
            let requiredFields = [
                "passwordCode"
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

            let reloadedCache = false;
            if(state.passwords == null){
                await dispatch("getData", {
                    allowCache: false
                });
                reloadedCache = true;
            }

            let item = null;
            for(let x = 0; x < 2; x++){
                for(let i = 0; i < state.passwords.tabs.length; i++){
                    for(let j = 0; j < state.passwords.tabs[i].passwords.length; j++){
                        item = state.passwords.tabs[i].passwords[j];
                        if(item.code == payload.passwordCode){
                            return item;
                        }
                    }
                }

                for(let i = 0; i < state.shared.length; i++){
                    item = state.shared[i];
                    if(item.code == payload.passwordCode){
                        return item;
                    }
                }

                if(!reloadedCache){
                     // Attempt to find password again after reloading the cache, just to be sure it doesn't exist
                     await dispatch("getData", {
                        allowCache: false
                    });
                    reloadedCache = true;
                }
                else{
                    break;
                }
            }

            return null;
        },
        /**
         * Retrieves password value from server
         * @param {*} param0 Provided by Vuex
         * @param {*} payload Required format:
         * {
         *      passwordCode: {String}
         * }
         * @returns Retrieved password value
         */
        async getPasswordValue({rootState, rootGetters}, payload) {
            let requiredFields = [
                "passwordCode"
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
            let response = null;

            try{
                response = await axios({
                    method: "POST",
                    url: rootState.apiUrl + API_USER_PASSWORD_COPY.replace("%%PASSWORD_CODE%%", payload.passwordCode),
                    headers: headers
                });
            } catch(error){
                handleStandardRequestResponses(error);

                throw {
                    type: ERRORS.UNKNOWN,
                    errors: []
                };
            }

            return response.data;
        },
        /**
         * Deletes selected password
         * @param {*} param0 Provided by Vuex
         * @param {*} payload Required format:
         * {
         *      passwordCode: {String}
         * }
         */
        async deletePassword({commit, rootState, rootGetters}, payload){
            let requiredFields = [
                "passwordCode"
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
                    url: rootState.apiUrl + API_USER_PASSWORD.replace("%%PASSWORD_CODE%%", payload.passwordCode),
                    headers: headers
                });
            } catch(error){
                handleStandardRequestResponses(error);

                throw {
                    type: ERRORS.UNKNOWN,
                    errors: []
                };
            }

            commit("deletePassword", {
                passwordCode: payload.passwordCode
            });
        },

        async updatePassword({commit, rootState, rootGetters}, payload){
            let requiredFields = [
                "passwordCode",
                "_tabId"
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
                ["password", "password"], ["title", "title"], ["description", "description"], ["username", "username"], ["url", "url"], ["tabId", "user_tab_id"]
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
                    url: rootState.apiUrl + API_USER_PASSWORD.replace("%%PASSWORD_CODE%%", payload.passwordCode),
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
            
            let updatedPassword = adaptPasswordData(response.data, payload._tabId);

            commit("updatePassword", updatedPassword);

            return updatedPassword;
        },
        async addPassword({commit, rootState, rootGetters}, payload){
            let requiredFields = [
                "tabId", "password", "title"
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
                    url: rootState.apiUrl + API_USER_PASSWORDS,
                    headers: headers,
                    data: {
                        user_tab_id: payload.tabId,
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

            let newPassword = adaptPasswordData(response.data, payload.tabId);

            commit("addPasswordToTab", {
                tabId: payload.tabId,
                password: newPassword
            });

            return newPassword;
        },

        /**
         * Searches for users available to share the password for
         * @param {*} param0 Provided by Vuex
         * @param {*} payload Format:
         * {
         *      passwordCode: {String},
         *      searchValue: {String}
         * }
         */
        async searchShareForUser({rootState, rootGetters}, payload){
            let requiredFields = [
                "passwordCode",
                "searchValue"
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
            let queryParams = {
                search_text: payload.searchValue
            };

            let headers = rootGetters.standardRequestHeaders;
            let response = null;

            let requestBody = {
                params: queryParams,
                headers: headers
            };

            try {
                response = await axios.get(
                    rootState.apiUrl + API_USER_PASSWORD_SHARE_SEARCH_USER.replace("%%PASSWORD_CODE%%", payload.passwordCode),
                    requestBody
                );
            } catch(error){
                handleStandardRequestResponses(error);

                throw {
                    type: ERRORS.UNKNOWN,
                    errors: []
                }
            }

            let data = adaptPasswordShareSearchUserData(response.data);
            return data;
        },
        /**
         * Shares a password for a user
         * @param {*} param0 Provided by Vuex
         * @param {*} payload Format:
         * {
         *      passwordCode: {String},
         *      userId: {Number}
         * }
         */
        async sharePassword({commit, rootState, rootGetters}, payload){
            let requiredFields = [
                "passwordCode",
                "userId"
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
            let response = null;

            try{
                response = await axios({
                    method: "POST",
                    url: rootState.apiUrl + API_USER_PASSWORD_SHARES.replace("%%PASSWORD_CODE%%", payload.passwordCode),
                    headers: headers,
                    data: {
                        user_id: payload.userId
                    }
                });
            } catch(error){
                handleStandardRequestResponses(error);

                throw {
                    type: ERRORS.UNKNOWN,
                    errors: []
                };
            }

            let share = {
                shareId: response.data.id,
                userId: response.data.user.id,
                username: response.data.user.username,
                fullName: response.data.user.full_name
            };
            
            commit("addPasswordShare", {
                code: payload.passwordCode,
                share: share
            });

            return share;
        },

        /**
         * Deletes chosen share to password
         * @param {*} param0 Provided by Vuex
         * @param {*} payload Format:
         * {
         *      passwordCode: {String},
         *      shareId: {Number}
         * }
         */
        async deleteShare({commit, rootState, rootGetters}, payload){
            let requiredFields = [
                "passwordCode",
                "shareId"
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
                    url: rootState.apiUrl + API_USER_PASSWORD_SHARE.replace("%%PASSWORD_CODE%%", payload.passwordCode).replace("%%SHARE_ID%%", payload.shareId),
                    headers: headers
                });
            } catch(error){
                handleStandardRequestResponses(error);

                throw {
                    type: ERRORS.UNKNOWN,
                    errors: []
                };
            }

            commit("deletePasswordShare", {
                code: payload.passwordCode,
                shareId: payload.shareId
            });
        }
    }
}