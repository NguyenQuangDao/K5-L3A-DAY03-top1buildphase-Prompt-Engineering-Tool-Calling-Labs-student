import React, { useState } from "react";
import {
  AlertTriangle,
  AtSign,
  BookOpen,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Clock,
  Copy,
  FileText,
  Globe,
  HelpCircle,
  ListFilter,
  Search,
  Send,
  Shield,
  Terminal,
  Wrench,
  XCircle,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { ToolEvent, ToolStatus } from "@/types";

interface ToolCallInspectorProps {
  toolEvents: ToolEvent[];
  finalAnswer?: string | null;
  turnStatus?: string;
  turnIndex?: number;
}

function getToolIcon(toolName: string): React.ReactNode {
  const cls = "h-3.5 w-3.5 text-muted-foreground shrink-0";
  switch (toolName) {
    case "lookup":
      return <Search className={cls} />;
    case "fetch":
      return <Globe className={cls} />;
    case "papers":
      return <BookOpen className={cls} />;
    case "paper_text":
      return <FileText className={cls} />;
    case "policy":
      return <Shield className={cls} />;
    case "send":
      return <Send className={cls} />;
    case "clarify":
      return <HelpCircle className={cls} />;
    case "format":
      return <ListFilter className={cls} />;
    case "timeline":
    case "social_search":
      return <AtSign className={cls} />;
    default:
      return <Wrench className={cls} />;
  }
}

function resolveStatus(event: ToolEvent): ToolStatus {
  if (event.ui_status) return event.ui_status;
  const res = event.result as Record<string, unknown> | null | undefined;
  if (res && typeof res === "object") {
    if (res.status === "needs_confirmation" || res.awaiting_user === true) {
      return "Awaiting Confirmation";
    }
    if (res.error) {
      return "Failed";
    }
  }
  return "Completed";
}

function StatusBadge({ status }: { status: ToolStatus }) {
  switch (status) {
    case "Completed":
      return (
        <Badge variant="success" className="gap-1 font-medium">
          <CheckCircle2 className="h-3 w-3" />
          Hoàn thành
        </Badge>
      );
    case "Failed":
      return (
        <Badge variant="destructive" className="gap-1 font-medium">
          <XCircle className="h-3 w-3" />
          Thất bại
        </Badge>
      );
    case "Awaiting Confirmation":
      return (
        <Badge variant="warning" className="gap-1 font-medium">
          <AlertTriangle className="h-3 w-3" />
          Chờ xác nhận
        </Badge>
      );
    case "Running":
      return (
        <Badge variant="info" className="gap-1 font-medium">
          <Clock className="h-3 w-3 animate-spin" />
          Đang chạy
        </Badge>
      );
    default:
      return (
        <Badge variant="secondary" className="gap-1 font-medium">
          <Clock className="h-3 w-3" />
          Đang chờ
        </Badge>
      );
  }
}

function CodeBlock({ value }: { value: unknown }) {
  const [copied, setCopied] = useState(false);
  const text =
    typeof value === "string" ? value : JSON.stringify(value ?? {}, null, 2);

  const handleCopy = () => {
    navigator.clipboard?.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1400);
    });
  };

  return (
    <div className="relative rounded-lg border bg-muted/50">
      <Button
        type="button"
        variant="ghost"
        size="icon"
        onClick={handleCopy}
        className="absolute right-1.5 top-1.5 z-10 h-6 w-6 text-muted-foreground hover:text-foreground"
        title="Copy JSON"
      >
        {copied ? <Check className="h-3 w-3 text-emerald-500" /> : <Copy className="h-3 w-3" />}
      </Button>
      <ScrollArea className="max-h-60 w-full">
        <pre className="p-3 pr-9 font-mono text-[11.5px] leading-relaxed text-foreground whitespace-pre-wrap break-words">
          {text}
        </pre>
      </ScrollArea>
    </div>
  );
}

