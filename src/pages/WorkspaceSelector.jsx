import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useWorkspace } from '../context/WorkspaceContext'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/card'
import { Button } from '../components/ui/button'

const WorkspaceSelector = () => {
    const navigate = useNavigate()
    const { workspaces, selectWorkspace } = useWorkspace()
    const [selectedId, setSelectedId] = useState(null)

    const handleSelect = (workspace) => {
        setSelectedId(workspace.id)
    }

    const handleContinue = () => {
        const workspace = workspaces.find(w => w.id === selectedId)
        if (workspace) {
            selectWorkspace(workspace)
            navigate('/dashboard')
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-background p-4">
            <div className="w-full max-w-2xl">
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold mb-2">Select Workspace</h1>
                    <p className="text-muted-foreground">Choose a workspace to continue</p>
                </div>

                <div className="grid gap-4">
                    {workspaces.length === 0 ? (
                        <Card>
                            <CardContent className="p-6 text-center">
                                <p className="text-muted-foreground mb-4">No workspaces found</p>
                                <Button onClick={() => navigate('/onboarding')}>Create Workspace</Button>
                            </CardContent>
                        </Card>
                    ) : (
                        workspaces.map((workspace) => (
                            <Card
                                key={workspace.id}
                                className={`cursor-pointer transition-all ${selectedId === workspace.id ? 'ring-2 ring-primary' : ''
                                    }`}
                                onClick={() => handleSelect(workspace)}
                            >
                                <CardHeader>
                                    <CardTitle>{workspace.name}</CardTitle>
                                    <CardDescription>{workspace.description || 'No description'}</CardDescription>
                                </CardHeader>
                            </Card>
                        ))
                    )}
                </div>

                {workspaces.length > 0 && (
                    <div className="mt-6 flex justify-end">
                        <Button onClick={handleContinue} disabled={!selectedId}>
                            Continue
                        </Button>
                    </div>
                )}
            </div>
        </div>
    )
}

export default WorkspaceSelector
