import { useState } from "react";
import { AlertTriangle, CheckCircle2, Maximize2, Send, ShieldAlert, XCircle } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import type { PendingConfirmation } from "@/types";

interface ConfirmationCardProps {
  pending: PendingConfirmation;
  msgIndex: number;
  onDecision: (confirmationId: string, msgIndex: number, approved: boolean) => void;
  onOpenModal: (confirmationId: string, msgIndex: number) => void;
}

export function ConfirmationCard({
  pending,
  msgIndex,
  onDecision,
  onOpenModal,
}: ConfirmationCardProps) {
  const [locked, setLocked] = useState(false);

  const handleAction = (approved: boolean) => {
    if (locked || pending.resolved) return;
    setLocked(true);
    onDecision(pending.confirmation_id, msgIndex, approved);
  };

  if (pending.resolved) {
    const isApproved = pending.decision === "approved";
    return (
      <Alert variant={isApproved ? "default" : "warning"} className="bg-card">
        {isApproved ? (
          <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
        ) : (
          <XCircle className="h-4 w-4 text-amber-600 dark:text-amber-400" />
        )}
        <AlertTitle className="text-xs font-semibold">
          {isApproved
            ? `Hành động đã được phê duyệt — ${pending.tool_name}(confirmed=True)`
            : `Hành động đã bị từ chối — ${pending.tool_name} đã hủy`}
        </AlertTitle>
        <AlertDescription className="text-xs">
          {isApproved
            ? `Người dùng đã chấp thuận thực hiện gửi tới: ${pending.destination}.`
            : `Không có tin nhắn nào được gửi ra ngoài tới ${pending.destination}.`}
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <Card className="border-amber-500/40 bg-card shadow-sm">
      <CardHeader className="pb-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <ShieldAlert className="h-4 w-4 text-amber-600 dark:text-amber-400" />
            <CardTitle className="text-sm font-semibold">
              Yêu cầu xác nhận hành động
            </CardTitle>
          </div>
          <div className="flex items-center gap-1.5">
            <Badge variant="warning" className="font-mono text-[11px]">
              needs_confirmation
            </Badge>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="h-7 px-2 text-xs text-muted-foreground"
              onClick={() => onOpenModal(pending.confirmation_id, msgIndex)}
              title="Mở cửa sổ chi tiết"
            >
              <Maximize2 className="mr-1 h-3 w-3" />
              Chi tiết
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-3 pb-3 text-xs">
        <div className="grid grid-cols-1 gap-2 rounded-lg border bg-muted/40 p-2.5 sm:grid-cols-2">
          <div>
            <span className="text-muted-foreground">Công cụ: </span>
            <code className="font-mono font-semibold text-foreground">
              {pending.tool_name} ({pending.underlying_tool})
            </code>
          </div>
          <div>
            <span className="text-muted-foreground">Đích đến: </span>
            <span className="font-medium text-foreground">{pending.destination}</span>
          </div>
        </div>

        <div className="space-y-1">
          <div className="font-mono text-[11px] font-medium text-muted-foreground">
            NỘI DUNG GỬI (PAYLOAD)
          </div>
          <div className="max-h-40 overflow-y-auto rounded-lg border bg-background p-3 font-mono text-xs leading-relaxed text-foreground whitespace-pre-wrap">
            {pending.text || "(Nội dung tin nhắn trống)"}
          </div>
        </div>

        <Alert variant="warning" className="py-2.5">
          <AlertTriangle className="h-3.5 w-3.5" />
          <AlertDescription className="text-xs">
            Cơ chế bảo vệ: Tham số <code className="font-mono">confirmed=True</code> chỉ được kích hoạt khi bạn phê duyệt. Nhấn Từ chối sẽ hủy tác vụ mà không gửi dữ liệu.
          </AlertDescription>
        </Alert>
      </CardContent>

      <Separator />
      <CardFooter className="flex flex-wrap items-center justify-end gap-2 pt-3">
        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={locked}
          onClick={() => handleAction(false)}
        >
          <XCircle className="h-3.5 w-3.5" />
          Từ chối
        </Button>
        <Button
          type="button"
          variant="default"
          size="sm"
          disabled={locked}
          onClick={() => handleAction(true)}
        >
          <Send className="h-3.5 w-3.5" />
          {locked ? "Đang xử lý..." : "Phê duyệt & Gửi"}
        </Button>
      </CardFooter>
    </Card>
  );
}
