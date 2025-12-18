export function useMe() {
    return {
        data: {
            id: 'user_mock',
            full_name: 'Commander',
            email: 'founder@raptorflow.com',
            subscription: {
                planId: 'plan_soar'
            }
        },
        isLoading: false,
        error: null
    }
}
