import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Mic, 
  MicOff, 
  MessageCircle, 
  Calendar, 
  Clock,
  User,
  AlertCircle,
  CheckCircle,
  XCircle,
  RefreshCw,
  Trash2,
  Wifi,
  WifiOff
} from 'lucide-react';
import { useVoiceChat } from '../hooks/useVoiceChat';
import { useVoiceStore } from '../stores/voiceStore';
import { format } from 'date-fns';

interface VoiceInterfaceProps {
  className?: string;
}

const VoiceInterface: React.FC<VoiceInterfaceProps> = ({ className = '' }) => {
  const { 
    toggleRecording, 
    isRecording, 
    isProcessing, 
    connectionStatus, 
    isConnected,
    error,
    resetConnection
  } = useVoiceChat();
  
  const { 
    messages, 
    clearMessages, 
    currentIntent,
    extractedEntities,
    suggestions,
    urgencyLevel
  } = useVoiceStore();

  const [showSuggestions, setShowSuggestions] = useState(false);
  const [audioSupported, setAudioSupported] = useState(true);
  const [microphonePermission, setMicrophonePermission] = useState<'granted' | 'denied' | 'prompt'>('prompt');

  useEffect(() => {
    // Check if audio recording is supported
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setAudioSupported(false);
    }

    // Check microphone permission
    navigator.permissions?.query({ name: 'microphone' as PermissionName })
      .then(permissionStatus => {
        setMicrophonePermission(permissionStatus.state as any);
        
        permissionStatus.onchange = () => {
          setMicrophonePermission(permissionStatus.state as any);
        };
      })
      .catch(() => {
        // Permissions API not supported
        setMicrophonePermission('prompt');
      });
  }, []);

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'text-green-500';
      case 'connecting': return 'text-yellow-500';
      case 'error': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const getConnectionStatusText = () => {
    switch (connectionStatus) {
      case 'connected': return 'Connected';
      case 'connecting': return 'Connecting...';
      case 'error': return 'Connection Error';
      default: return 'Disconnected';
    }
  };

  const getConnectionStatusIcon = () => {
    switch (connectionStatus) {
      case 'connected': return <Wifi className="w-4 h-4" />;
      case 'connecting': return <RefreshCw className="w-4 h-4 animate-spin" />;
      case 'error': return <WifiOff className="w-4 h-4" />;
      default: return <WifiOff className="w-4 h-4" />;
    }
  };

  const getUrgencyColor = () => {
    switch (urgencyLevel) {
      case 'emergency': return 'border-red-500 bg-red-50';
      case 'high': return 'border-orange-500 bg-orange-50';
      case 'medium': return 'border-yellow-500 bg-yellow-50';
      default: return 'border-blue-200 bg-blue-50';
    }
  };

  const renderExtractedInfo = () => {
    if (!extractedEntities || Object.keys(extractedEntities).length === 0) return null;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`p-4 rounded-lg border-2 ${getUrgencyColor()} mb-4`}
      >
        <h3 className="font-semibold text-gray-800 mb-2 flex items-center">
          <Calendar className="w-4 h-4 mr-2" />
          Appointment Details
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
          {extractedEntities.patient_name && (
            <div className="flex items-center">
              <User className="w-3 h-3 mr-2 text-gray-500" />
              <span className="text-gray-600">Patient:</span>
              <span className="ml-1 font-medium">{extractedEntities.patient_name}</span>
            </div>
          )}
          {extractedEntities.date && (
            <div className="flex items-center">
              <Calendar className="w-3 h-3 mr-2 text-gray-500" />
              <span className="text-gray-600">Date:</span>
              <span className="ml-1 font-medium">{extractedEntities.date}</span>
            </div>
          )}
          {extractedEntities.time && (
            <div className="flex items-center">
              <Clock className="w-3 h-3 mr-2 text-gray-500" />
              <span className="text-gray-600">Time:</span>
              <span className="ml-1 font-medium">{extractedEntities.time}</span>
            </div>
          )}
          {extractedEntities.doctor && (
            <div className="flex items-center">
              <User className="w-3 h-3 mr-2 text-gray-500" />
              <span className="text-gray-600">Doctor:</span>
              <span className="ml-1 font-medium">{extractedEntities.doctor}</span>
            </div>
          )}
          {extractedEntities.reason && (
            <div className="flex items-center col-span-full">
              <AlertCircle className="w-3 h-3 mr-2 text-gray-500" />
              <span className="text-gray-600">Reason:</span>
              <span className="ml-1 font-medium">{extractedEntities.reason}</span>
            </div>
          )}
        </div>
        
        {urgencyLevel === 'emergency' && (
          <div className="mt-3 p-2 bg-red-100 border border-red-300 rounded text-red-800 text-sm">
            <strong>⚠️ Emergency:</strong> For urgent medical care, please call 911 or visit your nearest emergency room.
          </div>
        )}
      </motion.div>
    );
  };

  const renderSuggestions = () => {
    if (!suggestions || suggestions.length === 0) return null;

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4"
      >
        <h4 className="text-sm font-medium text-blue-800 mb-2">💡 Helpful Suggestions:</h4>
        <ul className="space-y-1">
          {suggestions.map((suggestion, index) => (
            <li key={index} className="text-sm text-blue-700 flex items-start">
              <span className="w-1 h-1 rounded-full bg-blue-400 mt-2 mr-2 flex-shrink-0"></span>
              {suggestion}
            </li>
          ))}
        </ul>
      </motion.div>
    );
  };

  const canRecord = () => {
    return isConnected && audioSupported && microphonePermission !== 'denied';
  };

  const getRecordButtonMessage = () => {
    if (!isConnected) return 'Not connected to server';
    if (!audioSupported) return 'Audio not supported in this browser';
    if (microphonePermission === 'denied') return 'Microphone access denied';
    if (isProcessing) return 'Processing your request...';
    if (isRecording) return 'Listening... Click to stop';
    return 'Click to speak';
  };

  return (
    <div className={`flex flex-col h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50 ${className}`}>
      {/* Header */}
      <motion.div
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="bg-white/80 backdrop-blur-md border-b border-blue-100 p-4 shadow-sm"
      >
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-2 rounded-xl">
              <MessageCircle className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">DocTalk AI</h1>
              <p className="text-sm text-gray-600">Your Voice Assistant for Medical Appointments</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              <div className={getConnectionStatusColor()}>
                {getConnectionStatusIcon()}
              </div>
              <span className={`text-xs font-medium ${getConnectionStatusColor()}`}>
                {getConnectionStatusText()}
              </span>
            </div>
            
            {/* Microphone Permission Status */}
            {microphonePermission === 'denied' && (
              <div className="flex items-center space-x-1 text-red-500">
                <MicOff className="w-4 h-4" />
                <span className="text-xs">Mic Denied</span>
              </div>
            )}
            
            {/* Action Buttons */}
            <div className="flex items-center space-x-2">
              {connectionStatus === 'error' && resetConnection && (
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={resetConnection}
                  className="p-2 text-orange-600 hover:bg-orange-50 rounded-lg transition-colors"
                  title="Reconnect"
                >
                  <RefreshCw className="w-4 h-4" />
                </motion.button>
              )}
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowSuggestions(!showSuggestions)}
                className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="Toggle suggestions"
              >
                <AlertCircle className="w-4 h-4" />
              </motion.button>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={clearMessages}
                className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="Clear chat"
              >
                <Trash2 className="w-4 h-4" />
              </motion.button>
            </div>
          </div>
        </div>
        
        {/* Intent & Urgency Indicator */}
        {currentIntent && currentIntent !== 'general' && (
          <div className="max-w-4xl mx-auto mt-3">
            <div className={`px-3 py-1 rounded-full text-xs font-medium inline-flex items-center ${
              currentIntent === 'book_appointment' ? 'bg-green-100 text-green-800' :
              currentIntent === 'cancel_appointment' ? 'bg-red-100 text-red-800' :
              currentIntent === 'reschedule_appointment' ? 'bg-yellow-100 text-yellow-800' :
              currentIntent === 'emergency' ? 'bg-red-500 text-white animate-pulse' :
              'bg-blue-100 text-blue-800'
            }`}>
              {currentIntent === 'emergency' && <AlertCircle className="w-3 h-3 mr-1" />}
              Intent: {currentIntent.replace('_', ' ').toUpperCase()}
            </div>
          </div>
        )}
      </motion.div>

      {/* Error Display */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="max-w-4xl mx-auto mt-4 px-4"
          >
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-start">
                <XCircle className="w-5 h-5 text-red-500 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <h3 className="text-sm font-medium text-red-800">Connection Error</h3>
                  <p className="text-sm text-red-600 mt-1">{error}</p>
                  <div className="mt-2">
                    <button
                      onClick={resetConnection}
                      className="text-sm text-red-700 underline hover:no-underline"
                    >
                      Try reconnecting
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          
          {/* Extracted Information */}
          {renderExtractedInfo()}
          
          {/* Suggestions */}
          <AnimatePresence>
            {(showSuggestions || urgencyLevel === 'emergency') && renderSuggestions()}
          </AnimatePresence>
          
          {/* Welcome Message */}
          {messages.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center py-12"
            >
              <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-4 rounded-full w-20 h-20 mx-auto mb-6">
                <MessageCircle className="w-12 h-12 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome to DocTalk AI</h2>
              <p className="text-gray-600 mb-6 max-w-md mx-auto">
                I'm here to help you manage your medical appointments. You can book, reschedule, or cancel appointments using your voice.
              </p>
              
              {/* System Status Warnings */}
              <div className="space-y-3 mb-6">
                {!audioSupported && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 max-w-md mx-auto">
                    <AlertCircle className="w-5 h-5 text-yellow-600 mx-auto mb-2" />
                    <p className="text-yellow-800 text-sm">
                      Audio recording is not supported in your browser. Please use Chrome, Firefox, or Safari.
                    </p>
                  </div>
                )}
                
                {microphonePermission === 'denied' && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 max-w-md mx-auto">
                    <MicOff className="w-5 h-5 text-red-600 mx-auto mb-2" />
                    <p className="text-red-800 text-sm">
                      Microphone access is required for voice chat. Please enable it in your browser settings.
                    </p>
                  </div>
                )}
                
                {!isConnected && (
                  <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 max-w-md mx-auto">
                    <WifiOff className="w-5 h-5 text-orange-600 mx-auto mb-2" />
                    <p className="text-orange-800 text-sm">
                      Not connected to server. Please check your internet connection and try refreshing the page.
                    </p>
                  </div>
                )}
              </div>
              
              <div className="space-y-2 text-sm text-gray-500">
                <p>📅 Book appointments: "I need to schedule an appointment"</p>
                <p>🔄 Reschedule: "I need to change my appointment"</p>
                <p>❌ Cancel: "I want to cancel my appointment"</p>
                <p>📞 Emergency: "This is an emergency"</p>
              </div>
            </motion.div>
          )}

          {/* Messages */}
          <AnimatePresence>
            {messages.map((message, index) => (
              <motion.div
                key={message.id || index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} mb-4`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.type === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-white border border-gray-200 text-gray-900 shadow-sm'
                  }`}
                >
                  <p className="text-sm">{message.content}</p>
                  
                  {/* Message metadata */}
                  <div className={`text-xs mt-1 flex items-center justify-between ${
                    message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                  }`}>
                    <span>
                      {typeof message.timestamp === 'string' 
                        ? format(new Date(message.timestamp), 'HH:mm')
                        : format(message.timestamp, 'HH:mm')
                      }
                    </span>
                    {message.isAudio && (
                      <span className="ml-2">🎵</span>
                    )}
                    {message.intent && message.intent !== 'general' && (
                      <span className="ml-2 text-xs opacity-75">
                        {message.intent}
                      </span>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          
          {/* Processing Indicator */}
          <AnimatePresence>
            {isProcessing && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="flex justify-start mb-4"
              >
                <div className="bg-white border border-gray-200 text-gray-900 shadow-sm max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                    <span className="text-sm text-gray-600">Processing...</span>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Voice Control */}
      <motion.div
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="bg-white/80 backdrop-blur-md border-t border-blue-100 p-4"
      >
        <div className="max-w-4xl mx-auto flex items-center justify-center">
          <motion.button
            whileHover={{ scale: canRecord() ? 1.05 : 1 }}
            whileTap={{ scale: canRecord() ? 0.95 : 1 }}
            onClick={toggleRecording}
            disabled={!canRecord() || isProcessing}
            className={`w-16 h-16 rounded-full flex items-center justify-center transition-all duration-300 shadow-lg ${
              isRecording
                ? 'bg-red-500 text-white animate-pulse'
                : canRecord()
                ? 'bg-blue-500 text-white hover:bg-blue-600'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {isRecording ? (
              <MicOff className="w-8 h-8" />
            ) : (
              <Mic className="w-8 h-8" />
            )}
          </motion.button>
          
          <div className="ml-4 text-sm max-w-xs">
            <p className={`font-medium ${
              isRecording ? 'text-red-600' : 
              canRecord() ? 'text-gray-700' : 'text-gray-500'
            }`}>
              {isRecording ? 'Listening...' : canRecord() ? 'Click to speak' : 'Voice unavailable'}
            </p>
            <p className="text-gray-500 text-xs">
              {getRecordButtonMessage()}
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default VoiceInterface;