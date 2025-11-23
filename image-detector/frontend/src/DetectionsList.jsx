import React from 'react'

export function DetectionsList({ detections, onSelect, onDelete, onEdit }) {
  if (!detections.length) {
    return <p className="small">Belum ada data deteksi disimpan.</p>
  }

  return (
    <ul className="detections-list">
      {detections.map((item) => (
        <li key={item.id}>
          <div className="detection-meta">
            <div>
              <div className="badge">#{item.id}</div>
              <div className="small">{item.filename}</div>
              <div className="small">{new Date(item.created_at).toLocaleString()}</div>
            </div>
            <div className="small">{item.objects.length} objek</div>
          </div>
          <div className="controls">
            <button className="button secondary" onClick={() => onSelect(item)}>
              Lihat
            </button>
            <button className="button" onClick={() => onEdit(item)}>
              Edit
            </button>
            <button className="button danger" onClick={() => onDelete(item.id)}>
              Hapus
            </button>
          </div>
        </li>
      ))}
    </ul>
  )
}
