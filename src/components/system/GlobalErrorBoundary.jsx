import React from 'react'

class GlobalErrorBoundary extends React.Component {
    constructor(props) {
        super(props)
        this.state = { hasError: false, error: null, errorInfo: null }
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error }
    }

    componentDidCatch(error, errorInfo) {
        console.error('Uncaught error:', error, errorInfo)
        this.setState({ errorInfo })
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen flex items-center justify-center bg-red-50 p-6 font-sans text-red-900">
                    <div className="max-w-3xl w-full bg-white border border-red-200 rounded-xl shadow-xl overflow-hidden">
                        <div className="p-6 border-b border-red-100 bg-red-50/50">
                            <h1 className="text-2xl font-bold mb-2">Something went wrong</h1>
                            <p className="text-red-700">The application encountered a critical error and could not render.</p>
                        </div>
                        <div className="p-6 bg-gray-50 overflow-auto max-h-[60vh]">
                            <div className="mb-4">
                                <h3 className="font-semibold text-sm tracking-wide text-gray-600 mb-1">Error</h3>
                                <pre className="text-red-700 bg-red-50 p-3 rounded border border-red-100 whitespace-pre-wrap font-sans text-sm leading-relaxed">
                                    {this.state.error && this.state.error.toString()}
                                </pre>
                            </div>
                            <div>
                                <h3 className="font-semibold text-sm tracking-wide text-gray-600 mb-1">Stack Trace</h3>
                                <pre className="text-gray-700 text-sm whitespace-pre-wrap font-sans leading-relaxed">
                                    {this.state.errorInfo && this.state.errorInfo.componentStack}
                                </pre>
                            </div>
                        </div>
                        <div className="p-6 border-t border-gray-100 bg-white flex justify-end gap-3">
                            <button
                                onClick={() => window.location.reload()}
                                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
                            >
                                Reload Page
                            </button>
                        </div>
                    </div>
                </div>
            )
        }

        return this.props.children
    }
}

export default GlobalErrorBoundary
