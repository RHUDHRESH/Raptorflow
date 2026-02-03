// Unsplash image URLs for the landing page
// These are high-quality, relevant images for the artisanal coffeehouse aesthetic

export const UNSPLASH_IMAGES = {
  // Hero background - coffee/warm textures
  hero: {
    coffeeBeans: "https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=1920&q=80",
    warmLight: "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=1920&q=80",
    compassDetail: "https://images.unsplash.com/photo-1519074069444-1ba4fff66d16?w=1920&q=80",
  },

  // Feature section images
  features: {
    foundation: "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=800&q=80",
    cognitive: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&q=80",
    muse: "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=800&q=80",
    campaigns: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80",
  },

  // How it works section
  process: {
    onboard: "https://images.unsplash.com/photo-1553877522-43269d4ea984?w=600&q=80",
    generate: "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=600&q=80",
    execute: "https://images.unsplash.com/photo-1552664730-d307ca884978?w=600&q=80",
  },

  // Decorative textures
  textures: {
    paper: "https://images.unsplash.com/photo-1586075010923-2dd4570fb338?w=400&q=80",
    wood: "https://images.unsplash.com/photo-1542856204-436930c66c4f?w=400&q=80",
    leather: "https://images.unsplash.com/photo-1550989460-0adf9ea622e2?w=400&q=80",
    parchment: "https://images.unsplash.com/photo-1604147495798-57beb5d6af73?w=400&q=80",
  },
};

// Image optimization helper
export function getOptimizedImageUrl(url: string, width: number = 800, quality: number = 80): string {
  // Unsplash supports dynamic resizing via URL params
  const urlObj = new URL(url);
  urlObj.searchParams.set("w", width.toString());
  urlObj.searchParams.set("q", quality.toString());
  urlObj.searchParams.set("auto", "format");
  urlObj.searchParams.set("fit", "crop");
  return urlObj.toString();
}

// Preload critical images
export function preloadImages(urls: string[]): Promise<void[]> {
  return Promise.all(
    urls.map((url) => {
      return new Promise<void>((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve();
        img.onerror = reject;
        img.src = url;
      });
    })
  );
}

// Critical images to preload on landing page
export const CRITICAL_IMAGES = [
  UNSPLASH_IMAGES.features.foundation,
  UNSPLASH_IMAGES.features.cognitive,
  UNSPLASH_IMAGES.features.muse,
  UNSPLASH_IMAGES.features.campaigns,
];

export default UNSPLASH_IMAGES;
