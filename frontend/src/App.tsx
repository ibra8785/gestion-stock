
import { useEffect, useState } from 'react'
import './App.css'

// Rubriques principales de l'application
const navigation = [
  { name: 'Tableau de bord', icon: '▦' },
  { name: 'Produits', icon: '▤' },
  { name: 'Catégories', icon: '◫' },
  { name: 'Fournisseurs', icon: '♧' },
  { name: 'Approvisionnements', icon: '↓' },
  { name: 'Ventes', icon: '↗' },
  { name: 'Clients', icon: '♙' },
  { name: 'Dépenses', icon: '↘' },
]

// Structure des statistiques renvoyées par l'API Django
type DashboardData = {
  total_sales: number
  total_profit: number
  total_expenses: number
  net_profit: number
  sales_count: number
  stock_quantity: number
  stock_value: number
}

// Formate les montants en francs CFA
const formatMoney = (amount: number) =>
  `${new Intl.NumberFormat('fr-FR').format(amount)} FCFA`

// Calcule les coordonnées de la courbe du graphique
function createChartPoints(values: number[]) {
  const width = 720
  const height = 210
  const paddingX = 16
  const paddingY = 20
  const maximum = Math.max(...values, 1)

  return values.map((value, index) => ({
    x: paddingX + (index * (width - paddingX * 2)) / (values.length - 1),
    y: height - paddingY - (value / maximum) * (height - paddingY * 2),
  }))
}

// Données provisoires du graphique, en attendant l'API dédiée
const salesPeriods = {
  Jour: {
    labels: ['00 h', '04 h', '08 h', '12 h', '16 h', '20 h', '23 h'],
    values: [5, 12, 9, 25, 18, 32, 22],
    revenue: 185000,
    sold: 12,
    received: 25,
    transactions: 8,
    description: 'Évolution des ventes heure par heure',
  },
  Semaine: {
    labels: ['Lun.', 'Mar.', 'Mer.', 'Jeu.', 'Ven.', 'Sam.', 'Dim.'],
    values: [18, 30, 22, 45, 35, 58, 42],
    revenue: 925000,
    sold: 86,
    received: 140,
    transactions: 54,
    description: 'Évolution des ventes chaque jour',
  },
  Mois: {
    labels: ['1', '4', '7', '10', '13', '16', '19', '22', '25', '28', '31'],
    values: [20, 28, 24, 42, 35, 52, 44, 60, 48, 68, 58],
    revenue: 3850000,
    sold: 324,
    received: 560,
    transactions: 210,
    description: 'Évolution des ventes au cours du mois',
  },
  Année: {
    labels: [
      'Jan.', 'Fév.', 'Mar.', 'Avr.', 'Mai', 'Juin',
      'Juil.', 'Août', 'Sep.', 'Oct.', 'Nov.', 'Déc.',
    ],
    values: [25, 35, 30, 45, 40, 55, 48, 62, 53, 72, 64, 82],
    revenue: 42500000,
    sold: 3850,
    received: 6200,
    transactions: 2450,
    description: 'Comparaison des ventes mois par mois',
  },
}

type Period = keyof typeof salesPeriods

