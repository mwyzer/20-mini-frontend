import React, { useEffect, useMemo, useState } from 'react'
import { DetectionOverlay } from './DetectionOverlay'
import { DetectionsList } from './DetectionsList'

const API_BASE = 'http://localhost:8000'

const defaultObjects = [
  {
    label: 'cat',
    bbox: { x: 10, y: 10, width: 40, height: 30 },
    confidence: 0.88,
  },
]

function stringifyObjects(objects) {
  return JSON.stringify(objects, null, 2)
}

function parseObjects(text) {
  const parsed = JSON.parse(text)
  if (!Array.isArray(parsed)) {
    throw new Error('Payload harus berupa array objek deteksi.')
  }
  return parsed
}

export default function App() {
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [detection, setDetection] = useState(null)
  const [detections, setDetections] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [editState, setEditState] = useState({ id: null, filename: '', rawObjects: stringifyObjects(defaultObjects) })

  useEffect(() => {
    fetchDetections()
  }, [])

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
    }
  }, [previewUrl])

  const fetchDetections = async () => {
    try {
      const response = await fetch(`${API_BASE}/detections`)
      const payload = await response.json()
      setDetections(payload)
    } catch (err) {
      console.error(err)
      setError('Gagal memuat daftar deteksi.')
    }
  }

  const handleFileChange = (event) => {
    const selected = event.target.files?.[0]
    if (!selected) return
    setFile(selected)
    const preview = URL.createObjectURL(selected)
    setPreviewUrl(preview)
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Pilih file gambar terlebih dahulu.')
      return
    }
    setLoading(true)
    setError('')
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch(`${API_BASE}/detect-image`, {
        method: 'POST',
        body: formData,
      })
      if (!response.ok) {
        throw new Error('Upload gagal')
      }
      const data = await response.json()
      setDetection(data)
      await fetchDetections()
    } catch (err) {
      console.error(err)
      setError('Proses deteksi gagal. Pastikan server berjalan.')
    } finally {
      setLoading(false)
    }
  }

  const handleSelectDetection = (record) => {
    setDetection(record)
    setPreviewUrl('')
    setFile(null)
  }

  const handleDelete = async (id) => {
    try {
      await fetch(`${API_BASE}/detections/${id}`, { method: 'DELETE' })
      await fetchDetections()
      if (detection?.id === id) {
        setDetection(null)
      }
    } catch (err) {
      console.error(err)
      setError('Gagal menghapus data deteksi.')
    }
  }

  const handleEdit = (record) => {
    setEditState({
      id: record.id,
      filename: record.filename,
      rawObjects: stringifyObjects(record.objects),
    })
  }

  const handleUpdate = async () => {
    if (!editState.id) return
    try {
      const parsedObjects = parseObjects(editState.rawObjects)
      const response = await fetch(`${API_BASE}/detections/${editState.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filename: editState.filename,
          objects: parsedObjects,
        }),
      })
      if (!response.ok) {
        throw new Error('Update failed')
      }
      const updated = await response.json()
      setDetection(updated)
      setEditState({ id: null, filename: '', rawObjects: stringifyObjects(defaultObjects) })
      await fetchDetections()
    } catch (err) {
      console.error(err)
      setError('Gagal memperbarui data. Pastikan format JSON benar.')
    }
  }

  const overlayObjects = useMemo(() => detection?.objects ?? [], [detection])

  return (
    <div className="container">
      <h1>Dashboard Deteksi Gambar</h1>

      <div className="card">
        <h2>Upload & Deteksi</h2>
        <div className="flex-row">
          <div className="upload-area">
            <input type="file" accept="image/*" onChange={handleFileChange} />
            <div className="flex-row" style={{ alignItems: 'center' }}>
              <button className="button" disabled={loading} onClick={handleUpload}>
                {loading ? 'Memproses...' : 'Kirim ke Server'}
              </button>
              {loading && <span className="small">Mengirim & menganalisis...</span>}
            </div>
            {error && <div className="status">{error}</div>}
            {file && <div className="small">File terpilih: {file.name}</div>}
          </div>
          <div style={{ flex: 1, minWidth: 320 }}>
            <h3>Pratinjau</h3>
            {previewUrl ? (
              <DetectionOverlay imageUrl={previewUrl} objects={overlayObjects} />
            ) : detection ? (
              <p className="small">Tidak ada pratinjau lokal. Pilih gambar baru untuk melihat bounding box.</p>
            ) : (
              <p className="small">Unggah gambar untuk melihat hasil deteksi.</p>
            )}
          </div>
        </div>
      </div>

      {detection && (
        <div className="card">
          <h2>Hasil Terakhir</h2>
          <p className="small">ID #{detection.id} • {detection.filename}</p>
          <div className="image-preview">
            {previewUrl && <img src={previewUrl} alt="Uploaded preview" />}
            {!previewUrl && (
              <div style={{ padding: '1rem' }} className="small">
                Tidak ada gambar pratinjau lokal, tetapi bounding box masih dapat dilihat jika gambar diunggah ulang.
              </div>
            )}
            {overlayObjects.map((obj, idx) => (
              <div
                key={`${obj.label}-${idx}`}
                className="overlay-box"
                style={{
                  top: `${obj.bbox.y}%`,
                  left: `${obj.bbox.x}%`,
                  width: `${obj.bbox.width}%`,
                  height: `${obj.bbox.height}%`,
                }}
              >
                <span className="label">{obj.label}</span>
                {obj.confidence && <span className="confidence">{Math.round(obj.confidence * 100)}%</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="card">
        <h2>Daftar Deteksi (CRUD)</h2>
        <DetectionsList detections={detections} onSelect={handleSelectDetection} onDelete={handleDelete} onEdit={handleEdit} />

        <div style={{ marginTop: '1.25rem' }}>
          <h3>Edit / Buat Ulang</h3>
          <div className="flex-row">
            <div style={{ flex: 1, minWidth: 260 }}>
              <label className="small">Filename</label>
              <input
                style={{ width: '100%', padding: '0.6rem', borderRadius: 10, border: '1px solid #cbd5e1' }}
                value={editState.filename}
                onChange={(e) => setEditState((prev) => ({ ...prev, filename: e.target.value }))}
                placeholder="gambar.jpg"
              />
            </div>
            <div style={{ flex: 2, minWidth: 320 }}>
              <label className="small">Objects JSON</label>
              <textarea
                className="textarea"
                value={editState.rawObjects}
                onChange={(e) => setEditState((prev) => ({ ...prev, rawObjects: e.target.value }))}
              />
            </div>
          </div>
          <div className="controls" style={{ marginTop: '0.75rem' }}>
            <button className="button secondary" disabled={!editState.id} onClick={handleUpdate}>
              Simpan Perubahan
            </button>
            <button
              className="button"
              onClick={() => setEditState({ id: null, filename: '', rawObjects: stringifyObjects(defaultObjects) })}
            >
              Reset
            </button>
            {!editState.id && <span className="small">Pilih item untuk mulai mengedit.</span>}
          </div>
        </div>
      </div>
    </div>
  )
}
