import { FC } from 'react';
import { NavLink } from 'react-router-dom';
import {
    LayoutDashboard,
    Users,
    Activity,
    BrainCircuit,
    FlaskConical,
    BarChart3,
    School,
    Settings
} from 'lucide-react';

export const Sidebar: FC = () => {
    const navItems = [
        { icon: LayoutDashboard, label: 'Dashboard', to: '/' },
        { icon: Users, label: 'Students', to: '/students' },
        { icon: BrainCircuit, label: 'Logic Engine', to: '/logic' },
        { icon: Activity, label: 'Q-DNA', to: '/q-dna' },
        { icon: BarChart3, label: 'Reports', to: '/reports' },
        { icon: FlaskConical, label: 'Virtual Lab', to: '/lab' },
        { icon: School, label: 'School Info', to: '/school' },
    ];

    return (
        <aside className="w-64 bg-slate-900 text-white min-h-screen fixed left-0 top-0 overflow-y-auto">
            <div className="p-6 border-b border-slate-800">
                <h1 className="text-xl font-bold flex items-center gap-2">
                    <span className="text-primary-400">MATHESIS</span>
                    <span className="text-xs font-normal text-slate-400">Hub</span>
                </h1>
            </div>

            <nav className="p-4 space-y-1">
                {navItems.map((item) => (
                    <NavLink
                        key={item.to}
                        to={item.to}
                        className={({ isActive }) => `
                            flex items-center gap-3 px-3 py-2 rounded-md transition-colors
                            ${isActive
                                ? 'bg-primary text-white'
                                : 'text-slate-400 hover:text-white hover:bg-slate-800'}
                        `}
                    >
                        <item.icon size={20} />
                        <span>{item.label}</span>
                    </NavLink>
                ))}
            </nav>

            <div className="absolute bottom-0 w-full p-4 border-t border-slate-800">
                <button className="flex items-center gap-3 px-3 py-2 text-slate-400 hover:text-white w-full">
                    <Settings size={20} />
                    <span>Settings</span>
                </button>
            </div>
        </aside>
    );
};
