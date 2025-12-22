import { z } from 'zod';

export const brandKitSchema = z.object({
  brandVoice: z.string().min(1, 'Brand voice is required'),
  positioning: z.string().min(1, 'Positioning statement is required'),
  messagingPillars: z.array(z.string().min(1))
    .min(1, 'At least one messaging pillar is required')
    .max(5, 'Maximum of 5 messaging pillars allowed'),
});

export type BrandKit = z.infer<typeof brandKitSchema>;



export const defaultBrandKit: BrandKit = {

  brandVoice: '',

  positioning: '',

  messagingPillars: [''],

};



const STORAGE_KEY = 'rf_brand_kit';



export const saveBrandKit = (kit: BrandKit) => {

  if (typeof window !== 'undefined') {

    localStorage.setItem(STORAGE_KEY, JSON.stringify(kit));

  }

};



export const getBrandKit = (): BrandKit | null => {

  if (typeof window !== 'undefined') {

    const data = localStorage.getItem(STORAGE_KEY);

    return data ? JSON.parse(data) : null;

  }

  return null;

};
