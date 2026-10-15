
import { useEffect, useState } from 'react'
import App from './App'

type AuthStatus = {
  is_authenticated: boolean
  username: string | null
}

export default function AuthGate() {
  const [checking, setChecking] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    // Vérifie la session Django avant d'afficher le tableau de bord.
    async function checkAuthentication() {
      try {
        const response = await fetch('/accounts/auth-status/', {
          credentials: 'same-origin',
        })

        if (!response.ok) {
          throw new Error('Impossible de vérifier la connexion.')
        }

        const data: AuthStatus = await response.json()

        if (!data.is_authenticated) {
          // Redirige vers le formulaire de connexion Django.
          const destination = encodeURIComponent(
            'http://localhost:5173/',
          )

          window.location.href =
            `http://localhost:8000/accounts/login/?next=${destination}`

          return
        }

        // La session est valide : le tableau de bord peut s'afficher.
        setChecking(false)
      } catch {
        setError(
          'Impossible de contacter le serveur. Vérifie que Django fonctionne.',
        )
        setChecking(false)
      }
    }

    void checkAuthentication()
  }, [])

  if (checking) {
    return (
      <main
        style={{
          minHeight: '100vh',
          display: 'grid',
          placeItems: 'center',
          fontFamily: 'Arial, sans-serif',
        }}
      >
        Vérification de la connexion...
      </main>
    )
  }

  if (error) {
    return (
      <main
        style={{
          minHeight: '100vh',
          display: 'grid',
          placeContent: 'center',
          gap: '16px',
          padding: '24px',
          fontFamily: 'Arial, sans-serif',
          textAlign: 'center',
        }}
      >
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>
          Réessayer
        </button>
      </main>
    )
  }

  return <App />
}
