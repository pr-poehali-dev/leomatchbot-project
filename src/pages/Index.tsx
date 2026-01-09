import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import Icon from '@/components/ui/icon';
import {
  SidebarProvider,
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarTrigger,
} from '@/components/ui/sidebar';

const API_URL = 'https://functions.poehali.dev/10e0f84a-62e5-4319-b7d3-919727530b57';

const Index = () => {
  const [activeSection, setActiveSection] = useState('dashboard');
  const [stats, setStats] = useState({
    totalUsers: 0,
    activeMatches: 0,
    todayMessages: 0,
    pendingModeration: 0,
    usersGrowth: 0,
    matchesGrowth: 0,
    dailyActivity: [] as any[],
  });
  const [users, setUsers] = useState<any[]>([]);
  const [matches, setMatches] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [activeSection]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (activeSection === 'dashboard') {
        const statsRes = await fetch(`${API_URL}?action=stats`);
        const statsData = await statsRes.json();
        setStats(statsData);

        const usersRes = await fetch(`${API_URL}?action=users&status=all`);
        const usersData = await usersRes.json();
        setUsers((usersData.users || []).slice(0, 4));
      } else if (activeSection === 'users' || activeSection === 'moderation') {
        const usersRes = await fetch(`${API_URL}?action=users&status=all`);
        const usersData = await usersRes.json();
        setUsers(usersData.users || []);
      } else if (activeSection === 'messages') {
        const matchesRes = await fetch(`${API_URL}?action=matches`);
        const matchesData = await matchesRes.json();
        setMatches(matchesData.matches || []);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleModerate = async (userId: number, action: 'approve' | 'reject') => {
    try {
      await fetch(`${API_URL}?action=moderate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, action }),
      });
      loadData();
    } catch (error) {
      console.error('Error moderating user:', error);
    }
  };

  const recentUsers = (users || []).slice(0, 4);

  const menuItems = [
    { id: 'dashboard', icon: 'LayoutDashboard', label: 'Дашборд' },
    { id: 'moderation', icon: 'ShieldCheck', label: 'Модерация' },
    { id: 'messages', icon: 'MessageSquare', label: 'Сообщения' },
    { id: 'users', icon: 'Users', label: 'Пользователи' },
    { id: 'settings', icon: 'Settings', label: 'Настройки' },
  ];

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full">
        <Sidebar>
          <SidebarHeader className="border-b border-sidebar-border p-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
                <Icon name="Heart" size={20} className="text-white" />
              </div>
              <div>
                <h2 className="font-bold text-sidebar-foreground">LeoMatch</h2>
                <p className="text-xs text-sidebar-foreground/60">Admin Panel</p>
              </div>
            </div>
          </SidebarHeader>
          <SidebarContent className="p-2">
            <SidebarMenu>
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.id}>
                  <SidebarMenuButton
                    onClick={() => setActiveSection(item.id)}
                    isActive={activeSection === item.id}
                    className="w-full"
                  >
                    <Icon name={item.icon} size={18} />
                    <span>{item.label}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarContent>
        </Sidebar>

        <main className="flex-1 overflow-auto bg-[#F6F6F7]">
          <header className="sticky top-0 z-10 border-b border-border bg-white/80 backdrop-blur-sm">
            <div className="flex h-16 items-center gap-4 px-6">
              <SidebarTrigger />
              <h1 className="text-xl font-semibold">
                {menuItems.find((item) => item.id === activeSection)?.label}
              </h1>
              <div className="ml-auto flex items-center gap-3">
                <Button variant="ghost" size="icon">
                  <Icon name="Bell" size={20} />
                </Button>
                <Avatar>
                  <AvatarFallback>АД</AvatarFallback>
                </Avatar>
              </div>
            </div>
          </header>

          <div className="p-6">
            {activeSection === 'dashboard' && (
              <div className="space-y-6 animate-fade-in">
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                  <Card className="p-6 transition-all hover:shadow-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Пользователей</p>
                        <h3 className="text-2xl font-bold mt-1">{stats.totalUsers}</h3>
                      </div>
                      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                        <Icon name="Users" size={24} className="text-primary" />
                      </div>
                    </div>
                    <div className="mt-4 flex items-center gap-2 text-xs">
                      <Badge variant="secondary" className="bg-green-100 text-green-700">
                        +{stats.usersGrowth}%
                      </Badge>
                      <span className="text-muted-foreground">за неделю</span>
                    </div>
                  </Card>

                  <Card className="p-6 transition-all hover:shadow-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Активные матчи</p>
                        <h3 className="text-2xl font-bold mt-1">{stats.activeMatches}</h3>
                      </div>
                      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                        <Icon name="Heart" size={24} className="text-primary" />
                      </div>
                    </div>
                    <div className="mt-4 flex items-center gap-2 text-xs">
                      <Badge variant="secondary" className="bg-green-100 text-green-700">
                        +{stats.matchesGrowth}%
                      </Badge>
                      <span className="text-muted-foreground">за неделю</span>
                    </div>
                  </Card>

                  <Card className="p-6 transition-all hover:shadow-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Сообщений сегодня</p>
                        <h3 className="text-2xl font-bold mt-1">{stats.todayMessages}</h3>
                      </div>
                      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                        <Icon name="MessageSquare" size={24} className="text-primary" />
                      </div>
                    </div>
                    <div className="mt-4 flex items-center gap-2 text-xs">
                      <Badge variant="secondary" className="bg-blue-100 text-blue-700">
                        Стабильно
                      </Badge>
                      <span className="text-muted-foreground">к вчера</span>
                    </div>
                  </Card>

                  <Card className="p-6 transition-all hover:shadow-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">На модерации</p>
                        <h3 className="text-2xl font-bold mt-1">{stats.pendingModeration}</h3>
                      </div>
                      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-orange-100">
                        <Icon name="AlertCircle" size={24} className="text-orange-600" />
                      </div>
                    </div>
                    <div className="mt-4">
                      <Button size="sm" variant="outline" className="w-full">
                        Проверить
                      </Button>
                    </div>
                  </Card>
                </div>

                <div className="grid gap-6 md:grid-cols-2">
                  <Card className="p-6">
                    <h3 className="font-semibold mb-4 flex items-center gap-2">
                      <Icon name="TrendingUp" size={20} />
                      Активность по дням
                    </h3>
                    <div className="space-y-4">
                      {[
                        { day: 'Пн', matches: 45, messages: 234 },
                        { day: 'Вт', matches: 52, messages: 267 },
                        { day: 'Ср', matches: 38, messages: 198 },
                        { day: 'Чт', matches: 61, messages: 312 },
                        { day: 'Пт', matches: 48, messages: 245 },
                      ].map((item) => (
                        <div key={item.day} className="flex items-center gap-4">
                          <span className="w-8 text-sm font-medium text-muted-foreground">
                            {item.day}
                          </span>
                          <div className="flex-1">
                            <div className="flex gap-2">
                              <div
                                className="h-8 rounded bg-primary transition-all hover:opacity-80"
                                style={{ width: `${(item.matches / 70) * 100}%` }}
                              />
                              <div
                                className="h-8 rounded bg-primary/30 transition-all hover:opacity-80"
                                style={{ width: `${(item.messages / 350) * 100}%` }}
                              />
                            </div>
                          </div>
                          <div className="flex gap-4 text-xs">
                            <span className="text-muted-foreground">{item.matches} матчей</span>
                            <span className="text-muted-foreground">{item.messages} сообщений</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>

                  <Card className="p-6">
                    <h3 className="font-semibold mb-4 flex items-center gap-2">
                      <Icon name="Clock" size={20} />
                      Недавние пользователи
                    </h3>
                    <div className="space-y-3">
                      {recentUsers.map((user) => (
                        <div
                          key={user.id}
                          className="flex items-center justify-between p-3 rounded-lg hover:bg-muted/50 transition-colors"
                        >
                          <div className="flex items-center gap-3">
                            <Avatar>
                              <AvatarFallback>{(user.first_name || user.name || 'U').slice(0, 2)}</AvatarFallback>
                            </Avatar>
                            <div>
                              <div className="flex items-center gap-2">
                                <span className="font-medium text-sm">{user.first_name || user.name || 'User'}</span>
                                {user.verified && (
                                  <Icon name="BadgeCheck" size={14} className="text-primary" />
                                )}
                              </div>
                              <span className="text-xs text-muted-foreground">
                                {user.age} лет
                              </span>
                            </div>
                          </div>
                          <Badge
                            variant={
                              user.status === 'active'
                                ? 'default'
                                : user.status === 'moderation'
                                  ? 'secondary'
                                  : 'destructive'
                            }
                          >
                            {user.status === 'active'
                              ? 'Активен'
                              : user.status === 'moderation'
                                ? 'Проверка'
                                : 'Бан'}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </Card>
                </div>
              </div>
            )}

            {activeSection === 'moderation' && (
              <div className="space-y-6 animate-fade-in">
                <Tabs defaultValue="pending" className="w-full">
                  <TabsList>
                    <TabsTrigger value="pending">На проверке ({stats.pendingModeration})</TabsTrigger>
                    <TabsTrigger value="approved">Одобренные</TabsTrigger>
                    <TabsTrigger value="rejected">Отклоненные</TabsTrigger>
                  </TabsList>

                  <TabsContent value="pending" className="mt-6">
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                      {users.filter(u => !u.verified).slice(0, 6).map((user) => (
                        <Card key={user.id} className="overflow-hidden">
                          <div className="aspect-square bg-gradient-to-br from-primary/20 to-primary/5" />
                          <div className="p-4 space-y-4">
                            <div>
                              <h4 className="font-semibold">{user.first_name}</h4>
                              <p className="text-sm text-muted-foreground">
                                {user.age ? `${user.age} лет` : 'Возраст не указан'}, {user.city || 'Город не указан'}
                              </p>
                              {user.bio && <p className="text-xs text-muted-foreground mt-2">{user.bio}</p>}
                            </div>
                            <Separator />
                            <div className="flex gap-2">
                              <Button size="sm" className="flex-1" onClick={() => handleModerate(user.id, 'approve')}>
                                <Icon name="Check" size={16} />
                                Одобрить
                              </Button>
                              <Button size="sm" variant="destructive" className="flex-1" onClick={() => handleModerate(user.id, 'reject')}>
                                <Icon name="X" size={16} />
                                Отклонить
                              </Button>
                            </div>
                          </div>
                        </Card>
                      ))}
                    </div>
                  </TabsContent>
                </Tabs>
              </div>
            )}

            {activeSection === 'messages' && (
              <div className="space-y-6 animate-fade-in">
                <Card className="p-6">
                  <h3 className="font-semibold mb-4">Активные диалоги</h3>
                  {loading ? (
                    <p className="text-center text-muted-foreground py-8">Загрузка...</p>
                  ) : matches.length === 0 ? (
                    <p className="text-center text-muted-foreground py-8">Нет активных диалогов</p>
                  ) : (
                    <div className="space-y-3">
                      {matches.map((match) => (
                        <div
                          key={match.id}
                          className="flex items-center gap-4 p-4 rounded-lg border hover:bg-muted/50 transition-colors cursor-pointer"
                        >
                          <div className="flex -space-x-2">
                            <Avatar className="border-2 border-white">
                              <AvatarFallback>{match.user1_name?.slice(0, 2)}</AvatarFallback>
                            </Avatar>
                            <Avatar className="border-2 border-white">
                              <AvatarFallback>{match.user2_name?.slice(0, 2)}</AvatarFallback>
                            </Avatar>
                          </div>
                          <div className="flex-1">
                            <p className="font-medium text-sm">
                              {match.user1_name} и {match.user2_name}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              Создан {new Date(match.created_at).toLocaleDateString('ru-RU')}
                            </p>
                          </div>
                          <Badge>{match.message_count} сообщений</Badge>
                          <Icon name="ChevronRight" size={18} className="text-muted-foreground" />
                        </div>
                      ))}
                    </div>
                  )}
                </Card>
              </div>
            )}

            {activeSection === 'users' && (
              <div className="space-y-6 animate-fade-in">
                <Card className="p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="font-semibold">Все пользователи</h3>
                    <Button size="sm">
                      <Icon name="Download" size={16} />
                      Экспорт
                    </Button>
                  </div>
                  <div className="space-y-2">
                    {recentUsers.map((user) => (
                      <div
                        key={user.id}
                        className="flex items-center justify-between p-4 rounded-lg border hover:bg-muted/50 transition-colors"
                      >
                        <div className="flex items-center gap-4">
                          <Avatar>
                            <AvatarFallback>{(user.first_name || user.name || 'U').slice(0, 2)}</AvatarFallback>
                          </Avatar>
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-medium">{user.first_name || user.name || 'User'}</span>
                              {user.verified && (
                                <Icon name="BadgeCheck" size={16} className="text-primary" />
                              )}
                            </div>
                            <span className="text-sm text-muted-foreground">{user.age} лет</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <Badge
                            variant={
                              user.status === 'active'
                                ? 'default'
                                : user.status === 'moderation'
                                  ? 'secondary'
                                  : 'destructive'
                            }
                          >
                            {user.status === 'active'
                              ? 'Активен'
                              : user.status === 'moderation'
                                ? 'Проверка'
                                : 'Бан'}
                          </Badge>
                          <Button size="sm" variant="ghost">
                            <Icon name="MoreVertical" size={18} />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              </div>
            )}

            {activeSection === 'settings' && (
              <div className="space-y-6 animate-fade-in">
                <Card className="p-6">
                  <h3 className="font-semibold mb-6">Настройки бота</h3>
                  <div className="space-y-6">
                    <div>
                      <label className="text-sm font-medium mb-2 block">
                        Минимальный возраст
                      </label>
                      <input
                        type="number"
                        defaultValue={18}
                        className="w-full px-3 py-2 border rounded-lg"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium mb-2 block">
                        Максимальная дистанция (км)
                      </label>
                      <input
                        type="number"
                        defaultValue={50}
                        className="w-full px-3 py-2 border rounded-lg"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium mb-2 block">
                        Алгоритм подбора
                      </label>
                      <select className="w-full px-3 py-2 border rounded-lg">
                        <option>Случайный</option>
                        <option>По интересам</option>
                        <option>По геолокации</option>
                      </select>
                    </div>
                    <Separator />
                    <Button>Сохранить изменения</Button>
                  </div>
                </Card>
              </div>
            )}
          </div>
        </main>
      </div>
    </SidebarProvider>
  );
};

export default Index;