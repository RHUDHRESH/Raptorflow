import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useWorkspace } from '../context/WorkspaceContext';
import { ChevronsUpDown, Check, Plus } from 'lucide-react';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from './ui/popover';
import { Button } from './ui/button';

interface WorkspaceSelectorProps {
  open?: boolean;
}

export const WorkspaceSelector: React.FC<WorkspaceSelectorProps> = ({ open = true }) => {
  const { workspaces, currentWorkspace, selectWorkspace } = useWorkspace();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = React.useState(false);

  if (!currentWorkspace) return null;

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="ghost"
          className={`w-full justify-start ${open ? 'px-2' : 'px-0 justify-center'}`}
        >
          <div className="flex items-center gap-2 truncate">
            <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-neutral-900 text-white text-xs">
              {currentWorkspace.name.charAt(0).toUpperCase()}
            </div>
            {open && (
              <>
                <span className="truncate text-sm font-medium">
                  {currentWorkspace.name}
                </span>
                <ChevronsUpDown className="ml-auto h-4 w-4 shrink-0 opacity-50" />
              </>
            )}
          </div>
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-56 p-0" align="start">
        <div className="p-2">
          <div className="px-2 py-1.5 text-xs font-normal text-muted-foreground">
            Workspaces
          </div>
          {workspaces.map((workspace) => (
            <div
              key={workspace.id}
              onClick={() => {
                selectWorkspace(workspace);
                setIsOpen(false);
              }}
              className="relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none hover:bg-accent hover:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50 gap-2 cursor-pointer"
            >
              <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md border bg-background">
                {workspace.name.charAt(0).toUpperCase()}
              </div>
              <span className="truncate flex-1">{workspace.name}</span>
              {currentWorkspace.id === workspace.id && (
                <Check className="h-4 w-4" />
              )}
            </div>
          ))}
          <div className="h-px bg-muted my-1" />
          <div
            onClick={() => {
              navigate('/workspace/create');
              setIsOpen(false);
            }}
            className="relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none hover:bg-accent hover:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50 gap-2 cursor-pointer"
          >
            <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md border bg-background border-dashed">
              <Plus className="h-4 w-4" />
            </div>
            Create Workspace
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
};

export default WorkspaceSelector;
