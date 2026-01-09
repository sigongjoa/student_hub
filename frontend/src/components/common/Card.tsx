import { FC, HTMLAttributes } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
    title?: string;
}

export const Card: FC<CardProps> = ({ title, children, className, ...props }) => {
    return (
        <div className={`bg-white rounded-lg border border-slate-200 shadow-sm ${className}`} {...props}>
            {title && (
                <div className="px-6 py-4 border-b border-slate-100">
                    <h3 className="text-lg font-semibold text-slate-800">{title}</h3>
                </div>
            )}
            <div className="p-6">
                {children}
            </div>
        </div>
    );
};