function ExecutionResultSummary({ event }: { event: ToolEvent }) {
  const res = event.result;
  if (!res || typeof res !== "object") {
    return (
      <div className="rounded-lg border bg-muted/30 p-3 text-xs text-muted-foreground">
        Kết quả vô hướng: <span className="font-mono text-foreground">{String(res)}</span>
      </div>
    );
  }

  const obj = res as Record<string, unknown>;
  const error = obj.error ? String(obj.error) : null;
  const message = obj.message ? String(obj.message) : null;
  const status = obj.status ? String(obj.status) : null;
  const question = obj.question ? String(obj.question) : null;
  const items = Array.isArray(obj.items)
    ? obj.items
    : Array.isArray(obj.results)
      ? obj.results
      : Array.isArray(obj.papers)
        ? obj.papers
        : null;

  return (
    <div className="space-y-2 rounded-lg border bg-muted/30 p-3 text-xs">
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-muted-foreground">Công cụ:</span>
        <code className="rounded bg-muted px-1.5 py-0.5 font-mono text-[11px] font-medium text-foreground">
          {event.tool}
        </code>
        {status && (
          <>
            <span className="text-muted-foreground">Trạng thái:</span>
            <Badge variant="outline" className="font-mono text-[11px]">
              {status}
            </Badge>
          </>
        )}
        {typeof event.duration_ms === "number" && (
          <>
            <span className="text-muted-foreground">Thời gian:</span>
            <span className="font-mono text-foreground">{event.duration_ms} ms</span>
          </>
        )}
      </div>

      {error && (
        <div className="rounded-md border border-destructive/30 bg-destructive/10 px-2.5 py-2 text-destructive">
          <span className="font-semibold">{error}</span>
          {message ? `: ${message}` : ""}
        </div>
      )}

      {!error && status === "needs_confirmation" && (
        <div className="rounded-md border border-amber-500/30 bg-amber-500/10 px-2.5 py-2 text-amber-700 dark:text-amber-400">
          {message || "Hành động tạm dừng để chờ người dùng xác nhận."}
        </div>
      )}

      {question && (
        <div className="rounded-md border border-sky-500/30 bg-sky-500/10 px-2.5 py-2 text-sky-700 dark:text-sky-300">
          <span className="font-medium">Yêu cầu làm rõ: </span>
          {question}
        </div>
      )}

      {items && (
        <div className="text-muted-foreground">
          Trả về <span className="font-semibold text-foreground">{items.length}</span> mục dữ liệu.
        </div>
      )}

      {!error && status !== "needs_confirmation" && !question && !items && (
        <div className="text-muted-foreground">
          Trả về {Object.keys(obj).length} trường:{" "}
          <span className="font-mono text-[11px] text-foreground">
            {Object.keys(obj).join(", ") || "trống"}
          </span>
        </div>
      )}
    </div>
  );
}

