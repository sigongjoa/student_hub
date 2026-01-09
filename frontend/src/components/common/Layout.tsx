import { FC, ReactNode } from 'react';
import { Sidebar } from './Sidebar';

interface LayoutProps {
    children: ReactNode;
}

export const Layout: FC<LayoutProps> = ({ children }) => {
    return (
        <div className="min-h-screen bg-slate-50">
            <Sidebar />
            <main className="pl-64">
                <header className="h-16 bg-white border-b border-slate-200 sticky top-0 z-10 flex items-center px-8 justify-between">
                    <h2 className="text-lg font-medium text-slate-800">Student Hub</h2>
                    <div className="flex items-center gap-4">
                        <div className="w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold">
                            T
                        </div>
                    </div>
                </header>
                <div className="p-8">
                    {children}
                </div>
            </main>
        </div>
    );
};
