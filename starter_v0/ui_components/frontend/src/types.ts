export type ThemeMode = "light" | "dark";

export type ToolStatus =
  | "Pending"
  | "Running"
  | "Completed"
  | "Failed"
  | "Awaiting Confirmation";

export interface ToolEvent {
  tool: string;
  args: Record<string, unknown>;
  result: unknown;
  round?: number;
  step?: number;
  ui_status?: ToolStatus;
  duration_ms?: number;
}

export interface PendingConfirmation {
  confirmation_id: string;
  tool_name: string;
  underlying_tool: string;
  text: string;
  destination: string;
  args: Record<string, unknown>;
  resolved: boolean;
  decision: "approved" | "rejected" | null;
}

export interface PromptSuggestion {
  id: string;
  category: string;
  title: string;
  prompt: string;
  icon: string;
}

export type ComponentMode =
  | "welcome_screen"
  | "tool_inspector"
  | "confirmation_card"
  | "clarify_options";

export interface ComponentPropsArgs {
  mode: ComponentMode;
  theme: ThemeMode;
  // welcome_screen
  provider?: string;
  model?: string;
  version?: string;
  toolCount?: number;
  prompts?: PromptSuggestion[];
  // tool_inspector
  toolEvents?: ToolEvent[];
  finalAnswer?: string | null;
  turnStatus?: string;
  turnIndex?: number;
  // confirmation_card
  pending?: PendingConfirmation;
  msgIndex?: number;
  // clarify_options
  question?: string;
  options?: string[];
}

export interface ComponentActionPayload {
  event_id: string;
  type: "select_prompt" | "confirm_action" | "open_confirm_dialog" | "select_clarify_option";
  prompt?: string;
  confirmation_id?: string;
  msg_index?: number;
  approved?: boolean;
  option?: string;
}
