import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Export API_BASE_URL for direct use
export { API_BASE_URL };

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Enable sending cookies with requests
});

// Add interceptor to include Accept-Language header and Authorization token
api.interceptors.request.use((config) => {
  // Get language from cookie or localStorage
  const getLangFromCookie = () => {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === 'django_language') {
        return value;
      }
    }
    return null;
  };
  
  const language = getLangFromCookie() || localStorage.getItem('i18nextLng') || 'en';
  config.headers['Accept-Language'] = language;
  
  // Add Authorization header if token exists
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Championships
export const getChampionships = async () => {
  const response = await api.get('/championships/');
  // Handle both paginated and non-paginated responses
  return Array.isArray(response.data) ? response.data : response.data.results || [];
};

export const getChampionship = async (id) => {
  const response = await api.get(`/championships/${id}/`);
  return response.data;
};

// Races
export const getRaces = async (params = {}) => {
  const response = await api.get('/races/', { params });
  // Handle both paginated and non-paginated responses
  return Array.isArray(response.data) ? response.data : response.data.results || [];
};

export const getRace = async (id) => {
  const response = await api.get(`/races/${id}/`);
  return response.data;
};

// Race Days
export const getRaceDays = async (raceId) => {
  const response = await api.get(`/race-days/?race=${raceId}`);
  return Array.isArray(response.data) ? response.data : response.data.results || [];
};

// Race Day Results
export const getRaceDayResults = async (raceDayId) => {
  const response = await api.get(`/results/race-day-results/?race_day=${raceDayId}`);
  return Array.isArray(response.data) ? response.data : response.data.results || [];
};

// Race Results (overall)
export const getRaceResults = async (raceId, category = null) => {
  const params = { race: raceId };
  if (category) params.category = category;
  const response = await api.get('/results/race-results/', { params });
  return Array.isArray(response.data) ? response.data : response.data.results || [];
};

// Authentication
export const register = async (userData) => {
  const response = await api.post('/users/', userData);
  return response.data;
};

export const matchRider = async (matchData) => {
  const response = await api.post('/users/match_rider/', matchData);
  return response.data;
};

export const claimAccount = async (claimData) => {
  const response = await api.post('/users/claim_account/', claimData);
  return response.data;
};

export const activateAccount = async (activationCode) => {
  const response = await api.post('/users/activate/', { activation_code: activationCode });
  return response.data;
};

export const login = async (username, password) => {
  const response = await api.post('/auth/login/', { username, password });
  return response.data;
};

// Get current user info
export const getCurrentUser = async () => {
  const response = await api.get('/users/me/');
  return response.data;
};

// Language
export const setLanguage = async (language) => {
  const response = await api.post('/set-language/', { language });
  return response.data;
};

export const getLanguage = async () => {
  const response = await api.get('/get-language/');
  return response.data;
};

// Riders
export const getRider = async (id) => {
  const response = await api.get(`/riders/${id}/`);
  return response.data;
};

export const getRiderResults = async (id) => {
  const response = await api.get(`/riders/${id}/results/`);
  return Array.isArray(response.data) ? response.data : response.data.results || [];
};

export const getRiderChampionshipResults = async (riderId) => {
  const response = await api.get('/results/championship-results/', {
    params: { rider: riderId }
  });
  return Array.isArray(response.data) ? response.data : response.data.results || [];
};

export default api;

