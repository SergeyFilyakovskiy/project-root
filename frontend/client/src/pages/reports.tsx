import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AppLayout } from "@/components/layout/app-layout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { integrationApi } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import {
  FileText,
  Download,
  FileSpreadsheet,
  FileType,
  Loader2,
} from "lucide-react";
import { format, subDays } from "date-fns";

const today = format(new Date(), "yyyy-MM-dd");
const thirtyDaysAgo = format(subDays(new Date(), 30), "yyyy-MM-dd");

const EXPORT_FORMATS = [
  { value: "csv", label: "CSV", icon: FileSpreadsheet, description: "Для Excel и Google Sheets" },
  { value: "xlsx", label: "XLSX", icon: FileSpreadsheet, description: "Книга Excel с форматированием" },
  { value: "pdf", label: "PDF", icon: FileType, description: "Готовый отчёт для презентации" },
];

const REPORT_TYPES = [
  { value: "kpi", label: "KPI отчёт", description: "Клики, показы, CTR, расходы" },
  { value: "funnel", label: "Воронка", description: "Конверсионная воронка" },
  { value: "anomalies", label: "Аномалии", description: "Список обнаруженных аномалий" },
  { value: "compare", label: "Сравнение платформ", description: "Эффективность по платформам" },
];

export default function Reports() {
  const { toast } = useToast();
  const [integrationId, setIntegrationId] = useState("");
  const [dateFrom, setDateFrom] = useState(thirtyDaysAgo);
  const [dateTo, setDateTo] = useState(today);
  const [reportType, setReportType] = useState("kpi");
  const [exportFormat, setExportFormat] = useState("pdf");
  const [loading, setLoading] = useState(false);

  const { data: integrations } = useQuery({
    queryKey: ["/integrations"],
    queryFn: () => integrationApi.list(),
  });

  const handleExport = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        integration_id: integrationId || (integrations?.items?.[0]?.id ?? ""),
        date_from: dateFrom,
        date_to: dateTo,
        report_type: reportType,
        format: exportFormat,
      });
      const res = await fetch(`/api/reports/export?${params}`, { credentials: "include" });
      if (!res.ok) throw new Error("Ошибка генерации отчёта");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `admetrics_${reportType}_${dateFrom}_${dateTo}.${exportFormat}`;
      a.click();
      URL.revokeObjectURL(url);
      toast({ title: "Отчёт загружен" });
    } catch (e: any) {
      toast({ title: "Ошибка", description: e.message, variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout
      title="Отчёты"
      description="Генерация и экспорт аналитических отчётов"
    >
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Config panel */}
        <div className="lg:col-span-1 space-y-5">
          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Параметры отчёта</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label className="text-xs">Интеграция</Label>
                <Select value={integrationId} onValueChange={setIntegrationId}>
                  <SelectTrigger className="h-8 text-sm" data-testid="select-report-integration">
                    <SelectValue placeholder="Первая активная" />
                  </SelectTrigger>
                  <SelectContent>
                    {integrations?.items?.map((i: any) => (
                      <SelectItem key={i.id} value={i.id}>{i.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label className="text-xs">С</Label>
                  <Input
                    type="date"
                    value={dateFrom}
                    onChange={e => setDateFrom(e.target.value)}
                    className="h-8 text-sm"
                    data-testid="input-report-date-from"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-xs">По</Label>
                  <Input
                    type="date"
                    value={dateTo}
                    onChange={e => setDateTo(e.target.value)}
                    className="h-8 text-sm"
                    data-testid="input-report-date-to"
                  />
                </div>
              </div>

              <Separator />

              <div className="space-y-2">
                <Label className="text-xs">Тип отчёта</Label>
                <div className="space-y-2">
                  {REPORT_TYPES.map(rt => (
                    <button
                      key={rt.value}
                      className={`w-full text-left px-3 py-2.5 rounded-md border transition-colors ${
                        reportType === rt.value
                          ? "border-primary bg-primary/10 text-foreground"
                          : "border-border hover:bg-muted text-muted-foreground"
                      }`}
                      onClick={() => setReportType(rt.value)}
                      data-testid={`radio-report-${rt.value}`}
                    >
                      <p className="text-xs font-medium">{rt.label}</p>
                      <p className="text-xs opacity-70 mt-0.5">{rt.description}</p>
                    </button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Format + preview */}
        <div className="lg:col-span-2 space-y-5">
          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Формат экспорта</CardTitle>
              <CardDescription className="text-xs">Выберите формат файла</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-3">
                {EXPORT_FORMATS.map(({ value, label, icon: Icon, description }) => (
                  <button
                    key={value}
                    className={`p-4 rounded-lg border text-left transition-all ${
                      exportFormat === value
                        ? "border-primary bg-primary/10"
                        : "border-border hover:bg-muted"
                    }`}
                    onClick={() => setExportFormat(value)}
                    data-testid={`format-${value}`}
                  >
                    <Icon className={`w-6 h-6 mb-2 ${exportFormat === value ? "text-primary" : "text-muted-foreground"}`} />
                    <p className="text-sm font-medium text-foreground">{label}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{description}</p>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Summary */}
          <Card className="border-border bg-muted/30">
            <CardContent className="p-5">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-sm font-semibold text-foreground mb-1">Сводка</h3>
                  <p className="text-xs text-muted-foreground">Параметры генерируемого отчёта</p>
                </div>
                <FileText className="w-5 h-5 text-muted-foreground" />
              </div>
              <div className="space-y-2 text-sm mb-5">
                {[
                  { label: "Тип", value: REPORT_TYPES.find(r => r.value === reportType)?.label },
                  { label: "Интеграция", value: integrations?.items?.find((i: any) => i.id === integrationId)?.name ?? "Первая активная" },
                  { label: "Период", value: `${dateFrom} — ${dateTo}` },
                  { label: "Формат", value: exportFormat.toUpperCase() },
                ].map(({ label, value }) => (
                  <div key={label} className="flex items-center justify-between">
                    <span className="text-muted-foreground text-xs">{label}</span>
                    <Badge variant="secondary" className="text-xs">{value}</Badge>
                  </div>
                ))}
              </div>
              <Button
                className="w-full"
                onClick={handleExport}
                disabled={loading}
                data-testid="button-export"
              >
                {loading
                  ? <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  : <Download className="w-4 h-4 mr-2" />}
                Скачать отчёт
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}
