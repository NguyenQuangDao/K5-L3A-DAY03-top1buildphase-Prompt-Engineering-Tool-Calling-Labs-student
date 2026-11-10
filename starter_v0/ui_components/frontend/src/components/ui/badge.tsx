import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-xs font-medium transition-colors focus:outline-none focus:ring-1 focus:ring-ring",
  {
    variants: {
      variant: {
        default: "border-transparent bg-primary text-primary-foreground",
        secondary: "border-transparent bg-secondary text-secondary-foreground",
        destructive:
          "border-red-500/30 bg-red-500/10 text-red-600 dark:border-red-500/30 dark:bg-red-500/15 dark:text-red-400",
        outline: "border-border text-foreground bg-transparent",
        success:
          "border-emerald-500/25 bg-emerald-500/10 text-emerald-700 dark:border-emerald-500/30 dark:bg-emerald-500/15 dark:text-emerald-400",
        warning:
          "border-amber-500/30 bg-amber-500/10 text-amber-700 dark:border-amber-500/30 dark:bg-amber-500/15 dark:text-amber-400",
        info:
          "border-sky-500/30 bg-sky-500/10 text-sky-700 dark:border-sky-500/30 dark:bg-sky-500/15 dark:text-sky-400",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
