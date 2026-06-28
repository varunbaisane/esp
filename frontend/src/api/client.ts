import axios from "axios";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = sessionStorage.getItem("access_token") || localStorage.getItem("access_token");
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

const cache = new Map<string, { data: any; timestamp: number }>();
const CACHE_TTL = 60000; // 60 seconds

export const cachedGet = async <T>(url: string, params?: any, ttl = CACHE_TTL): Promise<T> => {
  const key = url + (params ? JSON.stringify(params) : '');
  const cached = cache.get(key);
  
  if (cached && Date.now() - cached.timestamp < ttl) {
    return cached.data as T;
  }
  
  const response = await apiClient.get<T>(url, { params });
  cache.set(key, { data: response.data, timestamp: Date.now() });
  
  return response.data;
};

export const clearCache = (urlPrefix?: string) => {
  if (urlPrefix) {
    for (const key of cache.keys()) {
      if (key.startsWith(urlPrefix)) {
        cache.delete(key);
      }
    }
  } else {
    cache.clear();
  }
};
