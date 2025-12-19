"use client";

import { useState } from "react";
import { Checkbox } from "@/components/ui/checkbox";
import { Clock } from "lucide-react";

interface ChecklistItem {
  id: string;
  text: string;
  completed: boolean;
  dueTime?: string;
}

interface DailyChecklistProps {
  items: ChecklistItem[];
  onToggle?: (id: string) => void;
}

export function DailyChecklist({ items, onToggle }: DailyChecklistProps) {
  const [checked, setChecked] = useState<Set<string>>(
    new Set(items.filter((i) => i.completed).map((i) => i.id))
  );

  const handleToggle = (id: string) => {
    const newChecked = new Set(checked);
    if (newChecked.has(id)) {
      newChecked.delete(id);
    } else {
      newChecked.add(id);
    }
    setChecked(newChecked);
    onToggle?.(id);
  };

  const completedCount = checked.size;
  const totalCount = items.length;
  const progressPercent = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;

  return (
    <div className="space-y-4">
      <div>
        <div className="flex items-center justify-between mb-2">
          <p className="text-sm font-semibold text-gray-900">
            Today's Moves
          </p>
          <p className="text-xs text-gray-600">
            {completedCount}/{totalCount}
          </p>
        </div>
        <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-primary transition-all"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      <div className="space-y-2">
        {items.map((item) => (
          <div
            key={item.id}
            className={`flex items-center gap-3 p-3 rounded-md transition border ${
              checked.has(item.id)
                ? "bg-gray-100 border-gray-200 opacity-60"
                : "bg-white border-gray-200 hover:bg-gray-50"
            }`}
          >
            <Checkbox
              checked={checked.has(item.id)}
              onCheckedChange={() => handleToggle(item.id)}
            />
            <div className="flex-1 min-w-0">
              <p
                className={`text-sm font-medium ${
                  checked.has(item.id)
                    ? "line-through text-gray-400"
                    : "text-gray-900"
                }`}
              >
                {item.text}
              </p>
              {item.dueTime && (
                <div className="flex items-center gap-1 mt-0.5">
                  <Clock className="w-3 h-3 text-gray-400" />
                  <p className="text-xs text-gray-500">{item.dueTime}</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
