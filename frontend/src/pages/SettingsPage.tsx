import { useEffect, useState } from 'react'
import {
  getAPIKeys, updateAPIKeys,
  getScoringWeights, updateScoringWeights,
  type APIKeysStatus,
} from '../api/settings'
import Spinner from '../components/ui/Spinner'

export default function SettingsPage() {
  const [keysStatus, setKeysStatus] = useState<APIKeysStatus | null>(null)
  const [weights, setWeights] = useState<Record<string, number> | null>(null)
  const [loading, setLoading] = useState(true)
  const [keyForm, setKeyForm] = useState({ serper_key: '', serpapi_key: '', hunter_key: '', apollo_key: '' })
  const [keySaving, setKeySaving] = useState(false)
  const [weightsSaving, setWeightsSaving] = useState(false)
  const [keyMsg, setKeyMsg] = useState('')
  const [weightsMsg, setWeightsMsg] = useState('')

  useEffect(() => {
    Promise.all([getAPIKeys(), getScoringWeights()])
      .then(([keys, w]) => {
        setKeysStatus(keys)
        setWeights(w)
      })
      .finally(() => setLoading(false))
  }, [])

  const handleKeysSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setKeySaving(true)
    setKeyMsg('')
    try {
      await updateAPIKeys(keyForm)
      const updated = await getAPIKeys()
      setKeysStatus(updated)
      setKeyForm({ serper_key: '', serpapi_key: '', hunter_key: '', apollo_key: '' })
      setKeyMsg('API keys updated')
    } catch {
      setKeyMsg('Failed to update keys')
    } finally {
      setKeySaving(false)
    }
  }

  const handleWeightsSave = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!weights) return
    setWeightsSaving(true)
    setWeightsMsg('')
    try {
      await updateScoringWeights(weights)
      setWeightsMsg('Scoring weights updated')
    } catch {
      setWeightsMsg('Failed to update weights')
    } finally {
      setWeightsSaving(false)
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center py-12"><Spinner /></div>
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Settings</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* API Keys */}
        <div className="bg-white rounded-xl border shadow-sm p-6">
          <h2 className="font-semibold mb-4">API Keys</h2>
          <div className="space-y-2 mb-4 text-sm">
            {keysStatus && (
              <>
                <div className="flex justify-between">
                  <span>Serper.dev</span>
                  <span className={keysStatus.serper_key_set ? 'text-green-600' : 'text-gray-400'}>
                    {keysStatus.serper_key_set ? 'Configured' : 'Not set'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>SerpAPI</span>
                  <span className={keysStatus.serpapi_key_set ? 'text-green-600' : 'text-gray-400'}>
                    {keysStatus.serpapi_key_set ? 'Configured' : 'Not set'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Hunter.io</span>
                  <span className={keysStatus.hunter_key_set ? 'text-green-600' : 'text-gray-400'}>
                    {keysStatus.hunter_key_set ? 'Configured' : 'Not set'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Apollo.io</span>
                  <span className={keysStatus.apollo_key_set ? 'text-green-600' : 'text-gray-400'}>
                    {keysStatus.apollo_key_set ? 'Configured' : 'Not set'}
                  </span>
                </div>
              </>
            )}
          </div>
          <form onSubmit={handleKeysSave} className="space-y-3">
            <input
              type="password"
              placeholder="Serper.dev API key"
              value={keyForm.serper_key}
              onChange={(e) => setKeyForm((p) => ({ ...p, serper_key: e.target.value }))}
              className="w-full px-3 py-2 border rounded-lg text-sm"
            />
            <input
              type="password"
              placeholder="SerpAPI key"
              value={keyForm.serpapi_key}
              onChange={(e) => setKeyForm((p) => ({ ...p, serpapi_key: e.target.value }))}
              className="w-full px-3 py-2 border rounded-lg text-sm"
            />
            <input
              type="password"
              placeholder="Hunter.io API key"
              value={keyForm.hunter_key}
              onChange={(e) => setKeyForm((p) => ({ ...p, hunter_key: e.target.value }))}
              className="w-full px-3 py-2 border rounded-lg text-sm"
            />
            <input
              type="password"
              placeholder="Apollo.io API key"
              value={keyForm.apollo_key}
              onChange={(e) => setKeyForm((p) => ({ ...p, apollo_key: e.target.value }))}
              className="w-full px-3 py-2 border rounded-lg text-sm"
            />
            {keyMsg && <p className="text-sm text-green-600">{keyMsg}</p>}
            <button
              type="submit"
              disabled={keySaving}
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {keySaving ? 'Saving...' : 'Save Keys'}
            </button>
          </form>
        </div>

        {/* Scoring Weights */}
        <div className="bg-white rounded-xl border shadow-sm p-6">
          <h2 className="font-semibold mb-4">Scoring Weights</h2>
          {weights && (
            <form onSubmit={handleWeightsSave} className="space-y-3">
              {Object.entries(weights).map(([key, val]) => (
                <div key={key} className="flex items-center justify-between gap-4">
                  <label className="text-sm text-gray-700 flex-1">{key.replace(/_/g, ' ')}</label>
                  <input
                    type="number"
                    value={val}
                    onChange={(e) => setWeights((prev) => prev ? { ...prev, [key]: Number(e.target.value) } : prev)}
                    className="w-20 px-2 py-1.5 border rounded-lg text-sm text-right"
                  />
                </div>
              ))}
              {weightsMsg && <p className="text-sm text-green-600">{weightsMsg}</p>}
              <button
                type="submit"
                disabled={weightsSaving}
                className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {weightsSaving ? 'Saving...' : 'Save Weights'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
