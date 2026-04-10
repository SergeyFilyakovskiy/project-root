import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { AppLayout } from "@/components/layout/app-layout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/lib/auth-context";
import { userApi } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import {
  User,
  Mail,
  Lock,
  Loader2,
  Shield,
  Moon,
  Sun,
  AlertTriangle,
} from "lucide-react";
import { Switch } from "@/components/ui/switch";

export default function Profile() {
  const { user, refetch, logout } = useAuth();
  const { toast } = useToast();
  const qc = useQueryClient();

  const [profileForm, setProfileForm] = useState({
    username: user?.username ?? "",
    email: user?.email ?? "",
  });

  const [passwordForm, setPasswordForm] = useState({
    old_password: "",
    new_password: "",
    new_password2: "",
  });

  const [darkMode, setDarkMode] = useState(
    document.documentElement.classList.contains("dark")
  );

  const toggleTheme = (val: boolean) => {
    setDarkMode(val);
    if (val) {
      document.documentElement.classList.add("dark");
      document.documentElement.classList.remove("light");
    } else {
      document.documentElement.classList.remove("dark");
      document.documentElement.classList.add("light");
    }
  };

  const updateMutation = useMutation({
    mutationFn: (d: { username?: string; email?: string }) => userApi.updateMe(d),
    onSuccess: () => {
      refetch();
      toast({ title: "Профиль обновлён" });
    },
    onError: (e: any) => toast({ title: "Ошибка", description: e.message, variant: "destructive" }),
  });

  const passwordMutation = useMutation({
    mutationFn: ({ old_password, new_password }: { old_password: string; new_password: string }) =>
      userApi.changePassword(old_password, new_password),
    onSuccess: () => {
      setPasswordForm({ old_password: "", new_password: "", new_password2: "" });
      toast({ title: "Пароль изменён" });
    },
    onError: (e: any) => toast({ title: "Ошибка", description: e.message, variant: "destructive" }),
  });

  const deleteMutation = useMutation({
    mutationFn: () => userApi.deleteMe(),
    onSuccess: () => {
      toast({ title: "Аккаунт удалён" });
      logout();
    },
    onError: (e: any) => toast({ title: "Ошибка", description: e.message, variant: "destructive" }),
  });

  const handleUpdateProfile = (e: React.FormEvent) => {
    e.preventDefault();
    updateMutation.mutate(profileForm);
  };

  const handleChangePassword = (e: React.FormEvent) => {
    e.preventDefault();
    if (passwordForm.new_password !== passwordForm.new_password2) {
      toast({ title: "Пароли не совпадают", variant: "destructive" });
      return;
    }
    passwordMutation.mutate({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password,
    });
  };

  return (
    <AppLayout
      title="Настройки"
      description="Управление аккаунтом и параметрами системы"
    >
      <div className="max-w-2xl space-y-5">
        {/* Profile info */}
        <Card className="border-border">
          <CardHeader className="pb-4">
            <CardTitle className="text-base flex items-center gap-2">
              <User className="w-4 h-4 text-primary" />
              Профиль
            </CardTitle>
            <CardDescription className="text-xs">Обновите данные вашего аккаунта</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4 mb-5">
              <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                <span className="text-lg font-bold text-primary">
                  {user?.email?.[0]?.toUpperCase() ?? "U"}
                </span>
              </div>
              <div>
                <p className="text-sm font-medium text-foreground">{user?.username ?? user?.email}</p>
                <p className="text-xs text-muted-foreground">{user?.email}</p>
                <Badge variant="secondary" className="text-xs mt-1">
                  <Shield className="w-2.5 h-2.5 mr-1" />
                  {user?.role ?? "user"}
                </Badge>
              </div>
            </div>

            <form onSubmit={handleUpdateProfile} className="space-y-4">
              <div className="space-y-2">
                <Label className="text-xs flex items-center gap-1.5">
                  <User className="w-3 h-3" /> Имя пользователя
                </Label>
                <Input
                  value={profileForm.username}
                  onChange={e => setProfileForm(p => ({ ...p, username: e.target.value }))}
                  className="h-9"
                  data-testid="input-profile-username"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-xs flex items-center gap-1.5">
                  <Mail className="w-3 h-3" /> Email
                </Label>
                <Input
                  type="email"
                  value={profileForm.email}
                  onChange={e => setProfileForm(p => ({ ...p, email: e.target.value }))}
                  className="h-9"
                  data-testid="input-profile-email"
                />
              </div>
              <Button
                type="submit"
                size="sm"
                disabled={updateMutation.isPending}
                data-testid="button-save-profile"
              >
                {updateMutation.isPending && <Loader2 className="w-3.5 h-3.5 animate-spin mr-2" />}
                Сохранить
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Password */}
        <Card className="border-border">
          <CardHeader className="pb-4">
            <CardTitle className="text-base flex items-center gap-2">
              <Lock className="w-4 h-4 text-primary" />
              Смена пароля
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleChangePassword} className="space-y-4">
              <div className="space-y-2">
                <Label className="text-xs">Текущий пароль</Label>
                <Input
                  type="password"
                  value={passwordForm.old_password}
                  onChange={e => setPasswordForm(p => ({ ...p, old_password: e.target.value }))}
                  className="h-9"
                  data-testid="input-old-password"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label className="text-xs">Новый пароль</Label>
                <Input
                  type="password"
                  value={passwordForm.new_password}
                  onChange={e => setPasswordForm(p => ({ ...p, new_password: e.target.value }))}
                  className="h-9"
                  data-testid="input-new-password"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label className="text-xs">Повторите новый пароль</Label>
                <Input
                  type="password"
                  value={passwordForm.new_password2}
                  onChange={e => setPasswordForm(p => ({ ...p, new_password2: e.target.value }))}
                  className="h-9"
                  data-testid="input-new-password2"
                  required
                />
              </div>
              <Button
                type="submit"
                size="sm"
                disabled={passwordMutation.isPending}
                data-testid="button-change-password"
              >
                {passwordMutation.isPending && <Loader2 className="w-3.5 h-3.5 animate-spin mr-2" />}
                Изменить пароль
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Appearance */}
        <Card className="border-border">
          <CardHeader className="pb-4">
            <CardTitle className="text-base">Оформление</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {darkMode ? <Moon className="w-4 h-4 text-primary" /> : <Sun className="w-4 h-4 text-chart-3" />}
                <div>
                  <p className="text-sm font-medium">Тёмная тема</p>
                  <p className="text-xs text-muted-foreground">
                    {darkMode ? "Включена" : "Выключена"}
                  </p>
                </div>
              </div>
              <Switch
                checked={darkMode}
                onCheckedChange={toggleTheme}
                data-testid="switch-dark-mode"
              />
            </div>
          </CardContent>
        </Card>

        {/* Danger zone */}
        <Card className="border-destructive/50">
          <CardHeader className="pb-4">
            <CardTitle className="text-base flex items-center gap-2 text-destructive">
              <AlertTriangle className="w-4 h-4" />
              Опасная зона
            </CardTitle>
            <CardDescription className="text-xs">
              Необратимые действия с аккаунтом
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between p-3 rounded-lg border border-destructive/30 bg-destructive/5">
              <div>
                <p className="text-sm font-medium text-foreground">Удалить аккаунт</p>
                <p className="text-xs text-muted-foreground">
                  Все данные будут удалены без возможности восстановления
                </p>
              </div>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => {
                  if (confirm("Вы уверены? Это действие необратимо.")) {
                    deleteMutation.mutate();
                  }
                }}
                disabled={deleteMutation.isPending}
                data-testid="button-delete-account"
              >
                {deleteMutation.isPending ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : "Удалить"}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
