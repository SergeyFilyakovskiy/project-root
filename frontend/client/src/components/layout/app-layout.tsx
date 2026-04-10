import { useState } from "react";
import { AppSidebar } from "./app-sidebar";
import { Button } from "@/components/ui/button";
import { PanelLeftClose, PanelLeft } from "lucide-react";

interface AppLayoutProps {
  children: React.ReactNode;
  title: string;
  description?: string;
  actions?: React.ReactNode;
}

export function AppLayout({ children, title, description, actions }: AppLayoutProps) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <AppSidebar collapsed={collapsed} />

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="flex items-center gap-4 h-16 px-6 border-b border-border bg-card flex-shrink-0">
          <Button
            variant="ghost"
            size="icon"
            className="w-8 h-8 text-muted-foreground"
            onClick={() => setCollapsed(c => !c)}
            data-testid="button-toggle-sidebar"
          >
            {collapsed ? <PanelLeft className="w-4 h-4" /> : <PanelLeftClose className="w-4 h-4" />}
          </Button>

          <div className="flex-1 min-w-0">
            <h1 className="text-base font-semibold text-foreground leading-none truncate">{title}</h1>
            {description && (
              <p className="text-xs text-muted-foreground mt-0.5 truncate">{description}</p>
            )}
          </div>

          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
