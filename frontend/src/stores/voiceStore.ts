import { create } from 'zustand';
import { VoiceState, VoiceMessage, VoiceResponse, ExtractedEntities } from '../types';

interface VoiceStore extends VoiceState {
  // Enhanced state
  currentIntent?: string;
  extractedEntities?: ExtractedEntities;
  suggestions?: string[];
  urgencyLevel?: 'low' | 'medium' | 'high' | 'emergency';
  error?: string;
  
  // Actions
  setRecording: (isRecording: boolean) => void;
  setProcessing: (isProcessing: boolean) => void;
  setPlaying: (isPlaying: boolean) => void;
  setConnectionStatus: (status: VoiceState['connectionStatus']) => void;
  setError: (error: string | undefined) => void;
  addMessage: (message: Omit<VoiceMessage, 'id'>) => void;
  updateLastMessage: (updates: Partial<VoiceMessage>) => void;
  setCurrentTranscript: (transcript: string) => void;
  updateCurrentIntent: (intent: string) => void;
  updateExtractedEntities: (entities: ExtractedEntities) => void;
  updateSuggestions: (suggestions: string[]) => void;
  updateUrgencyLevel: (level: 'low' | 'medium' | 'high' | 'emergency') => void;
  clearMessages: () => void;
  reset: () => void;
  processVoiceResponse: (response: VoiceResponse) => void;
}

export const useVoiceStore = create<VoiceStore>((set, get) => ({
  // Initial state
  isRecording: false,
  isProcessing: false,
  isPlaying: false,
  messages: [],
  currentTranscript: '',
  connectionStatus: 'disconnected',
  currentIntent: undefined,
  extractedEntities: undefined,
  suggestions: undefined,
  urgencyLevel: undefined,
  error: undefined,

  // Actions
  setRecording: (isRecording) => set({ isRecording }),
  
  setProcessing: (isProcessing) => set({ isProcessing }),
  
  setPlaying: (isPlaying) => set({ isPlaying }),
  
  setConnectionStatus: (connectionStatus) => set({ connectionStatus }),
  
  setError: (error) => set({ error }),
  
  addMessage: (message) => set((state) => ({
    messages: [
      ...state.messages,
      {
        ...message,
        id: `msg_${Date.now()}_${Math.random()}`,
      }
    ]
  })),
  
  updateLastMessage: (updates) => set((state) => {
    const messages = [...state.messages];
    if (messages.length > 0) {
      messages[messages.length - 1] = {
        ...messages[messages.length - 1],
        ...updates
      };
    }
    return { messages };
  }),
  
  setCurrentTranscript: (currentTranscript) => set({ currentTranscript }),
  
  updateCurrentIntent: (currentIntent) => set({ currentIntent }),
  
  updateExtractedEntities: (extractedEntities) => set({ extractedEntities }),
  
  updateSuggestions: (suggestions) => set({ suggestions }),
  
  updateUrgencyLevel: (urgencyLevel) => set({ urgencyLevel }),
  
  clearMessages: () => set({ 
    messages: [], 
    currentTranscript: '',
    currentIntent: undefined,
    extractedEntities: undefined,
    suggestions: undefined
  }),
  
  reset: () => set({
    messages: [],
    currentTranscript: '',
    currentIntent: undefined,
    extractedEntities: undefined,
    suggestions: undefined,
    urgencyLevel: undefined,
    error: undefined,
    isRecording: false,
    isProcessing: false,
    isPlaying: false
  }),
  
  processVoiceResponse: (response) => {
    const { 
      addMessage,
      updateCurrentIntent,
      updateExtractedEntities,
      updateSuggestions,
      updateUrgencyLevel,
      setError,
      setProcessing
    } = get();
    
    setProcessing(false);
    
    // Handle errors
    if (response.error) {
      setError(response.error);
      addMessage({
        type: 'assistant',
        content: `I'm sorry, there was an error: ${response.error}`,
        timestamp: new Date().toISOString()
      });
      return;
    } else {
      setError(undefined);
    }
    
    // Add user message if transcript exists
    if (response.transcript) {
      addMessage({
        type: 'user',
        content: response.transcript,
        timestamp: response.timestamp,
        isAudio: true
      });
    }
    
    // Process AI response
    if (response.ai_response?.text) {
      const aiMessage: Omit<VoiceMessage, 'id'> = {
        type: 'assistant',
        content: response.ai_response.text,
        timestamp: response.timestamp,
        isAudio: !!response.audio_response,
        intent: response.ai_response.intent,
        entities: response.ai_response.extracted_info
      };

      addMessage(aiMessage);
      
      // Update global state with extracted information
      if (response.ai_response.intent) {
        updateCurrentIntent(response.ai_response.intent);
      }
      
      if (response.ai_response.extracted_info) {
        updateExtractedEntities(response.ai_response.extracted_info);
      }
    }
    
    // Play audio if available - backend returns audio in audio_response field
    const audioData = response.audio_response;
    if (audioData) {
      try {
        const audioBlob = new Blob([
          Uint8Array.from(atob(audioData), c => c.charCodeAt(0))
        ], { type: 'audio/wav' });
        
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        // Add user interaction event listeners for audio playback
        const playAudio = async () => {
          try {
            const { setPlaying } = get();
            setPlaying(true);
            await audio.play();
            audio.onended = () => setPlaying(false);
          } catch (playError) {
            console.error('Audio play failed:', playError);
            const { setPlaying } = get();
            setPlaying(false);
            // If autoplay fails, try with user interaction
            document.addEventListener('click', () => {
              audio.play().catch(console.error);
            }, { once: true });
          }
        };
        
        playAudio();
        
      } catch (error) {
        console.error('Error playing audio:', error);
      }
    }
    
    // Handle appointment actions
    if (response.appointment_action) {
      console.log('Appointment action:', response.appointment_action);
      // This could trigger additional UI updates or notifications
    }
  }
}));
