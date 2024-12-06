import axios, { AxiosRequestConfig, AxiosResponse, AxiosError } from "axios"

declare global {
  interface Window {
    env: {
      NEXT_PUBLIC_API_URL: string;
    }
  }
}

const api = axios.create({
  baseURL: typeof window !== 'undefined' 
    ? window.env?.NEXT_PUBLIC_API_URL || "http://localhost:8000"
    : "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
})

interface UserData {
  email: string;
  password: string;
  full_name: string;
  company_name?: string;
  license_number?: string;
  role?: string;
}

interface LeadData {
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  status?: string;
  source?: string;
  notes?: string;
  metadata?: Record<string, any>;
}

interface QualificationData {
  criteria: Record<string, any>;
  conversation_history?: string[];
}

// Add request interceptor for authentication
api.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    const token = localStorage.getItem("token")
    if (token) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${token}`
      }
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Add response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Handle token expiration
      localStorage.removeItem("token")
      window.location.href = "/login"
    }
    return Promise.reject(error)
  }
)

// API endpoints
export const auth = {
  login: async (email: string, password: string) => {
    const response = await api.post("/auth/login", { email, password })
    return response.data
  },
  register: async (userData: UserData) => {
    const response = await api.post("/auth/register", userData)
    return response.data
  },
}

export const leads = {
  getAll: async () => {
    const response = await api.get("/leads")
    return response.data
  },
  getById: async (id: string) => {
    const response = await api.get(`/leads/${id}`)
    return response.data
  },
  create: async (leadData: LeadData) => {
    const response = await api.post("/leads", leadData)
    return response.data
  },
  update: async (id: string, leadData: Partial<LeadData>) => {
    const response = await api.put(`/leads/${id}`, leadData)
    return response.data
  },
  delete: async (id: string) => {
    await api.delete(`/leads/${id}`)
  },
  qualify: async (id: string, qualificationData: QualificationData) => {
    const response = await api.post(`/leads/${id}/qualify`, qualificationData)
    return response.data
  },
}

export default api 