function App() {
  // Données du tableau de bord récupérées auprès de Django
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [apiError, setApiError] = useState('')
  const [loggingOut, setLoggingOut] = useState(false)

  // Détecte les petits écrans pour adapter la déconnexion
  const [isMobile, setIsMobile] = useState(false)

  // Rubrique active et panneau de navigation mobile
  const [activePage, setActivePage] = useState('Tableau de bord')
  const [moreOpen, setMoreOpen] = useState(false)

  // Période sélectionnée dans le graphique provisoire
  const [selectedPeriod, setSelectedPeriod] = useState<Period>('Semaine')

  // Surveille la largeur de l'écran
  useEffect(() => {
    const mediaQuery = window.matchMedia('(max-width: 760px)')

    const updateScreenSize = () => {
      setIsMobile(mediaQuery.matches)
    }

    updateScreenSize()
    mediaQuery.addEventListener('change', updateScreenSize)

    return () => {
      mediaQuery.removeEventListener('change', updateScreenSize)
    }
  }, [])

  // Charge les statistiques depuis l'API Django
  useEffect(() => {
    async function loadDashboard() {
      try {
        const response = await fetch('/api/dashboard/', {
          credentials: 'same-origin',
        })

        if (response.status === 401 || response.status === 403) {
          // Une session expirée doit repasser par la connexion
          const destination = encodeURIComponent('http://localhost:5173/')
          window.location.href =
            `http://localhost:8000/accounts/login/?next=${destination}`
          return
        }

        if (!response.ok) {
          throw new Error(`Erreur HTTP ${response.status}`)
        }

        const data: DashboardData = await response.json()
        setDashboardData(data)
        setApiError('')
      } catch (error) {
        setApiError(
          error instanceof Error
            ? error.message
            : 'Impossible de charger les statistiques.',
        )
      } finally {
        setLoading(false)
      }
    }

    void loadDashboard()
  }, [])

  // Ferme la session Django
  const handleLogout = () => {
    if (loggingOut) return

    setLoggingOut(true)
    window.location.href = 'http://localhost:8000/accounts/logout/'
  }

  // Prépare les données du graphique provisoire
  const chartData = salesPeriods[selectedPeriod]
  const chartPoints = createChartPoints(chartData.values)

  const linePath = chartPoints
    .map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`)
    .join(' ')

  const areaPath = `${linePath} L 704 210 L 16 210 Z`

  // Date affichée automatiquement selon la date du jour
  const today = new Intl.DateTimeFormat('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(new Date())

  // Change de rubrique et ferme le panneau complémentaire
  const handleNavigation = (page: string) => {
    setActivePage(page)
    setMoreOpen(false)
  }

  // Construit un bouton de navigation réutilisable
  const renderNavigationItem = (item: (typeof navigation)[number]) => (
    <button
      key={item.name}
      type="button"
      title={item.name}
      aria-label={item.name}
      className={`nav-item ${activePage === item.name ? 'active' : ''}`}
      onClick={() => handleNavigation(item.name)}
    >
      <span className="nav-icon" aria-hidden="true">
        {item.icon}
      </span>
      <span className="nav-label">{item.name}</span>
    </button>
  )

  // Indicateurs construits avec les données réelles de l'API
  const stats = dashboardData
    ? [
        {
          title: 'Ventes cumulées',
          value: formatMoney(dashboardData.total_sales),
          detail: `${dashboardData.sales_count} ventes enregistrées`,
          icon: '↗',
          color: 'green',
        },
        {
          title: 'Valeur du stock',
          value: formatMoney(dashboardData.stock_value),
          detail: `${dashboardData.stock_quantity} unités restantes`,
          icon: '◈',
          color: 'purple',
        },
        {
          title: 'Bénéfice net',
          value: formatMoney(dashboardData.net_profit),
          detail: 'Bénéfice moins dépenses',
          icon: '＋',
          color: 'blue',
        },
        {
          title: 'Dépenses cumulées',
          value: formatMoney(dashboardData.total_expenses),
          detail: 'Toutes les dépenses enregistrées',
          icon: '↘',
          color: 'orange',
        },
      ]
    : []

  return (
    <div className="app-layout">
      {/* Barre latérale pour les grands écrans */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">S</div>
          <div className="brand-text">
            <strong>SDW GROUP</strong>
            <span>Gestion commerciale</span>
          </div>
        </div>

        <div className="nav-heading">MENU PRINCIPAL</div>

        <nav className="navigation" aria-label="Navigation principale">
          {navigation.map((item) => renderNavigationItem(item))}

          {/* Bouton complémentaire pour les petits écrans */}
          <button
            type="button"
            className={`nav-item mobile-more-toggle ${moreOpen ? 'active' : ''}`}
            aria-label="Afficher les autres rubriques"
            aria-expanded={moreOpen}
            aria-controls="mobile-more-panel"
            onClick={() => setMoreOpen((open) => !open)}
          >
            <span className="nav-icon" aria-hidden="true">⋯</span>
            <span className="nav-label">Plus</span>
          </button>
        </nav>

        {moreOpen && (
          <div className="mobile-more-panel" id="mobile-more-panel">
            <div className="mobile-more-heading">AUTRES RUBRIQUES</div>
            <nav aria-label="Autres rubriques">
              {navigation.slice(4).map((item) => renderNavigationItem(item))}
            </nav>
          </div>
        )}

        <div className="sidebar-bottom">
          <div className="help-card">
            <span className="help-icon">?</span>
            <strong>Besoin d’aide ?</strong>
            <p>Retrouvez les informations sur votre application.</p>
          </div>

          {/* Profil et déconnexion sur ordinateur */}
          <div className="user-profile">
            <div className="avatar">G</div>

            <div className="user-info">
              <strong>Gestionnaire</strong>
              <span>Compte connecté</span>
            </div>

            <button
              type="button"
              className="sidebar-logout-button"
              onClick={handleLogout}
              disabled={loggingOut}
              title="Fermer la session"
              aria-label="Se déconnecter"
            >
              <span aria-hidden="true">↪</span>
              {loggingOut ? 'Déconnexion...' : 'Déconnexion'}
            </button>
          </div>
        </div>
      </aside>

      {/* Contenu principal */}
      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">
            <span>Application</span>
            <span className="breadcrumb-separator">/</span>
            <strong>{activePage}</strong>
          </div>

          <div className="topbar-actions">
            <span className="today">{today}</span>

            {/* Déconnexion visible en haut sur petit écran */}
            {isMobile && (
              <button
                type="button"
                className="mobile-topbar-logout"
                onClick={handleLogout}
                disabled={loggingOut}
                aria-label="Se déconnecter"
                title="Fermer la session"
              >
                <span aria-hidden="true">↪</span>
                <span>
                  {loggingOut ? 'Déconnexion...' : 'Déconnexion'}
                </span>
              </button>
            )}

            <button
              className="notification-button"
              type="button"
              aria-label="Notifications"
            >
              ♧
              <span className="notification-dot" />
            </button>

            <div className="topbar-avatar">G</div>
          </div>
        </header>

        {activePage === 'Tableau de bord' ? (
          <div className="dashboard">
            {/* Titre et action principale */}
            <section className="page-heading">
              <div>
                <span className="eyebrow">VUE D'ENSEMBLE</span>
                <h1>Tableau de bord</h1>
                <p>Voici ce qui se passe dans votre gestion de stock.</p>
              </div>

              <button className="primary-button" type="button">
                <span aria-hidden="true">＋</span>
                Nouvelle opération
              </button>
            </section>

            {/* Statistiques réelles chargées depuis Django */}
            <section className="stats-grid" aria-label="Statistiques">
              {loading && <p>Chargement des statistiques...</p>}

              {!loading && apiError && (
                <p role="alert">
                  Impossible de charger les statistiques : {apiError}
                </p>
              )}

              {!loading &&
                !apiError &&
                stats.map((stat) => (
                  <article
                    className={`stat-card stat-${stat.color}`}
                    key={stat.title}
                  >
                    <div className="stat-top">
                      <span className="stat-title">{stat.title}</span>
                      <span className="stat-icon" aria-hidden="true">
                        {stat.icon}
                      </span>
                    </div>
                    <strong className="stat-value">{stat.value}</strong>
                    <span className="stat-detail">{stat.detail}</span>
                  </article>
                ))}
            </section>

            {/* Graphique provisoire : valeurs non issues de Django */}
            <section
              className="panel sales-panel"
              aria-label="Évolution illustrative des ventes"
              style={{ padding: '24px', marginBottom: '24px' }}
            >
              <div
                className="panel-heading"
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  gap: '16px',
                  flexWrap: 'wrap',
                }}
              >
                <div>
                  <h2>Évolution des ventes</h2>
                  <p>{chartData.description}</p>
                </div>

                <div
                  className="sales-periods"
                  role="group"
                  aria-label="Choisir une période"
                  style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}
                >
                  {(Object.keys(salesPeriods) as Period[]).map((period) => (
                    <button
                      key={period}
                      type="button"
                      aria-pressed={selectedPeriod === period}
                      onClick={() => setSelectedPeriod(period)}
                      style={{
                        border: '1px solid',
                        borderColor:
                          selectedPeriod === period ? '#048B9A' : '#E1E7EA',
                        borderRadius: '8px',
                        padding: '9px 13px',
                        background:
                          selectedPeriod === period ? '#048B9A' : 'transparent',
                        color: selectedPeriod === period ? '#FFFFFF' : 'inherit',
                        fontWeight: 600,
                        cursor: 'pointer',
                      }}
                    >
                      {period}
                    </button>
                  ))}
                </div>
              </div>

              <div style={{ marginTop: '26px' }}>
                <span
                  style={{
                    display: 'block',
                    color: '#64748B',
                    fontSize: '14px',
                    marginBottom: '6px',
                  }}
                >
                  Chiffre d'affaires illustratif de la période
                </span>

                <strong
                  style={{
                    display: 'block',
                    color: '#048B9A',
                    fontSize: 'clamp(24px, 3vw, 32px)',
                    marginBottom: '14px',
                  }}
                >
                  {formatMoney(chartData.revenue)}
                </strong>

                <div style={{ width: '100%', overflow: 'hidden' }}>
                  <svg
                    viewBox="0 0 720 250"
                    role="img"
                    aria-label={`Graphique illustratif : ${selectedPeriod.toLowerCase()}`}
                    style={{ display: 'block', width: '100%', height: 'auto' }}
                  >
                    <defs>
                      <linearGradient id="sales-area" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#048B9A" stopOpacity="0.22" />
                        <stop offset="100%" stopColor="#048B9A" stopOpacity="0.01" />
                      </linearGradient>
                    </defs>

                    {[30, 75, 120, 165, 210].map((y) => (
                      <line
                        key={y}
                        x1="16"
                        y1={y}
                        x2="704"
                        y2={y}
                        stroke="currentColor"
                        strokeOpacity="0.12"
                        strokeDasharray="4 5"
                      />
                    ))}

                    <path d={areaPath} fill="url(#sales-area)" />

                    <path
                      d={linePath}
                      fill="none"
                      stroke="#048B9A"
                      strokeWidth="3.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />

                    {chartPoints.map((point, index) => (
                      <circle
                        key={`${selectedPeriod}-${index}`}
                        cx={point.x}
                        cy={point.y}
                        r="4"
                        fill="#FFFFFF"
                        stroke="#048B9A"
                        strokeWidth="2.5"
                      >
                        <title>
                          {chartData.labels[index]} : valeur illustrative{' '}
                          {chartData.values[index]}
                        </title>
                      </circle>
                    ))}

                    {chartData.labels.map((label, index) => {
                      const point = chartPoints[index]
                      const showLabel =
                        chartData.labels.length <= 8 ||
                        index === 0 ||
                        index === chartData.labels.length - 1 ||
                        index % 2 === 0

                      return showLabel ? (
                        <text
                          key={`${selectedPeriod}-label-${label}`}
                          x={point.x}
                          y="242"
                          textAnchor="middle"
                          fontSize="12"
                          fill="currentColor"
                          opacity="0.7"
                        >
                          {label}
                        </text>
                      ) : null
                    })}
                  </svg>
                </div>
              </div>

              <div
                className="sales-summary-grid"
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
                  gap: '14px',
                  marginTop: '24px',
                }}
              >
                <article
                  className="sales-summary-card"
                  style={{
                    background: 'rgba(4, 139, 154, 0.08)',
                    borderRadius: '12px',
                    padding: '17px',
                  }}
                >
                  <span style={{ color: '#64748B', fontSize: '13px' }}>
                    Produits vendus
                  </span>
                  <strong style={{ display: 'block', fontSize: '25px', margin: '8px 0 4px' }}>
                    {new Intl.NumberFormat('fr-FR').format(chartData.sold)}
                  </strong>
                  <span style={{ color: '#64748B', fontSize: '12px' }}>
                    Unités illustratives
                  </span>
                </article>

                <article
                  className="sales-summary-card"
                  style={{
                    background: 'rgba(16, 185, 129, 0.09)',
                    borderRadius: '12px',
                    padding: '17px',
                  }}
                >
                  <span style={{ color: '#64748B', fontSize: '13px' }}>
                    Produits réceptionnés
                  </span>
                  <strong style={{ display: 'block', fontSize: '25px', margin: '8px 0 4px' }}>
                    {new Intl.NumberFormat('fr-FR').format(chartData.received)}
                  </strong>
                  <span style={{ color: '#64748B', fontSize: '12px' }}>
                    Unités illustratives
                  </span>
                </article>

                <article
                  className="sales-summary-card"
                  style={{
                    background: 'rgba(99, 102, 241, 0.08)',
                    borderRadius: '12px',
                    padding: '17px',
                  }}
                >
                  <span style={{ color: '#64748B', fontSize: '13px' }}>
                    Nombre de ventes
                  </span>
                  <strong style={{ display: 'block', fontSize: '25px', margin: '8px 0 4px' }}>
                    {new Intl.NumberFormat('fr-FR').format(chartData.transactions)}
                  </strong>
                  <span style={{ color: '#64748B', fontSize: '12px' }}>
                    Transactions illustratives
                  </span>
                </article>
              </div>

              <p style={{ color: '#64748B', fontSize: '12px', marginTop: '18px', lineHeight: 1.5 }}>
                Le graphique et ses indicateurs restent fictifs pour le moment.
                Nous les connecterons à des données calculées par l'API.
              </p>
            </section>

            {/* Alertes de stock provisoires */}
            <section className="content-grid">
              <article className="panel stock-panel">
                <div className="panel-heading">
                  <div>
                    <h2>Alertes de stock</h2>
                    <p>Produits nécessitant votre attention</p>
                  </div>
                  <span className="alert-badge">Données provisoires</span>
                </div>

                <p>
                  Cette section sera connectée aux quantités réellement
                  disponibles lorsque nous aurons défini le seuil de stock faible.
                </p>
              </article>

              <article className="panel actions-panel">
                <div className="panel-heading">
                  <div>
                    <h2>Actions rapides</h2>
                    <p>Accédez directement aux opérations</p>
                  </div>
                </div>

                <div className="quick-actions">
                  <button
                    className="quick-action"
                    type="button"
                    onClick={() => handleNavigation('Produits')}
                  >
                    <span className="quick-icon quick-blue">＋</span>
                    <span>
                      <strong>Ajouter un produit</strong>
                      <small>Enregistrer une référence</small>
                    </span>
                    <span className="quick-arrow" aria-hidden="true">→</span>
                  </button>

                  <button
                    className="quick-action"
                    type="button"
                    onClick={() => handleNavigation('Approvisionnements')}
                  >
                    <span className="quick-icon quick-purple">↓</span>
                    <span>
                      <strong>Approvisionner</strong>
                      <small>Enregistrer une entrée de stock</small>
                    </span>
                    <span className="quick-arrow" aria-hidden="true">→</span>
                  </button>

                  <button
                    className="quick-action"
                    type="button"
                    onClick={() => handleNavigation('Ventes')}
                  >
                    <span className="quick-icon quick-green">↗</span>
                    <span>
                      <strong>Nouvelle vente</strong>
                      <small>Enregistrer une sortie de stock</small>
                    </span>
                    <span className="quick-arrow" aria-hidden="true">→</span>
                  </button>
                </div>
              </article>
            </section>

            {/* Historique des mouvements à connecter ensuite */}
            <section className="panel movements-panel">
              <div className="panel-heading">
                <div>
                  <h2>Mouvements récents</h2>
                  <p>Les dernières entrées et sorties de stock</p>
                </div>

                <button
                  className="text-button"
                  type="button"
                  onClick={() => handleNavigation('Approvisionnements')}
                >
                  Voir l'historique <span aria-hidden="true">→</span>
                </button>
              </div>

              <p>
                L'historique réel sera affiché après connexion à l'API des
                mouvements de stock.
              </p>
            </section>

            <footer className="dashboard-footer">
              <span>Gestion Stock · Gestion commerciale</span>
              <span>Statistiques générales connectées à Django</span>
            </footer>
          </div>
        ) : (
          /* Pages provisoires des autres rubriques */
          <section className="placeholder-page">
            <span className="eyebrow">GESTION COMMERCIALE</span>
            <h1>{activePage}</h1>
            <p>
              Cette rubrique sera développée progressivement dans notre projet.
            </p>
            <button
              className="primary-button"
              type="button"
              onClick={() => handleNavigation('Tableau de bord')}
            >
              ← Retour au tableau de bord
            </button>
          </section>
        )}
      </main>
    </div>
  )
}

export default App
