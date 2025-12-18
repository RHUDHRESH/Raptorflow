export function usePlans() {
    return {
        data: [
            { id: 'plan_ascent', name: 'Ascent' },
            { id: 'plan_glide', name: 'Glide' },
            { id: 'plan_soar', name: 'Soar' }
        ],
        isLoading: false,
        error: null
    }
}
