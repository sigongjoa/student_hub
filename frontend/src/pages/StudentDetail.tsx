import { FC } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { Layout } from '../components/common/Layout';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { ArrowLeft, User, GraduationCap, Calendar } from 'lucide-react';

export const StudentDetail: FC = () => {
    const { id = '' } = useParams();
    const navigate = useNavigate();

    const { data: profile, isLoading } = useQuery({
        queryKey: ['profile', id],
        queryFn: () => api.getUnifiedProfile(id),
        enabled: !!id,
    });

    if (isLoading) return <Layout>Loading...</Layout>;
    if (!profile) return <Layout>Student not found</Layout>;

    return (
        <Layout>
            <div className="mb-6">
                <Button variant="ghost" className="pl-0 hover:bg-transparent hover:text-primary mb-2" onClick={() => navigate('/students')}>
                    <ArrowLeft size={16} className="mr-2" />
                    Back to Students
                </Button>
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="w-16 h-16 rounded-full bg-slate-200 flex items-center justify-center text-slate-500">
                            <User size={32} />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-slate-900">{profile.basic_info.name}</h1>
                            <p className="text-slate-500 flex items-center gap-2">
                                <span className="font-mono text-xs bg-slate-100 px-2 py-0.5 rounded text-slate-600">ID: {profile.student_id ? profile.student_id.split('-')[0] : 'N/A'}</span>
                                • Grade {profile.basic_info.grade}
                            </p>
                        </div>
                    </div>
                    <Button>Create Intervention</Button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-6">
                    <Card title="Quick Stats">
                        <div className="grid grid-cols-3 gap-4 text-center">
                            <div className="p-4 bg-slate-50 rounded-lg">
                                <p className="text-sm text-slate-500">Mastery Avg</p>
                                <p className="text-xl font-bold text-primary">{profile.mastery_summary?.average != null ? Math.round(profile.mastery_summary.average * 100) : 0}%</p>
                            </div>
                            <div className="p-4 bg-slate-50 rounded-lg">
                                <p className="text-sm text-slate-500">Attempts</p>
                                <p className="text-xl font-bold text-slate-900">{profile.mastery_summary?.total_attempts || 0}</p>
                            </div>
                            <div className="p-4 bg-slate-50 rounded-lg">
                                <p className="text-sm text-slate-500">Trend</p>
                                <p className="text-xl font-bold text-green-600">{profile.mastery_summary?.recent_trend || 'Stable'}</p>
                            </div>
                        </div>
                    </Card>

                    <Card title="Recent Activities">
                        <ul className="space-y-4">
                            {profile.recent_activities?.map((activity, idx) => (
                                <li key={idx} className="flex items-start gap-4 pb-4 border-b border-slate-100 last:border-0 last:pb-0">
                                    <div className="p-2 bg-blue-50 text-blue-600 rounded">
                                        <GraduationCap size={16} />
                                    </div>
                                    <div className="flex-1">
                                        <p className="font-medium text-slate-900">{activity.type}</p>
                                        <p className="text-sm text-slate-500">{new Date(activity.date).toLocaleDateString()}</p>
                                    </div>
                                    <span className="font-semibold text-slate-700">{activity.score} pts</span>
                                </li>
                            ))}
                            {!profile.recent_activities?.length && <p className="text-slate-500 italic">No recent activity.</p>}
                        </ul>
                    </Card>
                </div>

                <div className="space-y-6">
                    <Card title="School Info">
                        <div className="space-y-3">
                            <div>
                                <p className="text-xs text-slate-500 uppercase tracking-wide">School Code</p>
                                <p className="font-medium">{profile.basic_info.school_code}</p>
                            </div>
                            <div className="flex items-center gap-2 text-primary cursor-pointer hover:underline">
                                <Calendar size={14} />
                                <span className="text-sm">View Schedule</span>
                            </div>
                        </div>
                    </Card>

                    <Card title="Analytics">
                        <div className="h-48 flex items-center justify-center bg-slate-50 rounded text-slate-400 text-sm">
                            Mastery Radar Chart Placeholder
                        </div>
                    </Card>
                </div>
            </div>
        </Layout>
    );
};
