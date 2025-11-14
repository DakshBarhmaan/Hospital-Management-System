import json
import os
import random
import string
from datetime import datetime, timedelta

# -------------------------------
# Data Storage Files
# -------------------------------
USERS_FILE = "users.json"
PATIENTS_FILE = "patients.json"
DOCTORS_FILE = "doctors.json"
APPOINTMENTS_FILE = "appointments.json"
STAFF_FILE = "staff.json"

# -------------------------------
# Utility Functions
# -------------------------------
def generate_patient_id():
    """Generate a unique patient ID"""
    return f"P{random.randint(10000, 99999)}"


def generate_password():
    """Generate a random password"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(8))


def ensure_file_exists(path, default_content):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default_content, f, indent=2)

# -------------------------------
# User Class and Authentication
# -------------------------------
class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role

    def to_dict(self):
        return {"username": self.username, "password": self.password, "role": self.role}

    @classmethod
    def from_dict(cls, data):
        return cls(data["username"], data["password"], data["role"])  


class AuthenticationSystem:
    def __init__(self):
        self.users = self.load_users()

    def load_users(self):
        if not os.path.exists(USERS_FILE):
            default_users = [User("admin1", "admin123", "admin"), User("admin2", "admin456", "admin")]
            self.save_users(default_users)
            return default_users
        try:
            with open(USERS_FILE, 'r') as file:
                users_data = json.load(file)
                return [User.from_dict(user_data) for user_data in users_data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_users(self, users=None):
        if users is None:
            users = self.users
        users_data = [user.to_dict() for user in users]
        with open(USERS_FILE, 'w') as file:
            json.dump(users_data, file, indent=2)

    def admin_login(self):
        print("\n" + "="*40)
        print("           ADMIN LOGIN")
        print("="*40)
        username = input("Enter admin username: ").strip()
        password = input("Enter admin password: ").strip()
        for user in self.users:
            if user.username == username and user.password == password and user.role == "admin":
                print("\n[SUCCESS] Login Successful! Welcome Admin!")
                return True
        print("\n[ERROR] Invalid admin credentials!")
        return False

    def patient_login(self, patient_id, password):
        for user in self.users:
            if user.username == patient_id and user.password == password and user.role == "patient":
                return True
        return False

    def register_patient(self, patient_id, password):
        new_user = User(patient_id, password, "patient")
        self.users.append(new_user)
        self.save_users()

# -------------------------------
# Patient Class and Management
# -------------------------------
class Patient:
    def __init__(self, patient_id, name, phone, email, password):
        self.patient_id = patient_id
        self.name = name
        self.phone = phone
        self.email = email
        self.password = password

    def to_dict(self):
        return {"patient_id": self.patient_id, "name": self.name, "phone": self.phone, "email": self.email, "password": self.password}

    @classmethod
    def from_dict(cls, data):
        return cls(data["patient_id"], data["name"], data["phone"], data["email"], data["password"]) 

    def __str__(self):
        return f"ID: {self.patient_id}, Name: {self.name}, Phone: {self.phone}, Email: {self.email}"


class PatientManagement:
    def __init__(self, auth_system):
        self.auth_system = auth_system
        self.patients = self.load_patients()

    def load_patients(self):
        if not os.path.exists(PATIENTS_FILE):
            return []
        try:
            with open(PATIENTS_FILE, 'r') as file:
                patients_data = json.load(file)
                return [Patient.from_dict(patient_data) for patient_data in patients_data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_patients(self):
        patients_data = [patient.to_dict() for patient in self.patients]
        with open(PATIENTS_FILE, 'w') as file:
            json.dump(patients_data, file, indent=2)

    def register_new_patient(self, name, phone, email):
        patient_id = generate_patient_id()
        password = generate_password()
        # ensure uniqueness
        while self.search_by_id(patient_id):
            patient_id = generate_patient_id()
        patient = Patient(patient_id, name, phone, email, password)
        self.patients.append(patient)
        self.save_patients()
        self.auth_system.register_patient(patient_id, password)
        return patient_id, password

    def search_by_id(self, patient_id):
        for patient in self.patients:
            if patient.patient_id == patient_id:
                return patient
        return None

    def verify_patient(self, patient_id, password):
        patient = self.search_by_id(patient_id)
        if patient and patient.password == password:
            return True
        return False

    def display_all_patients(self):
        if not self.patients:
            print("[WARNING] No patients found.")
            return
        print("\n" + "="*80)
        print("                           PATIENT LIST")
        print("="*80)
        for patient in self.patients:
            print(patient)


# -------------------------------
# Doctor Class and Management
# -------------------------------
class Doctor:
    def __init__(self, doctor_id, name, specialization, shift_start_hour=9, shift_hours=8):
        """
        doctor_id : int
        name : str
        specialization : str
        shift_start_hour : integer 0-23 e.g., 9 -> 9:00 AM
        shift_hours : number of hours (should be 8)
        """
        self.doctor_id = doctor_id
        self.name = name
        self.specialization = specialization
        self.shift_start_hour = shift_start_hour
        self.shift_hours = shift_hours

    def to_dict(self):
        return {
            "doctor_id": self.doctor_id,
            "name": self.name,
            "specialization": self.specialization,
            "shift_start_hour": self.shift_start_hour,
            "shift_hours": self.shift_hours
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["doctor_id"], data["name"], data["specialization"], data.get("shift_start_hour", 9), data.get("shift_hours", 8))

    def __str__(self):
        start = datetime(2000, 1, 1, self.shift_start_hour).strftime("%I:%M %p")
        end_hour = self.shift_start_hour + self.shift_hours
        end = datetime(2000, 1, 1, end_hour).strftime("%I:%M %p")
        return f"ID: {self.doctor_id}, Name: Dr. {self.name}, Specialization: {self.specialization}, Timings: {start} - {end}"

    def slot_times(self):
        """Return a list of time strings for each slot (1 hour slots)"""
        slots = []
        for i in range(self.shift_hours):
            h = self.shift_start_hour + i
            # format hh:MM (24 to 12 later)
            start = datetime(2000, 1, 1, h).strftime("%H:%M")
            end = datetime(2000, 1, 1, h+1).strftime("%H:%M")
            slots.append(f"{start}-{end}")
        return slots


class DoctorManagement:
    def __init__(self):
        self.doctors = self.load_doctors()
        self.next_id = self.get_next_id()

    def default_doctors_list(self):
        # Doctor list with 20 specializations and names
        doctors_data = [
            (1, "Dr. Rajesh Kumar", "Cardiology"),
            (2, "Dr. Priya Sharma", "General Physician"),
            (3, "Dr. Amit Patel", "Orthopedics"),
            (4, "Dr. Sunita Singh", "Pediatrics"),
            (5, "Dr. Vikram Reddy", "Dermatology"),
            (6, "Dr. Neha Gupta", "ENT Specialist"),
            (7, "Dr. Arun Verma", "Neurology"),
            (8, "Dr. Kavita Joshi", "Psychiatry"),
            (9, "Dr. Sanjay Rao", "Ophthalmology"),
            (10, "Dr. Anita Deshpande", "Gynecology"),
            (11, "Dr. Rahul Bhat", "Endocrinology"),
            (12, "Dr. Meera Iyer", "Gastroenterology"),
            (13, "Dr. Karan Malhotra", "Pulmonology"),
            (14, "Dr. Swati Kapoor", "Nephrology"),
            (15, "Dr. Rohit Sinha", "Urology"),
            (16, "Dr. Nisha Menon", "Oncology"),
            (17, "Dr. Vikram Chawla", "Rheumatology"),
            (18, "Dr. Pooja Jain", "Dermatology (Cosmetic)"),
            (19, "Dr. Aditya Nair", "Sports Medicine"),
            (20, "Dr. Deepa Kaur", "Dentistry")
        ]

        default = []
        for doc_id, name, specialization in doctors_data:
            default.append(
                Doctor(
                    doc_id,
                    name.replace("Dr. ", ""),   # removing Dr. because your __str__ adds it automatically
                    specialization,
                    shift_start_hour=9,
                    shift_hours=8
                )
            )
        return default


    def load_doctors(self):
        if not os.path.exists(DOCTORS_FILE):
            default_doctors = self.default_doctors_list()
            self.save_doctors_list(default_doctors)
            return default_doctors
        try:
            with open(DOCTORS_FILE, 'r') as file:
                doctors_data = json.load(file)
                return [Doctor.from_dict(doctor_data) for doctor_data in doctors_data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_doctors(self):
        self.save_doctors_list(self.doctors)

    def save_doctors_list(self, doctors):
        doctors_data = [doctor.to_dict() for doctor in doctors]
        with open(DOCTORS_FILE, 'w') as file:
            json.dump(doctors_data, file, indent=2)

    def get_next_id(self):
        if not self.doctors:
            return 1
        return max(doctor.doctor_id for doctor in self.doctors) + 1

    def add_doctor(self, name, specialization, shift_start_hour=9, shift_hours=8):
        doctor = Doctor(self.next_id, name, specialization, shift_start_hour, shift_hours)
        self.doctors.append(doctor)
        self.next_id += 1
        self.save_doctors()
        print(f"[SUCCESS] Doctor {name} added successfully with ID: {doctor.doctor_id}")

    def view_doctors(self):
        if not self.doctors:
            print("[WARNING] No doctors found.")
            return
        print("\n" + "="*80)
        print("                           DOCTOR LIST")
        print("="*80)
        for doctor in self.doctors:
            print(doctor)

    def search_by_id(self, doctor_id):
        for doctor in self.doctors:
            if doctor.doctor_id == doctor_id:
                return doctor
        return None

    def filter_by_condition(self, condition):
        condition_lower = condition.lower()
        condition_mapping = {
            "heart": "Cardiology", "cardiac": "Cardiology", "chest pain": "Cardiology",
            "fever": "General Physician", "cold": "General Physician", "cough": "General Physician", "flu": "General Physician",
            "bone": "Orthopedics", "fracture": "Orthopedics", "joint": "Orthopedics", "back pain": "Orthopedics",
            "child": "Pediatrics", "baby": "Pediatrics",
            "skin": "Dermatology", "rash": "Dermatology", "acne": "Dermatology",
            "ear": "ENT Specialist", "nose": "ENT Specialist", "throat": "ENT Specialist", "sinus": "ENT Specialist",
            "headache": "Neurology", "migraine": "Neurology", "brain": "Neurology", "nerve": "Neurology"
        }
        matched_specialization = None
        for keyword, specialization in condition_mapping.items():
            if keyword in condition_lower:
                matched_specialization = specialization
                break
        if not matched_specialization:
            matched_specialization = "General Physician"
        filtered_doctors = [doctor for doctor in self.doctors if matched_specialization.lower() in doctor.specialization.lower()]
        return filtered_doctors, matched_specialization

    def update_doctor(self, doctor_id, name, specialization, shift_start_hour=9, shift_hours=8):
        doctor = self.search_by_id(doctor_id)
        if not doctor:
            return False
        doctor.name = name
        doctor.specialization = specialization
        doctor.shift_start_hour = shift_start_hour
        doctor.shift_hours = shift_hours
        self.save_doctors()
        return True

    def delete_doctor(self, doctor_id):
        for i, doctor in enumerate(self.doctors):
            if doctor.doctor_id == doctor_id:
                del self.doctors[i]
                self.save_doctors()
                return True
        return False


# -------------------------------
# Staff Class and Management
# -------------------------------
class Staff:
    def __init__(self, staff_id, name, role, shift_timings):
        self.staff_id = staff_id
        self.name = name
        self.role = role
        self.shift_timings = shift_timings

    def to_dict(self):
        return {"staff_id": self.staff_id, "name": self.name, "role": self.role, "shift_timings": self.shift_timings}

    @classmethod
    def from_dict(cls, data):
        return cls(data["staff_id"], data["name"], data["role"], data["shift_timings"]) 

    def __str__(self):
        return f"ID: {self.staff_id}, Name: {self.name}, Role: {self.role}, Shift: {self.shift_timings}"


class StaffManagement:
    def __init__(self):
        self.staff = self.load_staff()
        self.next_id = self.get_next_id()

    def load_staff(self):
        if not os.path.exists(STAFF_FILE):
            default_staff = [
                Staff(1, "Anjali Mehta", "Receptionist", "8:00 AM - 4:00 PM"),
                Staff(2, "Ravi Kumar", "Receptionist", "4:00 PM - 12:00 AM"),
                Staff(3, "Meena Sharma", "Nurse", "9:00 AM - 5:00 PM"),
                Staff(4, "Pooja Desai", "Nurse", "5:00 PM - 1:00 AM"),
                Staff(5, "Suresh Rao", "Management Staff", "9:00 AM - 6:00 PM")
            ]
            self.save_staff_list(default_staff)
            return default_staff
        try:
            with open(STAFF_FILE, 'r') as file:
                staff_data = json.load(file)
                return [Staff.from_dict(s_data) for s_data in staff_data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_staff(self):
        self.save_staff_list(self.staff)

    def save_staff_list(self, staff):
        staff_data = [s.to_dict() for s in staff]
        with open(STAFF_FILE, 'w') as file:
            json.dump(staff_data, file, indent=2)

    def get_next_id(self):
        if not self.staff:
            return 1
        return max(s.staff_id for s in self.staff) + 1

    def add_staff(self, name, role, shift_timings):
        staff_member = Staff(self.next_id, name, role, shift_timings)
        self.staff.append(staff_member)
        self.next_id += 1
        self.save_staff()
        print(f"[SUCCESS] Staff member {name} added successfully with ID: {staff_member.staff_id}")

    def view_staff(self):
        if not self.staff:
            print("[WARNING] No staff found.")
            return
        print("\n" + "="*80)
        print("                           HOSPITAL STAFF LIST")
        print("="*80)
        for staff_member in self.staff:
            print(staff_member)

    def search_by_id(self, staff_id):
        for staff_member in self.staff:
            if staff_member.staff_id == staff_id:
                return staff_member
        return None

    def update_staff(self, staff_id, name, role, shift_timings):
        staff_member = self.search_by_id(staff_id)
        if not staff_member:
            return False
        staff_member.name = name
        staff_member.role = role
        staff_member.shift_timings = shift_timings
        self.save_staff()
        return True

    def delete_staff(self, staff_id):
        for i, staff_member in enumerate(self.staff):
            if staff_member.staff_id == staff_id:
                del self.staff[i]
                self.save_staff()
                return True
        return False


# -------------------------------
# Appointment Class and Management
# -------------------------------
class Appointment:
    def __init__(self, appointment_id, patient_id, doctor_id, date, time_slot, reason="N/A"):
        self.appointment_id = appointment_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.visit_type = "General Consultation"
        self.condition = reason
        self.date = date  # "DD-MM-YYYY"
        self.time = time_slot  # "HH:MM-HH:MM"
        self.status = "Scheduled"

    def to_dict(self):
        return {
            "appointment_id": self.appointment_id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "visit_type": self.visit_type,
            "condition": self.condition,
            "date": self.date,
            "time": self.time,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data):
        appointment = cls(data["appointment_id"], data["patient_id"], data["doctor_id"], data["date"], data["time"], data.get("condition", "N/A"))
        appointment.status = data.get("status", "Scheduled")
        return appointment

    def __str__(self):
        return f"ID: {self.appointment_id}, Patient: {self.patient_id}, Doctor: {self.doctor_id}, Date: {self.date}, Time: {self.time}, Status: {self.status}"


class AppointmentManagement:
    def __init__(self):
        self.appointments = self.load_appointments()
        self.next_id = self.get_next_id()

    def load_appointments(self):
        if not os.path.exists(APPOINTMENTS_FILE):
            return []
        try:
            with open(APPOINTMENTS_FILE, 'r') as file:
                appointments_data = json.load(file)
                return [Appointment.from_dict(appt_data) for appt_data in appointments_data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_appointments(self):
        appointments_data = [appointment.to_dict() for appointment in self.appointments]
        with open(APPOINTMENTS_FILE, 'w') as file:
            json.dump(appointments_data, file, indent=2)

    def get_next_id(self):
        if not self.appointments:
            return 1
        return max(appointment.appointment_id for appointment in self.appointments) + 1

    def book_appointment(self, patient_id, doctor_id, date, time_slot, reason="N/A"):
        # check if slot already booked
        for appt in self.appointments:
            if appt.doctor_id == doctor_id and appt.date == date and appt.time == time_slot and appt.status == "Scheduled":
                print("[ERROR] Slot already booked.")
                return None
        appointment = Appointment(self.next_id, patient_id, doctor_id, date, time_slot, reason)
        self.appointments.append(appointment)
        self.next_id += 1
        self.save_appointments()
        print(f"[SUCCESS] Appointment booked successfully! Appointment ID: {appointment.appointment_id}")
        return appointment.appointment_id

    def view_appointments(self):
        if not self.appointments:
            print("[WARNING] No appointments found.")
            return
        print("\n" + "="*100)
        print("                                APPOINTMENTS LIST")
        print("="*100)
        for appointment in self.appointments:
            print(appointment)

    def view_patient_appointments(self, patient_id):
        patient_appointments = [appt for appt in self.appointments if appt.patient_id == patient_id]
        if not patient_appointments:
            print(f"[WARNING] No appointments found for Patient ID: {patient_id}")
            return
        print(f"\nAppointments for Patient ID: {patient_id}")
        print("-" * 100)
        for appointment in patient_appointments:
            print(appointment)

    def cancel_appointment(self, appointment_id):
        for appointment in self.appointments:
            if appointment.appointment_id == appointment_id:
                appointment.status = "Cancelled"
                self.save_appointments()
                return True
        return False

    def delete_appointment(self, appointment_id):
        for i, appointment in enumerate(self.appointments):
            if appointment.appointment_id == appointment_id:
                del self.appointments[i]
                self.save_appointments()
                return True
        return False

    # --- Schedule helpers ---
    def doctor_week_grid(self, doctor, start_date=None):
        """
        Returns a tuple (dates_list, slot_times, grid)
        dates_list: list of 7 date strings "DD-MM-YYYY" starting from start_date (or today)
        slot_times: list of slot time strings length = doctor.shift_hours
        grid: list of lists: rows = slots, cols = days; each cell is 'B' or 'U'
        """
        if start_date is None:
            start = datetime.now().date()
        else:
            start = start_date
        dates = [(start + timedelta(days=i)) for i in range(7)]
        date_strs = [d.strftime("%d-%m-%Y") for d in dates]
        slots = doctor.slot_times()  # list of times like ["09:00-10:00", ...]
        # create grid slots x days, default 'U'
        grid = [['_' for _ in range(7)] for _ in range(len(slots))]
        # mark booked slots
        for appt in self.appointments:
            if appt.doctor_id == doctor.doctor_id and appt.status == "Scheduled":
                try:
                    if appt.date in date_strs:
                        col = date_strs.index(appt.date)
                        if appt.time in slots:
                            row = slots.index(appt.time)
                            grid[row][col] = 'B'
                except ValueError:
                    continue
        return date_strs, slots, grid

    def print_week_schedule(self, doctor, start_date=None):
        dates, slots, grid = self.doctor_week_grid(doctor, start_date)
        # Header
        header = ["Slot\\Date"] + [datetime.strptime(d, "%d-%m-%Y").strftime("%a %d-%b") for d in dates]
        col_width = 15
        # print header
        print("\n" + "="* (col_width * (len(header))))
        print(f"Weekly schedule for Dr. {doctor.name} (Specialization: {doctor.specialization})")
        print("="* (col_width * (len(header))))
        header_line = "".join(h.center(col_width) for h in header)
        print(header_line)
        print("-" * len(header_line))
        # print rows
        for r, slot in enumerate(slots):
            row_cells = [slot.center(col_width)]
            for c in range(len(dates)):
                row_cells.append(grid[r][c].center(col_width))
            print("".join(row_cells))
        print("\nLegend: B = Booked, U = Unbooked")
        return dates, slots, grid


# -------------------------------
# Main Hospital Management System
# -------------------------------
class HospitalManagementSystem:
    def __init__(self):
        # ensure files exist
        ensure_file_exists(USERS_FILE, [])
        ensure_file_exists(PATIENTS_FILE, [])
        ensure_file_exists(DOCTORS_FILE, [])
        ensure_file_exists(APPOINTMENTS_FILE, [])
        ensure_file_exists(STAFF_FILE, [])

        self.auth_system = AuthenticationSystem()
        self.patient_management = PatientManagement(self.auth_system)
        self.doctor_management = DoctorManagement()
        self.staff_management = StaffManagement()
        self.appointment_management = AppointmentManagement()

    def main_menu(self):
        while True:
            print("\n" + "="*50)
            print("      HOSPITAL MANAGEMENT SYSTEM")
            print("="*50)
            print("Select Your Role:")
            print("1. Admin")
            print("2. Patient")
            print("3. Exit")
            choice = input("Enter your choice: ").strip()
            if choice == "1":
                if self.auth_system.admin_login():
                    self.admin_menu()
            elif choice == "2":
                self.patient_menu()
            elif choice == "3":
                print("Thank you for using Hospital Management System!")
                break
            else:
                print("[ERROR] Invalid choice! Please try again.")

    def admin_menu(self):
        while True:
            print("\n" + "="*50)
            print("           ADMIN DASHBOARD")
            print("="*50)
            print("1. Doctor Management")
            print("2. Hospital Staff Management")
            print("3. View All Patients")
            print("4. View All Appointments")
            print("5. Cancel Appointment")
            print("6. Logout")
            choice = input("Enter your choice: ").strip()
            if choice == "1":
                self.doctor_management_menu()
            elif choice == "2":
                self.staff_management_menu()
            elif choice == "3":
                self.patient_management.display_all_patients()
            elif choice == "4":
                self.appointment_management.view_appointments()
            elif choice == "5":
                self.cancel_appointment_admin()
            elif choice == "6":
                print("Logging out...")
                break
            else:
                print("[ERROR] Invalid choice! Please try again.")

    def patient_menu(self):
        while True:
            print("\n" + "="*50)
            print("          PATIENT PORTAL")
            print("="*50)
            print("1. Book New Appointment")
            print("2. View My Appointments")
            print("3. Cancel My Appointment")
            print("4. Back to Main Menu")
            choice = input("Enter your choice: ").strip()
            if choice == "1":
                self.book_appointment_patient()
            elif choice == "2":
                self.view_patient_appointments()
            elif choice == "3":
                self.cancel_appointment_patient()
            elif choice == "4":
                break
            else:
                print("[ERROR] Invalid choice! Please try again.")

    def doctor_management_menu(self):
        while True:
            print("\n" + "="*40)
            print("       DOCTOR MANAGEMENT")
            print("="*40)
            print("1. Add Doctor")
            print("2. View All Doctors")
            print("3. Update Doctor")
            print("4. Delete Doctor")
            print("5. Back to Admin Menu")
            choice = input("Enter your choice: ").strip()
            if choice == "1":
                self.add_doctor()
            elif choice == "2":
                self.doctor_management.view_doctors()
            elif choice == "3":
                self.update_doctor()
            elif choice == "4":
                self.delete_doctor()
            elif choice == "5":
                break
            else:
                print("[ERROR] Invalid choice! Please try again.")

    def staff_management_menu(self):
        while True:
            print("\n" + "="*40)
            print("       HOSPITAL STAFF MANAGEMENT")
            print("="*40)
            print("1. Add Staff Member")
            print("2. View All Staff")
            print("3. Update Staff")
            print("4. Delete Staff")
            print("5. Back to Admin Menu")
            choice = input("Enter your choice: ").strip()
            if choice == "1":
                self.add_staff()
            elif choice == "2":
                self.staff_management.view_staff()
            elif choice == "3":
                self.update_staff()
            elif choice == "4":
                self.delete_staff()
            elif choice == "5":
                break
            else:
                print("[ERROR] Invalid choice! Please try again.")

    def add_doctor(self):
        print("\n--- Add New Doctor ---")
        name = input("Enter doctor name: ").strip()
        specialization = input("Enter specialization: ").strip()
        try:
            shift_start_hour = int(input("Enter shift start hour (0-23, default 9): ").strip() or "9")
        except ValueError:
            shift_start_hour = 9
        try:
            shift_hours = int(input("Enter shift hours (default 8): ").strip() or "8")
        except ValueError:
            shift_hours = 8
        self.doctor_management.add_doctor(name, specialization, shift_start_hour, shift_hours)

    def update_doctor(self):
        try:
            doctor_id = int(input("Enter doctor ID to update: "))
            doctor = self.doctor_management.search_by_id(doctor_id)
            if not doctor:
                print("[ERROR] Doctor not found!")
                return
            print(f"Current doctor data: {doctor}")
            print("\nEnter new information: (leave blank to keep current)")
            name = input("Enter new name: ").strip() or doctor.name
            specialization = input("Enter new specialization: ").strip() or doctor.specialization
            try:
                shift_start_input = input(f"Enter new shift start hour (current {doctor.shift_start_hour}): ").strip()
                shift_start_hour = int(shift_start_input) if shift_start_input else doctor.shift_start_hour
            except ValueError:
                shift_start_hour = doctor.shift_start_hour
            try:
                shift_hours_input = input(f"Enter new shift hours (current {doctor.shift_hours}): ").strip()
                shift_hours = int(shift_hours_input) if shift_hours_input else doctor.shift_hours
            except ValueError:
                shift_hours = doctor.shift_hours
            if self.doctor_management.update_doctor(doctor_id, name, specialization, shift_start_hour, shift_hours):
                print("[SUCCESS] Doctor updated successfully!")
            else:
                print("[ERROR] Failed to update doctor!")
        except ValueError:
            print("[ERROR] Invalid input! Please enter valid data.")

    def delete_doctor(self):
        try:
            doctor_id = int(input("Enter doctor ID to delete: "))
            if self.doctor_management.delete_doctor(doctor_id):
                print("[SUCCESS] Doctor deleted successfully!")
            else:
                print("[ERROR] Doctor not found!")
        except ValueError:
            print("[ERROR] Invalid input! Please enter a valid ID.")

    def add_staff(self):
        print("\n--- Add New Staff Member ---")
        name = input("Enter staff name: ").strip()
        print("\nSelect Role:")
        print("1. Receptionist")
        print("2. Nurse")
        print("3. Management Staff")
        role_choice = input("Enter role choice: ").strip()
        role_map = {"1": "Receptionist", "2": "Nurse", "3": "Management Staff"}
        role = role_map.get(role_choice, "Staff")
        shift_timings = input("Enter shift timings: ").strip()
        self.staff_management.add_staff(name, role, shift_timings)

    def update_staff(self):
        try:
            staff_id = int(input("Enter staff ID to update: "))
            staff_member = self.staff_management.search_by_id(staff_id)
            if not staff_member:
                print("[ERROR] Staff member not found!")
                return
            print(f"Current staff data: {staff_member}")
            print("\nEnter new information:")
            name = input("Enter new name: ").strip() or staff_member.name
            print("\nSelect Role:")
            print("1. Receptionist")
            print("2. Nurse")
            print("3. Management Staff")
            role_choice = input("Enter role choice: ").strip()
            role_map = {"1": "Receptionist", "2": "Nurse", "3": "Management Staff"}
            role = role_map.get(role_choice, staff_member.role)
            shift_timings = input("Enter new shift timings: ").strip() or staff_member.shift_timings
            if self.staff_management.update_staff(staff_id, name, role, shift_timings):
                print("[SUCCESS] Staff updated successfully!")
            else:
                print("[ERROR] Failed to update staff!")
        except ValueError:
            print("[ERROR] Invalid input! Please enter valid data.")

    def delete_staff(self):
        try:
            staff_id = int(input("Enter staff ID to delete: "))
            if self.staff_management.delete_staff(staff_id):
                print("[SUCCESS] Staff deleted successfully!")
            else:
                print("[ERROR] Staff not found!")
        except ValueError:
            print("[ERROR] Invalid input! Please enter a valid ID.")

    # -------------------------------
    # Updated Booking Flow (doctor-first)
    # -------------------------------
    def book_appointment_patient(self):
        print("\n--- Book New Appointment ---")
        name = input("Enter your full name: ").strip()
        phone = input("Enter your contact number: ").strip()
        email = input("Enter your email: ").strip()
        patient_id, password = self.patient_management.register_new_patient(name, phone, email)
        print("\n" + "="*50)
        print("[SUCCESS] PATIENT REGISTERED SUCCESSFULLY!")
        print("="*50)
        print(f"Your Patient ID: {patient_id}")
        print(f"Your Password: {password}")
        print("IMPORTANT: Please save these credentials!")
        print("="*50)

        # Show all doctors (patient chooses doctor first)
        print("\nAvailable Doctors:")
        self.doctor_management.view_doctors()
        try:
            doctor_id = int(input("\nEnter Doctor ID to book appointment with: ").strip())
        except ValueError:
            print("[ERROR] Invalid Doctor ID!")
            return
        doctor = self.doctor_management.search_by_id(doctor_id)
        if not doctor:
            print("[ERROR] Invalid Doctor ID!")
            return

        # Show weekly schedule (next 7 days) with B/U
        dates, slots, grid = self.appointment_management.print_week_schedule(doctor)

        # Prompt for day and slot selection
        print("\nChoose the day and slot to book.")
        print(f"Enter Day number (1 for {dates[0]}, 7 for {dates[-1]})")
        try:
            day_choice = int(input("Day (1-7): ").strip())
            if day_choice < 1 or day_choice > 7:
                print("[ERROR] Day choice out of range.")
                return
        except ValueError:
            print("[ERROR] Invalid day input.")
            return

        # Show the chosen day's column with slot statuses for clarity
        print(f"\nSlots for {dates[day_choice-1]}:")
        for idx, slot_time in enumerate(slots, start=1):
            status = grid[idx-1][day_choice-1]
            print(f"{idx}. {slot_time} --> {status}")

        try:
            slot_choice = int(input(f"Choose slot number (1-{len(slots)}): ").strip())
            if slot_choice < 1 or slot_choice > len(slots):
                print("[ERROR] Slot choice out of range.")
                return
        except ValueError:
            print("[ERROR] Invalid slot input.")
            return

        chosen_status = grid[slot_choice-1][day_choice-1]
        if chosen_status == 'B':
            print("[ERROR] That slot is already booked. Please try another.")
            return

        chosen_date = dates[day_choice-1]  # "DD-MM-YYYY"
        chosen_time = slots[slot_choice-1]  # "HH:MM-HH:MM"
        reason = input("Optional: Briefly describe reason for visit (or press Enter to skip): ").strip() or "N/A"

        self.appointment_management.book_appointment(patient_id, doctor_id, chosen_date, chosen_time, reason)
        print("\n[SUCCESS] Your appointment has been booked successfully!")

    # --- New helper methods for patient/admin actions ---
    def view_patient_appointments(self):
        patient_id = input("Enter your Patient ID: ").strip()
        password = input("Enter your Password: ").strip()
        if not self.patient_management.verify_patient(patient_id, password):
            print("[ERROR] Invalid credentials!")
            return
        self.appointment_management.view_patient_appointments(patient_id)

    def cancel_appointment_patient(self):
        patient_id = input("Enter your Patient ID: ").strip()
        password = input("Enter your Password: ").strip()
        if not self.patient_management.verify_patient(patient_id, password):
            print("[ERROR] Invalid credentials!")
            return
        try:
            appointment_id = int(input("Enter Appointment ID to cancel: ").strip())
        except ValueError:
            print("[ERROR] Invalid Appointment ID!")
            return
        appt = next((a for a in self.appointment_management.appointments if a.appointment_id == appointment_id and a.patient_id == patient_id), None)
        if not appt:
            print("[ERROR] Appointment not found or does not belong to you!")
            return
        if self.appointment_management.cancel_appointment(appointment_id):
            print("[SUCCESS] Appointment cancelled successfully!")
        else:
            print("[ERROR] Failed to cancel appointment!")

    def cancel_appointment_admin(self):
        try:
            appointment_id = int(input("Enter Appointment ID to cancel: ").strip())
        except ValueError:
            print("[ERROR] Invalid Appointment ID!")
            return
        if self.appointment_management.cancel_appointment(appointment_id):
            print("[SUCCESS] Appointment cancelled successfully!")
        else:
            print("[ERROR] Appointment not found!")


if __name__ == "__main__":
    hms = HospitalManagementSystem()
    hms.main_menu()