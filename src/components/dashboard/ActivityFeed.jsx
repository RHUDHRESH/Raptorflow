import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/Button';
import { 
  Bell, 
  UserPlus, 
  ShoppingCart, 
  CreditCard, 
  AlertCircle, 
  CheckCircle, 
  TrendingUp,
  Package,
  MessageSquare,
  Star,
  Filter,
  RefreshCw
} from 'lucide-react';
import { Separator } from '@/components/ui/separator';

const generateMockActivity = () => {
  const activities = [
    {
      id: 1,
      type: 'user',
      icon: UserPlus,
      iconColor: 'text-orange-600',
      bgColor: 'bg-orange-50',
      title: 'New user registration',
      description: 'Sarah Johnson joined your platform',
      user: { name: 'Sarah Johnson', avatar: '/api/placeholder/32/32', initials: 'SJ' },
      timestamp: '2 minutes ago',
      priority: 'low',
      action: 'View Profile'
    },
    {
      id: 2,
      type: 'order',
      icon: ShoppingCart,
      iconColor: 'text-green-600',
      bgColor: 'bg-green-50',
      title: 'New order received',
      description: 'Order #12345 for $299.00',
      user: { name: 'Mike Chen', avatar: '/api/placeholder/32/32', initials: 'MC' },
      timestamp: '5 minutes ago',
      priority: 'medium',
      action: 'View Order'
    },
    {
      id: 3,
      type: 'payment',
      icon: CreditCard,
      iconColor: 'text-purple-600',
      bgColor: 'bg-purple-50',
      title: 'Payment successful',
      description: 'Payment of $1,250.00 processed',
      user: { name: 'Emma Wilson', avatar: '/api/placeholder/32/32', initials: 'EW' },
      timestamp: '10 minutes ago',
      priority: 'low',
      action: 'View Invoice'
    },
    {
      id: 4,
      type: 'alert',
      icon: AlertCircle,
      iconColor: 'text-red-600',
      bgColor: 'bg-red-50',
      title: 'Inventory alert',
      description: 'Product "Wireless Headphones" is running low',
      user: null,
      timestamp: '15 minutes ago',
      priority: 'high',
      action: 'Restock'
    },
    {
      id: 5,
      type: 'review',
      icon: Star,
      iconColor: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
      title: 'New product review',
      description: '5-star review on "Premium Laptop"',
      user: { name: 'Alex Turner', avatar: '/api/placeholder/32/32', initials: 'AT' },
      timestamp: '20 minutes ago',
      priority: 'medium',
      action: 'Read Review'
    },
    {
      id: 6,
      type: 'message',
      icon: MessageSquare,
      iconColor: 'text-orange-600',
      bgColor: 'bg-orange-50',
      title: 'New support ticket',
      description: 'Customer needs help with order #12344',
      user: { name: 'Lisa Brown', avatar: '/api/placeholder/32/32', initials: 'LB' },
      timestamp: '25 minutes ago',
      priority: 'high',
      action: 'Respond'
    },
    {
      id: 7,
      type: 'success',
      icon: CheckCircle,
      iconColor: 'text-green-600',
      bgColor: 'bg-green-50',
      title: 'Goal achieved',
      description: 'Monthly sales target reached!',
      user: null,
      timestamp: '30 minutes ago',
      priority: 'low',
      action: 'View Analytics'
    },
    {
      id: 8,
      type: 'product',
      icon: Package,
      iconColor: 'text-orange-600',
      bgColor: 'bg-orange-50',
      title: 'Product added',
      description: 'New product "Smart Watch" added to catalog',
      user: null,
      timestamp: '35 minutes ago',
      priority: 'medium',
      action: 'View Product'
    }
  ];

  return activities.sort((a, b) => {
    const timeOrder = ['2 minutes ago', '5 minutes ago', '10 minutes ago', '15 minutes ago', '20 minutes ago', '25 minutes ago', '30 minutes ago', '35 minutes ago'];
    return timeOrder.indexOf(a.timestamp) - timeOrder.indexOf(b.timestamp);
  });
};

const getPriorityBadge = (priority) => {
  switch (priority) {
    case 'high':
      return <Badge variant="destructive" className="text-xs">High</Badge>;
    case 'medium':
      return <Badge variant="secondary" className="text-xs">Medium</Badge>;
    default:
      return <Badge variant="outline" className="text-xs">Low</Badge>;
  }
};

