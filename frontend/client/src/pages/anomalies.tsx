import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { AppLayout } from "@/components/layout/app-layout";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { analyticsApi, integrationApi } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { AlertTriangle, CheckCircle2, Clock, Filter, AlertCircle } from "lucide-react";
import { format } from "date-fns";
import { ru } from "date-fns/locale";

const SEVERITY_COLORS: Record<string, string> = {
  high: "text-destructive bg-destructive/10",
  medium: "text-chart-3 bg-chart-3/10",
  low: "text-chart-1 bg-chart-1/10",
};

const SEVERITY_LABELS: Record<string, string> = {
  high: "Высокий",
  medium: "Средний",
  low: "Низкий",
};

export default function Anomalies() {
  const { toast } = useToast();
  const qc = useQueryClient();
  const [filterResolved, setFilterResolved] = useState<string>("unresolved");
  const [integrationId, setIntegrationId] = useState<string>("all");

  const { data: integrations } = useQuery({
    queryKey: ["/integrations"],
    queryFn: () => integrationApi.list(),
  });

  const isResolved = filterResolved === "all" ? undefined : filterResolved === "resolved";

  const { data: anomalies, isLoading } = useQuery({
    queryKey: ["/analytics/anomalies", integrationId, isResolved],
    queryFn: () =>
      analyticsApi.anomalies(
        integrationId !== "all" ? integrationId : undefined,
        isResolved,
      ),
  });

  const resolveMutation = useMutation({
    mutationFn: (id: string) => analyticsApi.resolveAnomaly(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["/analytics/anomalies"] });
      toast({ title: "Аномалия помечена как решённая" });
    },
    onError: (e: any) => toast({ title: "Ошибка", description: e.message, variant: "destructive" }),
  });

  const list = Array.isArray(anomalies) ? anomalies : [];

  return (
    <AppLayout
      title="Аномалии"
      description="Автоматически обнаруженные отклонения в показателях"
      actions={
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-muted-foreground" />
          <Select value={filterResolved} onValueChange={setFilterResolved}>
            <SelectTrigger className="w-36 h-8 text-xs" data-testid="select-filter-resolved">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="unresolved">Нерешённые</SelectItem>
              <SelectItem value="resolved">Решённые</SelectItem>
              <SelectItem value="all">Все</SelectItem>
            </SelectContent>
          </Select>
          <Select value={integrationId} onValueChange={setIntegrationId}>
            <SelectTrigger className="w-44 h-8 text-xs" data-testid="select-filter-integration">
              <SelectValue placeholder="Все интеграции" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Все интеграции</SelectItem>
              {integrations?.items?.map((i: any) => (
                <SelectItem key={i.id} value={i.id}>{i.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      }
    >
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <Card key={i} className="border-border">
              <CardContent className="p-4">
                <Skeleton className="h-16 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : list.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="w-14 h-14 rounded-2xl bg-chart-2/10 flex items-center justify-center mb-4">
            <CheckCircle2 className="w-7 h-7 text-chart-2" />
          </div>
          <h3 className="text-base font-medium mb-2">Аномалий нет</h3>
          <p className="text-sm text-muted-foreground">
            {filterResolved === "unresolved"
              ? "Все аномалии решены — отличная работа"
              : "По выбранным фильтрам аномалий не найдено"}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {list.map((anomaly: any) => (
            <Card
              key={anomaly.id}
              className={`border-border transition-opacity ${anomaly.is_resolved ? "opacity-60" : ""}`}
              data-testid={`card-anomaly-${anomaly.id}`}
            >
              <CardContent className="p-4">
                <div className="flex items-start gap-4">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    anomaly.is_resolved ? "bg-muted" : "bg-destructive/10"
                  }`}>
                    {anomaly.is_resolved
                      ? <CheckCircle2 className="w-4 h-4 text-muted-foreground" />
                      : <AlertTriangle className="w-4 h-4 text-destructive" />}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <span className="text-sm font-medium text-foreground">
                        {anomaly.metric ?? "Неизвестная метрика"}
                      </span>
                      {anomaly.severity && (
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${SEVERITY_COLORS[anomaly.severity] ?? "text-muted-foreground bg-muted"}`}>
                          {SEVERITY_LABELS[anomaly.severity] ?? anomaly.severity}
                        </span>
                      )}
                      <Badge variant={anomaly.is_resolved ? "secondary" : "destructive"} className="text-xs">
                        {anomaly.is_resolved ? "Решено" : "Активна"}
                      </Badge>
                    </div>

                    <p className="text-xs text-muted-foreground mb-2 line-clamp-2">
                      {anomaly.description ?? "Обнаружено значительное отклонение от нормы"}
                    </p>

                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {anomaly.detected_at
                          ? format(new Date(anomaly.detected_at), "dd MMM yyyy, HH:mm", { locale: ru })
                          : "—"}
                      </span>
                      {anomaly.integration_id && (
                        <span className="flex items-center gap-1">
                          <AlertCircle className="w-3 h-3" />
                          {integrations?.items?.find((i: any) => i.id === anomaly.integration_id)?.name ?? anomaly.integration_id}
                        </span>
                      )}
                    </div>
                  </div>

                  {!anomaly.is_resolved && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="text-xs h-8 flex-shrink-0"
                      onClick={() => resolveMutation.mutate(anomaly.id)}
                      disabled={resolveMutation.isPending}
                      data-testid={`button-resolve-${anomaly.id}`}
                    >
                      <CheckCircle2 className="w-3 h-3 mr-1.5" />
                      Решить
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </AppLayout>
  );
}
