// frontend/src/pages/SuppliersPage.tsx

import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { apiRequest } from '../services/api'
import './SuppliersPage.css'

// Informations d'un fournisseur renvoyées par Django
interface Supplier {
  id: number
  reference: string
  name: string
  phone: string
  address: string
}

// Champs du formulaire
interface SupplierForm {
  reference: string
  name: string
  phone: string
  address: string
}

// Valeurs initiales du formulaire
const emptyForm: SupplierForm = {
  reference: '',
  name: '',
  phone: '',
  address: '',
}

function SuppliersPage() {
  const [suppliers, setSuppliers] = useState<Supplier[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  // Le formulaire est fermé au premier affichage
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)

  const [form, setForm] = useState<SupplierForm>(emptyForm)
  const [search, setSearch] = useState('')
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState<'success' | 'error'>(
    'success',
  )

  // Charge les fournisseurs depuis l'API Django
  async function loadSuppliers() {
    setLoading(true)

    try {
      const data = await apiRequest<Supplier[]>('/api/suppliers/')
      setSuppliers(data)
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : 'Impossible de charger les fournisseurs.',
      )
      setMessageType('error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadSuppliers()
  }, [])

  // Filtre la liste en fonction de la recherche
  const filteredSuppliers = useMemo(() => {
    const query = search.trim().toLowerCase()

    if (!query) return suppliers

    return suppliers.filter((supplier) =>
      [
        supplier.reference,
        supplier.name,
        supplier.phone,
        supplier.address,
      ].some((value) => value?.toLowerCase().includes(query)),
    )
  }, [suppliers, search])

  // Met à jour un champ du formulaire
  function handleChange(field: keyof SupplierForm, value: string) {
    setForm((currentForm) => ({
      ...currentForm,
      [field]: value,
    }))
  }

  // Ferme le formulaire et réinitialise ses champs
  function resetForm() {
    setForm(emptyForm)
    setEditingId(null)
    setShowForm(false)
  }

  // Ouvre un formulaire vierge pour ajouter un fournisseur
  function handleAdd() {
    setForm(emptyForm)
    setEditingId(null)
    setMessage('')
    setShowForm(true)
  }

  // Ouvre le formulaire avec les données du fournisseur sélectionné
  function handleEdit(supplier: Supplier) {
    setEditingId(supplier.id)
    setForm({
      reference: supplier.reference,
      name: supplier.name,
      phone: supplier.phone,
      address: supplier.address,
    })
    setMessage('')
    setShowForm(true)

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    })
  }

  // Enregistre un nouveau fournisseur ou les modifications
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    setSaving(true)
    setMessage('')

    try {
      const payload: SupplierForm = {
        reference: form.reference.trim(),
        name: form.name.trim(),
        phone: form.phone.trim(),
        address: form.address.trim(),
      }

      if (editingId !== null) {
        await apiRequest<Supplier>(`/api/suppliers/${editingId}/`, {
          method: 'PUT',
          body: JSON.stringify(payload),
        })

        setMessage('Le fournisseur a été modifié avec succès.')
      } else {
        await apiRequest<Supplier>('/api/suppliers/', {
          method: 'POST',
          body: JSON.stringify(payload),
        })

        setMessage('Le fournisseur a été ajouté avec succès.')
      }

      setMessageType('success')
      resetForm()
      await loadSuppliers()
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "Une erreur est survenue lors de l'enregistrement.",
      )
      setMessageType('error')
    } finally {
      setSaving(false)
    }
  }

  // Supprime un fournisseur après confirmation
  async function handleDelete(supplier: Supplier) {
    const confirmed = window.confirm(
      `Voulez-vous vraiment supprimer le fournisseur « ${supplier.name} » ?`,
    )

    if (!confirmed) return

    setMessage('')

    try {
      await apiRequest<void>(`/api/suppliers/${supplier.id}/`, {
        method: 'DELETE',
      })

      if (editingId === supplier.id) {
        resetForm()
      }

      setMessage('Le fournisseur a été supprimé.')
      setMessageType('success')

      await loadSuppliers()
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : 'Impossible de supprimer ce fournisseur.',
      )
      setMessageType('error')
    }
  }

  return (
    <section className="suppliers-page">
      {/* En-tête et bouton d'ajout */}
      <header className="suppliers-heading">
        <div>
          <span className="suppliers-eyebrow">GESTION DES ACHATS</span>
          <h1>Fournisseurs</h1>
          <p>Gérez les coordonnées et les références de vos fournisseurs.</p>
        </div>

        <button
          type="button"
          className="suppliers-primary-button"
          onClick={handleAdd}
        >
          <span aria-hidden="true">＋</span>
          Ajouter un fournisseur
        </button>
      </header>

      {/* Messages de réussite ou d'erreur */}
      {message && (
        <div
          className={`suppliers-message suppliers-message-${messageType}`}
          role="status"
        >
          <span>{message}</span>

          <button
            type="button"
            className="suppliers-message-close"
            onClick={() => setMessage('')}
            aria-label="Fermer le message"
          >
            ×
          </button>
        </div>
      )}

      {/* Le formulaire apparaît uniquement lorsqu'on le demande */}
      {showForm && (
        <section className="suppliers-panel suppliers-form-panel">
          <div className="suppliers-panel-heading">
            <div>
              <h2>
                {editingId !== null
                  ? 'Modifier le fournisseur'
                  : 'Nouveau fournisseur'}
              </h2>
              <p>
                {editingId !== null
                  ? 'Modifiez les informations puis enregistrez.'
                  : 'Renseignez les informations du fournisseur.'}
              </p>
            </div>

            <button
              type="button"
              className="suppliers-close-button"
              onClick={resetForm}
              aria-label="Fermer le formulaire"
              title="Fermer"
            >
              ×
            </button>
          </div>

          <form className="suppliers-form" onSubmit={handleSubmit}>
            <div className="suppliers-form-grid">
              <label className="suppliers-field">
                <span>Référence *</span>
                <input
                  type="text"
                  name="reference"
                  placeholder="Ex. FOUR-002"
                  value={form.reference}
                  onChange={(event) =>
                    handleChange('reference', event.target.value)
                  }
                  required
                />
              </label>

              <label className="suppliers-field">
                <span>Nom du fournisseur *</span>
                <input
                  type="text"
                  name="name"
                  placeholder="Ex. Société ABC"
                  value={form.name}
                  onChange={(event) =>
                    handleChange('name', event.target.value)
                  }
                  required
                />
              </label>

              <label className="suppliers-field">
                <span>Téléphone</span>
                <input
                  type="tel"
                  name="phone"
                  placeholder="Ex. +225 07 00 00 00 00"
                  value={form.phone}
                  onChange={(event) =>
                    handleChange('phone', event.target.value)
                  }
                />
              </label>

              <label className="suppliers-field">
                <span>Adresse</span>
                <input
                  type="text"
                  name="address"
                  placeholder="Ex. Abidjan"
                  value={form.address}
                  onChange={(event) =>
                    handleChange('address', event.target.value)
                  }
                />
              </label>
            </div>

            <div className="suppliers-form-actions">
              <button
                type="button"
                className="suppliers-secondary-button"
                onClick={resetForm}
                disabled={saving}
              >
                Annuler
              </button>

              <button
                type="submit"
                className="suppliers-primary-button"
                disabled={saving}
              >
                {saving
                  ? 'Enregistrement...'
                  : editingId !== null
                    ? 'Enregistrer les modifications'
                    : 'Ajouter le fournisseur'}
              </button>
            </div>
          </form>
        </section>
      )}

      {/* Liste des fournisseurs */}
      <section className="suppliers-panel suppliers-list-panel">
        <div className="suppliers-panel-heading suppliers-list-heading">
          <div>
            <h2>Liste des fournisseurs</h2>
            <p>
              {filteredSuppliers.length}{' '}
              {filteredSuppliers.length > 1
                ? 'fournisseurs affichés'
                : 'fournisseur affiché'}
            </p>
          </div>

          <label className="suppliers-search">
            <span aria-hidden="true">⌕</span>
            <input
              type="search"
              placeholder="Rechercher..."
              aria-label="Rechercher un fournisseur"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </label>
        </div>

        {loading ? (
          <div className="suppliers-state">
            <span className="suppliers-loader" />
            <p>Chargement des fournisseurs...</p>
          </div>
        ) : filteredSuppliers.length === 0 ? (
          <div className="suppliers-state">
            <span className="suppliers-empty-icon" aria-hidden="true">
              ♧
            </span>
            <h3>
              {search
                ? 'Aucun résultat'
                : 'Aucun fournisseur enregistré'}
            </h3>
            <p>
              {search
                ? 'Essayez un autre nom, une autre référence ou un autre numéro.'
                : 'Cliquez sur « Ajouter un fournisseur » pour enregistrer votre premier fournisseur.'}
            </p>
          </div>
        ) : (
          <div className="suppliers-table-container">
            <table className="suppliers-table">
              <thead>
                <tr>
                  <th>Référence</th>
                  <th>Fournisseur</th>
                  <th>Téléphone</th>
                  <th>Adresse</th>
                  <th className="suppliers-actions-heading">Actions</th>
                </tr>
              </thead>

              <tbody>
                {filteredSuppliers.map((supplier) => (
                  <tr key={supplier.id}>
                    <td>
                      <span className="suppliers-reference">
                        {supplier.reference}
                      </span>
                    </td>

                    <td>
                      <div className="suppliers-name-cell">
                        <span className="suppliers-avatar">
                          {supplier.name.charAt(0).toUpperCase()}
                        </span>
                        <strong>{supplier.name}</strong>
                      </div>
                    </td>

                    <td>{supplier.phone || '—'}</td>
                    <td>{supplier.address || '—'}</td>

                    <td>
                      <div className="suppliers-row-actions">
                        <button
                          type="button"
                          className="suppliers-icon-button"
                          onClick={() => handleEdit(supplier)}
                          aria-label={`Modifier ${supplier.name}`}
                          title="Modifier"
                        >
                          <svg
                            viewBox="0 0 24 24"
                            width="17"
                            height="17"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="1.8"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            aria-hidden="true"
                          >
                            <path d="M12 20h9" />
                            <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L8 18l-4 1 1-4Z" />
                          </svg>
                        </button>

                        <button
                          type="button"
                          className="suppliers-icon-button suppliers-icon-button--danger"
                          onClick={() => void handleDelete(supplier)}
                          aria-label={`Supprimer ${supplier.name}`}
                          title="Supprimer"
                        >
                          <svg
                            viewBox="0 0 24 24"
                            width="17"
                            height="17"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="1.8"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            aria-hidden="true"
                          >
                            <path d="M3 6h18" />
                            <path d="M8 6V4h8v2" />
                            <path d="m19 6-1 14H6L5 6" />
                            <path d="M10 11v5M14 11v5" />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </section>
  )
}

export default SuppliersPage