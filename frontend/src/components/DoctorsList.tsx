import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { 
  UserCheck, 
  Phone, 
  Mail, 
  MapPin, 
  Award,
  Edit,
  Trash2,
  Plus,
  Search,
  Filter,
  Star,
  Briefcase
} from 'lucide-react';

interface WorkingHours {
  day: string;
  start_time: string;
  end_time: string;
  is_available: boolean;
}

interface Doctor {
  id: string;
  doctor_id: string;
  first_name: string;
  last_name: string;
  title: string;
  specialty: string;
  department?: string;
  email?: string;
  phone?: string;
  office_location?: string;
  education?: string[];
  certifications?: string[];
  years_experience?: number;
  languages?: string[];
  bio?: string;
  consultation_fee?: number;
  working_hours?: WorkingHours[];
  is_available: boolean;
  is_active: boolean;
  rating?: number;
  total_reviews: number;
  created_at: string;
  updated_at: string;
}

interface DoctorsListProps {
  onDoctorSelect?: (doctor: Doctor) => void;
  onEdit?: (doctor: Doctor) => void;
  onCreateNew?: () => void;
}

const DoctorsList: React.FC<DoctorsListProps> = ({ 
  onDoctorSelect,
  onEdit,
  onCreateNew 
}) => {
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    specialty: '',
    department: '',
    min_experience: '',
    is_available: '',
    is_active: true
  });
  const [showFilters, setShowFilters] = useState(false);

  const fetchDoctors = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();
      if (searchQuery) params.append('q', searchQuery);
      if (filters.specialty) params.append('specialty', filters.specialty);
      if (filters.department) params.append('department', filters.department);
      if (filters.min_experience) params.append('min_experience', filters.min_experience);
      if (filters.is_available !== '') params.append('is_available', filters.is_available);
      if (filters.is_active !== undefined) params.append('is_active', filters.is_active.toString());

      const endpoint = searchQuery || Object.values(filters).some(f => f !== '' && f !== true) 
        ? `http://localhost:8000/api/doctors/search/?${params.toString()}`
        : 'http://localhost:8000/api/doctors/';

      const response = await fetch(endpoint);
      if (!response.ok) throw new Error('Failed to fetch doctors');
      
      const data = await response.json();
      setDoctors(data);
    } catch (err) {
      console.error('Error fetching doctors:', err);
      setError('Failed to load doctors');
    } finally {
      setLoading(false);
    }
  }, [searchQuery, filters]);

  useEffect(() => {
    fetchDoctors();
  }, [fetchDoctors]);

  const handleDeactivate = async (doctorId: string) => {
    if (!window.confirm('Are you sure you want to deactivate this doctor?')) return;

    try {
      const response = await fetch(`http://localhost:8000/api/doctors/${doctorId}`, {
        method: 'DELETE'
      });

      if (!response.ok) throw new Error('Failed to deactivate doctor');

      await fetchDoctors(); // Refresh list
    } catch (err) {
      console.error('Error deactivating doctor:', err);
      alert('Failed to deactivate doctor');
    }
  };

  const getAvailabilityStatus = (doctor: Doctor): string => {
    if (!doctor.is_active) return 'Inactive';
    if (!doctor.is_available) return 'Unavailable';
    
    const today = new Date().toLocaleString('en-US', { weekday: 'long' });
    const todaySchedule = doctor.working_hours?.find(
      wh => wh.day.toLowerCase() === today.toLowerCase()
    );
    
    if (todaySchedule && todaySchedule.is_available) {
      return `Available (${todaySchedule.start_time} - ${todaySchedule.end_time})`;
    }
    
    return 'Available';
  };

  const getStatusBadgeColor = (doctor: Doctor): string => {
    if (!doctor.is_active) return 'bg-gray-100 text-gray-800';
    if (!doctor.is_available) return 'bg-red-100 text-red-800';
    return 'bg-green-100 text-green-800';
  };

  const handleDoctorClick = (doctor: Doctor) => {
    onDoctorSelect?.(doctor);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-red-600 mb-2">Error: {error}</div>
          <button
            onClick={fetchDoctors}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Doctors</h1>
        {onCreateNew && (
          <button
            onClick={onCreateNew}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <Plus className="h-5 w-5 mr-2" />
            Add Doctor
          </button>
        )}
      </div>

      {/* Search and Filters */}
      <div className="bg-white p-4 rounded-lg shadow space-y-4">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search doctors..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            <Filter className="h-4 w-4 mr-2" />
            Filters
          </button>
        </div>

        {showFilters && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="grid grid-cols-1 md:grid-cols-5 gap-4 pt-4 border-t"
          >
            <input
              type="text"
              placeholder="Specialty"
              value={filters.specialty}
              onChange={(e) => setFilters({...filters, specialty: e.target.value})}
              className="px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="text"
              placeholder="Department"
              value={filters.department}
              onChange={(e) => setFilters({...filters, department: e.target.value})}
              className="px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="number"
              placeholder="Min Experience"
              value={filters.min_experience}
              onChange={(e) => setFilters({...filters, min_experience: e.target.value})}
              className="px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <select
              value={filters.is_available}
              onChange={(e) => setFilters({...filters, is_available: e.target.value})}
              className="px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Availability</option>
              <option value="true">Available</option>
              <option value="false">Unavailable</option>
            </select>
            <button
              onClick={() => setFilters({
                specialty: '',
                department: '',
                min_experience: '',
                is_available: '',
                is_active: true
              })}
              className="px-3 py-2 text-gray-600 hover:text-gray-900"
            >
              Clear Filters
            </button>
          </motion.div>
        )}
      </div>

      {/* Results Count */}
      <div className="text-sm text-gray-600">
        Showing {doctors.length} doctor{doctors.length !== 1 ? 's' : ''}
      </div>

      {/* Doctors Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {doctors.map((doctor) => (
          <motion.div
            key={doctor.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer"
            onClick={() => handleDoctorClick(doctor)}
          >
            <div className="p-6">
              {/* Header */}
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {doctor.title} {doctor.first_name} {doctor.last_name}
                  </h3>
                  <p className="text-sm text-gray-600">{doctor.doctor_id}</p>
                </div>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeColor(doctor)}`}>
                  {getAvailabilityStatus(doctor)}
                </span>
              </div>

              {/* Specialty and Department */}
              <div className="space-y-2 mb-4">
                <div className="flex items-center text-sm text-gray-600">
                  <Briefcase className="h-4 w-4 mr-2" />
                  <span className="font-medium">{doctor.specialty}</span>
                  {doctor.department && (
                    <>
                      <span className="mx-2">•</span>
                      <span>{doctor.department}</span>
                    </>
                  )}
                </div>
                {doctor.years_experience && (
                  <div className="flex items-center text-sm text-gray-600">
                    <Award className="h-4 w-4 mr-2" />
                    <span>{doctor.years_experience} years experience</span>
                  </div>
                )}
              </div>

              {/* Contact Info */}
              {(doctor.email || doctor.phone || doctor.office_location) && (
                <div className="space-y-1 mb-4 text-sm text-gray-600">
                  {doctor.email && (
                    <div className="flex items-center">
                      <Mail className="h-4 w-4 mr-2" />
                      <span>{doctor.email}</span>
                    </div>
                  )}
                  {doctor.phone && (
                    <div className="flex items-center">
                      <Phone className="h-4 w-4 mr-2" />
                      <span>{doctor.phone}</span>
                    </div>
                  )}
                  {doctor.office_location && (
                    <div className="flex items-center">
                      <MapPin className="h-4 w-4 mr-2" />
                      <span>{doctor.office_location}</span>
                    </div>
                  )}
                </div>
              )}

              {/* Rating and Consultation Fee */}
              <div className="flex justify-between items-center mb-4">
                {doctor.rating && (
                  <div className="flex items-center">
                    <Star className="h-4 w-4 text-yellow-400 mr-1" />
                    <span className="text-sm font-medium">{doctor.rating}</span>
                    <span className="text-sm text-gray-500 ml-1">({doctor.total_reviews})</span>
                  </div>
                )}
                {doctor.consultation_fee && (
                  <div className="text-lg font-semibold text-green-600">
                    ${doctor.consultation_fee}
                  </div>
                )}
              </div>

              {/* Languages */}
              {doctor.languages && doctor.languages.length > 0 && (
                <div className="mb-4">
                  <div className="flex flex-wrap gap-1">
                    {doctor.languages.map((language, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800"
                      >
                        {language}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Bio */}
              {doctor.bio && (
                <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                  {doctor.bio}
                </p>
              )}

              {/* Actions */}
              <div className="flex gap-2 pt-4 border-t">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDoctorClick(doctor);
                  }}
                  className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-blue-300 text-blue-700 rounded-md hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <UserCheck className="h-4 w-4 mr-2" />
                  View Details
                </button>
                {onEdit && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onEdit(doctor);
                    }}
                    className="inline-flex items-center px-3 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                )}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeactivate(doctor.id);
                  }}
                  className="inline-flex items-center px-3 py-2 border border-red-300 text-red-700 rounded-md hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-500"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Empty State */}
      {doctors.length === 0 && !loading && (
        <div className="text-center py-12">
          <UserCheck className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No doctors found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchQuery || Object.values(filters).some(f => f !== '' && f !== true)
              ? 'Try adjusting your search criteria.'
              : 'Get started by adding a new doctor.'}
          </p>
          {onCreateNew && (
            <div className="mt-6">
              <button
                onClick={onCreateNew}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <Plus className="h-5 w-5 mr-2" />
                Add First Doctor
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DoctorsList;
