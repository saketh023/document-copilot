type EnvName =
  | 'VITE_API_BASE_URL'
  | 'VITE_SUPABASE_URL'
  | 'VITE_SUPABASE_ANON_KEY'

function required(name: EnvName): string {
  const value: unknown = import.meta.env[name]
  if (typeof value !== 'string' || !value.trim()) {
    throw new Error(`Missing required environment variable: ${name}`)
  }
  return value.trim()
}

function httpUrl(name: EnvName): string {
  const value = required(name)
  let url: URL
  try {
    url = new URL(value)
  } catch {
    throw new Error(`${name} must be an absolute HTTP or HTTPS URL`)
  }
  if (
    !['http:', 'https:'].includes(url.protocol) ||
    url.username || url.password || url.search || url.hash
  ) {
    throw new Error(`${name} must be an HTTP or HTTPS URL without credentials, query, or fragment`)
  }
  return url.toString().replace(/\/+$/, '')
}

export const env = Object.freeze({
  apiBaseUrl: httpUrl('VITE_API_BASE_URL'),
  supabaseUrl: httpUrl('VITE_SUPABASE_URL'),
  supabaseAnonKey: required('VITE_SUPABASE_ANON_KEY'),
})
