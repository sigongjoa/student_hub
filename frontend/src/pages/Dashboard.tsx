import { FC } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { Layout } from '../components/common/Layout';
import { Card } from '../components/common/Card';
import { Users, AlertCircle, CheckCircle, TrendingUp } from 'lucide-react';

const StatCard: FC<{ title: string; value: string | number; icon: any; change?: string; color: string }> = ({
    title, value, icon: Icon, change, color
}) => (
    <Card className="p-0 overflow-hidden">
        <div className="p-6 flex items-start justify-between">
            <div>
                <p className="text-sm font-medium text-slate-500 mb-1">{title}</p>
                <h3 className="text-2xl font-bold text-slate-900">{value}</h3>
                {change && (
                    <p className={`text-xs mt-2 font-medium ${change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                        {change} from last month
                    </p>
                )}
            </div>
            <div className={`p-3 rounded-lg ${color} bg-opacity-10 text-white`}>
                <Icon size={24} className={color.replace('bg-', 'text-')} />
            </div>
        </div>
    </Card>
);

export const Dashboard: FC = () => {
    const { data: students = [] } = useQuery({
        queryKey: ['students'],
        queryFn: api.getStudents,
    });

    return (
        <Layout>
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
                <p className="text-slate-500">Welcome back! Here's what's happening today.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <StatCard
                    title="Total Students"
                    value={students.length}
                    icon={Users}
                    change="+12%"
                    color="bg-primary"
                />
                <StatCard
                    title="At Risk"
                    value={Math.floor(students.length * 0.15)} // Mock logic
                    icon={AlertCircle}
                    change="-2%"
                    color="bg-red-500"
                />
                <StatCard
                    title="Active Interventions"
                    value={Math.floor(students.length * 0.3)} // Mock logic
                    icon={TrendingUp}
                    change="+5%"
                    color="bg-amber-500"
                />
                <StatCard
                    title="Avg. Mastery"
                    value="78%"
                    icon={CheckCircle}
                    change="+1.5%"
                    color="bg-green-500"
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card title="Recent Activity">
                    <p className="text-slate-500 py-8 text-center">Activity timeline graph placeholder</p>
                </Card>
                <Card title="Intervention Efficacy">
                    <p className="text-slate-500 py-8 text-center">Chart placeholder</p>
                </Card>
            </div>
        </Layout>
    );
};
