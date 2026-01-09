import { FC } from 'react';
import type { Student } from '../../types';
import { Button } from '../../components/common/Button';
import { Link } from 'react-router-dom';
import { MoreHorizontal } from 'lucide-react';

interface StudentTableProps {
    students: Student[];
    isLoading?: boolean;
}

export const StudentTable: FC<StudentTableProps> = ({ students, isLoading }) => {
    if (isLoading) {
        return <div className="p-8 text-center text-slate-500">Loading students...</div>;
    }

    if (students.length === 0) {
        return <div className="p-8 text-center text-slate-500">No students found.</div>;
    }

    return (
        <div className="overflow-x-auto">
            <table className="w-full text-left">
                <thead>
                    <tr className="border-b border-slate-200 text-slate-500 text-sm">
                        <th className="py-3 px-4 font-medium">Name</th>
                        <th className="py-3 px-4 font-medium">ID</th>
                        <th className="py-3 px-4 font-medium">Grade</th>
                        <th className="py-3 px-4 font-medium">Class</th>
                        <th className="py-3 px-4 font-medium">Joined</th>
                        <th className="py-3 px-4 font-medium text-right">Actions</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                    {students.map((student) => (
                        <tr key={student.id} className="hover:bg-slate-50 group">
                            <td className="py-3 px-4 font-medium text-slate-900">
                                <Link to={`/students/${student.id}`} className="hover:text-primary underline-offset-4 hover:underline">
                                    {student.name}
                                </Link>
                            </td>
                            <td className="py-3 px-4 text-slate-500 font-mono text-xs">{student.id.slice(0, 8)}...</td>
                            <td className="py-3 px-4 text-slate-600">{student.grade}</td>
                            <td className="py-3 px-4 text-slate-600">{student.class_name || '-'}</td>
                            <td className="py-3 px-4 text-slate-500 text-sm">
                                {new Date(student.created_at).toLocaleDateString()}
                            </td>
                            <td className="py-3 px-4 text-right">
                                <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100">
                                    <MoreHorizontal size={16} />
                                </Button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};
