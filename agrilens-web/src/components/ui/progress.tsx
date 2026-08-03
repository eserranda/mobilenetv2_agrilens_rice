"use client"

import { Progress as ProgressPrimitive } from "@base-ui/react/progress"

import { cn } from "@/lib/utils"

function Progress({
  className,
  children,
  value,
  ...props
}: ProgressPrimitive.Root.Props) {
  return (
    <ProgressPrimitive.Root
      value={value}
      data-slot="progress"
      className={(state) =>
        cn(
          "flex flex-wrap gap-3",
          typeof className === "function" ? className(state) : className
        )
      }
      {...props}
    >
      {children}
      <ProgressTrack>
        <ProgressIndicator />
      </ProgressTrack>
    </ProgressPrimitive.Root>
  )
}

function ProgressTrack({ className, ...props }: ProgressPrimitive.Track.Props) {
  return (
    <ProgressPrimitive.Track
      className={(state) =>
        cn(
          "relative flex h-1 w-full items-center overflow-x-hidden rounded-full bg-muted",
          typeof className === "function" ? className(state) : className
        )
      }
      data-slot="progress-track"
      {...props}
    />
  )
}

function ProgressIndicator({
  className,
  ...props
}: ProgressPrimitive.Indicator.Props) {
  return (
    <ProgressPrimitive.Indicator
      data-slot="progress-indicator"
      className={(state) =>
        cn(
          "h-full bg-primary transition-all",
          typeof className === "function" ? className(state) : className
        )
      }
      {...props}
    />
  )
}

function ProgressLabel({ className, ...props }: ProgressPrimitive.Label.Props) {
  return (
    <ProgressPrimitive.Label
      className={(state) =>
        cn(
          "text-sm font-medium",
          typeof className === "function" ? className(state) : className
        )
      }
      data-slot="progress-label"
      {...props}
    />
  )
}

function ProgressValue({ className, ...props }: ProgressPrimitive.Value.Props) {
  return (
    <ProgressPrimitive.Value
      className={(state) =>
        cn(
          "ml-auto text-sm text-muted-foreground tabular-nums",
          typeof className === "function" ? className(state) : className
        )
      }
      data-slot="progress-value"
      {...props}
    />
  )
}

export {
  Progress,
  ProgressTrack,
  ProgressIndicator,
  ProgressLabel,
  ProgressValue,
}
