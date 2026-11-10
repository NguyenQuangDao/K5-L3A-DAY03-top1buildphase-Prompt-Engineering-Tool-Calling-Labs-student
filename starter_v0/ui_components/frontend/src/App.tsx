import { useEffect, useRef } from "react";
import { Streamlit, withStreamlitConnection, type ComponentProps } from "streamlit-component-lib";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ClarifyOptions } from "@/components/features/ClarifyOptions";
import { ConfirmationCard } from "@/components/features/ConfirmationCard";
import { ToolCallInspector } from "@/components/features/ToolCallInspector";
import { WelcomeScreen } from "@/components/features/WelcomeScreen";
import type { ComponentActionPayload, ComponentPropsArgs } from "@/types";

function makeEventId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

function emitAction(payload: Omit<ComponentActionPayload, "event_id">) {
  Streamlit.setComponentValue({
    event_id: makeEventId(),
    ...payload,
  });
}

function ResearchWorkspaceComponent(props: ComponentProps) {
  const args = (props.args || {}) as ComponentPropsArgs;
  const containerRef = useRef<HTMLDivElement>(null);

  const theme = args.theme === "light" ? "light" : "dark";

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
  }, [theme]);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const updateHeight = () => {
      const h = el.getBoundingClientRect().height;
      Streamlit.setFrameHeight(Math.ceil(h) + 2);
    };

    updateHeight();

    const observer = new ResizeObserver(() => {
      updateHeight();
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, [args]);

  const renderContent = () => {
    switch (args.mode) {
      case "welcome_screen":
        return (
          <WelcomeScreen
            provider={args.provider || "openrouter"}
            model={args.model || "openai/gpt-4o-mini"}
            version={args.version || "v3"}
            toolCount={args.toolCount ?? 0}
            prompts={args.prompts || []}
            onSelectPrompt={(prompt) => emitAction({ type: "select_prompt", prompt })}
          />
        );

      case "tool_inspector":
        return (
          <ToolCallInspector
            toolEvents={args.toolEvents || []}
            finalAnswer={args.finalAnswer}
            turnStatus={args.turnStatus}
            turnIndex={args.turnIndex}
          />
        );

      case "confirmation_card":
        if (!args.pending) return null;
        return (
          <ConfirmationCard
            pending={args.pending}
            msgIndex={args.msgIndex ?? 0}
            onDecision={(confirmationId, msgIndex, approved) =>
              emitAction({
                type: "confirm_action",
                confirmation_id: confirmationId,
                msg_index: msgIndex,
                approved,
              })
            }
            onOpenModal={(confirmationId, msgIndex) =>
              emitAction({
                type: "open_confirm_dialog",
                confirmation_id: confirmationId,
                msg_index: msgIndex,
              })
            }
          />
        );

      case "clarify_options":
        return (
          <ClarifyOptions
            options={args.options || []}
            onSelectOption={(option) =>
              emitAction({
                type: "select_clarify_option",
                option,
              })
            }
          />
        );

      default:
        return null;
    }
  };

  return (
    <TooltipProvider>
      <div ref={containerRef} className="w-full py-0.5">
        {renderContent()}
      </div>
    </TooltipProvider>
  );
}

export default withStreamlitConnection(ResearchWorkspaceComponent);
