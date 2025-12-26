import * as React from "react"
import { cn } from "@/lib/utils"

interface ButtonGroupProps extends React.HTMLAttributes<HTMLDivElement> {
    children: React.ReactNode
}

const ButtonGroup = React.forwardRef<HTMLDivElement, ButtonGroupProps>(
    ({ className, children, ...props }, ref) => {
        return (
            <div
                ref={ref}
                className={cn(
                    "flex items-center -space-x-px rounded-md",
                    "[&_>_button]:rounded-none [&_>_button:first-child]:rounded-l-md [&_>_button:last-child]:rounded-r-md",
                    "[&_>_button]:border [&_>_button]:border-input",
                    "[&_>_button:focus-visible]:relative [&_>_button:focus-visible]:z-10",
                    className
                )}
                {...props}
            >
                {children}
            </div>
        )
    }
)
ButtonGroup.displayName = "ButtonGroup"

export { ButtonGroup }
