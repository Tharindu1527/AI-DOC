from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId
from models.appointment import Appointment, AppointmentCreate, AppointmentUpdate, AppointmentResponse
from database.mongodb import get_database
import logging
import re

logger = logging.getLogger(__name__)

class AppointmentService:
    def __init__(self):
        self.collection_name = "appointments"
        self.available_doctors = [
            "Dr. Smith", "Dr. Johnson", "Dr. Williams", "Dr. Brown", 
            "Dr. Davis", "Dr. Miller", "Dr. Wilson", "Dr. Moore"
        ]
        self.business_hours = {
            "start": 9,  # 9 AM
            "end": 17,   # 5 PM
            "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
        }

    async def create_appointment(self, appointment_data: AppointmentCreate) -> AppointmentResponse:
        """Create a new appointment"""
        try:
            db = get_database()
            appointment = Appointment(**appointment_data.dict())
            result = await db[self.collection_name].insert_one(appointment.dict(by_alias=True))
            
            created_appointment = await db[self.collection_name].find_one({"_id": result.inserted_id})
            return AppointmentResponse(
                id=str(created_appointment["_id"]),
                **{k: v for k, v in created_appointment.items() if k != "_id"}
            )
        except Exception as e:
            logger.error(f"Error creating appointment: {e}")
            raise

    async def get_appointment(self, appointment_id: str) -> Optional[AppointmentResponse]:
        """Get appointment by ID"""
        try:
            db = get_database()
            appointment = await db[self.collection_name].find_one({"_id": ObjectId(appointment_id)})
            
            if appointment:
                return AppointmentResponse(
                    id=str(appointment["_id"]),
                    **{k: v for k, v in appointment.items() if k != "_id"}
                )
            return None
        except Exception as e:
            logger.error(f"Error getting appointment: {e}")
            raise

    async def get_appointments_by_patient(self, patient_id: str) -> List[AppointmentResponse]:
        """Get all appointments for a patient"""
        try:
            db = get_database()
            cursor = db[self.collection_name].find({"patient_id": patient_id})
            appointments = await cursor.to_list(length=None)
            
            return [
                AppointmentResponse(
                    id=str(appointment["_id"]),
                    **{k: v for k, v in appointment.items() if k != "_id"}
                )
                for appointment in appointments
            ]
        except Exception as e:
            logger.error(f"Error getting patient appointments: {e}")
            raise

    async def get_appointments_by_doctor(self, doctor_name: str, date: Optional[datetime] = None) -> List[AppointmentResponse]:
        """Get appointments for a doctor, optionally filtered by date"""
        try:
            db = get_database()
            query = {"doctor_name": doctor_name}
            
            if date:
                start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_of_day = start_of_day + timedelta(days=1)
                query["appointment_date"] = {
                    "$gte": start_of_day,
                    "$lt": end_of_day
                }
            
            cursor = db[self.collection_name].find(query)
            appointments = await cursor.to_list(length=None)
            
            return [
                AppointmentResponse(
                    id=str(appointment["_id"]),
                    **{k: v for k, v in appointment.items() if k != "_id"}
                )
                for appointment in appointments
            ]
        except Exception as e:
            logger.error(f"Error getting doctor appointments: {e}")
            raise

    async def update_appointment(self, appointment_id: str, update_data: AppointmentUpdate) -> Optional[AppointmentResponse]:
        """Update an appointment"""
        try:
            db = get_database()
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            update_dict["updated_at"] = datetime.utcnow()
            
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(appointment_id)},
                {"$set": update_dict}
            )
            
            if result.modified_count:
                updated_appointment = await db[self.collection_name].find_one({"_id": ObjectId(appointment_id)})
                return AppointmentResponse(
                    id=str(updated_appointment["_id"]),
                    **{k: v for k, v in updated_appointment.items() if k != "_id"}
                )
            return None
        except Exception as e:
            logger.error(f"Error updating appointment: {e}")
            raise

    async def cancel_appointment(self, appointment_id: str) -> bool:
        """Cancel an appointment"""
        try:
            update_data = AppointmentUpdate(status="cancelled")
            result = await self.update_appointment(appointment_id, update_data)
            return result is not None
        except Exception as e:
            logger.error(f"Error cancelling appointment: {e}")
            raise

    async def get_available_slots(self, doctor_name: str, date: datetime) -> List[datetime]:
        """Get available time slots for a doctor on a specific date"""
        try:
            # Get existing appointments for the doctor on the date
            existing_appointments = await self.get_appointments_by_doctor(doctor_name, date)
            
            # Generate all possible slots (9 AM to 5 PM, 30-minute intervals)
            start_time = date.replace(hour=9, minute=0, second=0, microsecond=0)
            end_time = date.replace(hour=17, minute=0, second=0, microsecond=0)
            
            all_slots = []
            current_time = start_time
            while current_time < end_time:
                all_slots.append(current_time)
                current_time += timedelta(minutes=30)
            
            # Remove booked slots
            booked_slots = [apt.appointment_date for apt in existing_appointments if apt.status != "cancelled"]
            available_slots = [slot for slot in all_slots if slot not in booked_slots]
            
            return available_slots
        except Exception as e:
            logger.error(f"Error getting available slots: {e}")
            raise

    async def create_appointment_from_voice(self, entities: Dict[str, Any], intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create appointment from voice chat entities"""
        try:
            # Validate required fields
            required_fields = ['patient_name', 'date', 'time']
            missing_fields = [field for field in required_fields if not entities.get(field)]
            
            if missing_fields:
                return {
                    'success': False,
                    'message': f"Missing required information: {', '.join(missing_fields)}",
                    'missing_fields': missing_fields
                }
            
            # Parse and validate date/time
            try:
                appointment_datetime = datetime.strptime(
                    f"{entities['date']} {entities['time']}", 
                    "%Y-%m-%d %H:%M"
                )
            except ValueError as e:
                return {
                    'success': False,
                    'message': 'Invalid date or time format',
                    'error': str(e)
                }
            
            # Check if slot is available
            if not await self._is_slot_available(appointment_datetime, entities.get('doctor')):
                available_slots = await self.get_available_slots(appointment_datetime.date())
                return {
                    'success': False,
                    'message': 'The requested time slot is not available',
                    'available_slots': [slot.strftime('%H:%M') for slot in available_slots[:5]]
                }
            
            # Create appointment
            appointment_data = AppointmentCreate(
                patient_name=entities['patient_name'],
                patient_phone=entities.get('phone', ''),
                patient_email=entities.get('email', ''),
                appointment_date=appointment_datetime,
                doctor_name=entities.get('doctor', 'Dr. Smith'),
                reason=entities.get('reason', 'General consultation'),
                status='confirmed'
            )
            
            appointment = await self.create_appointment(appointment_data)
            
            return {
                'success': True,
                'appointment': appointment,
                'message': f"Appointment booked successfully for {appointment_datetime.strftime('%B %d, %Y at %I:%M %p')}"
            }
            
        except Exception as e:
            logger.error(f"Error creating appointment from voice: {e}")
            return {
                'success': False,
                'message': 'Failed to create appointment',
                'error': str(e)
            }

    async def _is_slot_available(self, datetime_slot: datetime, doctor_name: str = None) -> bool:
        """Check if a specific slot is available"""
        try:
            db = get_database()
            
            # Build query
            query = {
                "appointment_date": datetime_slot,
                "status": {"$nin": ["cancelled"]}
            }
            
            if doctor_name:
                query["doctor_name"] = doctor_name
            
            existing = await db[self.collection_name].find_one(query)
            return existing is None
            
        except Exception as e:
            logger.error(f"Error checking slot availability: {e}")
            return False

    async def search_appointments(self, query: str = "", filters: Dict[str, Any] = None) -> List[AppointmentResponse]:
        """Search appointments with text query and filters"""
        try:
            db = get_database()
            
            # Build MongoDB query
            mongo_query = {}
            
            # Text search
            if query:
                mongo_query["$or"] = [
                    {"patient_name": {"$regex": query, "$options": "i"}},
                    {"doctor_name": {"$regex": query, "$options": "i"}},
                    {"reason": {"$regex": query, "$options": "i"}}
                ]
            
            # Apply filters
            if filters:
                if filters.get('status'):
                    mongo_query['status'] = filters['status']
                if filters.get('doctor'):
                    mongo_query['doctor_name'] = filters['doctor']
                if filters.get('date_from'):
                    mongo_query['appointment_date'] = {"$gte": filters['date_from']}
                if filters.get('date_to'):
                    if 'appointment_date' not in mongo_query:
                        mongo_query['appointment_date'] = {}
                    mongo_query['appointment_date']['$lte'] = filters['date_to']
            
            cursor = db[self.collection_name].find(mongo_query).sort("appointment_date", 1)
            appointments = await cursor.to_list(length=100)  # Limit to 100 results
            
            return [
                AppointmentResponse(
                    id=str(appointment["_id"]),
                    **{k: v for k, v in appointment.items() if k != "_id"}
                )
                for appointment in appointments
            ]
            
        except Exception as e:
            logger.error(f"Error searching appointments: {e}")
            return []

    async def get_appointment_statistics(self) -> Dict[str, Any]:
        """Get appointment statistics for dashboard"""
        try:
            db = get_database()
            
            # Get current date range
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            week_start = today - timedelta(days=today.weekday())
            month_start = today.replace(day=1)
            
            # Run aggregation pipelines
            stats = {}
            
            # Today's appointments
            stats['today'] = await db[self.collection_name].count_documents({
                "appointment_date": {"$gte": today, "$lt": tomorrow},
                "status": {"$nin": ["cancelled"]}
            })
            
            # This week's appointments
            stats['this_week'] = await db[self.collection_name].count_documents({
                "appointment_date": {"$gte": week_start},
                "status": {"$nin": ["cancelled"]}
            })
            
            # This month's appointments
            stats['this_month'] = await db[self.collection_name].count_documents({
                "appointment_date": {"$gte": month_start},
                "status": {"$nin": ["cancelled"]}
            })
            
            # Status distribution
            status_pipeline = [
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            status_results = await db[self.collection_name].aggregate(status_pipeline).to_list(length=None)
            stats['by_status'] = {item['_id']: item['count'] for item in status_results}
            
            # Doctor distribution
            doctor_pipeline = [
                {"$group": {"_id": "$doctor_name", "count": {"$sum": 1}}}
            ]
            doctor_results = await db[self.collection_name].aggregate(doctor_pipeline).to_list(length=None)
            stats['by_doctor'] = {item['_id']: item['count'] for item in doctor_results}
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting appointment statistics: {e}")
            return {}

    def validate_appointment_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate appointment data from voice input"""
        errors = []
        suggestions = []
        
        # Validate patient name
        if not data.get('patient_name') or len(data['patient_name'].strip()) < 2:
            errors.append("Patient name is required")
            suggestions.append("Please provide the patient's full name")
        
        # Validate date
        if data.get('date'):
            try:
                apt_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
                if apt_date < datetime.now().date():
                    errors.append("Appointment date cannot be in the past")
                    suggestions.append("Please choose a future date")
                elif apt_date.strftime('%A').lower() not in self.business_hours['days']:
                    errors.append("Appointments are only available on weekdays")
                    suggestions.append("Please choose Monday through Friday")
            except ValueError:
                errors.append("Invalid date format")
                suggestions.append("Please use format YYYY-MM-DD")
        else:
            errors.append("Appointment date is required")
            suggestions.append("Please specify when you'd like the appointment")
        
        # Validate time
        if data.get('time'):
            try:
                apt_time = datetime.strptime(data['time'], '%H:%M').time()
                if apt_time.hour < self.business_hours['start'] or apt_time.hour >= self.business_hours['end']:
                    errors.append(f"Appointments are only available from {self.business_hours['start']}:00 AM to {self.business_hours['end']}:00 PM")
                    suggestions.append(f"Please choose a time between {self.business_hours['start']}:00 AM and {self.business_hours['end']-1}:30 PM")
            except ValueError:
                errors.append("Invalid time format")
                suggestions.append("Please use format HH:MM (24-hour)")
        else:
            errors.append("Appointment time is required")
            suggestions.append("Please specify what time you prefer")
        
        # Validate doctor
        if data.get('doctor') and data['doctor'] not in self.available_doctors:
            errors.append("Doctor not available")
            suggestions.append(f"Available doctors: {', '.join(self.available_doctors)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'suggestions': suggestions
        }

appointment_service = AppointmentService()