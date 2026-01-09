import { useState } from 'react';
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

const Index = () => {
  const [activeSection, setActiveSection] = useState('dashboard');

  const stats = {
    totalUsers: 2847,
    activeMatches: 156,
    todayMessages: 1234,
    pendingModeration: 23,
  };

  const recentUsers = [
    { id: 1, name: 'Анна К.', age: 24, status: 'active', avatar: '', verified: true },
    { id: 2, name: 'Дмитрий М.', age: 28, status: 'moderation', avatar: '', verified: false },
    { id: 3, name: 'Елена С.', age: 26, status: 'active', avatar: '', verified: true },
    { id: 4, name: 'Алексей П.', age: 30, status: 'banned', avatar: '', verified: false },
  ];

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
                        +12.5%
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
                        +8.3%
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
                              <AvatarFallback>{user.name.slice(0, 2)}</AvatarFallback>
                            </Avatar>
                            <div>
                              <div className="flex items-center gap-2">
                                <span className="font-medium text-sm">{user.name}</span>
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
                      {[1, 2, 3].map((i) => (
                        <Card key={i} className="overflow-hidden">
                          <div className="aspect-square bg-gradient-to-br from-primary/20 to-primary/5" />
                          <div className="p-4 space-y-4">
                            <div>
                              <h4 className="font-semibold">Пользователь #{i}</h4>
                              <p className="text-sm text-muted-foreground">25 лет, Москва</p>
                            </div>
                            <Separator />
                            <div className="flex gap-2">
                              <Button size="sm" className="flex-1">
                                <Icon name="Check" size={16} />
                                Одобрить
                              </Button>
                              <Button size="sm" variant="destructive" className="flex-1">
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
                  <div className="space-y-3">
                    {[1, 2, 3, 4].map((i) => (
                      <div
                        key={i}
                        className="flex items-center gap-4 p-4 rounded-lg border hover:bg-muted/50 transition-colors cursor-pointer"
                      >
                        <div className="flex -space-x-2">
                          <Avatar className="border-2 border-white">
                            <AvatarFallback>А</AvatarFallback>
                          </Avatar>
                          <Avatar className="border-2 border-white">
                            <AvatarFallback>Д</AvatarFallback>
                          </Avatar>
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-sm">Анна К. и Дмитрий М.</p>
                          <p className="text-xs text-muted-foreground">
                            Последнее сообщение 5 минут назад
                          </p>
                        </div>
                        <Badge>42 сообщения</Badge>
                        <Icon name="ChevronRight" size={18} className="text-muted-foreground" />
                      </div>
                    ))}
                  </div>
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
                            <AvatarFallback>{user.name.slice(0, 2)}</AvatarFallback>
                          </Avatar>
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-medium">{user.name}</span>
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
