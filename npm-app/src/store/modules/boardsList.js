import axios from 'axios'
import ERRORS from '@/consts/standardErrors'
import { handleStandardRequestResponses } from '@/store/index.js'

const CACHING_TIME_IN_SECONDS = 60;
const API_BOARDS_LIST = "api/v1/boards/";
const API_BOARD = "api/v1/board/%%BOARD_ID%%";
const API_BOARD_LEAVE = "api/v1/board/%%BOARD_ID%%/leave/";

function adaptListResponseData(response){
	let item;
	let result = [];
	for(let i = 0; i < response.items.length; i++){
		item = response.items[i];

		result.push({
			id: item.id,
			name: item.name,
			description: item.description,
			isOwner: item.is_owner,
			isAdmin: item.is_admin
		});
	}
	return result;
}

function sortByNameCompare(a, b){
	if(a.name < b.name){
		return -1;
	}
	else if(a.name > b.name){
		return 1;
	}
	return 0;
}

/**
 * Validates add request parameters
 * @param {Object} payload Payload to validate. Format:
 * {
 * 		name: {String},
 * 		[description]: {String}
 * }
 * @returns Validated payload
 * @throws Dictionary of errors if validation fails
 */
function addBoardValidate(payload){
	let error = false;
	let errors = {};
	let validatedData = {};

	// --- Board name validation ---
	let tmpErr = false;
	let tmpVal = payload.name;
	if (typeof(tmpVal) === 'undefined' 
		|| tmpVal == null 
		|| tmpVal == ''
	){
		tmpErr = true;
		errors["name"] = {
			string: "This field is required",
			code: "required",
			kwargs: null
		};
	}
	else if(tmpVal.length > 50){
		tmpErr = true;
		errors["name"] = {
			string: "The maximum length for this field is 50 characters",
			code: "too_long",
			kwargs: {
				maxLength: 50
			}
		};
	}
	if (tmpErr) error = true;
	else {
		validatedData["name"] = tmpVal;
	}
	

	// --- Board description validation ---
	tmpErr = false;
	tmpVal = payload.description;
	if (typeof(tmpVal) === 'undefined'
		|| tmpVal == null 
		|| tmpVal == ''
	){
		tmpVal = null; // Valid value
	}
	else if(tmpVal.length > 1024){
		tmpErr = true;
		errors["description"] = {
			string: "The maximum length for this field is 1024 characters",
			code: "too_long",
			kwargs: {
				maxLength: 1024
			}
		}
	}

	if (tmpErr) error = true;
	else {
		validatedData["description"] = tmpVal;
	}

	if(error){
		throw {
			type: ERRORS.VALIDATION,
			errors: errors
		};
	}

	return validatedData;
}

