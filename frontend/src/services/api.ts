
/**
 * Service commun de communication avec l'API Django.
 * Toutes les pages du frontend pourront utiliser ces fonctions.
 */

/**
 * Récupère le jeton CSRF enregistré dans les cookies Django.
 * Ce jeton protège les requêtes qui modifient les données.
 */
function getCsrfToken(): string {
  const cookies = document.cookie.split(';')

  const csrfCookie = cookies.find((cookie) =>
    cookie.trim().startsWith('csrftoken='),
  )

  if (!csrfCookie) {
    return ''
  }

  return decodeURIComponent(csrfCookie.trim().substring('csrftoken='.length))
}

/**
 * Envoie une requête à l'API et retourne les données reçues.
 *
 * Exemples :
 * apiRequest<Product[]>('/api/products/')
 * apiRequest<Product>('/api/products/', {
 *   method: 'POST',
 *   body: JSON.stringify(product),
 * })
 */
export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers)

  headers.set('Accept', 'application/json')

  const method = (options.method ?? 'GET').toUpperCase()
  const isSafeMethod = ['GET', 'HEAD', 'OPTIONS', 'TRACE'].includes(method)

  if (options.body && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }

  if (!isSafeMethod) {
    const csrfToken = getCsrfToken()

    if (csrfToken) {
      headers.set('X-CSRFToken', csrfToken)
    }
  }

  const response = await fetch(path, {
    ...options,
    method,
    headers,
    credentials: 'same-origin',
  })

  if (response.status === 204) {
    return undefined as T
  }

  const contentType = response.headers.get('content-type')
  let data: unknown

  if (contentType?.includes('application/json')) {
    data = await response.json()
  } else {
    data = await response.text()
  }

  if (!response.ok) {
    let message = `Erreur HTTP ${response.status}`

    if (typeof data === 'string' && data.trim()) {
      message = data
    } else if (typeof data === 'object' && data !== null) {
      const errorData = data as Record<string, unknown>

      if (typeof errorData.detail === 'string') {
        message = errorData.detail
      } else if (typeof errorData.message === 'string') {
        message = errorData.message
      } else {
        message = Object.entries(errorData)
          .map(([field, errors]) => {
            const description = Array.isArray(errors)
              ? errors.join(', ')
              : String(errors)

            return `${field} : ${description}`
          })
          .join(' | ')
      }
    }

    throw new Error(message)
  }

  return data as T
}
