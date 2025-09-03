import React, { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import { 
  Home, 
  Mic, 
  Users, 
  UserCheck, 
  Calendar,
  Menu,
  X
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import Dashboard from './components/Dashboard';
import VoiceInterface from './components/VoiceInterface';
import PatientsList from './components/PatientsList';
import DoctorsList from './components/DoctorsList';
import AppointmentsList from './components/AppointmentsList';
import './index.css';

type ActiveView = 'dashboard' | 'voice' | 'patients' | 'doctors' | 'appointments';

function App() {
  const [activeView, setActiveView] = useState<ActiveView>('dashboard');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home },
    { id: 'voice', label: 'Voice Chat', icon: Mic },
    { id: 'patients', label: 'Patients', icon: Users },
    { id: 'doctors', label: 'Doctors', icon: UserCheck },
    { id: 'appointments', label: 'Appointments', icon: Calendar }
  ] as const;

  const renderActiveView = () => {
    switch (activeView) {
      case 'dashboard':
        return <Dashboard onNavigate={(section) => setActiveView(section as ActiveView)} />;
      case 'voice':
        return <VoiceInterface />;
      case 'patients':
        return <PatientsList 
          onCreateNew={() => console.log('Create new patient')}
          onEdit={(patient) => console.log('Edit patient:', patient)}
          onPatientSelect={(patient) => console.log('Select patient:', patient)}
        />;
      case 'doctors':
        return <DoctorsList 
          onCreateNew={() => console.log('Create new doctor')}
          onEdit={(doctor) => console.log('Edit doctor:', doctor)}
          onDoctorSelect={(doctor) => console.log('Select doctor:', doctor)}
        />;
      case 'appointments':
        return <AppointmentsList 
          onCreateNew={() => console.log('Create new appointment')}
          onEdit={(appointment) => console.log('Edit appointment:', appointment)}
          onCancel={(appointment) => console.log('Cancel appointment:', appointment)}
          onAppointmentSelect={(appointment) => console.log('Select appointment:', appointment)}
        />;
      default:
        return <Dashboard onNavigate={(section) => setActiveView(section as ActiveView)} />;
    }
  };

  const getCurrentTitle = () => {
    const item = navigationItems.find(item => item.id === activeView);
    return item ? item.label : 'Dashboard';
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <AnimatePresence>
        {(isSidebarOpen || window.innerWidth >= 1024) && (
          <motion.div
            initial={{ x: -280 }}
            animate={{ x: 0 }}
            exit={{ x: -280 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed lg:static inset-y-0 left-0 z-50 w-72 bg-white shadow-xl lg:shadow-none flex flex-col"
          >
            {/* Sidebar Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div>
                <h1 className="text-xl font-bold text-gray-900">DocTalk AI</h1>
                <p className="text-sm text-gray-600">Medical Practice Management</p>
              </div>
              <button
                onClick={() => setIsSidebarOpen(false)}
                className="lg:hidden p-2 rounded-lg hover:bg-gray-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-4 py-6 space-y-2">
              {navigationItems.map((item) => (
                <motion.button
                  key={item.id}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => {
                    setActiveView(item.id);
                    setIsSidebarOpen(false);
                  }}
                  className={`w-full flex items-center space-x-3 px-4 py-3 text-left rounded-lg transition-colors ${
                    activeView === item.id
                      ? 'bg-blue-50 text-blue-700 border border-blue-200'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <item.icon className={`w-5 h-5 ${
                    activeView === item.id ? 'text-blue-600' : 'text-gray-500'
                  }`} />
                  <span className="font-medium">{item.label}</span>
                </motion.button>
              ))}
            </nav>

            {/* Sidebar Footer */}
            <div className="p-4 border-t border-gray-200">
              <div className="text-sm text-gray-500 text-center">
                <p>DocTalk AI v1.0.0</p>
                <p>Real-time Medical Assistant</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Overlay for mobile */}
      <AnimatePresence>
        {isSidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsSidebarOpen(false)}
            className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          />
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-h-0">
        {/* Top Bar */}
        <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg hover:bg-gray-100"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">{getCurrentTitle()}</h2>
              <p className="text-sm text-gray-600">Manage your medical practice efficiently</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="text-sm text-gray-500">
              {new Date().toLocaleDateString('en-US', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeView}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.2 }}
            >
              {renderActiveView()}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>

      {/* Toaster */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#fff',
            color: '#374151',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
            border: '1px solid #e5e7eb',
            borderRadius: '12px',
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </div>
  );
}

export default App; 