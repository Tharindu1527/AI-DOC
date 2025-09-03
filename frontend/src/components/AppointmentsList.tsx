import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Calendar, 
  Clock, 
  User, 
  Phone,
  Edit,
  Trash2,
  Plus,
  Search,
  Filter,
  CheckCircle,
  XCircle,
  AlertCircle,
  RefreshCw
} from 'lucide-react';
import { format, parseISO, isToday, isTomorrow, isPast } from 'date-fns';

interface Appointment {
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

interface AppointmentsListProps {
  onAppointmentSelect?: (appointment: Appointment) => void;
  onEdit?: (appointment: Appointment) => void;
  onCancel?: (appointment: Appointment) => void;
  onCreateNew?: () => void;
}

const AppointmentsList: React.FC<AppointmentsListProps> = ({ 
  onAppointmentSelect,
  onEdit,
  onCancel,
  onCreateNew 
}) => {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    status: '',
    doctor: '',
    date_from: '',
    date_to: '',
    include_cancelled: false
  });
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchAppointments();
  }, [searchQuery, filters]);

  const fetchAppointments = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();
      if (searchQuery) params.append('q', searchQuery);
      if (filters.status) params.append('status', filters.status);
      if (filters.doctor) params.append('doctor', filters.doctor);
      if (filters.date_from) params.append('date_from', filters.date_from);
      if (filters.date_to) params.append('date_to', filters.date_to);
      
      const endpoint = searchQuery || Object.values(filters).some(f => f !== '' && f !== false) 
        ? `/api/appointments/search/?${params.toString()}`
        : `/api/appointments/all/?include_cancelled=${filters.include_cancelled}`;

      const response = await fetch(endpoint);
      if (!response.ok) throw new Error('Failed to fetch appointments');

      const data = await response.json();
      setAppointments(data);
    } catch (err) {
      console.error('Error fetching appointments:', err);
      setError('Failed to load appointments');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (appointmentId: string) => {
    if (!window.confirm('Are you sure you want to cancel this appointment?')) return;

    try {
      const response = await fetch(`/api/appointments/${appointmentId}`, {
        method: 'DELETE'
      });

      if (!response.ok) throw new Error('Failed to cancel appointment');

      await fetchAppointments(); // Refresh list
    } catch (err) {
      console.error('Error cancelling appointment:', err);
      alert('Failed to cancel appointment');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'scheduled': return <Clock className="w-4 h-4" />;
      case 'completed': return <CheckCircle className="w-4 h-4" />;
      case 'cancelled': return <XCircle className="w-4 h-4" />;
      case 'rescheduled': return <RefreshCw className="w-4 h-4" />;
      default: return <AlertCircle className="w-4 h-4" />;
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'scheduled': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      case 'rescheduled': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDateLabel = (dateString: string): string => {
    const date = parseISO(dateString);
    if (isToday(date)) return 'Today';
    if (isTomorrow(date)) return 'Tomorrow';
    return format(date, 'MMM d, yyyy');
  };

  const getUrgencyIndicator = (appointment: Appointment): string => {
    const appointmentDate = parseISO(appointment.appointment_date);
    const now = new Date();
    const hoursUntil = (appointmentDate.getTime() - now.getTime()) / (1000 * 60 * 60);
    
    if (appointment.status === 'cancelled') return '';
    if (isPast(appointmentDate) && appointment.status === 'scheduled') return 'overdue';
    if (hoursUntil <= 2 && hoursUntil > 0) return 'urgent';
    if (hoursUntil <= 24 && hoursUntil > 2) return 'soon';
    return '';
  };

  const AppointmentCard: React.FC<{ appointment: Appointment }> = ({ appointment }) => {
    const urgency = getUrgencyIndicator(appointment);
    const appointmentDate = parseISO(appointment.appointment_date);
    
    return (
      <motion.div
        layout
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className={`card hover:shadow-lg transition-all cursor-pointer ${
          urgency === 'overdue' ? 'border-l-4 border-red-500' : 
          urgency === 'urgent' ? 'border-l-4 border-orange-500' :
          urgency === 'soon' ? 'border-l-4 border-yellow-500' : ''
        }`}
        onClick={() => {
          setSelectedAppointment(appointment);
          onAppointmentSelect?.(appointment);
        }}
      >
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center space-x-3">
            <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-3 rounded-full">
              <Calendar className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                {appointment.patient_name}
              </h3>
              <p className="text-sm text-gray-500">with {appointment.doctor_name}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(appointment.status)}`}>
              {getStatusIcon(appointment.status)}
              <span className="capitalize">{appointment.status}</span>
            </div>
            
            {urgency && (
              <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                urgency === 'overdue' ? 'bg-red-500 text-white' :
                urgency === 'urgent' ? 'bg-orange-500 text-white' :
                'bg-yellow-500 text-white'
              }`}>
                {urgency === 'overdue' ? 'OVERDUE' : urgency === 'urgent' ? 'URGENT' : 'SOON'}
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm mb-4">
          <div className="flex items-center space-x-2 text-gray-600">
            <Calendar className="w-4 h-4" />
            <span>{getDateLabel(appointment.appointment_date)}</span>
          </div>
          
          <div className="flex items-center space-x-2 text-gray-600">
            <Clock className="w-4 h-4" />
            <span>
              {format(appointmentDate, 'h:mm a')}
              {appointment.duration_minutes && ` (${appointment.duration_minutes} min)`}
            </span>
          </div>
          
          <div className="flex items-center space-x-2 text-gray-600">
            <User className="w-4 h-4" />
            <span>ID: {appointment.patient_id}</span>
          </div>
          
          {appointment.patient_phone && (
            <div className="flex items-center space-x-2 text-gray-600">
              <Phone className="w-4 h-4" />
              <span>{appointment.patient_phone}</span>
            </div>
          )}
        </div>

        {appointment.notes && (
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-700">{appointment.notes}</p>
          </div>
        )}

        {(onEdit || onCancel) && appointment.status !== 'completed' && appointment.status !== 'cancelled' && (
          <div className="flex space-x-2 pt-4 border-t border-gray-100">
            {onEdit && (
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={(e) => {
                  e.stopPropagation();
                  onEdit(appointment);
                }}
                className="flex-1 btn-secondary text-sm py-2 flex items-center justify-center space-x-2"
              >
                <Edit className="w-4 h-4" />
                <span>Reschedule</span>
              </motion.button>
            )}
            {onCancel && (
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={(e) => {
                  e.stopPropagation();
                  handleCancel(appointment.id);
                }}
                className="flex-1 bg-red-50 text-red-600 border border-red-200 font-semibold py-2 px-4 rounded-lg text-sm flex items-center justify-center space-x-2"
              >
                <Trash2 className="w-4 h-4" />
                <span>Cancel</span>
              </motion.button>
            )}
          </div>
        )}

        <div className="mt-3 pt-3 border-t border-gray-100 text-xs text-gray-500">
          <p>Created: {format(parseISO(appointment.created_at), 'MMM d, yyyy h:mm a')}</p>
        </div>
      </motion.div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex items-center space-x-3">
          <div className="bg-purple-100 p-2 rounded-lg">
            <Calendar className="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Appointments</h1>
            <p className="text-gray-600">{appointments.length} appointments found</p>
          </div>
        </div>
        
        <div className="flex space-x-3">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setShowFilters(!showFilters)}
            className="btn-secondary flex items-center space-x-2"
          >
            <Filter className="w-4 h-4" />
            <span>Filters</span>
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onCreateNew}
            className="btn-primary flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>New Appointment</span>
          </motion.button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search appointments by patient name or doctor..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>

        {showFilters && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="card bg-gray-50"
          >
            <h3 className="font-medium text-gray-900 mb-3">Filters</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  value={filters.status}
                  onChange={(e) => setFilters({...filters, status: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                >
                  <option value="">All</option>
                  <option value="scheduled">Scheduled</option>
                  <option value="completed">Completed</option>
                  <option value="cancelled">Cancelled</option>
                  <option value="rescheduled">Rescheduled</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Doctor</label>
                <input
                  type="text"
                  value={filters.doctor}
                  onChange={(e) => setFilters({...filters, doctor: e.target.value})}
                  placeholder="Doctor name"
                  className="w-full p-2 border border-gray-300 rounded-lg"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">From Date</label>
                <input
                  type="date"
                  value={filters.date_from}
                  onChange={(e) => setFilters({...filters, date_from: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">To Date</label>
                <input
                  type="date"
                  value={filters.date_to}
                  onChange={(e) => setFilters({...filters, date_to: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                />
              </div>
              
              <div>
                <label className="flex items-center space-x-2 text-sm font-medium text-gray-700">
                  <input
                    type="checkbox"
                    checked={filters.include_cancelled}
                    onChange={(e) => setFilters({...filters, include_cancelled: e.target.checked})}
                    className="rounded"
                  />
                  <span>Include Cancelled</span>
                </label>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Error State */}
      {error && (
        <div className="text-center py-12">
          <p className="text-red-600 mb-4">{error}</p>
          <button onClick={fetchAppointments} className="btn-primary">
            Retry
          </button>
        </div>
      )}

      {/* Results */}
      {!loading && !error && (
        <>
          {appointments.length === 0 ? (
            <div className="text-center py-12">
              <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No appointments found</h3>
              <p className="text-gray-600 mb-4">Try adjusting your search or filters</p>
              <button onClick={onCreateNew} className="btn-primary">
                Schedule New Appointment
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {appointments.map((appointment) => (
                <AppointmentCard key={appointment.id} appointment={appointment} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default AppointmentsList;
