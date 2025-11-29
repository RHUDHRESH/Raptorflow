import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWorkspace } from '../context/WorkspaceContext';
import { Loader2, Plus } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/card';

export default function CreateWorkspace() {
    const { createNewWorkspace } = useWorkspace();
    const navigate = useNavigate();
    const [name, setName] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!name.trim()) return;

        setLoading(true);
        setError('');

        try {
            const result = await createNewWorkspace(name.trim());
            
            if (result.success) {
                navigate('/dashboard'); // Or wherever the main dashboard is
            } else {
                setError(result.error || 'Failed to create workspace');
            }
        } catch (err) {
            console.error('Workspace creation error:', err);
            setError(err instanceof Error ? err.message : 'An unexpected error occurred');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-neutral-50 p-4">
            <Card className="w-full max-w-md">
                <CardHeader>
                    <CardTitle>Create Your Workspace</CardTitle>
                    <CardDescription>
                        Enter a name for your new RaptorFlow workspace.
                    </CardDescription>
                </CardHeader>
                <form onSubmit={handleSubmit}>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <label htmlFor="name" className="text-sm font-medium">
                                Workspace Name
                            </label>
                            <Input
                                id="name"
                                placeholder="Acme Corp, Project X, etc."
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                disabled={loading}
                                autoFocus
                            />
                        </div>
                        {error && (
                            <div className="text-sm text-red-500 bg-red-50 p-2 rounded">
                                {error}
                            </div>
                        )}
                    </CardContent>
                    <CardFooter className="flex justify-between">
                        <Button 
                            type="button" 
                            variant="ghost" 
                            onClick={() => navigate(-1)}
                            disabled={loading}
                        >
                            Cancel
                        </Button>
                        <Button type="submit" disabled={loading || !name.trim()}>
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Creating...
                                </>
                            ) : (
                                <>
                                    <Plus className="mr-2 h-4 w-4" />
                                    Create Workspace
                                </>
                            )}
                        </Button>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
}
