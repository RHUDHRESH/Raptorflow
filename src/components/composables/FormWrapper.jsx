import * as React from "react"
import { cn } from "../../lib/utils"
import { Button } from "../ui/button"

const FormWrapper = ({ title, description, onSubmit, children, className, submitText = "Submit", cancelText = "Cancel", onCancel }) => {
    return (
        <form onSubmit={onSubmit} className={cn("space-y-6", className)}>
            {(title || description) && (
                <div className="space-y-2">
                    {title && <h2 className="text-2xl font-bold tracking-tight">{title}</h2>}
                    {description && <p className="text-muted-foreground">{description}</p>}
                </div>
            )}
            <div className="space-y-4">
                {children}
            </div>
            <div className="flex justify-end gap-4">
                {onCancel && (
                    <Button type="button" variant="outline" onClick={onCancel}>
                        {cancelText}
                    </Button>
                )}
                <Button type="submit">{submitText}</Button>
            </div>
        </form>
    )
}

export { FormWrapper }