export function ToolCallInspector({
  toolEvents,
  finalAnswer,
  turnStatus,
}: ToolCallInspectorProps) {
  const [panelOpen, setPanelOpen] = useState(true);
  const [openSteps, setOpenSteps] = useState<Record<number, boolean>>(() => {
    const init: Record<number, boolean> = {};
    toolEvents.forEach((ev, idx) => {
      const s = resolveStatus(ev);
      init[idx] = s === "Failed" || s === "Awaiting Confirmation" || toolEvents.length <= 2;
    });
    return init;
  });

  if (toolEvents.length === 0) {
    return (
      <Card className="border-border/80 bg-card/60 shadow-none">
        <div className="flex items-center justify-between px-3.5 py-2.5 text-xs">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Terminal className="h-3.5 w-3.5" />
            <span className="font-medium text-foreground">Giám sát công cụ (Tool Inspector)</span>
            <span>·</span>
            <span>Phản hồi trực tiếp từ mô hình (0 công cụ được gọi)</span>
          </div>
          <Badge variant="secondary" className="text-[11px] font-normal">
            {turnStatus || "answered"}
          </Badge>
        </div>
      </Card>
    );
  }

  const statuses = toolEvents.map(resolveStatus);
  const overallStatus: ToolStatus = statuses.includes("Awaiting Confirmation")
    ? "Awaiting Confirmation"
    : statuses.includes("Failed")
      ? "Failed"
      : statuses.includes("Running")
        ? "Running"
        : "Completed";

  const totalDurationMs = toolEvents.reduce(
    (sum, ev) => sum + (typeof ev.duration_ms === "number" ? ev.duration_ms : 0),
    0
  );
  const hasDuration = toolEvents.some((ev) => typeof ev.duration_ms === "number");

  const toggleAll = (expand: boolean) => {
    const next: Record<number, boolean> = {};
    toolEvents.forEach((_, idx) => {
      next[idx] = expand;
    });
    setOpenSteps(next);
  };

  return (
    <Card className="overflow-hidden border-border bg-card shadow-sm">
      <Collapsible open={panelOpen} onOpenChange={setPanelOpen}>
        <div className="flex flex-wrap items-center justify-between gap-2 px-3.5 py-2.5">
          <CollapsibleTrigger asChild>
            <button
              type="button"
              className="flex flex-1 items-center gap-2 text-left text-xs font-medium text-foreground hover:opacity-80"
            >
              {panelOpen ? (
                <ChevronDown className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
              ) : (
                <ChevronRight className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
              )}
              <Terminal className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
              <span className="font-semibold tracking-tight">Chi tiết gọi công cụ (Tool Inspector)</span>
              <span className="text-muted-foreground">·</span>
              <span className="font-mono text-[11px] text-muted-foreground">
                {toolEvents.length} lượt gọi
              </span>
              {hasDuration && (
                <>
                  <span className="text-muted-foreground">·</span>
                  <span className="font-mono text-[11px] text-muted-foreground">
                    {totalDurationMs} ms
                  </span>
                </>
              )}
            </button>
          </CollapsibleTrigger>

          <div className="flex items-center gap-2">
            {panelOpen && toolEvents.length > 1 && (
              <div className="flex items-center gap-1">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="h-6 px-2 text-[11px] text-muted-foreground"
                  onClick={() => toggleAll(true)}
                >
                  Mở tất cả
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="h-6 px-2 text-[11px] text-muted-foreground"
                  onClick={() => toggleAll(false)}
                >
                  Thu gọn
                </Button>
              </div>
            )}
            <StatusBadge status={overallStatus} />
          </div>
        </div>

        <CollapsibleContent>
          <Separator />
          <div className="divide-y divide-border">
            {toolEvents.map((event, idx) => {
              const status = resolveStatus(event);
              const isOpen = !!openSteps[idx];
              const stepNum = event.step ?? idx + 1;
              const roundNum = event.round ?? 1;

              return (
                <Collapsible
                  key={`${event.tool}-${idx}`}
                  open={isOpen}
                  onOpenChange={(val) =>
                    setOpenSteps((prev) => ({ ...prev, [idx]: val }))
                  }
                >
                  <CollapsibleTrigger asChild>
                    <button
                      type="button"
                      className="flex w-full items-center justify-between gap-2 px-3.5 py-2.5 text-left transition-colors hover:bg-muted/50"
                    >
                      <div className="flex min-w-0 items-center gap-2.5">
                        {isOpen ? (
                          <ChevronDown className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                        ) : (
                          <ChevronRight className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                        )}
                        <span className="font-mono text-[11px] text-muted-foreground">
                          #{stepNum}
                        </span>
                        {getToolIcon(event.tool)}
                        <code className="truncate font-mono text-xs font-semibold text-foreground">
                          {event.tool}
                        </code>
                        <span className="hidden rounded bg-muted px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground sm:inline">
                          Vòng {roundNum}
                        </span>
                      </div>

                      <div className="flex shrink-0 items-center gap-2">
                        {typeof event.duration_ms === "number" && (
                          <span className="font-mono text-[11px] text-muted-foreground">
                            {event.duration_ms}ms
                          </span>
                        )}
                        <StatusBadge status={status} />
                      </div>
                    </button>
                  </CollapsibleTrigger>

                  <CollapsibleContent>
                    <div className="bg-muted/20 px-3.5 pb-3.5 pt-2">
                      <Tabs defaultValue="args" className="w-full">
                        <TabsList className="grid w-full grid-cols-4 sm:w-auto sm:inline-grid">
                          <TabsTrigger value="args">Tham số (Args)</TabsTrigger>
                          <TabsTrigger value="raw">Dữ liệu thô (Raw)</TabsTrigger>
                          <TabsTrigger value="result">Kết quả thực thi</TabsTrigger>
                          <TabsTrigger value="final">Câu trả lời cuối</TabsTrigger>
                        </TabsList>

                        <TabsContent value="args">
                          <CodeBlock value={event.args} />
                        </TabsContent>

                        <TabsContent value="raw">
                          <CodeBlock value={event.result} />
                        </TabsContent>

                        <TabsContent value="result">
                          <ExecutionResultSummary event={event} />
                        </TabsContent>

                        <TabsContent value="final">
                          <ScrollArea className="max-h-52 rounded-lg border bg-muted/30 p-3">
                            {finalAnswer ? (
                              <div className="text-xs leading-relaxed text-foreground whitespace-pre-wrap">
                                {finalAnswer}
                              </div>
                            ) : (
                              <div className="text-xs italic text-muted-foreground">
                                Chưa có câu trả lời tổng hợp cuối cùng.
                              </div>
                            )}
                          </ScrollArea>
                        </TabsContent>
                      </Tabs>
                    </div>
                  </CollapsibleContent>
                </Collapsible>
              );
            })}
          </div>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  );
}
