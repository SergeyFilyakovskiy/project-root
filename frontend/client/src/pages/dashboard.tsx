import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AppLayout } from "@/components/layout/app-layout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { integrationApi, analyticsApi } from "@/lib/api";
import {
  MousePointerClick, Eye, TrendingUp, DollarSign,
  AlertTriangle, Link2, ArrowUpRight, ArrowDownRight,
} from "lucide-react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from "recharts";
import { format, subDays } from "date-fns";
import { ru } from "date-fns/locale";

const today = format(new Date(), "yyyy-MM-dd");
const thirtyDaysAgo = format(subDays(new Date(), 30), "yyyy-MM-dd");

function KpiCard({ title, value, icon: Icon, change, loading, color = "text-primary" }: {
  title: string; value: string; icon: React.ElementType;
  change?: number; loading?: boolean; color?: string;
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
                  {change >= 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
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
  const [selectedId, setSelectedId] = useState<string>("");

  const { data: integrations, isLoading: intLoading } = useQuery({
    queryKey: ["/integrations"],
    queryFn: () => integrationApi.list(),
  });

  // После загрузки интеграций — берём первую если ничего не выбрано
  const effectiveId = selectedId || integrations?.items?.[0]?.id;

  const { data: kpiData, isLoading: kpiLoading } = useQuery({
    queryKey: ["/analytics/kpi", effectiveId, thirtyDaysAgo, today],
    queryFn: () => analyticsApi.kpi(effectiveId, thirtyDaysAgo, today),
    enabled: !!effectiveId,
  });

  const { data: timeseriesData, isLoading: chartLoading } = useQuery({
    queryKey: ["/analytics/timeseries", effectiveId, thirtyDaysAgo, today],
    queryFn: () => analyticsApi.timeseries(effectiveId, thirtyDaysAgo, today),
    enabled: !!effectiveId,
  });

  const { data: anomalies } = useQuery({
    queryKey: ["/analytics/anomalies", false],
    queryFn: () => analyticsApi.anomalies(undefined, false),
  });

  const unresolvedCount = Array.isArray(anomalies) ? anomalies.length : 0;
  const activeCount = integrations?.items?.filter((i: any) => i.is_active).length ?? 0;

  const kpi = kpiData ?? {};
  const isLoading = intLoading || kpiLoading;

  // Форматируем даты для графика: "2024-04-01" → "01 апр"
  const chartData = Array.isArray(timeseriesData)
    ? timeseriesData.map((r: any) => ({
        ...r,
        date: format(new Date(r.date), "dd MMM", { locale: ru }),
      }))
    : [];

  const selectedIntegration = integrations?.items?.find((i: any) => i.id === effectiveId);

  return (
    <AppLayout
      title="Дашборд"
      description={`Данные за последние 30 дней · ${format(new Date(), "dd MMMM yyyy", { locale: ru })}`}
    >
      {/* Селектор интеграции */}
      <div className="mb-5">
        <Select
          value={effectiveId || ""}
          onValueChange={setSelectedId}
        >
          <SelectTrigger className="w-64 h-8 text-sm" data-testid="select-integration">
            <SelectValue placeholder="Выберите интеграцию" />
          </SelectTrigger>
          <SelectContent>
            {integrations?.items?.map((i: any) => (
              <SelectItem key={i.id} value={i.id}>
                {i.name} · {i.platform}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* KPI карточки */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <KpiCard
          title="Клики"
          value={kpi.total_clicks?.toLocaleString("ru-RU") ?? "—"}
          icon={MousePointerClick}
          loading={isLoading}
          color="text-chart-1"
        />
        <KpiCard
          title="Показы"
          value={kpi.total_impressions?.toLocaleString("ru-RU") ?? "—"}
          icon={Eye}
          loading={isLoading}
          color="text-chart-2"
        />
        <KpiCard
          title="CTR"
          value={kpi.ctr != null ? `${Number(kpi.ctr).toFixed(2)}%` : "—"}
          icon={TrendingUp}
          loading={isLoading}
          color="text-chart-3"
        />
        <KpiCard
          title="Расходы"
          value={kpi.total_spend != null ? `${kpi.total_spend.toLocaleString("ru-RU")} ₽` : "—"}
          icon={DollarSign}
          loading={isLoading}
          color="text-chart-4"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* График */}
        <Card className="lg:col-span-2 border-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Динамика кликов</CardTitle>
            <CardDescription className="text-xs">
              {selectedIntegration ? `Интеграция: ${selectedIntegration.name}` : "Выберите интеграцию"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {chartLoading ? (
              <Skeleton className="h-56 w-full" />
            ) : chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={chartData} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
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
                    name="Клики"
                    stroke="hsl(var(--chart-1))"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-56 flex items-center justify-center text-sm text-muted-foreground">
                Нет данных за выбранный период
              </div>
            )}
          </CardContent>
        </Card>

        {/* Правая колонка */}
        <div className="space-y-4">
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
                    className="flex items-center justify-between py-1.5 cursor-pointer"
                    onClick={() => setSelectedId(int.id)}
                    data-testid={`integration-row-${int.id}`}
                  >
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${int.id === effectiveId ? "bg-primary" : int.is_active ? "bg-chart-2" : "bg-muted-foreground"}`} />
                      <span className="text-sm text-foreground truncate max-w-[120px]">{int.name}</span>
                    </div>
                    <Badge variant={int.is_active ? "default" : "secondary"} className="text-xs">
                      {int.platform}
                    </Badge>
                  </div>
                ))
              ) : (
                <p className="text-xs text-muted-foreground text-center py-3">Нет активных интеграций</p>
              )}
              <div className="pt-1 border-t border-border text-xs text-muted-foreground">
                {activeCount} активных
              </div>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2">
                <AlertTriangle className={`w-4 h-4 ${unresolvedCount > 0 ? "text-chart-3" : "text-muted-foreground"}`} />
                Аномалии
                {unresolvedCount > 0 && (
                  <Badge variant="destructive" className="text-xs ml-auto">{unresolvedCount}</Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {unresolvedCount === 0 ? (
                <p className="text-xs text-muted-foreground text-center py-3">Аномалий не обнаружено</p>
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