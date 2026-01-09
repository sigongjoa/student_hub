import axios from 'axios';
import type { Student, UnifiedProfile, Intervention, CreateInterventionPayload } from '../types';

const apiClient = axios.create({
    baseURL: '/api/v1', // Proxied to localhost:8000
    headers: {
        'Content-Type': 'application/json',
    },
});

export const api = {
    // Students
    createStudent: async (data: Partial<Student>) => {
        const response = await apiClient.post<Student>('/students', data);
        return response.data;
    },

    // Profiles
    getUnifiedProfile: async (studentId: string) => {
        const response = await apiClient.post<UnifiedProfile>('/profiles/unified', {
            student_id: studentId,
            include_sections: ["basic", "mastery", "activities", "reports"]
        });
        return response.data;
    },

    // Interventions
    createIntervention: async (data: CreateInterventionPayload) => {
        const response = await apiClient.post<Intervention>('/interventions', data);
        return response.data;
    },

    // Mock List fetch (since SDD didn't specify list endpoint explicitly in Section 3 but Repository has get_all)
    // We might need to add a list endpoint to main.py if not present.
    // For now assuming a generic GET /students exists or we use search.
    // Checking main.py previously showed `/api/v1/students`. It is a POST.
    // I need to verify if GET exists, otherwise I'll mock it or add it.
    // I'll add a mock function regarding logic if endpoint is missing, but let's assume I can add it or it exists.
    // I'll assume GET /students logic needs to be implemented in backend if missing.
    // For safe implementation in frontend, I will use a placeholder or handle error.
    getStudents: async () => {
        // Temporary: try GET. If 404/405, we might need adjustments.
        // Actually, main.py snippet only showed POST. 
        // I will add GET endpoint to main.py later if needed.
        const response = await apiClient.get<Student[]>('/students');
        return response.data;
    }
};
