import { env } from '@/lib/env'
import { supabase } from '@/lib/supabase'

export class ApiError extends Error {
  readonly status: number | null
  readonly isNetworkError: boolean

  constructor(message: string, status: number | null, options?: ErrorOptions) {
    super(message, options)
    this.name = 'ApiError'
    this.status = status
    this.isNetworkError = status === null
  }
}

export type RequestOptions = {
  signal?: AbortSignal
  timeoutMs?: number
}

function errorMessage(body: unknown, status: number): string {
  if (typeof body === 'object' && body !== null && 'detail' in body) {
    if (typeof body.detail === 'string') return body.detail
  }
  return `Request failed (${status})`
}

export async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  options: RequestOptions = {},
): Promise<T> {
  const url = new URL(`${env.apiBaseUrl}/${path.replace(/^\/+/, '')}`)
  // Keep credentials scoped to the configured backend, even for malformed paths.
  if (url.origin !== new URL(env.apiBaseUrl).origin) {
    throw new Error('API requests must use the configured backend origin')
  }

  const { data, error } = await supabase.auth.getSession()
  if (error) throw error

  const headers = new Headers({ Accept: 'application/json' })
  if (data.session) headers.set('Authorization', `Bearer ${data.session.access_token}`)
  if (body !== undefined) headers.set('Content-Type', 'application/json')
  const json = body === undefined ? undefined : JSON.stringify(body)

  const timeout = AbortSignal.timeout(options.timeoutMs ?? 30_000)
  const signal = options.signal ? AbortSignal.any([options.signal, timeout]) : timeout
  try {
    const response = await fetch(url, {
      method,
      headers,
      body: json,
      signal,
      redirect: 'error',
    })
    if (!response.ok) {
      const errorBody: unknown = await response.json().catch(() => null)
      throw new ApiError(errorMessage(errorBody, response.status), response.status)
    }
    if (response.status === 204) return undefined as T
    return await response.json() as T
  } catch (error) {
    if (error instanceof ApiError || options.signal?.aborted) throw error
    if (timeout.aborted) {
      throw new ApiError('Request timed out', null, { cause: error })
    }
    if (error instanceof TypeError) {
      throw new ApiError('Unable to reach the API. Check your connection and CORS configuration.', null, { cause: error })
    }
    throw error
  }
}
