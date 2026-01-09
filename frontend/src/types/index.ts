export interface Student {
    id: string;
    name: string;
    school_id: string;
    grade: number;
    class_name?: string;
    email?: string;
    created_at: string;
    updated_at: string;
}

export interface UnifiedProfile {
    student_id: string;
    basic_info: {
        name: string;
        grade: number;
        school_code: string;
    };
    mastery_summary?: {
        average: number;
        total_attempts: number;
        recent_trend: string;
    };
    recent_activities?: {
        date: string;
        type: string;
        score: number;
    }[];
    latest_reports?: {
        id: string;
        date: string;
        summary: string;
    }[];
    heatmap_data?: Record<string, number>;
    generated_at: string;
}

export interface Intervention {
    id: string;
    student_id: string;
    type: string;
    status: 'active' | 'paused' | 'completed' | 'cancelled';
    progress: {
        completed: number;
        total: number;
    };
    created_at: string;
    weak_areas: {
        concept: string;
        current_mastery: number;
        target_mastery: number;
    }[];
    learning_path: {
        step: number;
        activity: string;
        concept?: string;
        estimated_duration: number;
    }[];
}

export interface CreateInterventionPayload {
    student_id: string;
    type?: string;
    trigger?: string;
    reason?: string;
    target_level?: number;
    duration_days?: number;
}
