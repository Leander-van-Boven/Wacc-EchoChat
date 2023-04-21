export const DEBUG = process.env.NODE_ENV  === 'development' || false

export const HOST = process.env.VUE_APP_API_URL ? process.env.VUE_APP_API_URL : `${window.location.host}/api`
export const API_URL = process.env.VUE_APP_API_URL ? `http://${HOST}` : `${window.location.origin}/api`
export const WEBSOCKET_URL = `ws://${HOST}/ws`
export const DEFAULT_USER_ID = '00000000-0000-4000-a000-000000000000'
export const DEFAULT_USERNAME = DEBUG ? 'Jochie-0' : ''
export const DEFAULT_PASSWORD = DEBUG ? 'password' : ''
export const DEFAULT_ADMIN_USERNAME = DEBUG ? 'admin' : ''
export const DEFAULT_ADMIN_PASSWORD = DEBUG ? 'admin' : ''

export const DEFAULT_MESSAGE_FETCH_COUNT = 50
