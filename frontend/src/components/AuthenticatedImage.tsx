import { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';

interface AuthenticatedImageProps {
  src: string;
  alt: string;
  className?: string;
  fallback?: string;
}

export const AuthenticatedImage = ({ src, alt, className, fallback }: AuthenticatedImageProps) => {
  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const [error, setError] = useState(false);
  const accessToken = useAuthStore((state) => state.accessToken);

  useEffect(() => {
    let cancelled = false;
    
    const loadImage = async () => {
      if (!accessToken) {
        setError(true);
        return;
      }

      try {
        const response = await fetch(src, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to load image');
        }

        const blob = await response.blob();
        
        if (!cancelled) {
          const objectUrl = URL.createObjectURL(blob);
          setImageSrc(objectUrl);
          setError(false);
        }
      } catch (err) {
        if (!cancelled) {
          console.error('Error loading image:', err);
          setError(true);
        }
      }
    };

    loadImage();

    return () => {
      cancelled = true;
      if (imageSrc) {
        URL.revokeObjectURL(imageSrc);
      }
    };
  }, [src, accessToken]);

  if (error || !imageSrc) {
    const fallbackSrc = fallback || 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23f0f0f0" width="400" height="300"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-size="18"%3E📷 Cargando...%3C/text%3E%3C/svg%3E';
    
    return (
      <img
        src={error ? (fallback || 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23fee" width="400" height="300"/%3E%3Ctext fill="%23c33" x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-size="16"%3E⚠️ Imagen no disponible%3C/text%3E%3C/svg%3E') : fallbackSrc}
        alt={alt}
        className={className}
      />
    );
  }

  return (
    <img
      src={imageSrc}
      alt={alt}
      className={className}
    />
  );
};
