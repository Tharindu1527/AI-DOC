import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { 
  User, 
  Phone, 
  Mail, 
  MapPin, 
  Calendar,
  Edit,
  Trash2,
  Plus,
  Search,
  Filter,
  Users
} from 'lucide-react';

interface Patient {
  id: string;
  patient_id: string;
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  date_of_birth?: string;
  gender?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  medical_history?: string[];
  allergies?: string[];
  medications?: string[];
  insurance_provider?: string;
  insurance_id?: string;
  notes?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface PatientsListProps {
  onPatientSelect?: (patient: Patient) => void;
  onEdit?: (patient: Patient) => void;
  onCreateNew?: () => void;
}

const PatientsList: React.FC<PatientsListProps> = ({ 
  onPatientSelect,
  onEdit,
  onCreateNew 
}) => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    gender: '',
    city: '',
    age_from: '',
    age_to: '',
    is_active: true
  });
  const [showFilters, setShowFilters] = useState(false);

  const fetchPatients = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();
      if (searchQuery) params.append('q', searchQuery);
      if (filters.gender) params.append('gender', filters.gender);
      if (filters.city) params.append('city', filters.city);
      if (filters.age_from) params.append('age_from', filters.age_from);
      if (filters.age_to) params.append('age_to', filters.age_to);
      if (filters.is_active !== undefined) params.append('is_active', filters.is_active.toString());

      const endpoint = searchQuery || Object.values(filters).some(f => f !== '' && f !== true) 
        ? `http://localhost:8000/api/patients/search/?${params.toString()}`
        : 'http://localhost:8000/api/patients/';

      const response = await fetch(endpoint);
      if (!response.ok) throw new Error('Failed to fetch patients');
      
      const data = await response.json();
      setPatients(data);
    } catch (err) {
      console.error('Error fetching patients:', err);
      setError('Failed to load patients');
    } finally {
      setLoading(false);
    }
  }, [searchQuery, filters]);

  useEffect(() => {
    fetchPatients();
  }, [fetchPatients]);

  const calculateAge = (dateOfBirth: string): number | null => {
    if (!dateOfBirth) return null;
    const today = new Date();
    const birth = new Date(dateOfBirth);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return age;
  };

  const handleDeactivate = async (patientId: string) => {
    if (!window.confirm('Are you sure you want to deactivate this patient?')) return;

    try {
      const response = await fetch(`/api/patients/${patientId}`, {
        method: 'DELETE'
      });

      if (!response.ok) throw new Error('Failed to deactivate patient');

      await fetchPatients(); // Refresh list
    } catch (err) {
      console.error('Error deactivating patient:', err);
      alert('Failed to deactivate patient');
    }
  };

  const PatientCard: React.FC<{ patient: Patient }> = ({ patient }) => {
    const age = patient.date_of_birth ? calculateAge(patient.date_of_birth) : null;
    
    return (
      <motion.div
        layout
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="card hover:shadow-lg transition-shadow cursor-pointer"
        onClick={() => {
          onPatientSelect?.(patient);
        }}
      >
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center space-x-3">
            <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-3 rounded-full">
              <User className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                {patient.first_name} {patient.last_name}
              </h3>
              <p className="text-sm text-gray-500">ID: {patient.patient_id}</p>
            </div>
          </div>
          
          <div className="flex space-x-2">
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={(e) => {
                e.stopPropagation();
                onEdit?.(patient);
              }}
              className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
            >
              <Edit className="w-4 h-4" />
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={(e) => {
                e.stopPropagation();
                handleDeactivate(patient.id);
              }}
              className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
            >
              <Trash2 className="w-4 h-4" />
            </motion.button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
          {patient.phone && (
            <div className="flex items-center space-x-2 text-gray-600">
              <Phone className="w-4 h-4" />
              <span>{patient.phone}</span>
            </div>
          )}
          {patient.email && (
            <div className="flex items-center space-x-2 text-gray-600">
              <Mail className="w-4 h-4" />
              <span>{patient.email}</span>
            </div>
          )}
          {age && (
            <div className="flex items-center space-x-2 text-gray-600">
              <Calendar className="w-4 h-4" />
              <span>{age} years old</span>
            </div>
          )}
          {patient.gender && (
            <div className="flex items-center space-x-2 text-gray-600">
              <User className="w-4 h-4" />
              <span className="capitalize">{patient.gender}</span>
            </div>
          )}
          {patient.city && (
            <div className="flex items-center space-x-2 text-gray-600">
              <MapPin className="w-4 h-4" />
              <span>{patient.city}, {patient.state}</span>
            </div>
          )}
        </div>

        {((patient.allergies && patient.allergies.length > 0) || (patient.medications && patient.medications.length > 0)) && (
          <div className="mt-3 pt-3 border-t border-gray-100">
            {patient.allergies && patient.allergies.length > 0 && (
              <div className="mb-2">
                <span className="text-xs font-medium text-red-600">Allergies:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {patient.allergies.slice(0, 3).map((allergy, index) => (
                    <span key={index} className="bg-red-50 text-red-700 text-xs px-2 py-1 rounded">
                      {allergy}
                    </span>
                  ))}
                  {patient.allergies.length > 3 && (
                    <span className="text-xs text-gray-500">+{patient.allergies.length - 3} more</span>
                  )}
                </div>
              </div>
            )}
            {patient.medications && patient.medications.length > 0 && (
              <div>
                <span className="text-xs font-medium text-blue-600">Medications:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {patient.medications.slice(0, 2).map((med, index) => (
                    <span key={index} className="bg-blue-50 text-blue-700 text-xs px-2 py-1 rounded">
                      {med}
                    </span>
                  ))}
                  {patient.medications.length > 2 && (
                    <span className="text-xs text-gray-500">+{patient.medications.length - 2} more</span>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </motion.div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex items-center space-x-3">
          <div className="bg-blue-100 p-2 rounded-lg">
            <Users className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Patients</h1>
            <p className="text-gray-600">{patients.length} patients found</p>
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
            <span>New Patient</span>
          </motion.button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search patients by name, email, phone, or ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Gender</label>
                <select
                  value={filters.gender}
                  onChange={(e) => setFilters({...filters, gender: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                >
                  <option value="">All</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                <input
                  type="text"
                  value={filters.city}
                  onChange={(e) => setFilters({...filters, city: e.target.value})}
                  placeholder="Enter city"
                  className="w-full p-2 border border-gray-300 rounded-lg"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Min Age</label>
                <input
                  type="number"
                  value={filters.age_from}
                  onChange={(e) => setFilters({...filters, age_from: e.target.value})}
                  placeholder="0"
                  className="w-full p-2 border border-gray-300 rounded-lg"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Max Age</label>
                <input
                  type="number"
                  value={filters.age_to}
                  onChange={(e) => setFilters({...filters, age_to: e.target.value})}
                  placeholder="120"
                  className="w-full p-2 border border-gray-300 rounded-lg"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  value={filters.is_active.toString()}
                  onChange={(e) => setFilters({...filters, is_active: e.target.value === 'true'})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                >
                  <option value="true">Active Only</option>
                  <option value="false">Inactive Only</option>
                </select>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Error State */}
      {error && (
        <div className="text-center py-12">
          <p className="text-red-600 mb-4">{error}</p>
          <button onClick={fetchPatients} className="btn-primary">
            Retry
          </button>
        </div>
      )}

      {/* Results */}
      {!loading && !error && (
        <>
          {patients.length === 0 ? (
            <div className="text-center py-12">
              <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No patients found</h3>
              <p className="text-gray-600 mb-4">Try adjusting your search or filters</p>
              <button onClick={onCreateNew} className="btn-primary">
                Create New Patient
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {patients.map((patient) => (
                <PatientCard key={patient.id} patient={patient} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default PatientsList;
