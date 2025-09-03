from datetime import datetime, time
from typing import List, Optional, Dict, Any
from bson import ObjectId
from models.doctor import Doctor, DoctorCreate, DoctorUpdate, DoctorResponse, WorkingHours
from database.mongodb import get_database
import logging
import uuid

logger = logging.getLogger(__name__)

class DoctorService:
    def __init__(self):
        self.collection_name = "doctors"

    async def create_doctor(self, doctor_data: DoctorCreate) -> DoctorResponse:
        """Create a new doctor"""
        try:
            db = get_database()
            
            # Generate unique doctor ID
            doctor_id = f"D{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
            
            # Create doctor with generated ID
            doctor_dict = doctor_data.dict()
            doctor_dict['doctor_id'] = doctor_id
            
            # Set default working hours if not provided
            if not doctor_dict.get('working_hours'):
                doctor_dict['working_hours'] = [
                    {"day": "Monday", "start_time": time(9, 0), "end_time": time(17, 0), "is_available": True},
                    {"day": "Tuesday", "start_time": time(9, 0), "end_time": time(17, 0), "is_available": True},
                    {"day": "Wednesday", "start_time": time(9, 0), "end_time": time(17, 0), "is_available": True},
                    {"day": "Thursday", "start_time": time(9, 0), "end_time": time(17, 0), "is_available": True},
                    {"day": "Friday", "start_time": time(9, 0), "end_time": time(17, 0), "is_available": True},
                    {"day": "Saturday", "start_time": time(9, 0), "end_time": time(13, 0), "is_available": False},
                    {"day": "Sunday", "start_time": time(9, 0), "end_time": time(13, 0), "is_available": False}
                ]
            
            doctor = Doctor(**doctor_dict)
            result = await db[self.collection_name].insert_one(doctor.dict(by_alias=True))
            
            created_doctor = await db[self.collection_name].find_one({"_id": result.inserted_id})
            return DoctorResponse(
                id=str(created_doctor["_id"]),
                **{k: v for k, v in created_doctor.items() if k != "_id"}
            )
        except Exception as e:
            logger.error(f"Error creating doctor: {e}")
            raise

    async def get_doctor(self, doctor_id: str) -> Optional[DoctorResponse]:
        """Get doctor by ID or doctor_id"""
        try:
            db = get_database()
            
            # Try to find by ObjectId first, then by doctor_id
            query = {"doctor_id": doctor_id}
            if ObjectId.is_valid(doctor_id):
                query = {"$or": [{"_id": ObjectId(doctor_id)}, {"doctor_id": doctor_id}]}
            
            doctor = await db[self.collection_name].find_one(query)
            
            if doctor:
                return DoctorResponse(
                    id=str(doctor["_id"]),
                    **{k: v for k, v in doctor.items() if k != "_id"}
                )
            return None
        except Exception as e:
            logger.error(f"Error getting doctor: {e}")
            raise

    async def get_all_doctors(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[DoctorResponse]:
        """Get all doctors with pagination"""
        try:
            db = get_database()
            
            query = {}
            if active_only:
                query["is_active"] = True
            
            cursor = db[self.collection_name].find(query).skip(skip).limit(limit).sort("last_name", 1)
            doctors = await cursor.to_list(length=limit)
            
            return [
                DoctorResponse(
                    id=str(doctor["_id"]),
                    **{k: v for k, v in doctor.items() if k != "_id"}
                )
                for doctor in doctors
            ]
        except Exception as e:
            logger.error(f"Error getting doctors: {e}")
            raise

    async def get_available_doctors(self, specialty: str = None) -> List[DoctorResponse]:
        """Get available doctors, optionally filtered by specialty"""
        try:
            db = get_database()
            
            query = {"is_active": True, "is_available": True}
            if specialty:
                query["specialty"] = {"$regex": specialty, "$options": "i"}
            
            cursor = db[self.collection_name].find(query).sort("last_name", 1)
            doctors = await cursor.to_list(length=None)
            
            return [
                DoctorResponse(
                    id=str(doctor["_id"]),
                    **{k: v for k, v in doctor.items() if k != "_id"}
                )
                for doctor in doctors
            ]
        except Exception as e:
            logger.error(f"Error getting available doctors: {e}")
            raise

    async def update_doctor(self, doctor_id: str, update_data: DoctorUpdate) -> Optional[DoctorResponse]:
        """Update a doctor"""
        try:
            db = get_database()
            
            # Build query
            query = {"doctor_id": doctor_id}
            if ObjectId.is_valid(doctor_id):
                query = {"$or": [{"_id": ObjectId(doctor_id)}, {"doctor_id": doctor_id}]}
            
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            update_dict["updated_at"] = datetime.utcnow()
            
            result = await db[self.collection_name].update_one(
                query,
                {"$set": update_dict}
            )
            
            if result.modified_count:
                updated_doctor = await db[self.collection_name].find_one(query)
                return DoctorResponse(
                    id=str(updated_doctor["_id"]),
                    **{k: v for k, v in updated_doctor.items() if k != "_id"}
                )
            return None
        except Exception as e:
            logger.error(f"Error updating doctor: {e}")
            raise

    async def deactivate_doctor(self, doctor_id: str) -> bool:
        """Deactivate a doctor (soft delete)"""
        try:
            db = get_database()
            
            query = {"doctor_id": doctor_id}
            if ObjectId.is_valid(doctor_id):
                query = {"$or": [{"_id": ObjectId(doctor_id)}, {"doctor_id": doctor_id}]}
            
            result = await db[self.collection_name].update_one(
                query,
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error deactivating doctor: {e}")
            return False

    async def search_doctors(self, query: str = "", filters: Dict[str, Any] = None) -> List[DoctorResponse]:
        """Search doctors with text query and filters"""
        try:
            db = get_database()
            
            # Build MongoDB query
            mongo_query = {}
            
            # Text search
            if query:
                mongo_query["$or"] = [
                    {"first_name": {"$regex": query, "$options": "i"}},
                    {"last_name": {"$regex": query, "$options": "i"}},
                    {"specialty": {"$regex": query, "$options": "i"}},
                    {"department": {"$regex": query, "$options": "i"}},
                    {"doctor_id": {"$regex": query, "$options": "i"}}
                ]
            
            # Apply filters
            if filters:
                if filters.get('is_active') is not None:
                    mongo_query['is_active'] = filters['is_active']
                if filters.get('is_available') is not None:
                    mongo_query['is_available'] = filters['is_available']
                if filters.get('specialty'):
                    mongo_query['specialty'] = {"$regex": filters['specialty'], "$options": "i"}
                if filters.get('department'):
                    mongo_query['department'] = {"$regex": filters['department'], "$options": "i"}
                if filters.get('min_experience'):
                    mongo_query['years_experience'] = {"$gte": int(filters['min_experience'])}
            
            cursor = db[self.collection_name].find(mongo_query).sort("last_name", 1)
            doctors = await cursor.to_list(length=100)  # Limit to 100 results
            
            return [
                DoctorResponse(
                    id=str(doctor["_id"]),
                    **{k: v for k, v in doctor.items() if k != "_id"}
                )
                for doctor in doctors
            ]
            
        except Exception as e:
            logger.error(f"Error searching doctors: {e}")
            return []

    async def get_doctor_by_name(self, name: str) -> Optional[DoctorResponse]:
        """Find doctor by name (used for voice appointments)"""
        try:
            db = get_database()
            
            # Remove "Dr." prefix if present and clean name
            clean_name = name.replace("Dr.", "").replace("Doctor", "").strip()
            
            # Search for exact match first, then partial
            queries = [
                # Exact last name match
                {"last_name": {"$regex": f"^{clean_name}$", "$options": "i"}},
                # Partial last name match
                {"last_name": {"$regex": clean_name, "$options": "i"}},
                # Full name search
                {"$or": [
                    {"first_name": {"$regex": clean_name, "$options": "i"}},
                    {"last_name": {"$regex": clean_name, "$options": "i"}}
                ]}
            ]
            
            for query in queries:
                query["is_active"] = True
                query["is_available"] = True
                doctor = await db[self.collection_name].find_one(query)
                if doctor:
                    return DoctorResponse(
                        id=str(doctor["_id"]),
                        **{k: v for k, v in doctor.items() if k != "_id"}
                    )
            
            return None
        except Exception as e:
            logger.error(f"Error finding doctor by name: {e}")
            return None

    async def get_doctor_statistics(self) -> Dict[str, Any]:
        """Get doctor statistics for dashboard"""
        try:
            db = get_database()
            
            stats = {}
            
            # Total doctors
            stats['total_doctors'] = await db[self.collection_name].count_documents({"is_active": True})
            
            # Available doctors
            stats['available_doctors'] = await db[self.collection_name].count_documents({
                "is_active": True,
                "is_available": True
            })
            
            # Specialty distribution
            specialty_pipeline = [
                {"$match": {"is_active": True}},
                {"$group": {"_id": "$specialty", "count": {"$sum": 1}}}
            ]
            specialty_results = await db[self.collection_name].aggregate(specialty_pipeline).to_list(length=None)
            stats['by_specialty'] = {item['_id']: item['count'] for item in specialty_results}
            
            # Department distribution
            department_pipeline = [
                {"$match": {"is_active": True, "department": {"$ne": None}}},
                {"$group": {"_id": "$department", "count": {"$sum": 1}}}
            ]
            department_results = await db[self.collection_name].aggregate(department_pipeline).to_list(length=None)
            stats['by_department'] = {item['_id']: item['count'] for item in department_results}
            
            # Experience distribution
            experience_pipeline = [
                {"$match": {"is_active": True, "years_experience": {"$exists": True}}},
                {
                    "$group": {
                        "_id": {
                            "$switch": {
                                "branches": [
                                    {"case": {"$lt": ["$years_experience", 5]}, "then": "0-4 years"},
                                    {"case": {"$and": [{"$gte": ["$years_experience", 5]}, {"$lt": ["$years_experience", 10]}]}, "then": "5-9 years"},
                                    {"case": {"$and": [{"$gte": ["$years_experience", 10]}, {"$lt": ["$years_experience", 20]}]}, "then": "10-19 years"},
                                    {"case": {"$gte": ["$years_experience", 20]}, "then": "20+ years"}
                                ],
                                "default": "Unknown"
                            }
                        },
                        "count": {"$sum": 1}
                    }
                }
            ]
            experience_results = await db[self.collection_name].aggregate(experience_pipeline).to_list(length=None)
            stats['by_experience'] = {item['_id']: item['count'] for item in experience_results}
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting doctor statistics: {e}")
            return {}

# Create global instance
doctor_service = DoctorService()