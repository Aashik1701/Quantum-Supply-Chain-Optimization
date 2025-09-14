import React from 'react'

type BackgroundVideoProps = {
  src: string
  className?: string
  /** When true, renders a subtle dark overlay to improve text contrast */
  withOverlay?: boolean
  /** Tailwind classes for the overlay element */
  overlayClassName?: string
}

/**
 * Full-bleed background video for hero/pages. Position its parent as relative and stack content above it.
 */
const BackgroundVideo: React.FC<BackgroundVideoProps> = ({
  src,
  className = '',
  withOverlay = false,
  overlayClassName = 'absolute inset-0 bg-black/40',
}) => {
  if (!src) return null
  return (
    <div className={`absolute inset-0 -z-10 overflow-hidden ${className}`}>
      <video
        autoPlay
        loop
        muted
        playsInline
        className="absolute top-0 left-0 w-full h-full object-cover"
      >
        <source src={src} type="video/mp4" />
      </video>
      {withOverlay && <div className={overlayClassName} />}
    </div>
  )
}

export default BackgroundVideo
