import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AppLayout } from "@/components/layout/app-layout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { analyticsApi, integrationApi } from "@/lib/api";
import { format, subDays } from "date-fns";
import { ru } from "date-fns/locale";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  FunnelChart,
  Funnel,
  LabelList,
} from "recharts";
import { BarChart2, TrendingUp } from "lucide-react";

const today = format(new Date(), "yyyy-MM-dd");
const thirtyDaysAgo = format(subDays(new Date(), 30), "yyyy-MM-dd");
const sixtyDaysAgo = format(subDays(new Date(), 60), "yyyy-MM-dd");

const COLORS = [
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-3))",
  "hsl(var(--chart-4))",
  "hsl(var(--chart-5))",
];

const demoFunnel = [
  { name: "Показы", value: 120000, fill: "hsl(var(--chart-1))" },
  { name: "Клики", value: 8400, fill: "hsl(var(--chart-2))" },
  { name: "Лиды", value: 620, fill: "hsl(var(--chart-3))" },
  { name: "Конверсии", value: 94, fill: "hsl(var(--chart-4))" },
];

const demoPlatforms = [
  { platform: "Google Ads", clicks: 3200, cost: 45000, ctr: 2.8 },
  { platform: "Яндекс Директ", clicks: 2800, cost: 32000, ctr: 3.1 },
  { platform: "Meta Ads", clicks: 2100, cost: 28000, ctr: 1.9 },
];

