import React from 'react';
import { motion } from 'framer-motion';
import { Calendar, Clock, User, Phone, MapPin } from 'lucide-react';
import { Appointment } from '../types';
import { format } from 'date-fns';

interface AppointmentCardProps {
  appointment: Appointment;
  onEdit?: (appointment: Appointment) => void;
  onCancel?: (appointment: Appointment) => void;
}

const AppointmentCard: React.FC<AppointmentCardProps> = ({
  appointment,
  onEdit,
  onCancel
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled': return 'bg-green-100 text-green-800';
      case 'completed': return 'bg-blue-100 text-blue-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      case 'rescheduled': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="card hover:shadow-lg transition-shadow duration-200"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-2 rounded-lg">
            <Calendar className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Dr. {appointment.doctor_name}
            </h3>
            <p className="text-sm text-gray-600">
              {format(new Date(appointment.appointment_date), 'EEEE, MMMM d, yyyy')}
            </p>
          </div>
        </div>
        
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(appointment.status)}`}>
          {appointment.status.charAt(0).toUpperCase() + appointment.status.slice(1)}
        </span>
      </div>

      <div className="space-y-3">
        <div className="flex items-center space-x-3 text-sm text-gray-600">
          <Clock className="w-4 h-4" />
          <span>
            {format(new Date(appointment.appointment_date), 'h:mm a')} 
            {appointment.duration_minutes && ` (${appointment.duration_minutes} minutes)`}
          </span>
        </div>

        <div className="flex items-center space-x-3 text-sm text-gray-600">
          <User className="w-4 h-4" />
          <span>{appointment.patient_name}</span>
        </div>

        {appointment.patient_phone && (
          <div className="flex items-center space-x-3 text-sm text-gray-600">
            <Phone className="w-4 h-4" />
            <span>{appointment.patient_phone}</span>
          </div>
        )}

        {appointment.notes && (
          <div className="mt-3 p-3 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-700">{appointment.notes}</p>
          </div>
        )}
      </div>

      {(onEdit || onCancel) && appointment.status !== 'completed' && appointment.status !== 'cancelled' && (
        <div className="flex space-x-2 mt-4 pt-4 border-t border-gray-100">
          {onEdit && (
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onEdit(appointment)}
              className="flex-1 btn-secondary text-sm py-2"
            >
              Reschedule
            </motion.button>
          )}
          {onCancel && (
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onCancel(appointment)}
              className="flex-1 bg-red-50 text-red-600 border border-red-200 font-semibold py-2 px-4 rounded-lg shadow-sm hover:shadow-md transform transition-all duration-200 hover:scale-105 active:scale-95 text-sm"
            >
              Cancel
            </motion.button>
          )}
        </div>
      )}
    </motion.div>
  );
};

export default AppointmentCard; 