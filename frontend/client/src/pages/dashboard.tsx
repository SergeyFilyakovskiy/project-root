import { useQuery } from "@tanstack/react-query";
import { AppLayout } from "@/components/layout/app-layout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { integrationApi, analyticsApi } from "@/lib/api";
import {
  MousePointerClick,
  Eye,
  TrendingUp,
  DollarSign,
  AlertTriangle,
  Link2,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { format, subDays } from "date-fns";
import { ru } from "date-fns/locale";

const today = format(new Date(), "yyyy-MM-dd");
const thirtyDaysAgo = format(subDays(new Date(), 30), "yyyy-MM-dd");

// Fallback demo chart data
const demoChartData = Array.from({ length: 14 }, (_, i) => ({
  date: format(subDays(new Date(), 13 - i), "dd MMM", { locale: ru }),
  clicks: Math.floor(Math.random() * 1200 + 400),
  impressions: Math.floor(Math.random() * 40000 + 15000),
  cost: Math.floor(Math.random() * 8000 + 2000),
}));

function KpiCard({
  title,
  value,
  icon: Icon,
  change,
  loading,
  color = "text-primary",
}: {
  title: string;
  value: string;
  icon: React.ElementType;
  change?: number;
  loading?: boolean;
  color?: string;
}) {
  return (
    <Card className="border-border" data-testid={`card-kpi-${title}`}>
      <CardContent className="pt-5 pb-5">
        {loading ? (
          <div className="space-y-2">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-7 w-32" />
          </div>
        ) : (
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs text-muted-foreground mb-1.5">{title}</p>
              <p className="text-xl font-bold text-foreground">{value}</p>
              {change !== undefined && (
                <div className={`flex items-center gap-1 mt-1 text-xs ${change >= 0 ? "text-chart-2" : "text-destructive"}`}>
                  {change >= 0
                    ? <ArrowUpRight className="w-3 h-3" />
                    : <ArrowDownRight className="w-3 h-3" />}
                  <span>{Math.abs(change).toFixed(1)}% vs прошлый период</span>
                </div>
              )}
            </div>
            <div className={`w-9 h-9 rounded-lg bg-muted flex items-center justify-center ${color}`}>
              <Icon className="w-4 h-4" />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function Dashboard() {
  const { data: integrations, isLoading: intLoading } = useQuery({
    queryKey: ["/integrations"],
    queryFn: () => integrationApi.list(),
  });

  const firstIntegration = integrations?.items?.[0];

  const { data: kpiData, isLoading: kpiLoading } = useQuery({
    queryKey: ["/analytics/kpi", firstIntegration?.id],
    queryFn: () => analyticsApi.kpi(firstIntegration!.id, thirtyDaysAgo, today),
    enabled: !!firstIntegration?.id,
  });

  const { data: anomalies } = useQuery({
    queryKey: ["/analytics/anomalies", false],
    queryFn: () => analyticsApi.anomalies(undefined, false),
  });

  const unresolvedCount = Array.isArray(anomalies) ? anomalies.length : 0;
  const activeCount = integrations?.items?.filter((i: any) => i.is_active).length ?? 0;

  const kpi = kpiData ?? {};
  const isLoading = intLoading || kpiLoading;

  return (
    <AppLayout
      title="Дашборд"
      description={`Данные за последние 30 дней · ${format(new Date(), "dd MMMM yyyy", { locale: ru })}`}
    >
      {/* KPI grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <KpiCard
          title="Клики"
          value={kpi.total_clicks?.toLocaleString("ru-RU") ?? "—"}
          icon={MousePointerClick}
          change={kpi.clicks_change}
          loading={isLoading}
          color="text-chart-1"
        />
        <KpiCard
          title="Показы"
          value={kpi.total_impressions?.toLocaleString("ru-RU") ?? "—"}
          icon={Eye}
          change={kpi.impressions_change}
          loading={isLoading}
          color="text-chart-2"
        />
        <KpiCard
          title="CTR"
          value={kpi.ctr ? `${(kpi.ctr * 100).toFixed(2)}%` : "—"}
          icon={TrendingUp}
          change={kpi.ctr_change}
          loading={isLoading}
          color="text-chart-3"
        />
        <KpiCard
          title="Расходы"
          value={kpi.total_cost ? `${kpi.total_cost.toLocaleString("ru-RU")} ₽` : "—"}
          icon={DollarSign}
          change={kpi.cost_change}
          loading={isLoading}
          color="text-chart-4"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Main chart */}
        <Card className="lg:col-span-2 border-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Динамика кликов</CardTitle>
            <CardDescription className="text-xs">
              {firstIntegration
                ? `Интеграция: ${firstIntegration.name}`
                : "Подключите интеграцию для отображения данных"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={demoChartData} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis
                  dataKey="date"
                  tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip
                  contentStyle={{
                    background: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "8px",
                    color: "hsl(var(--foreground))",
                    fontSize: 12,
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="clicks"
                  stroke="hsl(var(--chart-1))"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Status cards */}
        <div className="space-y-4">
          {/* Integrations status */}
          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2">
                <Link2 className="w-4 h-4 text-primary" />
                Интеграции
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {intLoading ? (
                <div className="space-y-2">
                  <Skeleton className="h-10 w-full" />
                  <Skeleton className="h-10 w-full" />
                </div>
              ) : integrations?.items?.length ? (
                integrations.items.slice(0, 4).map((int: any) => (
                  <div
                    key={int.id}
                    className="flex items-center justify-between py-1.5"
                    data-testid={`integration-row-${int.id}`}
                  >
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${int.is_active ? "bg-chart-2" : "bg-muted-foreground"}`} />
                      <span className="text-sm text-foreground truncate max-w-[120px]">{int.name}</span>
                    </div>
                    <Badge
                      variant={int.is_active ? "default" : "secondary"}
                      className="text-xs"
                    >
                      {int.platform}
                    </Badge>
                  </div>
                ))
              ) : (
                <p className="text-xs text-muted-foreground text-center py-3">
                  Нет активных интеграций
                </p>
              )}
              <div className="pt-1 border-t border-border text-xs text-muted-foreground">
                {activeCount} активных
              </div>
            </CardContent>
          </Card>

          {/* Anomalies */}
          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2">
                <AlertTriangle className={`w-4 h-4 ${unresolvedCount > 0 ? "text-chart-3" : "text-muted-foreground"}`} />
                Аномалии
                {unresolvedCount > 0 && (
                  <Badge variant="destructive" className="text-xs ml-auto">
                    {unresolvedCount}
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {unresolvedCount === 0 ? (
                <p className="text-xs text-muted-foreground text-center py-3">
                  Аномалий не обнаружено
                </p>
              ) : (
                <p className="text-sm text-chart-3">
                  Обнаружено {unresolvedCount} нерешённых аномалий. Перейдите на страницу аномалий для подробностей.
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}
