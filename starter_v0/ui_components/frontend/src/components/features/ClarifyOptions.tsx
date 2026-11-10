import { useState } from "react";
import { MessageSquarePlus } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ClarifyOptionsProps {
  options: string[];
  onSelectOption: (option: string) => void;
}

export function ClarifyOptions({ options, onSelectOption }: ClarifyOptionsProps) {
  const [selected, setSelected] = useState<string | null>(null);

  if (!options || options.length === 0) return null;

  return (
    <div className="space-y-1.5 pt-1">
      <div className="flex items-center gap-1.5 text-[11px] font-medium text-muted-foreground">
        <MessageSquarePlus className="h-3 w-3" />
        <span>Gợi ý phản hồi nhanh</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {options.map((opt) => (
          <Button
            key={opt}
            type="button"
            variant="outline"
            size="sm"
            disabled={selected !== null}
            onClick={() => {
              setSelected(opt);
              onSelectOption(opt);
            }}
            className="h-auto whitespace-normal py-1.5 text-left text-xs"
          >
            {opt}
          </Button>
        ))}
      </div>
    </div>
  );
}
