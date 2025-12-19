"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Move } from "@/lib/types";
import { formatDate } from "@/lib/utils/formatters";

interface MoveCardProps {
  move: Move;
  onShip?: () => void;
  onOpen?: () => void;
}

export function MoveCard({ move, onShip, onOpen }: MoveCardProps) {
  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition bg-white">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <Badge variant="outline" className="text-xs">
              {move.status}
            </Badge>
            <Badge variant="secondary" className="text-xs">
              {move.channel}
            </Badge>
          </div>
          <h4 className="font-semibold text-gray-900 truncate text-sm">
            {move.title}
          </h4>
          {move.due_date && (
            <p className="text-xs text-gray-600 mt-1">
              Due: {formatDate(move.due_date)}
            </p>
          )}
        </div>
        <div className="text-right">
          <p className="text-xs text-gray-500">{move.asset_count} assets</p>
        </div>
      </div>

      <div className="flex gap-2">
        {move.status === "ready" && (
          <Button
            size="sm"
            variant="default"
            onClick={onShip}
            className="flex-1"
          >
            Ship
          </Button>
        )}
        <Button
          size="sm"
          variant={move.status === "ready" ? "ghost" : "default"}
          onClick={onOpen}
          className={move.status === "ready" ? "flex-1" : ""}
        >
          {move.status === "ready" ? "Details" : "Open"}
        </Button>
      </div>
    </div>
  );
}
