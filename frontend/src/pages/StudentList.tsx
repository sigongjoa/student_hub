import { FC } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { Layout } from '../components/common/Layout';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { StudentTable } from '../features/students/StudentTable';
import { Plus, Search, Filter } from 'lucide-react';

export const StudentList: FC = () => {
    const { data: students = [], isLoading } = useQuery({
        queryKey: ['students'],
        queryFn: api.getStudents,
    });

    return (
        <Layout>
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Students</h1>
                    <p className="text-slate-500">Manage your students and view their progress.</p>
                </div>
                <Button>
                    <Plus size={18} className="mr-2" />
                    Add Student
                </Button>
            </div>

            <Card className="mb-6">
                <div className="flex gap-4 mb-6">
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                        <input
                            type="text"
                            placeholder="Search by name, ID, or school..."
                            className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                        />
                    </div>
                    <Button variant="outline">
                        <Filter size={18} className="mr-2" />
                        Filters
                    </Button>
                </div>

                <StudentTable students={students} isLoading={isLoading} />
            </Card>
        </Layout>
    );
};
