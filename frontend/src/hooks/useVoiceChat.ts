import { useEffect, useRef, useCallback } from 'react';
import { useVoiceStore } from '../stores/voiceStore';
import { VoiceResponse } from '../types';

interface UseVoiceChatOptions {
  autoConnect?: boolean;
  apiUrl?: string;
}

export const useVoiceChat = (options: UseVoiceChatOptions = {}) => {
  const {
    autoConnect = true,
    apiUrl = 'ws://localhost:8000/api/voice/stream'
  } = options;

  const websocketRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioContextRef = useRef<AudioContext | null>(null);

  const {
    isRecording,
    isProcessing,
    connectionStatus,
    error,
    setRecording,
    setProcessing,
    setConnectionStatus,
    setError,
    updateCurrentIntent,
    updateExtractedEntities,
    updateSuggestions,
    updateUrgencyLevel,
    processVoiceResponse
  } = useVoiceStore();

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (websocketRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setConnectionStatus('connecting');
    
    const ws = new WebSocket(apiUrl);
    
    ws.onopen = () => {
      console.log('Connected to voice chat');
      setConnectionStatus('connected');
    };
    
    ws.onmessage = (event) => {
      try {
        const response: VoiceResponse = JSON.parse(event.data);
        processVoiceResponse(response);
        
        if (response.audio_response) {
          playAudioResponse(response.audio_response);
        }
        
        setProcessing(false);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
        setProcessing(false);
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnectionStatus('error');
      setProcessing(false);
    };
    
    ws.onclose = () => {
      console.log('Disconnected from voice chat');
      setConnectionStatus('disconnected');
      setProcessing(false);
    };
    
    websocketRef.current = ws;
  }, [apiUrl, setConnectionStatus, processVoiceResponse, setProcessing]);

  // Start recording
  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        } 
      });
      
      audioChunksRef.current = [];
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm'
      });
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        sendAudioToServer(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start(100);
      setRecording(true);
      
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Unable to access microphone. Please check permissions.');
    }
  }, [setRecording]);

  // Stop recording
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
      setProcessing(true);
    }
  }, [isRecording, setRecording, setProcessing]);

  // Send audio to server
  const sendAudioToServer = useCallback(async (audioBlob: Blob) => {
    if (!websocketRef.current || websocketRef.current.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected');
      setProcessing(false);
      return;
    }

    try {
      const arrayBuffer = await audioBlob.arrayBuffer();
      const base64Audio = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));
      
      websocketRef.current.send(JSON.stringify({
        type: 'audio',
        audio: base64Audio
      }));
      
    } catch (error) {
      console.error('Error sending audio:', error);
      setProcessing(false);
    }
  }, [setProcessing]);

  // Play audio response
  const playAudioResponse = useCallback(async (base64Audio: string) => {
    try {
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      }
      
      const audioData = atob(base64Audio);
      const arrayBuffer = new ArrayBuffer(audioData.length);
      const view = new Uint8Array(arrayBuffer);
      
      for (let i = 0; i < audioData.length; i++) {
        view[i] = audioData.charCodeAt(i);
      }
      
      const audioBuffer = await audioContextRef.current.decodeAudioData(arrayBuffer);
      const source = audioContextRef.current.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(audioContextRef.current.destination);
      source.start();
      
    } catch (error) {
      console.error('Error playing audio:', error);
    }
  }, []);

  // Toggle recording
  const toggleRecording = useCallback(() => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  }, [isRecording, startRecording, stopRecording]);

  // Enhanced error handling and reconnection
  const resetConnection = useCallback(() => {
    if (websocketRef.current) {
      websocketRef.current.close();
      websocketRef.current = null;
    }
    setError(undefined);
    setTimeout(() => {
      connect();
    }, 1000);
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect();
    }
    
    return () => {
      if (websocketRef.current) {
        websocketRef.current.close();
      }
    };
  }, [autoConnect, connect]);

  return {
    connect,
    startRecording,
    stopRecording,
    toggleRecording,
    resetConnection,
    isRecording,
    isProcessing,
    connectionStatus,
    isConnected: connectionStatus === 'connected',
    error
  };
};