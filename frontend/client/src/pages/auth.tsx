import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { authApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { Loader2, BarChart3, TrendingUp, Zap } from "lucide-react";
import { SiGoogleads, SiYandexcloud, SiFacebook } from "react-icons/si";

export default function AuthPage() {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const { toast } = useToast();

  // Login form
  const [loginData, setLoginData] = useState({ username: "", password: "" });

  // Register form
  const [regData, setRegData] = useState({
    username: "",
    email: "",
    password: "",
    password2: "",
    first_name: "",
    last_name: "",
  });

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(loginData.username, loginData.password);
    } catch (err: any) {
      toast({ title: "Ошибка входа", description: err.message, variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (regData.password !== regData.password2) {
      toast({ title: "Пароли не совпадают", variant: "destructive" });
      return;
    }
    setLoading(true);
    try {
      await authApi.register({
        username: regData.username,
        email: regData.email,
        password: regData.password,
        first_name: regData.first_name || undefined,
        last_name: regData.last_name || undefined,
      });
      toast({ title: "Аккаунт создан", description: "Теперь войдите в систему" });
      setMode("login");
      setLoginData({ username: regData.username, password: "" });
    } catch (err: any) {
      toast({ title: "Ошибка регистрации", description: err.message, variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex">
      {/* Left panel — branding */}
      <div className="hidden lg:flex flex-col justify-between w-1/2 bg-[hsl(222_20%_8%)] border-r border-border p-12">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-primary flex items-center justify-center">
            <BarChart3 className="w-5 h-5 text-primary-foreground" />
          </div>
          <span className="text-lg font-semibold text-foreground">AdMetrics</span>
        </div>

        <div className="space-y-10">
          <div>
            <h1 className="text-3xl font-bold text-foreground leading-tight mb-4">
              Единая платформа<br />мониторинга рекламы
            </h1>
            <p className="text-muted-foreground text-base leading-relaxed max-w-sm">
              Собирайте данные из Google Ads, Яндекс Директ и Meta Ads в одном месте. Анализируйте эффективность, выявляйте аномалии и строите отчёты автоматически.
            </p>
          </div>

          <div className="space-y-4">
            {[
              { icon: TrendingUp, text: "KPI и воронки по всем платформам", color: "text-chart-1" },
              { icon: Zap, text: "Автоматическое обнаружение аномалий", color: "text-chart-2" },
              { icon: BarChart3, text: "Экспорт отчётов в PDF, CSV, XLSX", color: "text-chart-3" },
            ].map(({ icon: Icon, text, color }) => (
              <div key={text} className="flex items-center gap-3">
                <div className={`w-8 h-8 rounded-md bg-muted flex items-center justify-center ${color}`}>
                  <Icon className="w-4 h-4" />
                </div>
                <span className="text-sm text-muted-foreground">{text}</span>
              </div>
            ))}
          </div>

          <div className="space-y-2">
            <p className="text-xs text-muted-foreground">Поддерживаемые платформы</p>
            <div className="flex items-center gap-4">
              <SiGoogleads className="w-6 h-6 text-muted-foreground hover:text-foreground transition-colors" />
              <SiYandexcloud className="w-6 h-6 text-muted-foreground hover:text-foreground transition-colors" />
              <SiFacebook className="w-6 h-6 text-muted-foreground hover:text-foreground transition-colors" />
            </div>
          </div>
        </div>

        <p className="text-xs text-muted-foreground">© 2026 AdMetrics. Все права защищены.</p>
      </div>

      {/* Right panel — form */}
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-md space-y-6">
          {/* Mobile logo */}
          <div className="flex items-center gap-3 lg:hidden">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
              <BarChart3 className="w-4 h-4 text-primary-foreground" />
            </div>
            <span className="text-base font-semibold">AdMetrics</span>
          </div>

          <Card className="border-border bg-card">
            <CardHeader className="pb-4">
              <CardTitle className="text-xl">
                {mode === "login" ? "Вход в систему" : "Создать аккаунт"}
              </CardTitle>
              <CardDescription>
                {mode === "login"
                  ? "Введите учётные данные для доступа к платформе"
                  : "Заполните форму для регистрации"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {mode === "login" ? (
                <form onSubmit={handleLogin} className="space-y-4" data-testid="form-login">
                  <div className="space-y-2">
                    <Label htmlFor="username">Имя пользователя</Label>
                    <Input
                      id="username"
                      data-testid="input-username"
                      placeholder="username"
                      value={loginData.username}
                      onChange={e => setLoginData(p => ({ ...p, username: e.target.value }))}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="password">Пароль</Label>
                    <Input
                      id="password"
                      type="password"
                      data-testid="input-password"
                      placeholder="••••••••"
                      value={loginData.password}
                      onChange={e => setLoginData(p => ({ ...p, password: e.target.value }))}
                      required
                    />
                  </div>
                  <Button
                    type="submit"
                    className="w-full"
                    disabled={loading}
                    data-testid="button-login"
                  >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                    Войти
                  </Button>
                </form>
              ) : (
                <form onSubmit={handleRegister} className="space-y-4" data-testid="form-register">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-2">
                      <Label htmlFor="first_name">Имя</Label>
                      <Input
                        id="first_name"
                        placeholder="Иван"
                        value={regData.first_name}
                        onChange={e => setRegData(p => ({ ...p, first_name: e.target.value }))}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="last_name">Фамилия</Label>
                      <Input
                        id="last_name"
                        placeholder="Иванов"
                        value={regData.last_name}
                        onChange={e => setRegData(p => ({ ...p, last_name: e.target.value }))}
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="reg-username">Имя пользователя</Label>
                    <Input
                      id="reg-username"
                      placeholder="username"
                      value={regData.username}
                      onChange={e => setRegData(p => ({ ...p, username: e.target.value }))}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="reg-email">Email</Label>
                    <Input
                      id="reg-email"
                      type="email"
                      placeholder="email@company.com"
                      value={regData.email}
                      onChange={e => setRegData(p => ({ ...p, email: e.target.value }))}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="reg-password">Пароль</Label>
                    <Input
                      id="reg-password"
                      type="password"
                      placeholder="••••••••"
                      value={regData.password}
                      onChange={e => setRegData(p => ({ ...p, password: e.target.value }))}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="reg-password2">Повторите пароль</Label>
                    <Input
                      id="reg-password2"
                      type="password"
                      placeholder="••••••••"
                      value={regData.password2}
                      onChange={e => setRegData(p => ({ ...p, password2: e.target.value }))}
                      required
                    />
                  </div>
                  <Button type="submit" className="w-full" disabled={loading} data-testid="button-register">
                    {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                    Зарегистрироваться
                  </Button>
                </form>
              )}

              <div className="mt-4 text-center text-sm text-muted-foreground">
                {mode === "login" ? (
                  <>Нет аккаунта?{" "}
                    <button
                      className="text-primary hover:underline"
                      onClick={() => setMode("register")}
                      data-testid="link-switch-register"
                    >
                      Зарегистрироваться
                    </button>
                  </>
                ) : (
                  <>Уже есть аккаунт?{" "}
                    <button
                      className="text-primary hover:underline"
                      onClick={() => setMode("login")}
                      data-testid="link-switch-login"
                    >
                      Войти
                    </button>
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