export default function Analytics() {
  const [integrationId, setIntegrationId] = useState<string>("");
  const [dateFrom, setDateFrom] = useState(thirtyDaysAgo);
  const [dateTo, setDateTo] = useState(today);
  const [periodAFrom] = useState(thirtyDaysAgo);
  const [periodATo] = useState(today);
  const [periodBFrom] = useState(sixtyDaysAgo);
  const [periodBTo] = useState(thirtyDaysAgo);

  const { data: integrations } = useQuery({
    queryKey: ["/integrations"],
    queryFn: () => integrationApi.list(),
  });

  const effectiveId = integrationId || integrations?.items?.[0]?.id;

  const { data: kpi, isLoading: kpiLoading } = useQuery({
    queryKey: ["/analytics/kpi", effectiveId, dateFrom, dateTo],
    queryFn: () => analyticsApi.kpi(effectiveId, dateFrom, dateTo),
    enabled: !!effectiveId,
  });

  const { data: funnel, isLoading: funnelLoading } = useQuery({
    queryKey: ["/analytics/funnel", effectiveId, dateFrom, dateTo],
    queryFn: () => analyticsApi.funnel(effectiveId, dateFrom, dateTo),
    enabled: !!effectiveId,
  });

  const { data: compareData, isLoading: compareLoading } = useQuery({
    queryKey: ["/analytics/compare/periods", effectiveId, periodAFrom, periodATo, periodBFrom, periodBTo],
    queryFn: () => analyticsApi.comparePeriods(effectiveId, periodAFrom, periodATo, periodBFrom, periodBTo),
    enabled: !!effectiveId,
  });

  const { data: platformData, isLoading: platformLoading } = useQuery({
    queryKey: ["/analytics/compare/platforms", effectiveId, dateFrom, dateTo],
    queryFn: () => analyticsApi.comparePlatforms(effectiveId, dateFrom, dateTo),
    enabled: !!effectiveId,
  });

  const funnelData = Array.isArray(funnel) && funnel.length > 0
    ? funnel.map((d: any, i: number) => ({ ...d, fill: COLORS[i % COLORS.length] }))
    : demoFunnel;

  const platformChartData = Array.isArray(platformData) && platformData.length > 0
    ? platformData
    : demoPlatforms;

  return (
    <AppLayout
      title="Аналитика"
      description="Глубокий анализ эффективности рекламных кампаний"
    >
      {/* Filters */}
      <div className="flex flex-wrap items-end gap-4 mb-6 p-4 rounded-lg bg-card border border-border">
        <div className="space-y-1.5">
          <Label className="text-xs">Интеграция</Label>
          <Select
            value={integrationId || ""}
            onValueChange={setIntegrationId}
          >
            <SelectTrigger className="w-52 h-8 text-sm" data-testid="select-integration">
              <SelectValue placeholder="Все интеграции" />
            </SelectTrigger>
            <SelectContent>
              {integrations?.items?.map((i: any) => (
                <SelectItem key={i.id} value={i.id}>{i.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-1.5">
          <Label className="text-xs">С</Label>
          <Input
            type="date"
            value={dateFrom}
            onChange={e => setDateFrom(e.target.value)}
            className="w-36 h-8 text-sm"
            data-testid="input-date-from"
          />
        </div>
        <div className="space-y-1.5">
          <Label className="text-xs">По</Label>
          <Input
            type="date"
            value={dateTo}
            onChange={e => setDateTo(e.target.value)}
            className="w-36 h-8 text-sm"
            data-testid="input-date-to"
          />
        </div>
      </div>

      {!effectiveId ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <BarChart2 className="w-12 h-12 text-muted-foreground mb-4" />
          <h3 className="text-base font-medium mb-2">Нет данных</h3>
          <p className="text-sm text-muted-foreground">
            Добавьте хотя бы одну интеграцию для отображения аналитики
          </p>
        </div>
      ) : (
        <Tabs defaultValue="kpi" className="space-y-4">
          <TabsList className="h-8">
            <TabsTrigger value="kpi" className="text-xs">KPI</TabsTrigger>
            <TabsTrigger value="funnel" className="text-xs">Воронка</TabsTrigger>
            <TabsTrigger value="periods" className="text-xs">Сравнение периодов</TabsTrigger>
            <TabsTrigger value="platforms" className="text-xs">Сравнение платформ</TabsTrigger>
          </TabsList>

          {/* KPI Tab */}
          <TabsContent value="kpi">
            {kpiLoading ? (
              <div className="grid grid-cols-2 gap-4">
                {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-28" />)}
              </div>
            ) : kpi ? (
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {[
                  { label: "Клики", value: kpi.total_clicks?.toLocaleString("ru-RU"), color: "text-chart-1" },
                  { label: "Показы", value: kpi.total_impressions?.toLocaleString("ru-RU"), color: "text-chart-2" },
                  { label: "CTR", value: kpi.ctr ? `${(kpi.ctr * 100).toFixed(2)}%` : "—", color: "text-chart-3" },
                  { label: "Расходы", value: kpi.total_cost ? `${kpi.total_cost.toLocaleString("ru-RU")} ₽` : "—", color: "text-chart-4" },
                  { label: "CPC", value: kpi.cpc ? `${kpi.cpc.toFixed(2)} ₽` : "—", color: "text-chart-1" },
                  { label: "CPA", value: kpi.cpa ? `${kpi.cpa.toFixed(2)} ₽` : "—", color: "text-chart-5" },
                  { label: "ROAS", value: kpi.roas ? kpi.roas.toFixed(2) : "—", color: "text-chart-2" },
                  { label: "Конверсии", value: kpi.conversions?.toLocaleString("ru-RU") ?? "—", color: "text-chart-3" },
                ].map(({ label, value, color }) => (
                  <Card key={label} className="border-border">
                    <CardContent className="pt-4 pb-4">
                      <p className="text-xs text-muted-foreground mb-1">{label}</p>
                      <p className={`text-xl font-bold ${color}`}>{value ?? "—"}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground text-center py-8">Нет данных за выбранный период</p>
            )}
          </TabsContent>

          {/* Funnel Tab */}
          <TabsContent value="funnel">
            <Card className="border-border">
              <CardHeader>
                <CardTitle className="text-base">Воронка конверсий</CardTitle>
                <CardDescription className="text-xs">
                  {funnelLoading ? "Загрузка..." : "Путь пользователя от показа до конверсии"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {funnelData.map((step: any, idx: number) => {
                    const maxVal = funnelData[0]?.value ?? 1;
                    const pct = Math.round((step.value / maxVal) * 100);
                    return (
                      <div key={step.name} className="space-y-1" data-testid={`funnel-step-${idx}`}>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-foreground">{step.name}</span>
                          <div className="flex items-center gap-3">
                            <span className="text-muted-foreground text-xs">{pct}%</span>
                            <span className="font-medium text-foreground w-20 text-right">
                              {step.value.toLocaleString("ru-RU")}
                            </span>
                          </div>
                        </div>
                        <div className="h-2 bg-muted rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all duration-500"
                            style={{ width: `${pct}%`, background: step.fill }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Compare periods Tab */}
          <TabsContent value="periods">
            <Card className="border-border">
              <CardHeader>
                <CardTitle className="text-base">Сравнение периодов</CardTitle>
                <CardDescription className="text-xs">
                  Текущий период (30 дней) vs предыдущий (31-60 дней назад)
                </CardDescription>
              </CardHeader>
              <CardContent>
                {compareLoading ? (
                  <Skeleton className="h-56 w-full" />
                ) : compareData ? (
                  <ResponsiveContainer width="100%" height={240}>
                    <BarChart
                      data={[
                        {
                          metric: "Клики",
                          "Период A": compareData.period_a?.total_clicks,
                          "Период B": compareData.period_b?.total_clicks,
                        },
                        {
                          metric: "CTR",
                          "Период A": (compareData.period_a?.ctr * 100)?.toFixed(2),
                          "Период B": (compareData.period_b?.ctr * 100)?.toFixed(2),
                        },
                      ]}
                      margin={{ top: 4, right: 8, left: -16, bottom: 0 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis dataKey="metric" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} tickLine={false} axisLine={false} />
                      <YAxis tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} tickLine={false} axisLine={false} />
                      <Tooltip contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8, color: "hsl(var(--foreground))", fontSize: 12 }} />
                      <Legend wrapperStyle={{ fontSize: 12 }} />
                      <Bar dataKey="Период A" fill="hsl(var(--chart-1))" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="Период B" fill="hsl(var(--chart-2))" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-8">Нет данных</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Compare platforms Tab */}
          <TabsContent value="platforms">
            <Card className="border-border">
              <CardHeader>
                <CardTitle className="text-base">Сравнение платформ</CardTitle>
                <CardDescription className="text-xs">Клики и расходы по рекламным платформам</CardDescription>
              </CardHeader>
              <CardContent>
                {platformLoading ? (
                  <Skeleton className="h-56 w-full" />
                ) : (
                  <ResponsiveContainer width="100%" height={240}>
                    <BarChart
                      data={platformChartData}
                      margin={{ top: 4, right: 8, left: -16, bottom: 0 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis dataKey="platform" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} tickLine={false} axisLine={false} />
                      <YAxis tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} tickLine={false} axisLine={false} />
                      <Tooltip contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8, color: "hsl(var(--foreground))", fontSize: 12 }} />
                      <Legend wrapperStyle={{ fontSize: 12 }} />
                      <Bar dataKey="clicks" name="Клики" fill="hsl(var(--chart-1))" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="cost" name="Расходы (₽)" fill="hsl(var(--chart-3))" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </AppLayout>
  );
}
