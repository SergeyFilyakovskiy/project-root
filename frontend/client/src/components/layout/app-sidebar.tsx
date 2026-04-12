import { Link, useLocation } from "wouter";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  LayoutDashboard,
  Link2,
  BarChart2,
  AlertTriangle,
  FileText,
  Settings,
  LogOut,
  BarChart3,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Дашборд", icon: LayoutDashboard },
  { href: "/integrations", label: "Интеграции", icon: Link2 },
  { href: "/analytics", label: "Аналитика", icon: BarChart2 },
  { href: "/anomalies", label: "Аномалии", icon: AlertTriangle, badge: "!" },
  { href: "/reports", label: "Отчёты", icon: FileText },
];

const bottomItems = [
  { href: "/profile", label: "Настройки", icon: Settings },
];

interface AppSidebarProps {
  collapsed?: boolean;
}

export function AppSidebar({ collapsed }: AppSidebarProps) {
  const [location] = useLocation();
  const { user, logout } = useAuth();

  return (
    <aside
      className={cn(
        "flex flex-col h-screen bg-[hsl(var(--sidebar-background))] border-r border-[hsl(var(--sidebar-border))] transition-all duration-200",
        collapsed ? "w-16" : "w-60"
      )}
    >
      {/* Logo */}
      <div className={cn("flex items-center gap-3 p-4 h-16 border-b border-[hsl(var(--sidebar-border))]", collapsed && "justify-center px-0")}>
        <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center flex-shrink-0">
          <BarChart3 className="w-4 h-4 text-primary-foreground" />
        </div>
        {!collapsed && (
          <span className="font-semibold text-foreground text-base leading-none">AdMetrics</span>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 py-3 overflow-y-auto">
        <ul className="space-y-0.5 px-2">
          {navItems.map(({ href, label, icon: Icon, badge }) => {
            const active = location === href || (href !== "/" && location.startsWith(href));
            return (
              <li key={href}>
                <Link href={href}>
                  <a
                    className={cn(
                      "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors group relative",
                      collapsed && "justify-center px-0 w-10 mx-auto",
                      active
                        ? "bg-[hsl(var(--sidebar-accent))] text-[hsl(var(--sidebar-accent-foreground))] font-medium"
                        : "text-[hsl(var(--sidebar-foreground))] hover:bg-[hsl(var(--sidebar-accent))] hover:text-[hsl(var(--sidebar-accent-foreground))]"
                    )}
                    data-testid={`nav-${href.replace("/", "") || "dashboard"}`}
                  >
                    <Icon className={cn("w-4 h-4 flex-shrink-0", active && "text-primary")} />
                    {!collapsed && (
                      <>
                        <span className="flex-1">{label}</span>
                        {badge && (
                          <Badge variant="destructive" className="text-xs h-4 px-1">
                            {badge}
                          </Badge>
                        )}
                      </>
                    )}
                    {collapsed && (
                      <span className="sr-only">{label}</span>
                    )}
                  </a>
                </Link>
              </li>
            );
          })}
        </ul>

        <Separator className="my-3 mx-2 bg-[hsl(var(--sidebar-border))]" />

        <ul className="space-y-0.5 px-2">
          {bottomItems.map(({ href, label, icon: Icon }) => {
            const active = location === href;
            return (
              <li key={href}>
                <Link href={href}>
                  <a
                    className={cn(
                      "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
                      collapsed && "justify-center px-0 w-10 mx-auto",
                      active
                        ? "bg-[hsl(var(--sidebar-accent))] text-[hsl(var(--sidebar-accent-foreground))] font-medium"
                        : "text-[hsl(var(--sidebar-foreground))] hover:bg-[hsl(var(--sidebar-accent))] hover:text-[hsl(var(--sidebar-accent-foreground))]"
                    )}
                    data-testid={`nav-profile`}
                  >
                    <Icon className={cn("w-4 h-4 flex-shrink-0", active && "text-primary")} />
                    {!collapsed && <span>{label}</span>}
                  </a>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* User section */}
      <div className={cn("p-2 border-t border-[hsl(var(--sidebar-border))]", collapsed && "flex justify-center")}>
        {!collapsed ? (
          <div className="flex items-center gap-2 px-2 py-2 rounded-md hover:bg-[hsl(var(--sidebar-accent))] transition-colors group">
            <div className="w-7 h-7 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
              <span className="text-xs font-semibold text-primary">
                {user?.profile?.first_name?.[0]?.toUpperCase() ?? user?.email?.[0]?.toUpperCase() ?? "U"}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-foreground truncate">{user?.profile?.username || user?.email}</p>
              <p className="text-xs text-muted-foreground truncate">{user?.role}</p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="w-6 h-6 opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-destructive"
              onClick={() => logout()}
              data-testid="button-logout"
            >
              <LogOut className="w-3.5 h-3.5" />
            </Button>
          </div>
        ) : (
          <Button
            variant="ghost"
            size="icon"
            className="w-9 h-9 text-muted-foreground hover:text-destructive"
            onClick={() => logout()}
            data-testid="button-logout-collapsed"
          >
            <LogOut className="w-4 h-4" />
          </Button>
        )}
      </div>
    </aside>
  );
}
