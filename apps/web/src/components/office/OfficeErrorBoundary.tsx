"use client";

import { Component, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}
interface State {
  hasError: boolean;
  message: string;
}

export class OfficeErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, message: "" };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, message: error.message };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center w-full h-screen bg-[#08081a]">
          <div className="text-center">
            <p className="text-white/60 text-sm mb-2">Office canvas unavailable</p>
            <p className="text-slate-500 text-xs">{this.state.message}</p>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
