import { useCallback, useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import { apiRequest } from '../services/api'
import './ProductsPage.css'

/** Structure d'un produit renvoyé par l'API Django. */
type Product = {
  id: number
  reference: string
  name: string
  category: string
  format: string
  unit: string
  selling_price: string
}

/** Champs du formulaire de création et de modification. */
type ProductForm = {
  reference: string
  name: string
  category: string
  format: string
  unit: string
  selling_price: string
}

const emptyForm: ProductForm = {
  reference: '',
  name: '',
  category: '',
  format: '',
  unit: '',
  selling_price: '',
}

/** Formate un montant en francs CFA. */
function formatCurrency(value: string | number): string {
  const amount = Number(value)

  if (!Number.isFinite(amount)) {
    return '—'
  }

  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'XOF',
    maximumFractionDigits: 0,
  }).format(amount)
}

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [search, setSearch] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingProduct, setEditingProduct] = useState<Product | null>(null)
  const [form, setForm] = useState<ProductForm>(emptyForm)
  const [saving, setSaving] = useState(false)
  const [deletingId, setDeletingId] = useState<number | null>(null)

  /** Charge les produits enregistrés dans Django. */
  const loadProducts = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const data = await apiRequest<Product[]>('/api/products/')
      setProducts(data)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Impossible de charger les produits.',
      )
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadProducts()
  }, [loadProducts])

  /** Recherche dans la référence, le nom, la catégorie et le format. */
  const filteredProducts = useMemo(() => {
    const query = search.trim().toLocaleLowerCase('fr')

    if (!query) {
      return products
    }

    return products.filter((product) =>
      [
        product.reference,
        product.name,
        product.category,
        product.format,
        product.unit,
      ].some((value) => value.toLocaleLowerCase('fr').includes(query)),
    )
  }, [products, search])

  /** Prépare un formulaire vierge pour la création. */
  function openCreateForm() {
    setEditingProduct(null)
    setForm(emptyForm)
    setError('')
    setSuccess('')
    setShowForm(true)
  }

  /** Préremplit le formulaire avec le produit sélectionné. */
  function openEditForm(product: Product) {
    setEditingProduct(product)
    setForm({
      reference: product.reference,
      name: product.name,
      category: product.category,
      format: product.format,
      unit: product.unit,
      selling_price: product.selling_price,
    })
    setError('')
    setSuccess('')
    setShowForm(true)
  }

  /** Met à jour un champ du formulaire. */
  function updateField(field: keyof ProductForm, value: string) {
    setForm((previous) => ({
      ...previous,
      [field]: value,
    }))
  }

  /** Enregistre le nouveau produit ou les modifications. */
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setSuccess('')

    const price = Number(form.selling_price)

    if (!Number.isFinite(price) || price < 0) {
      setError('Le prix de vente doit être un nombre positif ou nul.')
      return
    }

    const payload: ProductForm = {
      reference: form.reference.trim(),
      name: form.name.trim(),
      category: form.category.trim(),
      format: form.format.trim(),
      unit: form.unit.trim(),
      selling_price: form.selling_price,
    }

    setSaving(true)

    try {
      if (editingProduct) {
        await apiRequest<Product>(
          `/api/products/${editingProduct.id}/`,
          {
            method: 'PUT',
            body: JSON.stringify(payload),
          },
        )

        setSuccess('Le produit a été modifié avec succès.')
      } else {
        await apiRequest<Product>('/api/products/', {
          method: 'POST',
          body: JSON.stringify(payload),
        })

        setSuccess('Le produit a été ajouté avec succès.')
      }

      setShowForm(false)
      setEditingProduct(null)
      setForm(emptyForm)
      await loadProducts()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Une erreur est survenue pendant l’enregistrement.',
      )
    } finally {
      setSaving(false)
    }
  }

  /** Demande confirmation avant de supprimer un produit. */
  async function handleDelete(product: Product) {
    const confirmed = window.confirm(
      `Voulez-vous vraiment supprimer le produit « ${product.name} » (${product.reference}) ?`,
    )

    if (!confirmed) {
      return
    }

    setError('')
    setSuccess('')
    setDeletingId(product.id)

    try {
      await apiRequest<void>(`/api/products/${product.id}/`, {
        method: 'DELETE',
      })

      setProducts((previous) =>
        previous.filter((item) => item.id !== product.id),
      )
      setSuccess(`Le produit « ${product.name} » a été supprimé.`)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Impossible de supprimer ce produit.',
      )
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <section className="products-page">
      <header className="products-page__header">
        <div>
          <p className="products-page__eyebrow">GESTION DU STOCK</p>
          <h1>Produits</h1>
          <p className="products-page__description">
            Consulte et gère les produits enregistrés dans ton stock.
          </p>
        </div>

        <button
          className="products-page__primary-button"
          type="button"
          onClick={openCreateForm}
        >
          <span aria-hidden="true">＋</span>
          Nouveau produit
        </button>
      </header>

      {error && (
        <div
          className="products-page__alert products-page__alert--error"
          role="alert"
        >
          <span>{error}</span>
          <button
            type="button"
            onClick={() => setError('')}
            aria-label="Fermer"
          >
            ×
          </button>
        </div>
      )}

      {success && (
        <div
          className="products-page__alert products-page__alert--success"
          role="status"
        >
          <span>{success}</span>
          <button
            type="button"
            onClick={() => setSuccess('')}
            aria-label="Fermer"
          >
            ×
          </button>
        </div>
      )}

      <div className="products-page__summary">
        <div className="products-page__summary-icon" aria-hidden="true">
          ▦
        </div>
        <div>
          <p className="products-page__summary-label">Produits enregistrés</p>
          <strong>{products.length}</strong>
        </div>
      </div>

      <div className="products-page__toolbar">
        <label className="products-page__search">
          <span aria-hidden="true">⌕</span>
          <span className="products-page__visually-hidden">
            Rechercher un produit
          </span>
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Rechercher par référence, nom, catégorie..."
          />
        </label>

        <button
          className="products-page__secondary-button"
          type="button"
          onClick={() => void loadProducts()}
          disabled={loading}
        >
          ↻ Actualiser
        </button>
      </div>

      {showForm && (
        <div className="products-page__form-panel">
          <div className="products-page__form-header">
            <div>
              <h2>
                {editingProduct ? 'Modifier le produit' : 'Nouveau produit'}
              </h2>
              <p>Les informations seront enregistrées dans Django.</p>
            </div>

            <button
              className="products-page__close-button"
              type="button"
              onClick={() => setShowForm(false)}
              aria-label="Fermer le formulaire"
              disabled={saving}
            >
              ×
            </button>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="products-page__form-grid">
              <label>
                Référence *
                <input
                  required
                  maxLength={100}
                  value={form.reference}
                  onChange={(event) =>
                    updateField('reference', event.target.value)
                  }
                  placeholder="Ex. CC-05L"
                />
              </label>

              <label>
                Nom du produit *
                <input
                  required
                  maxLength={200}
                  value={form.name}
                  onChange={(event) =>
                    updateField('name', event.target.value)
                  }
                  placeholder="Ex. Coca-Cola"
                />
              </label>

              <label>
                Catégorie *
                <input
                  required
                  maxLength={100}
                  value={form.category}
                  onChange={(event) =>
                    updateField('category', event.target.value)
                  }
                  placeholder="Ex. Boissons"
                />
              </label>

              <label>
                Format
                <input
                  maxLength={100}
                  value={form.format}
                  onChange={(event) =>
                    updateField('format', event.target.value)
                  }
                  placeholder="Ex. 0.5"
                />
              </label>

              <label>
                Unité
                <input
                  maxLength={50}
                  value={form.unit}
                  onChange={(event) =>
                    updateField('unit', event.target.value)
                  }
                  placeholder="Ex. L, pièce, carton"
                />
              </label>

              <label>
                Prix de vente (FCFA) *
                <input
                  required
                  type="number"
                  min="0"
                  step="0.01"
                  value={form.selling_price}
                  onChange={(event) =>
                    updateField('selling_price', event.target.value)
                  }
                  placeholder="Ex. 120000"
                />
              </label>
            </div>

            <div className="products-page__form-actions">
              <button
                className="products-page__secondary-button"
                type="button"
                onClick={() => setShowForm(false)}
                disabled={saving}
              >
                Annuler
              </button>

              <button
                className="products-page__primary-button"
                type="submit"
                disabled={saving}
              >
                {saving
                  ? 'Enregistrement...'
                  : editingProduct
                    ? 'Enregistrer les modifications'
                    : 'Enregistrer le produit'}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="products-page__table-panel">
        <div className="products-page__table-heading">
          <div>
            <h2>Liste des produits</h2>
            <p>
              {filteredProducts.length}{' '}
              {filteredProducts.length > 1 ? 'résultats' : 'résultat'}
            </p>
          </div>
        </div>

        {loading ? (
          <div className="products-page__state">
            <span
              className="products-page__spinner"
              aria-hidden="true"
            />
            Chargement des produits...
          </div>
        ) : filteredProducts.length === 0 ? (
          <div className="products-page__state">
            <span
              className="products-page__empty-icon"
              aria-hidden="true"
            >
              ▦
            </span>
            <strong>
              {search
                ? 'Aucun produit trouvé'
                : 'Aucun produit enregistré'}
            </strong>
            <p>
              {search
                ? 'Essaie une autre recherche.'
                : 'Ajoute ton premier produit pour commencer.'}
            </p>
            {!search && (
              <button
                className="products-page__primary-button"
                type="button"
                onClick={openCreateForm}
              >
                Ajouter un produit
              </button>
            )}
          </div>
        ) : (
          <div className="products-page__table-scroll">
            <table className="products-page__table">
              <thead>
                <tr>
                  <th>Produit</th>
                  <th>Référence</th>
                  <th>Catégorie</th>
                  <th>Format / unité</th>
                  <th className="products-page__price-heading">
                    Prix de vente
                  </th>
                  <th className="products-page__actions-heading">
                    Actions
                  </th>
                </tr>
              </thead>

              <tbody>
                {filteredProducts.map((product) => (
                  <tr key={product.id}>
                    <td>
                      <div className="products-page__product-name">
                        <span
                          className="products-page__product-avatar"
                          aria-hidden="true"
                        >
                          {product.name.trim().charAt(0).toUpperCase() || '?'}
                        </span>
                        <strong>{product.name}</strong>
                      </div>
                    </td>

                    <td>
                      <span className="products-page__reference">
                        {product.reference}
                      </span>
                    </td>

                    <td>
                      <span className="products-page__category">
                        {product.category || 'Sans catégorie'}
                      </span>
                    </td>

                    <td>
                      {[product.format, product.unit]
                        .filter(Boolean)
                        .join(' ') || '—'}
                    </td>

                    <td className="products-page__price">
                      {formatCurrency(product.selling_price)}
                    </td>

                    <td>
                      <div className="products-page__row-actions">
                        <button
                          className="products-page__icon-button"
                          type="button"
                          onClick={() => openEditForm(product)}
                          aria-label={`Modifier ${product.name}`}
                          title="Modifier"
                        >
                          <svg
                            aria-hidden="true"
                            viewBox="0 0 24 24"
                            width="16"
                            height="16"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="1.8"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          >
                            <path d="M12 20h9" />
                            <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L8 18l-4 1 1-4Z" />
                          </svg>
                        </button>

                        <button
                          className="products-page__icon-button products-page__icon-button--danger"
                          type="button"
                          onClick={() => void handleDelete(product)}
                          disabled={deletingId === product.id}
                          aria-label={`Supprimer ${product.name}`}
                          title="Supprimer"
                        >
                          {deletingId === product.id ? (
                            '…'
                          ) : (
                            <svg
                              aria-hidden="true"
                              viewBox="0 0 24 24"
                              width="16"
                              height="16"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="1.8"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            >
                              <path d="M3 6h18" />
                              <path d="M8 6V4h8v2" />
                              <path d="m19 6-1 14H6L5 6" />
                              <path d="M10 11v5M14 11v5" />
                            </svg>
                          )}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  )
}