export function ActivityFeed({ filter = 'all', onRefresh }) {
  const [activities, setActivities] = useState([]);
  const [filteredActivities, setFilteredActivities] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setActivities(generateMockActivity());
  }, []);

  useEffect(() => {
    if (filter === 'all') {
      setFilteredActivities(activities);
    } else {
      setFilteredActivities(activities.filter(activity => activity.priority === filter));
    }
  }, [activities, filter]);

  const handleRefresh = () => {
    setIsLoading(true);
    setTimeout(() => {
      setActivities(generateMockActivity());
      setIsLoading(false);
      onRefresh?.();
    }, 1000);
  };

  return (
    <Card className="bg-zinc-900/50 border border-white/5">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bell className="w-5 h-5 text-orange-400" />
            <CardTitle className="text-white">Activity Feed</CardTitle>
            <Badge variant="secondary" className="ml-2 bg-white/10 text-white/60">
              {filteredActivities.length}
            </Badge>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRefresh}
            disabled={isLoading}
            className="h-8 w-8 p-0 text-white/60 hover:text-white hover:bg-white/5"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
        <CardDescription className="text-white/40">Real-time updates from your platform</CardDescription>
      </CardHeader>
      
      <CardContent className="p-0">
        <div className="max-h-96 overflow-y-auto">
          <AnimatePresence>
            {filteredActivities.map((activity, index) => (
              <motion.div
                key={activity.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
              >
                <div className="p-4 hover:bg-white/5 transition-colors">
                  <div className="flex items-start gap-3">
                    <div className={`p-2 rounded-lg ${activity.bgColor}`}>
                      <activity.icon className={`w-4 h-4 ${activity.iconColor}`} />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-medium text-sm text-white">
                              {activity.title}
                            </h4>
                            {getPriorityBadge(activity.priority)}
                          </div>
                          <p className="text-sm text-white/60 mb-2">
                            {activity.description}
                          </p>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              {activity.user && (
                                <div className="flex items-center gap-2">
                                  <Avatar className="w-6 h-6">
                                    <AvatarImage src={activity.user.avatar} alt={activity.user.name} />
                                    <AvatarFallback className="text-xs">
                                      {activity.user.initials}
                                    </AvatarFallback>
                                  </Avatar>
                                  <span className="text-xs text-white/40">
                                    {activity.user.name}
                                  </span>
                                </div>
                              )}
                              <span className="text-xs text-white/20">
                                {activity.timestamp}
                              </span>
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-6 text-xs text-orange-400 hover:text-orange-300 p-2"
                            >
                              {activity.action}
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                {index < filteredActivities.length - 1 && (
                  <Separator className="mx-4 bg-white/10" />
                )}
              </motion.div>
            ))}
          </AnimatePresence>
          
          {filteredActivities.length === 0 && (
            <div className="p-8 text-center">
              <Bell className="w-8 h-8 text-white/20 mx-auto mb-2" />
              <p className="text-sm text-white/40">No activities found</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export function ActivityFilters({ activeFilter, onFilterChange }) {
  const filters = [
    { value: 'all', label: 'All Activities', count: 8 },
    { value: 'high', label: 'High Priority', count: 2 },
    { value: 'medium', label: 'Medium Priority', count: 4 },
    { value: 'low', label: 'Low Priority', count: 2 }
  ];

  return (
    <div className="flex items-center gap-2 p-2 bg-zinc-900/50 rounded-lg border border-white/5">
      <Filter className="w-4 h-4 text-white/40" />
      {filters.map((filter) => (
        <Button
          key={filter.value}
          variant={activeFilter === filter.value ? 'default' : 'ghost'}
          size="sm"
          onClick={() => onFilterChange(filter.value)}
          className={`h-8 text-xs ${
            activeFilter === filter.value 
              ? 'bg-orange-600 text-white' 
              : 'text-white/60 hover:text-white hover:bg-white/5'
          }`}
        >
          {filter.label}
          <Badge variant="secondary" className="ml-2 text-xs bg-white/10 text-white/60">
            {filter.count}
          </Badge>
        </Button>
      ))}
    </div>
  );
}
