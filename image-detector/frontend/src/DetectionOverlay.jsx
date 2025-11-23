import React from 'react'

export function DetectionOverlay({ imageUrl, objects }) {
  if (!imageUrl) {
    return null
  }

  return (
    <div className="image-preview">
      <img src={imageUrl} alt="Uploaded preview" />
      {objects?.map((obj, idx) => (
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
  )
}
