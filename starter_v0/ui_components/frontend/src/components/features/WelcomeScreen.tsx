import React from "react";
import {
  ArrowUpRight,
  BookOpen,
  FileText,
  HelpCircle,
  Search,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import type { PromptSuggestion } from "@/types";

interface WelcomeScreenProps {
  provider: string;
  model: string;
  version: string;
  toolCount: number;
  prompts: PromptSuggestion[];
  onSelectPrompt: (prompt: string) => void;
}

function getPromptIcon(iconName: string): React.ReactNode {
  const cls = "h-4 w-4 text-muted-foreground group-hover:text-foreground transition-colors shrink-0";
  switch (iconName) {
    case "search":
      return <Search className={cls} />;
    case "book":
      return <BookOpen className={cls} />;
    case "help":
      return <HelpCircle className={cls} />;
    case "shield-alert":
      return <ShieldAlert className={cls} />;
    case "shield-check":
      return <ShieldCheck className={cls} />;
    case "file":
      return <FileText className={cls} />;
    default:
      return <Sparkles className={cls} />;
  }
}

export function WelcomeScreen({
  provider,
  model,
  version,
  toolCount,
  prompts,
  onSelectPrompt,
}: WelcomeScreenProps) {
  return (
    <div className="mx-auto w-full max-w-3xl py-6">
      <div className="mb-6 space-y-2 text-center sm:text-left">
        <div className="flex flex-wrap items-center justify-center gap-2 sm:justify-start">
          <Badge variant="secondary" className="font-mono text-[11px]">
            {version}
          </Badge>
          <Badge variant="outline" className="font-mono text-[11px] text-muted-foreground">
            {provider} / {model}
          </Badge>
          <Badge variant="outline" className="font-mono text-[11px] text-muted-foreground">
            {toolCount} công cụ sẵn sàng
          </Badge>
        </div>

        <h2 className="text-2xl font-semibold tracking-tight text-foreground">
          Bạn muốn nghiên cứu nội dung gì hôm nay?
        </h2>
        <p className="text-sm text-muted-foreground">
          Hệ thống đa tác tử đa bước suy luận, truy vết công cụ thời gian thực, trích dẫn nguồn minh bạch và cơ chế phê duyệt an toàn.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-2">
        {prompts.map((item) => (
          <Card
            key={item.id}
            className="group cursor-pointer border-border/90 bg-card p-3.5 transition-all hover:border-foreground/25 hover:bg-muted/40"
            onClick={() => onSelectPrompt(item.prompt)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                onSelectPrompt(item.prompt);
              }
            }}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-2">
                {getPromptIcon(item.icon)}
                <span className="text-xs font-medium text-foreground">{item.title}</span>
              </div>
              <ArrowUpRight className="h-3.5 w-3.5 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100 shrink-0" />
            </div>
            <p className="mt-2 line-clamp-2 text-xs leading-relaxed text-muted-foreground">
              {item.prompt}
            </p>
          </Card>
        ))}
      </div>
    </div>
  );
}
