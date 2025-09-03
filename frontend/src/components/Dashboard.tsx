import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Users, 
  UserCheck, 
  Calendar, 
  Activity,
  TrendingUp,
  BarChart3,
  PieChart,
  Search,
  Plus,
  Database,
  RefreshCw,
  XCircle
} from 'lucide-react';

interface Statistics {
  patients: {
    total_patients: number;
    new_this_month: number;
    by_gender: Record<string, number>;
    by_age_group: Record<string, number>;
  };
  doctors: {
    total_doctors: number;
    available_doctors: number;
    by_specialty: Record<string, number>;
    by_department: Record<string, number>;
    by_experience: Record<string, number>;
  };
  appointments: {
    today: number;
    this_week: number;
    this_month: number;
    by_status: Record<string, number>;
    by_doctor: Record<string, number>;
  };
}

interface DashboardProps {
  onNavigate: (section: string) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreatingSample, setIsCreatingSample] = useState(false);
  const [isClearingDb, setIsClearingDb] = useState(false);

  const fetchStatistics = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [patientsRes, doctorsRes, appointmentsRes] = await Promise.all([
        fetch('http://localhost:8000/api/patients/statistics'),
        fetch('http://localhost:8000/api/doctors/statistics'),
        fetch('http://localhost:8000/api/appointments/statistics')
      ]);

      if (!patientsRes.ok || !doctorsRes.ok || !appointmentsRes.ok) {
        throw new Error('Failed to fetch statistics');
      }

      const [patientsData, doctorsData, appointmentsData] = await Promise.all([
        patientsRes.json(),
        doctorsRes.json(),
        appointmentsRes.json()
      ]);

      setStatistics({
        patients: patientsData,
        doctors: doctorsData,
        appointments: appointmentsData
      });
    } catch (err) {
      console.error('Error fetching statistics:', err);
      setError('Failed to load dashboard statistics');
    } finally {
      setLoading(false);
    }
  };

  const createSampleData = async () => {
    try {
      setIsCreatingSample(true);
      const response = await fetch('http://localhost:8000/api/admin/create-sample-data', {
        method: 'POST',
      });
      const data = await response.json();
      if (response.ok) {
        alert('Sample data created successfully!');
        fetchStatistics(); // Refresh stats
      } else {
        alert(`Error: ${data.error || 'Failed to create sample data'}`);
      }
    } catch (error) {
      alert(`Error: ${error}`);
    } finally {
      setIsCreatingSample(false);
    }
  };

  const clearDatabase = async () => {
    if (!window.confirm('Are you sure you want to clear all database data? This cannot be undone.')) {
      return;
    }
    
    try {
      setIsClearingDb(true);
      const response = await fetch('http://localhost:8000/api/admin/clear-database', {
        method: 'POST',
      });
      const data = await response.json();
      if (response.ok) {
        alert('Database cleared successfully!');
        fetchStatistics(); // Refresh stats
      } else {
        alert(`Error: ${data.error || 'Failed to clear database'}`);
      }
    } catch (error) {
      alert(`Error: ${error}`);
    } finally {
      setIsClearingDb(false);
    }
  };

  useEffect(() => {
    fetchStatistics();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">{error}</p>
        <button 
          onClick={fetchStatistics}
          className="btn-primary"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!statistics) return null;

  const quickActions = [
    { icon: Plus, label: 'New Patient', action: () => onNavigate('patients-create'), color: 'bg-blue-500' },
    { icon: Plus, label: 'New Doctor', action: () => onNavigate('doctors-create'), color: 'bg-green-500' },
    { icon: Calendar, label: 'Schedule Appointment', action: () => onNavigate('appointments-create'), color: 'bg-purple-500' },
    { icon: Search, label: 'Search Records', action: () => onNavigate('search'), color: 'bg-orange-500' }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">DocTalk AI Dashboard</h1>
          <p className="text-gray-600 mt-2">Comprehensive medical practice management</p>
        </div>
        <div className="flex space-x-3">
          {/* Admin buttons */}
          <button
            onClick={fetchStatistics}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            <span className="hidden sm:block">Refresh</span>
          </button>
          <button
            onClick={createSampleData}
            disabled={isCreatingSample}
            className="flex items-center gap-2 px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50"
          >
            <Database className={`h-4 w-4 ${isCreatingSample ? 'animate-spin' : ''}`} />
            <span className="hidden sm:block">{isCreatingSample ? 'Creating...' : 'Sample Data'}</span>
          </button>
          <button
            onClick={clearDatabase}
            disabled={isClearingDb}
            className="flex items-center gap-2 px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors disabled:opacity-50"
          >
            <XCircle className={`h-4 w-4 ${isClearingDb ? 'animate-spin' : ''}`} />
            <span className="hidden sm:block">{isClearingDb ? 'Clearing...' : 'Clear DB'}</span>
          </button>
          
          {/* Quick action buttons */}
          {quickActions.map((action, index) => (
            <motion.button
              key={index}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={action.action}
              className={`${action.color} text-white px-4 py-2 rounded-lg flex items-center space-x-2 shadow-lg`}
            >
              <action.icon className="w-4 h-4" />
              <span className="hidden sm:block">{action.label}</span>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card bg-gradient-to-r from-blue-500 to-blue-600 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100">Total Patients</p>
              <h3 className="text-3xl font-bold">{statistics.patients.total_patients}</h3>
              <p className="text-blue-200 text-sm">+{statistics.patients.new_this_month} this month</p>
            </div>
            <Users className="w-12 h-12 text-blue-200" />
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card bg-gradient-to-r from-green-500 to-green-600 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100">Available Doctors</p>
              <h3 className="text-3xl font-bold">{statistics.doctors.available_doctors}</h3>
              <p className="text-green-200 text-sm">of {statistics.doctors.total_doctors} total</p>
            </div>
            <UserCheck className="w-12 h-12 text-green-200" />
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card bg-gradient-to-r from-purple-500 to-purple-600 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100">Today's Appointments</p>
              <h3 className="text-3xl font-bold">{statistics.appointments.today}</h3>
              <p className="text-purple-200 text-sm">{statistics.appointments.this_week} this week</p>
            </div>
            <Calendar className="w-12 h-12 text-purple-200" />
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card bg-gradient-to-r from-orange-500 to-orange-600 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100">Monthly Appointments</p>
              <h3 className="text-3xl font-bold">{statistics.appointments.this_month}</h3>
              <p className="text-orange-200 text-sm">Active bookings</p>
            </div>
            <Activity className="w-12 h-12 text-orange-200" />
          </div>
        </motion.div>
      </div>

      {/* Detailed Statistics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {/* Patient Demographics */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card"
        >
          <div className="flex items-center space-x-3 mb-4">
            <div className="bg-blue-100 p-2 rounded-lg">
              <PieChart className="w-5 h-5 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold">Patient Demographics</h3>
          </div>
          
          <div className="space-y-3">
            <div>
              <h4 className="font-medium text-gray-700 mb-2">By Gender</h4>
              {Object.entries(statistics.patients.by_gender).map(([gender, count]) => (
                <div key={gender} className="flex justify-between items-center py-1">
                  <span className="text-gray-600 capitalize">{gender}</span>
                  <span className="font-medium">{count}</span>
                </div>
              ))}
            </div>
            
            <div>
              <h4 className="font-medium text-gray-700 mb-2">By Age Group</h4>
              {Object.entries(statistics.patients.by_age_group).map(([age, count]) => (
                <div key={age} className="flex justify-between items-center py-1">
                  <span className="text-gray-600">{age}</span>
                  <span className="font-medium">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Doctor Specialties */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="card"
        >
          <div className="flex items-center space-x-3 mb-4">
            <div className="bg-green-100 p-2 rounded-lg">
              <BarChart3 className="w-5 h-5 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold">Doctor Specialties</h3>
          </div>
          
          <div className="space-y-3">
            {Object.entries(statistics.doctors.by_specialty).map(([specialty, count]) => (
              <div key={specialty} className="flex justify-between items-center py-2 border-b border-gray-100 last:border-b-0">
                <span className="text-gray-700">{specialty}</span>
                <span className="font-medium text-green-600">{count}</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Appointment Status */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="card"
        >
          <div className="flex items-center space-x-3 mb-4">
            <div className="bg-purple-100 p-2 rounded-lg">
              <TrendingUp className="w-5 h-5 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold">Appointment Status</h3>
          </div>
          
          <div className="space-y-3">
            {Object.entries(statistics.appointments.by_status).map(([status, count]) => {
              const getStatusColor = (status: string) => {
                switch (status) {
                  case 'scheduled': return 'bg-blue-500';
                  case 'completed': return 'bg-green-500';
                  case 'cancelled': return 'bg-red-500';
                  case 'rescheduled': return 'bg-yellow-500';
                  default: return 'bg-gray-500';
                }
              };
              
              return (
                <div key={status} className="flex justify-between items-center py-2">
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${getStatusColor(status)}`}></div>
                    <span className="text-gray-700 capitalize">{status}</span>
                  </div>
                  <span className="font-medium">{count}</span>
                </div>
              );
            })}
          </div>
        </motion.div>
      </div>

      {/* Quick Access Buttons */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
        className="card"
      >
        <h3 className="text-lg font-semibold mb-4">Quick Access</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button 
            onClick={() => onNavigate('patients')}
            className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
          >
            <Users className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-700">All Patients</p>
          </button>
          <button 
            onClick={() => onNavigate('doctors')}
            className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-green-500 hover:bg-green-50 transition-colors"
          >
            <UserCheck className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-700">All Doctors</p>
          </button>
          <button 
            onClick={() => onNavigate('appointments')}
            className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-colors"
          >
            <Calendar className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-700">All Appointments</p>
          </button>
          <button 
            onClick={() => onNavigate('voice')}
            className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-orange-500 hover:bg-orange-50 transition-colors"
          >
            <Activity className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-700">Voice Chat</p>
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default Dashboard;
