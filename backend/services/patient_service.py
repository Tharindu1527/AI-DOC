from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId
from models.patient import Patient, PatientCreate, PatientUpdate, PatientResponse
from database.mongodb import get_database
import logging
import re
import uuid

logger = logging.getLogger(__name__)

class PatientService:
    def __init__(self):
        self.collection_name = "patients"

    async def create_patient(self, patient_data: PatientCreate) -> PatientResponse:
        """Create a new patient"""
        try:
            db = get_database()
            
            # Generate unique patient ID
            patient_id = f"P{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
            
            # Create patient with generated ID
            patient_dict = patient_data.dict()
            patient_dict['patient_id'] = patient_id
            patient = Patient(**patient_dict)
            
            result = await db[self.collection_name].insert_one(patient.dict(by_alias=True))
            
            created_patient = await db[self.collection_name].find_one({"_id": result.inserted_id})
            return PatientResponse(
                id=str(created_patient["_id"]),
                **{k: v for k, v in created_patient.items() if k != "_id"}
            )
        except Exception as e:
            logger.error(f"Error creating patient: {e}")
            raise

    async def get_patient(self, patient_id: str) -> Optional[PatientResponse]:
        """Get patient by ID or patient_id"""
        try:
            db = get_database()
            
            # Try to find by ObjectId first, then by patient_id
            query = {"patient_id": patient_id}
            if ObjectId.is_valid(patient_id):
                query = {"$or": [{"_id": ObjectId(patient_id)}, {"patient_id": patient_id}]}
            
            patient = await db[self.collection_name].find_one(query)
            
            if patient:
                return PatientResponse(
                    id=str(patient["_id"]),
                    **{k: v for k, v in patient.items() if k != "_id"}
                )
            return None
        except Exception as e:
            logger.error(f"Error getting patient: {e}")
            raise

    async def get_all_patients(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[PatientResponse]:
        """Get all patients with pagination"""
        try:
            db = get_database()
            
            query = {}
            if active_only:
                query["is_active"] = True
            
            cursor = db[self.collection_name].find(query).skip(skip).limit(limit).sort("last_name", 1)
            patients = await cursor.to_list(length=limit)
            
            return [
                PatientResponse(
                    id=str(patient["_id"]),
                    **{k: v for k, v in patient.items() if k != "_id"}
                )
                for patient in patients
            ]
        except Exception as e:
            logger.error(f"Error getting patients: {e}")
            raise

    async def update_patient(self, patient_id: str, update_data: PatientUpdate) -> Optional[PatientResponse]:
        """Update a patient"""
        try:
            db = get_database()
            
            # Build query
            query = {"patient_id": patient_id}
            if ObjectId.is_valid(patient_id):
                query = {"$or": [{"_id": ObjectId(patient_id)}, {"patient_id": patient_id}]}
            
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            update_dict["updated_at"] = datetime.utcnow()
            
            result = await db[self.collection_name].update_one(
                query,
                {"$set": update_dict}
            )
            
            if result.modified_count:
                updated_patient = await db[self.collection_name].find_one(query)
                return PatientResponse(
                    id=str(updated_patient["_id"]),
                    **{k: v for k, v in updated_patient.items() if k != "_id"}
                )
            return None
        except Exception as e:
            logger.error(f"Error updating patient: {e}")
            raise

    async def deactivate_patient(self, patient_id: str) -> bool:
        """Deactivate a patient (soft delete)"""
        try:
            db = get_database()
            
            query = {"patient_id": patient_id}
            if ObjectId.is_valid(patient_id):
                query = {"$or": [{"_id": ObjectId(patient_id)}, {"patient_id": patient_id}]}
            
            result = await db[self.collection_name].update_one(
                query,
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error deactivating patient: {e}")
            return False

    async def search_patients(self, query: str = "", filters: Dict[str, Any] = None) -> List[PatientResponse]:
        """Search patients with text query and filters"""
        try:
            db = get_database()
            
            # Build MongoDB query
            mongo_query = {}
            
            # Text search
            if query:
                mongo_query["$or"] = [
                    {"first_name": {"$regex": query, "$options": "i"}},
                    {"last_name": {"$regex": query, "$options": "i"}},
                    {"email": {"$regex": query, "$options": "i"}},
                    {"phone": {"$regex": query, "$options": "i"}},
                    {"patient_id": {"$regex": query, "$options": "i"}}
                ]
            
            # Apply filters
            if filters:
                if filters.get('is_active') is not None:
                    mongo_query['is_active'] = filters['is_active']
                if filters.get('gender'):
                    mongo_query['gender'] = filters['gender']
                if filters.get('city'):
                    mongo_query['city'] = {"$regex": filters['city'], "$options": "i"}
                if filters.get('age_from') or filters.get('age_to'):
                    current_year = datetime.now().year
                    if filters.get('age_from'):
                        max_birth_year = current_year - int(filters['age_from'])
                        mongo_query.setdefault('date_of_birth', {})['$lte'] = datetime(max_birth_year, 12, 31)
                    if filters.get('age_to'):
                        min_birth_year = current_year - int(filters['age_to'])
                        mongo_query.setdefault('date_of_birth', {})['$gte'] = datetime(min_birth_year, 1, 1)
            
            cursor = db[self.collection_name].find(mongo_query).sort("last_name", 1)
            patients = await cursor.to_list(length=100)  # Limit to 100 results
            
            return [
                PatientResponse(
                    id=str(patient["_id"]),
                    **{k: v for k, v in patient.items() if k != "_id"}
                )
                for patient in patients
            ]
            
        except Exception as e:
            logger.error(f"Error searching patients: {e}")
            return []

    async def get_patient_by_name_phone(self, name: str = None, phone: str = None) -> Optional[PatientResponse]:
        """Find patient by name or phone (used for voice appointments)"""
        try:
            db = get_database()
            
            query_conditions = []
            
            if name:
                # Split name and search for combinations
                name_parts = name.strip().split()
                if len(name_parts) >= 2:
                    first_name, last_name = name_parts[0], " ".join(name_parts[1:])
                    query_conditions.append({
                        "$and": [
                            {"first_name": {"$regex": first_name, "$options": "i"}},
                            {"last_name": {"$regex": last_name, "$options": "i"}}
                        ]
                    })
                else:
                    # Search in both first and last name
                    query_conditions.append({
                        "$or": [
                            {"first_name": {"$regex": name, "$options": "i"}},
                            {"last_name": {"$regex": name, "$options": "i"}}
                        ]
                    })
            
            if phone:
                # Clean phone number for search
                clean_phone = re.sub(r'[^\d]', '', phone)
                query_conditions.append({"phone": {"$regex": clean_phone, "$options": "i"}})
            
            if not query_conditions:
                return None
            
            query = {"$or": query_conditions} if len(query_conditions) > 1 else query_conditions[0]
            query["is_active"] = True  # Only active patients
            
            patient = await db[self.collection_name].find_one(query)
            
            if patient:
                return PatientResponse(
                    id=str(patient["_id"]),
                    **{k: v for k, v in patient.items() if k != "_id"}
                )
            return None
        except Exception as e:
            logger.error(f"Error finding patient by name/phone: {e}")
            return None

    async def get_patient_statistics(self) -> Dict[str, Any]:
        """Get patient statistics for dashboard"""
        try:
            db = get_database()
            
            stats = {}
            
            # Total patients
            stats['total_patients'] = await db[self.collection_name].count_documents({"is_active": True})
            
            # New patients this month
            current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            stats['new_this_month'] = await db[self.collection_name].count_documents({
                "created_at": {"$gte": current_month_start},
                "is_active": True
            })
            
            # Gender distribution
            gender_pipeline = [
                {"$match": {"is_active": True}},
                {"$group": {"_id": "$gender", "count": {"$sum": 1}}}
            ]
            gender_results = await db[self.collection_name].aggregate(gender_pipeline).to_list(length=None)
            stats['by_gender'] = {item['_id'] or 'Unknown': item['count'] for item in gender_results}
            
            # Age groups
            current_year = datetime.now().year
            age_pipeline = [
                {"$match": {"is_active": True, "date_of_birth": {"$exists": True}}},
                {
                    "$addFields": {
                        "age": {"$subtract": [current_year, {"$year": "$date_of_birth"}]}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "$switch": {
                                "branches": [
                                    {"case": {"$lt": ["$age", 18]}, "then": "Under 18"},
                                    {"case": {"$and": [{"$gte": ["$age", 18]}, {"$lt": ["$age", 35]}]}, "then": "18-34"},
                                    {"case": {"$and": [{"$gte": ["$age", 35]}, {"$lt": ["$age", 55]}]}, "then": "35-54"},
                                    {"case": {"$gte": ["$age", 55]}, "then": "55+"}
                                ],
                                "default": "Unknown"
                            }
                        },
                        "count": {"$sum": 1}
                    }
                }
            ]
            age_results = await db[self.collection_name].aggregate(age_pipeline).to_list(length=None)
            stats['by_age_group'] = {item['_id']: item['count'] for item in age_results}
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting patient statistics: {e}")
            return {}

# Create global instance
patient_service = PatientService()
