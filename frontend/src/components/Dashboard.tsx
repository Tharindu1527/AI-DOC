import React, { useState, useEffect } from 'react';
import { 
  Users, 
  UserCheck, 
  Calendar, 
  Activity,
  RefreshCw,
  Database,
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

  // Simple API call function - no retries, no complex logic
  const fetchData = async (url: string) => {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return response.json();
  };

  // Load data ONCE on component mount
  useEffect(() => {
    let isMounted = true;

    const loadData = async () => {
      try {
        console.log('Loading dashboard data...');
        
        const [patientsData, doctorsData, appointmentsData] = await Promise.all([
          fetchData('http://localhost:8000/api/patients/statistics'),
          fetchData('http://localhost:8000/api/doctors/statistics'),
          fetchData('http://localhost:8000/api/appointments/statistics')
        ]);

        if (isMounted) {
          setStatistics({
            patients: patientsData,
            doctors: doctorsData,
            appointments: appointmentsData
          });
          setLoading(false);
          console.log('Dashboard data loaded successfully');
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Failed to load data');
          setLoading(false);
          console.error('Dashboard load error:', err);
        }
      }
    };

    loadData();

    return () => {
      isMounted = false;
    };
  }, []); // Empty dependency array - run ONLY once

  const handleRefresh = () => {
    setLoading(true);
    setError(null);
    window.location.reload(); // Simple refresh
  };

  const handleCreateSample = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/admin/create-sample-data', {
        method: 'POST'
      });
      
      if (response.ok) {
        alert('Sample data created successfully!');
        window.location.reload();
      } else {
        alert('Failed to create sample data');
      }
    } catch (error) {
      alert('Error creating sample data');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p>Loading Dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-red-800 mb-2">Error Loading Dashboard</h3>
        <p className="text-red-600 mb-4">{error}</p>
        <button 
          onClick={handleRefresh}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!statistics) {
    return (
      <div className="text-center py-12">
        <Database className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-yellow-800 mb-2">No Data Available</h3>
        <button 
          onClick={handleCreateSample}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Create Sample Data
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8 p-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">DocTalk AI Dashboard</h1>
          <p className="text-gray-600">Medical practice management</p>
        </div>
        <div className="space-x-2">
          <button
            onClick={handleRefresh}
            className="px-3 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
          >
            <RefreshCw className="w-4 h-4 inline mr-2" />
            Refresh
          </button>
          <button
            onClick={handleCreateSample}
            className="px-3 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            <Database className="w-4 h-4 inline mr-2" />
            Sample Data
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-6 rounded-lg cursor-pointer hover:shadow-lg"
             onClick={() => onNavigate('patients')}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100">Total Patients</p>
              <h3 className="text-3xl font-bold">{statistics.patients.total_patients}</h3>
              <p className="text-blue-200 text-sm">+{statistics.patients.new_this_month} this month</p>
            </div>
            <Users className="w-12 h-12 text-blue-200" />
          </div>
        </div>

        <div className="bg-gradient-to-r from-green-500 to-green-600 text-white p-6 rounded-lg cursor-pointer hover:shadow-lg"
             onClick={() => onNavigate('doctors')}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100">Available Doctors</p>
              <h3 className="text-3xl font-bold">{statistics.doctors.available_doctors}</h3>
              <p className="text-green-200 text-sm">of {statistics.doctors.total_doctors} total</p>
            </div>
            <UserCheck className="w-12 h-12 text-green-200" />
          </div>
        </div>

        <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white p-6 rounded-lg cursor-pointer hover:shadow-lg"
             onClick={() => onNavigate('appointments')}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100">Today's Appointments</p>
              <h3 className="text-3xl font-bold">{statistics.appointments.today}</h3>
              <p className="text-purple-200 text-sm">{statistics.appointments.this_week} this week</p>
            </div>
            <Calendar className="w-12 h-12 text-purple-200" />
          </div>
        </div>

        <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white p-6 rounded-lg cursor-pointer hover:shadow-lg"
             onClick={() => onNavigate('voice')}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100">Monthly Appointments</p>
              <h3 className="text-3xl font-bold">{statistics.appointments.this_month}</h3>
              <p className="text-orange-200 text-sm">Voice available</p>
            </div>
            <Activity className="w-12 h-12 text-orange-200" />
          </div>
        </div>
      </div>

      {/* Quick Access */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Quick Access</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button 
            onClick={() => onNavigate('patients')}
            className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50"
          >
            <Users className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-700">Patients</p>
          </button>
          <button 
            onClick={() => onNavigate('doctors')}
            className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-green-500 hover:bg-green-50"
          >
            <UserCheck className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-700">Doctors</p>
          </button>
          <button 
            onClick={() => onNavigate('appointments')}
            className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-purple-500 hover:bg-purple-50"
          >
            <Calendar className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-700">Appointments</p>
          </button>
          <button 
            onClick={() => onNavigate('voice')}
            className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-orange-500 hover:bg-orange-50"
          >
            <Activity className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-700">Voice Chat</p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;