export default {
	namespaced: true,

	state: {
		cachedAt: null,
		items: null
	},

	getters: {
		getBoardsSortedByName: (state) => {
			if(state.items == null){
				return null;
			}

			return state.items.sort(sortByNameCompare);
		},
		getBoardById: (state) => (id) => {
			if (state.items == null) {
				return null;
			}

			return state.items.find(item => item.id === id);
		}
	},

	mutations: {
		reset(state){
			state.cachedAt = null;
			state.items = null;
		},
		/**
		 * Assigns new list of items to cache
		 * @param {*} state Provided by Vuex
		 * @param {Object} payload Required format of the object: 
		 * items: [{
		 *      id: {Number},
		 *      name: {String},
		 *      description: {String},
		 *      isOwner: {Boolean},
		 * 		isAdmin: {Boolean}
		 * }, { ... }, ... ]
		 */
		newCache (state, payload) {
			state.cachedAt = new Date();
			state.items = payload.items;
		},
		/**
		 * Inserts board to cache if cache exists 
		 * @param {*} state Provided by Vuex
		 * @param {Object} payload Required format:
		 * {
		 * 		id: {Number},
		 * 		name: {String},
		 * 		description: {String},
		 * 		isOwner: {Boolean},
		 * 		isAdmin: {Boolean}
		 * }
		 */
		insertBoard (state, payload) {
			if(state.items != null){
				state.items.push(payload);
			}
		},

		/**
		 * Removes board from cache if cache exists
		 * @param {*} state Provided by Vuex
		 * @param {Object} payload Required format:
		 * {
		 * 		id: {Number}
		 * }
		 */
		removeBoard (state, payload) {
			if(state.items != null){
				for(let i = 0; i < state.items.length; i++){
					if(state.items[i].id == payload.id){
						state.items.splice(i, 1);
						break;
					}
				}
			}
		}
	},

	actions: {		
		async getData({state, commit, rootState, rootGetters}, noCache=true) {
			// If cache isn't outdated, just use the cache
			if (!noCache && state.cachedAt != null && state.items != null){
				let now = new Date();
				let diff = now - state.cachedAt;

				if(diff / 1000 < CACHING_TIME_IN_SECONDS){
					return state.items;
				}
			}

			let headers = rootGetters.standardRequestHeaders;
			let response = null;
			try{
				response = await axios({
					method: 'get',
					url: rootState.apiUrl + API_BOARDS_LIST,
					headers: headers
				});
			} catch(error){
				handleStandardRequestResponses(error);

				if (error.response.status == 400){
					// This should never happen
					throw {
						type: ERRORS.BAD_REQUEST,
						errors: []
					};
				}
				else{
					throw {
						type: ERRORS.UNKNOWN,
						errors: []
					};
				}
			}
			let items = adaptListResponseData(response.data);

			commit({
				type: 'newCache',
				items: items
			});

			return items;
		},

		/**
		 * Adds board to database
		 * @param {*} param0 Provided by Vuex
		 * @param {Object} payload Required format:
		 * {
		 * 		name: {String},
		 * 		[description]: {String},
		 * }
		 * @returns Created board instance
		 * @throws Any errors that can occur (including validation errors)
		 */
		async addBoard({commit, rootState, rootGetters}, payload){
			let data = addBoardValidate(payload);

			let headers = rootGetters.standardRequestHeaders;
			let response = null;
			try {
				response = await axios({
					method: 'post',
					url: rootState.apiUrl + API_BOARDS_LIST,
					headers: headers,
					data: data
				});
			} catch(error) {
				// Handles standard responses: netowrk error, authorization, internal, throttling
				handleStandardRequestResponses(error);

				if (error.response.status == 400){
					// This should never happen
					throw {
						type: ERRORS.BAD_REQUEST,
						errors: []
					};
				}
				else{
					throw {
						type: ERRORS.UNKNOWN,
						errors: []
					};
				}
			}

			let newBoard = {
				id: response.data.id,
				name: response.data.name,
				description: response.data.description,
				isOwner: true,
				isAdmin: true
			};

			commit("insertBoard", newBoard);

			return newBoard;
		},

		/**
		 * Deletes board from database
		 * @param {*} param0 Provided by Vuex
		 * @param {*} payload Required format: 
		 * {
		 * 		id: {Number}
		 * }
		 * @throws Any errors that can occur (including validation errors)
		 */
		async deleteBoard({commit, rootState, rootGetters}, payload){
			if (typeof(payload.id) === 'undefined'){
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
			try {
				await axios({
					method: 'delete',
					url: rootState.apiUrl + API_BOARD.replace("%%BOARD_ID%%", payload.id),
					headers: headers
				});
			} catch(error) {
				handleStandardRequestResponses(error);

				throw {
					type: ERRORS.UNKNOWN,
					errors: []
				};
			}

			commit("removeBoard", { id: payload.id });
		},

		/**
		 * Removes user assignment from the board (if user is not the board owner)
		 * @param {*} param0 Provided by Vuex
		 * @param {Object} payload Required format:
		 * {
		 * 		id: {Number}
		 * }
		 * @throws Any errors that occur
		 */
		async leaveBoard({commit, rootState, rootGetters}, payload){
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
			try{
				await axios({
					method: "delete",
					url: rootState.apiUrl + API_BOARD_LEAVE.replace("%%BOARD_ID%%", payload.id),
					headers: headers
				});
			} catch(error) {
				handleStandardRequestResponses(error);

				throw {
					type: ERRORS.UNKNOWN,
					errors: []
				};
			}

			commit("removeBoard", { id: payload.id });
		}
	}
}