export interface Appointment {
  id: string;
  patient_id: string;
  patient_name: string;
  patient_phone?: string;
  doctor_name: string;
  appointment_date: string;
  duration_minutes: number;
  status: 'scheduled' | 'completed' | 'cancelled' | 'rescheduled';
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateAppointmentData {
  patient_id: string;
  patient_name: string;
  patient_phone?: string;
  doctor_name: string;
  appointment_date: string;
  duration_minutes?: number;
  status?: string;
  notes?: string;
}

export interface VoiceMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: string | Date;
  confidence?: number;
  intent?: string;
  entities?: Record<string, any>;
  urgency?: 'low' | 'medium' | 'high' | 'emergency';
  isAudio?: boolean;
  processing?: boolean;
}

export interface VoiceResponse {
  transcript?: string;
  ai_response?: {
    text: string;
    intent: string;
    extracted_info: Record<string, any>;
  };
  audio_response?: string;
  timestamp: string;
  error?: string;
  appointment_action?: {
    status: string;
    message: string;
    appointment?: Appointment;
    available_slots?: string[];
    missing?: string[];
  };
}

export interface Doctor {
  name: string;
  specialty: string;
  available: boolean;
}

export interface AvailabilitySlot {
  time: string;
  available: boolean;
}

export interface AvailabilityResponse {
  doctor: string;
  date: string;
  available_slots: string[];
}

export interface VoiceState {
  isRecording: boolean;
  isProcessing: boolean;
  isPlaying: boolean;
  messages: VoiceMessage[];
  currentTranscript: string;
  connectionStatus: 'disconnected' | 'connecting' | 'connected' | 'error';
}

export interface AppointmentState {
  appointments: Appointment[];
  selectedAppointment: Appointment | null;
  loading: boolean;
  error: string | null;
}

export interface ExtractedEntities {
  patient_name?: string;
  date?: string;
  time?: string;
  doctor?: string;
  reason?: string;
  phone?: string;
  email?: string;
}

export interface VoiceStore {
  messages: VoiceMessage[];
  currentIntent?: string;
  extractedEntities?: ExtractedEntities;
  suggestions?: string[];
  urgencyLevel?: 'low' | 'medium' | 'high' | 'emergency';
  addMessage: (message: Omit<VoiceMessage, 'id'>) => void;
  clearMessages: () => void;
  updateCurrentIntent: (intent: string) => void;
  updateExtractedEntities: (entities: ExtractedEntities) => void;
  updateSuggestions: (suggestions: string[]) => void;
  updateUrgencyLevel: (level: 'low' | 'medium' | 'high' | 'emergency') => void;
}