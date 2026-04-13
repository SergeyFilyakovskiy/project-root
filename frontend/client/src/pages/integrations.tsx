import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { AppLayout } from "@/components/layout/app-layout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { integrationApi } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import {
  Plus,
  Trash2,
  ExternalLink,
  CheckCircle2,
  Loader2,
  Link2,
  AlertCircle,
} from "lucide-react";
import { SiGoogleads, SiYandexcloud, SiFacebook } from "react-icons/si";
import { format } from "date-fns";
import { ru } from "date-fns/locale";

const PLATFORM_ICONS: Record<string, React.ElementType> = {
  google_ads: SiGoogleads,
  yandex_direct: SiYandexcloud,
  meta_ads: SiFacebook,
};

const PLATFORM_LABELS: Record<string, string> = {
  google_ads: "Google Ads",
  yandex_direct: "Яндекс Директ",
  meta_ads: "Meta Ads",
};

function IntegrationCard({ integration, onDelete, onOAuth }: {
  integration: any;
  onDelete: (id: string) => void;
  onOAuth: (id: string) => void;
}) {
  const PlatformIcon = PLATFORM_ICONS[integration.platform] ?? Link2;
  const isExpired = integration.token_expires_at
    ? new Date(integration.token_expires_at) < new Date()
    : true;

  return (
    <Card className="border-border" data-testid={`card-integration-${integration.id}`}>
      <CardContent className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center">
              <PlatformIcon className="w-5 h-5 text-foreground" />
            </div>
            <div>
              <p className="text-sm font-medium text-foreground">{integration.name}</p>
              <p className="text-xs text-muted-foreground">
                {PLATFORM_LABELS[integration.platform] ?? integration.platform}
              </p>
            </div>
          </div>
          <Badge variant={integration.is_active ? "default" : "secondary"} className="text-xs">
            {integration.is_active ? "Активна" : "Отключена"}
          </Badge>
        </div>

        {/* Token status — берётся из token_expires_at в ответе списка */}
        <div className="flex items-center gap-2 mb-4">
          {!isExpired ? (
            <>
              <CheckCircle2 className="w-3.5 h-3.5 text-chart-2" />
              <span className="text-xs text-chart-2">
                Токен действует до{" "}
                {format(new Date(integration.token_expires_at), "dd MMM yyyy", { locale: ru })}
              </span>
            </>
          ) : (
            <>
              <AlertCircle className="w-3.5 h-3.5 text-chart-3" />
              <span className="text-xs text-chart-3">Требуется авторизация</span>
            </>
          )}
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            className="flex-1 text-xs h-8"
            onClick={() => onOAuth(integration.id)}
            data-testid={`button-oauth-${integration.id}`}
          >
            <ExternalLink className="w-3 h-3 mr-1.5" />
            {isExpired ? "Авторизовать" : "Переподключить"}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="w-8 h-8 text-muted-foreground hover:text-destructive"
            onClick={() => onDelete(integration.id)}
            data-testid={`button-delete-${integration.id}`}
          >
            <Trash2 className="w-3.5 h-3.5" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export default function Integrations() {
  const { toast } = useToast();
  const qc = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [form, setForm] = useState({ name: "", platform: "" });

  const { data, isLoading } = useQuery({
    queryKey: ["/integrations"],
    queryFn: () => integrationApi.list(),
  });

  // Перезагружаем список когда:
  // 1. Вкладка получает фокус (пользователь вернулся после OAuth в новой вкладке)
  // 2. В URL есть ?oauth=success (редирект пришёл в эту же вкладку)
  const checkOAuthSuccess = () => {
    const hash = window.location.hash; // "#/integrations?oauth=success"
    const queryString = hash.includes("?") ? hash.split("?")[1] : "";
    const params = new URLSearchParams(queryString);
    if (params.get("oauth") === "success") {
      qc.invalidateQueries({ queryKey: ["/integrations"] });
      toast({ title: "Интеграция подключена", description: "Токен успешно получен" });
      window.history.replaceState({}, "", window.location.pathname + "#/integrations");
    }
  };

  useEffect(() => {
    // Проверяем сразу при маунте — вдруг уже есть ?oauth=success
    checkOAuthSuccess();

    // Слушаем изменение hash — срабатывает когда бэк редиректит
    // обратно на /#/integrations?oauth=success пока страница уже открыта
    window.addEventListener("hashchange", checkOAuthSuccess);

    return () => window.removeEventListener("hashchange", checkOAuthSuccess);
  }, []);

  const createMutation = useMutation({
    mutationFn: (d: { name: string; platform: string }) => integrationApi.create(d),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["/integrations"] });
      setShowCreate(false);
      setForm({ name: "", platform: "" });
      toast({ title: "Интеграция создана" });
    },
    onError: (e: any) => toast({ title: "Ошибка", description: e.message, variant: "destructive" }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => integrationApi.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["/integrations"] });
      setDeleteId(null);
      toast({ title: "Интеграция удалена" });
    },
    onError: (e: any) => toast({ title: "Ошибка", description: e.message, variant: "destructive" }),
  });

  const handleOAuth = async (id: string) => {
    try {
      const res = await integrationApi.oauthInit(id);
      if (res?.auth_url) {
        // Открываем в той же вкладке — тогда после callback фронт получит ?oauth=success
        window.location.href = res.auth_url;
      }
    } catch (e: any) {
      toast({ title: "Ошибка OAuth", description: e.message, variant: "destructive" });
    }
  };

  const integrations = data?.items ?? [];

  return (
    <AppLayout
      title="Интеграции"
      description="Управление подключениями к рекламным платформам"
      actions={
        <Button size="sm" onClick={() => setShowCreate(true)} data-testid="button-add-integration">
          <Plus className="w-4 h-4 mr-2" />
          Добавить
        </Button>
      }
    >
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map(i => (
            <Card key={i} className="border-border">
              <CardContent className="p-5 space-y-3">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-8 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : integrations.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="w-14 h-14 rounded-2xl bg-muted flex items-center justify-center mb-4">
            <Link2 className="w-7 h-7 text-muted-foreground" />
          </div>
          <h3 className="text-base font-medium text-foreground mb-2">Нет интеграций</h3>
          <p className="text-sm text-muted-foreground max-w-xs mb-5">
            Подключите рекламные платформы, чтобы начать мониторинг эффективности
          </p>
          <Button size="sm" onClick={() => setShowCreate(true)}>
            <Plus className="w-4 h-4 mr-2" /> Добавить интеграцию
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {integrations.map((int: any) => (
            <IntegrationCard
              key={int.id}
              integration={int}
              onDelete={setDeleteId}
              onOAuth={handleOAuth}
            />
          ))}
        </div>
      )}

      {/* Create dialog */}
      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Новая интеграция</DialogTitle>
            <DialogDescription>Подключите рекламную платформу для сбора данных</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <Label>Название</Label>
              <Input
                placeholder="Например: Google Ads — Основной аккаунт"
                value={form.name}
                onChange={e => setForm(p => ({ ...p, name: e.target.value }))}
                data-testid="input-integration-name"
              />
            </div>
            <div className="space-y-2">
              <Label>Платформа</Label>
              <Select value={form.platform} onValueChange={v => setForm(p => ({ ...p, platform: v }))}>
                <SelectTrigger data-testid="select-platform">
                  <SelectValue placeholder="Выберите платформу" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="google_ads">
                    <span className="flex items-center gap-2"><SiGoogleads className="w-4 h-4" /> Google Ads</span>
                  </SelectItem>
                  <SelectItem value="yandex_direct">
                    <span className="flex items-center gap-2"><SiYandexcloud className="w-4 h-4" /> Яндекс Директ</span>
                  </SelectItem>
                  <SelectItem value="meta_ads">
                    <span className="flex items-center gap-2"><SiFacebook className="w-4 h-4" /> Meta Ads</span>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreate(false)}>Отмена</Button>
            <Button
              onClick={() => createMutation.mutate(form)}
              disabled={!form.name || !form.platform || createMutation.isPending}
              data-testid="button-create-integration"
            >
              {createMutation.isPending && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
              Создать
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete confirm */}
      <AlertDialog open={!!deleteId} onOpenChange={open => !open && setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Удалить интеграцию?</AlertDialogTitle>
            <AlertDialogDescription>
              Все данные этой интеграции будут удалены. Это действие необратимо.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Отмена</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive hover:bg-destructive/90"
              onClick={() => deleteId && deleteMutation.mutate(deleteId)}
              data-testid="button-confirm-delete"
            >
              {deleteMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : "Удалить"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </AppLayout>
  );
}
