import * as React from "react"
import { cn } from "../../lib/utils"

const ChartWrapper = ({ title, description, children, className }) => {
    return (
        <div className={cn("rounded-lg border bg-card text-card-foreground shadow-sm", className)}>
            {(title || description) && (
                <div className="flex flex-col space-y-1.5 p-6">
                    {title && <h3 className="text-2xl font-semibold leading-none tracking-tight">{title}</h3>}
                    {description && <p className="text-sm text-muted-foreground">{description}</p>}
                </div>
            )}
            <div className="p-6 pt-0">
                {children}
            </div>
        </div>
    )
}

export { ChartWrapper }
