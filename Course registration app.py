import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import datetime

# --- Helper Functions (Unchanged) ---
def time_to_minutes(time_str):
    """Converts 'HH:MM' to total minutes from midnight."""
    try:
        hours, minutes = map(int, time_str.split(":"))
        return hours * 60 + minutes
    except ValueError:
        print(f"Error converting time string: {time_str}")
        return 0

def is_time_conflict(schedule1, schedule2):
    """Checks if two schedules conflict."""
    day1, start1, end1 = schedule1
    day2, start2, end2 = schedule2
    if day1 != day2: return False
    try:
        s1, e1 = time_to_minutes(start1), time_to_minutes(end1)
        s2, e2 = time_to_minutes(start2), time_to_minutes(end2)
        if s1 >= e1 or s2 >= e2: return False # Invalid interval
        return s1 < e2 and s2 < e1
    except Exception: return False

def is_within_allowed_time(schedule):
    """Check schedule is Mon-Fri, 08:00-17:50."""
    day, start, end = schedule
    allowed_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    if day not in allowed_days: return False
    try:
        start_minutes = time_to_minutes(start)
        end_minutes = time_to_minutes(end)
        if start_minutes >= end_minutes: return False # Invalid interval
        if start_minutes < time_to_minutes("08:00") or end_minutes > time_to_minutes("17:50"): return False
        return True
    except Exception: return False

# --- Data Model Classes (Unchanged) ---
class Student:
    def __init__(self, student_id, name):
        self.student_id = student_id
        self.name = name
        self.registered_courses = set()

class Course:
    def __init__(self, course_id, name, instructor, schedule, max_students=30, credits=3):
        if not (isinstance(schedule, (tuple, list)) and len(schedule) == 3 and
                isinstance(schedule[0], str) and isinstance(schedule[1], str) and isinstance(schedule[2], str)):
                raise ValueError(f"Invalid schedule format for Course {course_id}.")
        if not is_within_allowed_time(schedule):
                raise ValueError(f"Course {course_id} schedule {schedule} invalid/outside allowed hours.")
        self.course_id = course_id
        self.name = name
        self.instructor = instructor
        self.schedule = schedule
        self.enrolled_students = set()
        self.max_students = max_students
        self.credits = credits

# --- EnrollmentSystem Class (Unchanged logic, ensure print statements are reasonable) ---
class EnrollmentSystem:
    def __init__(self):
        self.students = {}
        self.courses = {}
        self.data_dir = 'data'
        self.students_file = os.path.join(self.data_dir, 'students.csv')
        self.courses_file = os.path.join(self.data_dir, 'courses.csv')
        self.enrollments_file = os.path.join(self.data_dir, 'enrollments.csv')

        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        self.load_data()

        if not self.courses:
            print("No courses found, creating hypothetical courses...")
            self.courses = create_hypothetical_courses()
            self.save_courses()
        else:
            print(f"Loaded {len(self.courses)} courses.")

    def load_data(self):
        # Load students
        try:
            if os.path.exists(self.students_file):
                with open(self.students_file, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    next(reader) # Skip header
                    for i, row in enumerate(reader):
                        if len(row) >= 2 and row[0].strip() and row[1].strip():
                            self.students[row[0].strip()] = Student(row[0].strip(), row[1].strip())
                        # else: print(f"Skipping invalid student row {i+1}") # Optional debug
        except Exception as e: print(f"Error loading students: {e}")

        # Load courses
        try:
            if os.path.exists(self.courses_file):
                with open(self.courses_file, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    next(reader) # Skip header
                    for i, row in enumerate(reader):
                        if len(row) >= 5:
                            try:
                                course_id, name, instructor, day, time_range = map(str.strip, row[:5])
                                max_students = int(row[5].strip()) if len(row) > 5 and row[5].strip().isdigit() else 30
                                credits = int(row[6].strip()) if len(row) > 6 and row[6].strip().isdigit() else 3
                                if not all([course_id, name, instructor, day, time_range]): continue

                                start_time, end_time = map(str.strip, time_range.split('-'))
                                schedule = (day, start_time, end_time)
                                self.courses[course_id] = Course(course_id, name, instructor, schedule, max_students, credits)
                            except Exception as ve: print(f"Error processing course row {i+1} ('{row[0]}'): {ve}")
                        # else: print(f"Skipping short course row {i+1}") # Optional debug
        except Exception as e: print(f"Error loading courses: {e}")

        # Load enrollments
        try:
            if os.path.exists(self.enrollments_file):
                with open(self.enrollments_file, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    next(reader) # Skip header
                    for i, row in enumerate(reader):
                        if len(row) >= 2:
                            student_id, course_id = map(str.strip, row[:2])
                            if student_id in self.students and course_id in self.courses:
                                self.students[student_id].registered_courses.add(course_id)
                                self.courses[course_id].enrolled_students.add(student_id)
                            # else: print(f"Skipping invalid enrollment row {i+1}") # Optional debug
        except Exception as e: print(f"Error loading enrollments: {e}")

    def save_data(self):
        self.save_students()
        self.save_courses()
        self.save_enrollments()

    def save_students(self):
        try:
            with open(self.students_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['student_id', 'name'])
                for student_id in sorted(self.students.keys()):
                    writer.writerow([self.students[student_id].student_id, self.students[student_id].name])
        except IOError as e: print(f"Error saving students: {e}")

    def save_courses(self):
        try:
            with open(self.courses_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['course_id', 'name', 'instructor', 'day', 'time', 'max_students', 'credits'])
                for course_id in sorted(self.courses.keys()):
                    course = self.courses[course_id]
                    day, start, end = course.schedule
                    writer.writerow([course.course_id, course.name, course.instructor, day, f"{start}-{end}", course.max_students, course.credits])
        except IOError as e: print(f"Error saving courses: {e}")

    def save_enrollments(self):
        try:
            with open(self.enrollments_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['student_id', 'course_id'])
                for student_id in sorted(self.students.keys()):
                    for course_id in sorted(list(self.students[student_id].registered_courses)):
                        if course_id in self.courses: # Only save enrollments for existing courses
                            writer.writerow([student_id, course_id])
        except IOError as e: print(f"Error saving enrollments: {e}")

    def add_student(self, student_id, name):
        # Validate student ID: must be alphanumeric and convert to uppercase
        if not student_id.isalnum():
            raise ValueError("Student ID must be alphanumeric.")
        student_id = student_id.upper()

        # Validate name: must only contain letters
        if not name.replace(" ", "").isalpha():  # Allow spaces in names
            raise ValueError("Name must only contain letters.")

        if not student_id or not name:
            raise ValueError("Student ID and Name cannot be empty.")
        if student_id in self.students:
            raise ValueError(f"Student ID '{student_id}' already exists.")
        
        self.students[student_id] = Student(student_id, name)
        self.save_students()
        print(f"Student '{name}' ({student_id}) added.")

    def enroll_student(self, student_id, course_id):
        if student_id not in self.students: raise ValueError(f"Student '{student_id}' does not exist.")
        if course_id not in self.courses: raise ValueError(f"Course '{course_id}' does not exist.")
        student = self.students[student_id]
        course = self.courses[course_id]
        if course_id in student.registered_courses: raise ValueError(f"Already enrolled in {course.name} ({course_id}).")
        if len(course.enrolled_students) >= course.max_students: raise ValueError(f"Course {course.name} ({course_id}) is full.")

        current_credits = sum(self.courses[cid].credits for cid in student.registered_courses if cid in self.courses)
        MAX_CREDITS = 18
        if current_credits + course.credits > MAX_CREDITS:
                raise ValueError(f"Cannot enroll. Exceeds max {MAX_CREDITS} credits (Current: {current_credits}, Adding: {course.credits}).")

        for cid in student.registered_courses:
            if cid in self.courses and is_time_conflict(course.schedule, self.courses[cid].schedule):
                raise ValueError(f"Time conflict with {self.courses[cid].name} ({cid}).")

        student.registered_courses.add(course_id)
        course.enrolled_students.add(student_id)
        self.save_enrollments()
        print(f"Student '{student_id}' enrolled in '{course_id}'.")

    def drop_course(self, student_id, course_id):
        if student_id not in self.students:
            raise ValueError(f"Student '{student_id}' does not exist.")
        student = self.students[student_id]
        if course_id not in student.registered_courses:
            raise ValueError(f"Not enrolled in course '{course_id}'.")

        course_exists = course_id in self.courses

        # Calculate current credits
        current_credits = sum(self.courses[cid].credits for cid in student.registered_courses if cid in self.courses)
        MIN_CREDITS = 9

        # Remove the course from the student's registered courses
        student.registered_courses.remove(course_id)
        if course_exists:
            self.courses[course_id].enrolled_students.discard(student_id)  # Use discard to avoid KeyError

        # Check if dropping the course goes below the minimum credits
        new_credits = current_credits - (self.courses[course_id].credits if course_exists else 0)
        if new_credits < MIN_CREDITS:
            print(f"Warning: Dropping this course will reduce your total credits to {new_credits}, which is below the minimum allowable ({MIN_CREDITS}).")

        self.save_enrollments()
        print(f"Student '{student_id}' dropped course '{course_id}'.")

    def get_student_courses(self, student_id):
        if student_id not in self.students: raise ValueError("Student does not exist.")
        return [self.courses[cid] for cid in self.students[student_id].registered_courses if cid in self.courses]

    def get_available_courses(self):
        return list(self.courses.values())


# --- (create_hypothetical_courses - Unchanged) ---
def create_hypothetical_courses():
    """Creates a dictionary of hypothetical courses with more details."""
    courses = {}
    schedule_data = [
        ('MATH101', 'Calculus I', 'Dr. Smith', ('Monday', '11:00', '11:50'), 35, 4),
        ('PHYS101', 'General Physics I', 'Dr. Johnson', ('Tuesday', '10:00', '11:50'), 30, 4),
        ('CHEM101', 'General Chemistry I', 'Dr. Lee', ('Wednesday', '09:00', '09:50'), 40, 3),
        ('ENG101', 'Composition I', 'Prof. Brown', ('Thursday', '12:00', '12:50'), 25, 3),
        ('HIST101', 'World History', 'Dr. Davis', ('Friday', '14:00', '14:50'), 30, 3),
        ('CS101', 'Intro to Programming', 'Prof. Wilson', ('Monday', '13:00', '14:20'), 30, 3),
        ('BIO101', 'Principles of Biology', 'Dr. Martinez', ('Tuesday', '14:00', '14:50'), 35, 3),
        ('PSY101', 'Intro to Psychology', 'Dr. Taylor', ('Wednesday', '11:00', '11:50'), 30, 3),
        ('ECON101', 'Microeconomics', 'Prof. Anderson', ('Thursday', '09:00', '10:20'), 28, 3),
        ('ART101', 'Art Appreciation', 'Dr. White', ('Friday', '10:00', '10:50'), 20, 3),
        ('SPAN101', 'Elementary Spanish I', 'Prof. Garcia', ('Monday', '08:00', '08:50'), 25, 4),
        ('MUSI100', 'Music Fundamentals', 'Dr. Evans', ('Wednesday', '15:00', '16:20'), 15, 3)
    ]
    for course_id, name, instructor, schedule, max_s, creds in schedule_data:
        try:
            courses[course_id] = Course(course_id, name, instructor, schedule, max_students=max_s, credits=creds)
        except ValueError as ve:
            print(f"Error creating hypothetical course {course_id}: {ve}")
    return courses
# ---------------------------------
# Tkinter UI Application - Enhanced Styling
# ---------------------------------
class RegistrationApp:
    def __init__(self, root, enrollment_system):
        self.root = root
        self.system = enrollment_system
        self.current_student_id = None

        # --- Enhanced Styling ---
        self.bg_color = "#f8f9fa"          # Lighter grey background
        self.primary_color = "#00529b"      # Calm Blue (keep)
        self.secondary_color = "#e9ecef"    # Very light grey for accents/alternating rows
        self.text_color = "#212529"        # Darker text
        self.light_text_color = "#ffffff" # White text
        self.error_color = "#dc3545"        # Bootstrap danger red
        self.success_color = "#28a745"      # Bootstrap success green
        self.border_color = "#dee2e6"      # Light border color
        self.selected_bg = "#cfe2ff"        # Light blue for selection
        self.selected_fg = "#002a52"        # Darker blue text for selection

        self.root.title("University Course Registration")
        self.root.geometry("950x700") # Slightly wider/taller default size
        self.root.minsize(800, 600)
        self.root.configure(bg=self.bg_color)

        # --- Style Configuration ---
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except tk.TclError:
            style.theme_use('default')

        # General Widget Styles
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground=self.text_color, font=("Segoe UI", 10))
        style.configure("TEntry", font=("Segoe UI", 10), padding=5, relief="flat") # Flat look for entry
        style.map("TEntry",
            bordercolor=[('focus', self.primary_color)], # Blue border on focus
            highlightcolor=[('focus', self.primary_color)],
            relief=[('focus', 'solid')] # Add solid relief on focus
            )

        # Button Styles
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=(10, 5), relief="flat", borderwidth=1,
                        foreground=self.primary_color, background=self.light_text_color)  # Explicitly set colors
        style.map("TButton",
                  background=[('active', self.secondary_color), ('!active', self.light_text_color)],
                  foreground=[('!active', self.primary_color)],
                  bordercolor=[('!active', self.primary_color)]
                  )

        style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"), background=self.primary_color, foreground=self.light_text_color, padding=(12, 6))
        style.map("Accent.TButton",
                  background=[('active', '#003c75'), ('!disabled', self.primary_color)],  # Darker blue on hover/press
                  foreground=[('!disabled', self.light_text_color)],  # Ensure text is visible
                  relief=[('pressed', 'sunken'), ('!pressed', 'raised')]
                  )

        # Tab Styles (if applicable)
        style.configure("TNotebook.Tab", font=("Segoe UI", 10), padding=(10, 5),
                        foreground=self.primary_color, background=self.light_text_color)  # Explicitly set colors
        style.map("TNotebook.Tab",
                  background=[('selected', self.secondary_color), ('!selected', self.light_text_color)],
                  foreground=[('selected', self.primary_color), ('!selected', self.primary_color)]
                  )

        # Title & Header Styles
        style.configure("Header.TFrame", background=self.primary_color) # Frame for main titles
        style.configure("Title.TLabel", background=self.primary_color, foreground=self.light_text_color, font=("Segoe UI", 16, "bold"), padding=(10, 10, 10, 10)) # Main screen titles
        style.configure("Info.TLabel", background=self.primary_color, foreground=self.light_text_color, font=("Segoe UI", 10)) # For student info header

        # Labelframe Styles
        style.configure("TLabelframe", background=self.bg_color, bordercolor=self.border_color, relief="groove", borderwidth=1)
        style.configure("TLabelframe.Label", background=self.bg_color, foreground=self.primary_color, font=("Segoe UI", 11, "bold"), padding=(5, 2))

        # Separator Style
        style.configure("TSeparator", background=self.border_color)

        # Treeview Styles
        style.configure("Treeview",
                            background=self.light_text_color, # White background for rows
                            foreground=self.text_color,
                            fieldbackground=self.light_text_color,
                            borderwidth=1,
                            relief="solid",
                            rowheight=25) # Increase row height slightly
        style.map("Treeview",
                            background=[('selected', self.selected_bg)], # Background of selected item
                            foreground=[('selected', self.selected_fg)]) # Text color of selected item

        style.configure("Treeview.Heading",
                            font=("Segoe UI", 10, "bold"),
                            padding=(5, 5),
                            background=self.secondary_color, # Light grey heading background
                            foreground=self.primary_color,      # Blue heading text
                            relief="ridge",                      # Give headings a slight ridge
                            borderwidth=1)
        style.map("Treeview.Heading", relief=[('active','groove'),('!active','ridge')]) # Change relief on hover

        # --- Main Container ---
        self.main_container = ttk.Frame(self.root, padding=(0, 0)) # No padding here, handled by screens
        self.main_container.pack(fill=tk.BOTH, expand=True)
        # Configure rows/columns for the container to hold the header+content structure
        self.main_container.grid_rowconfigure(1, weight=1) # Content area expands
        self.main_container.grid_columnconfigure(0, weight=1)


        # --- Frame Dictionary ---
        self.frames = {}
        # Order matters if some frames depend on styles defined before them
        for F in (WelcomeScreen, LoginScreen, RegistrationScreen, CourseScreen, TimetableScreen):
            page_name = F.__name__
            # Use grid layout for frames within main_container
            frame = F(parent=self.main_container, controller=self)
            self.frames[page_name] = frame
            # Place frame in row 1, spanning the column. Row 0 can be for a potential global header if needed.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("WelcomeScreen")

    def get_frame(self, page_name):
        return self.frames[page_name]

    def show_frame(self, page_name):
        """Show a frame for the given page name"""
        frame = self.frames[page_name]
        if hasattr(frame, 'clear_status'): frame.clear_status()
        if hasattr(frame, 'refresh_data'): frame.refresh_data()
        frame.tkraise()

    def set_status(self, frame_name, message, is_error=True):
        frame = self.frames.get(frame_name)
        if frame and hasattr(frame, 'status_label'):
            color = self.error_color if is_error else self.success_color
            frame.status_label.config(text=message, foreground=color, font=("Segoe UI", 9, "italic")) # Italicize status

    def login_successful(self, student_id):
        self.current_student_id = student_id
        course_frame = self.get_frame("CourseScreen")
        # No need to call update_student_info here, refresh_data() does it when shown
        self.show_frame("CourseScreen")

    def logout(self):
        self.current_student_id = None
        login_frame = self.get_frame("LoginScreen")
        if hasattr(login_frame, 'clear_entries'): login_frame.clear_entries()
        self.show_frame("WelcomeScreen")

# --------------------------
# Screen Frame Classes (with style adjustments)
# --------------------------

class BaseScreen(ttk.Frame):
    """Base class for screens"""
    def __init__(self, parent, controller):
        super().__init__(parent, padding=(0,0)) # Add padding to the screen frame itself
        self.controller = controller
        self.system = controller.system
        self.status_label = None
        self.content_area = ttk.Frame(self, padding=(20,15))
        self.content_area.pack(fill=tk.BOTH, expand=True)

    def create_status_label(self, parent):
        """Helper to create a standard status label"""
        self.status_label = ttk.Label(parent, text="", font=("Segoe UI", 9), anchor="center", wraplength=600)
        return self.status_label

    def create_header(self, text):
        """Creates a styled header section for a screen"""
        # Place header directly in self (the BaseScreen frame), not content_area
        header_frame = ttk.Frame(self, style="Header.TFrame")
        # Corrected pack call - no negative padding
        header_frame.pack(fill=tk.X, side=tk.TOP, pady=(0, 0)) # No padding needed here directly

        title_label = ttk.Label(header_frame, text=text, style="Title.TLabel", anchor="center")
        title_label.pack(fill=tk.X, expand=True, ipady=5) # Add internal padding to make title taller

        # Add separator below header in the main frame (self)
        separator = ttk.Separator(self, orient='horizontal')
        separator.pack(fill=tk.X, side=tk.TOP, pady=(0, 15)) # Add space below separator

    def clear_status(self):
        if self.status_label: self.status_label.config(text="")
    def refresh_data(self): pass # Placeholder


class WelcomeScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.create_header("University Course Registration")

        # Place content inside self.content_area
        center_frame = ttk.Frame(self.content_area) # Use self.content_area
        center_frame.pack(expand=True) # Center content vertically

        description = ttk.Label(
            center_frame,
            text="Welcome! Please log in or register to manage your courses.",
            font=("Segoe UI", 11),
            wraplength=500, justify="center", anchor="center"
        )
        description.pack(pady=(0, 30))

        login_reg_btn = ttk.Button(
            center_frame, text="Login / Register",
            command=lambda: controller.show_frame("LoginScreen"),
            style="Accent.TButton", width=20
        )
        login_reg_btn.pack(pady=10)

class LoginScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.create_header("Student Login / Register")

        center_frame = ttk.Frame(self) # Frame to hold the form elements
        center_frame.pack(expand=True)

        form_frame = ttk.Frame(center_frame) # Inner frame for grid layout
        form_frame.pack()

        # Student ID
        ttk.Label(form_frame, text="Student ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=8)
        self.student_id_entry = ttk.Entry(form_frame, width=35)
        self.student_id_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=8)

        # Name
        ttk.Label(form_frame, text="Full Name:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=8)
        self.name_entry = ttk.Entry(form_frame, width=35)
        self.name_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=8)

        # Button Frame
        btn_frame = ttk.Frame(center_frame)
        btn_frame.pack(pady=(25, 10))

        login_btn = ttk.Button(btn_frame, text="Login", command=self.login_student, width=12, style="Accent.TButton")
        login_btn.pack(side=tk.LEFT, padx=10)

        register_btn = ttk.Button(btn_frame, text="Register New", command=self.go_to_register, width=14) # Regular style button
        register_btn.pack(side=tk.LEFT, padx=10)

        # Status Label
        self.status_label = self.create_status_label(center_frame)
        self.status_label.pack(pady=(10, 0), fill=tk.X)

        form_frame.columnconfigure(1, weight=1)

    def clear_entries(self):
        self.student_id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.clear_status()

    # Updated login_student function
    def login_student(self):
        self.clear_status()
        student_id = self.student_id_entry.get().strip().upper()  # Ensure Student ID is case-insensitive
        name = self.name_entry.get().strip()

        if not student_id or not name:
            self.controller.set_status("LoginScreen", "Please enter both Student ID and Name.")
            return

        if student_id in self.system.students:
            # Check if the name matches the registered name
            if self.system.students[student_id].name.lower() == name.lower():
                self.controller.login_successful(student_id)
            else:
                self.controller.set_status("LoginScreen", "Incorrect name for this Student ID.")
        else:
            # If Student ID is not found, prompt the user to register
            self.controller.set_status("LoginScreen", "Student ID not found. Please register or check the ID.")

    def go_to_register(self):
        reg_frame = self.controller.get_frame("RegistrationScreen")
        reg_frame.prefill_fields(self.student_id_entry.get().strip(), self.name_entry.get().strip())
        self.controller.show_frame("RegistrationScreen")

class RegistrationScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.create_header("New Student Registration")

        center_frame = ttk.Frame(self)
        center_frame.pack(expand=True)

        form_frame = ttk.Frame(center_frame)
        form_frame.pack()

        # Student ID
        ttk.Label(form_frame, text="Student ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=8)
        self.student_id_entry = ttk.Entry(form_frame, width=35)
        self.student_id_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=8)

        # Name
        ttk.Label(form_frame, text="Full Name:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=8)
        self.name_entry = ttk.Entry(form_frame, width=35)
        self.name_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=8)

        # Button Frame
        btn_frame = ttk.Frame(center_frame)
        btn_frame.pack(pady=(25, 10))

        register_btn = ttk.Button(btn_frame, text="Complete Registration", command=self.complete_registration, style="Accent.TButton", width=20)
        register_btn.pack(side=tk.LEFT, padx=10)

        back_btn = ttk.Button(btn_frame, text="Back to Login", command=lambda: controller.show_frame("LoginScreen"), width=15)
        back_btn.pack(side=tk.LEFT, padx=10)

        # Status Label
        self.status_label = self.create_status_label(center_frame)
        self.status_label.pack(pady=(10, 0), fill=tk.X)

        form_frame.columnconfigure(1, weight=1)

    def prefill_fields(self, student_id, name):
        self.student_id_entry.delete(0, tk.END)
        self.student_id_entry.insert(0, student_id)
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, name)
        self.clear_status()

    def clear_entries(self):
        self.student_id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.clear_status()

    # Updated complete_registration function
    def complete_registration(self):
        self.clear_status()
        student_id = self.student_id_entry.get().strip().upper()  # Ensure Student ID is case-insensitive
        name = self.name_entry.get().strip()

        try:
            # Validate student ID: must be alphanumeric
            if not student_id.isalnum():
                raise ValueError("Student ID must be alphanumeric.")

            # Validate name: must only contain letters
            if not name.replace(" ", "").isalpha():  # Allow spaces in names
                raise ValueError("Name must only contain letters.")

            if not student_id or not name:
                raise ValueError("Please enter both Student ID and Name.")

            if student_id in self.system.students:
                raise ValueError(f"Student ID '{student_id}' is already registered. Please log in.")

            # Add the new student to the system
            self.system.add_student(student_id, name)
            self.controller.set_status("RegistrationScreen", f"Student '{name}' registered successfully! Logging in...", is_error=False)

            # Add a small delay before switching screen to show the success message
            self.after(1500, lambda: self.controller.login_successful(student_id))
            self.clear_entries()
        except ValueError as e:
            self.controller.set_status("RegistrationScreen", str(e))
        except Exception as e:
            self.controller.set_status("RegistrationScreen", f"An unexpected error occurred: {e}")

class CourseScreen(BaseScreen):
    def __init__(self, parent, controller):
        # Override padding for this screen
        super().__init__(parent=parent, controller=controller)
        self['padding'] = (0, 0) # Remove outer padding for this screen
        self.current_student_courses_ids = set()
        self.selected_available_course = None
        self.selected_enrolled_course = None

        # --- Top Header ---
        # Use grid layout for more control over the header elements
        header_outer_frame = ttk.Frame(self, style="Header.TFrame", padding=(10, 5)) # Frame with bg color
        header_outer_frame.pack(fill=tk.X, side=tk.TOP)

        header_outer_frame.columnconfigure(0, weight=1) # Allow student info to expand

        self.student_info_label = ttk.Label(header_outer_frame, text="Student:", style="Info.TLabel")
        self.student_info_label.grid(row=0, column=0, sticky=tk.W, padx=(5,10))

        self.credits_label = ttk.Label(header_outer_frame, text="Credits: 0", style="Info.TLabel")
        self.credits_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))

        logout_btn = ttk.Button(header_outer_frame, text="Logout", command=controller.logout, width=8, style="TButton") # Use regular button style for contrast
        # Change button style for header
        style = ttk.Style()
        style.configure("Header.TButton", font=("Segoe UI", 9, "bold"), padding=(5, 2), foreground=self.controller.primary_color, background=self.controller.light_text_color)
        style.map("Header.TButton", background=[('active', self.controller.secondary_color)])
        logout_btn.config(style="Header.TButton")
        logout_btn.grid(row=0, column=2, sticky=tk.E, padx=(0,5))


        # --- Main Content Frame (below header) ---
        content_frame = ttk.Frame(self, padding=(15, 15, 15, 0)) # Add padding around content area
        content_frame.pack(fill=tk.BOTH, expand=True)

        # --- PanedWindow for resizable split ---
        paned_window = tk.PanedWindow(content_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, bg=controller.border_color, sashwidth=6, bd=0)
        paned_window.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # --- Available Courses Section ---
        available_outer_frame = ttk.Frame(paned_window, padding=0)  # Container for label frame + button
        available_frame = ttk.LabelFrame(available_outer_frame, text="Available Courses", padding=(10, 5))
        available_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))  # Label frame takes most space

        paned_window.add(available_outer_frame)

        cols = ('id', 'name', 'instructor', 'schedule', 'enrollment', 'credits')
        self.available_tree = ttk.Treeview(available_frame, columns=cols, show='headings', selectmode='browse')
        self.available_tree.heading('id', text='ID', anchor=tk.W)
        self.available_tree.heading('name', text='Name', anchor=tk.W)
        self.available_tree.heading('instructor', text='Instructor', anchor=tk.W)
        self.available_tree.heading('schedule', text='Schedule', anchor=tk.W)
        self.available_tree.heading('enrollment', text='Enrollment', anchor=tk.CENTER)
        self.available_tree.heading('credits', text='Credits', anchor=tk.CENTER)

        self.available_tree.column('id', width=80, stretch=False)
        self.available_tree.column('name', width=200)
        self.available_tree.column('instructor', width=150)
        self.available_tree.column('schedule', width=120)
        self.available_tree.column('enrollment', width=100, anchor=tk.CENTER)
        self.available_tree.column('credits', width=70, anchor=tk.CENTER)

        self.available_tree.pack(fill=tk.BOTH, expand=True)
        self.available_tree.bind('<<TreeviewSelect>>', self.on_available_course_select)

        enroll_button = ttk.Button(available_outer_frame, text="Enroll", command=self.enroll_selected_course, style="Accent.TButton", width=10)
        enroll_button.pack(pady=5, fill=tk.X)

        # --- Enrolled Courses Section ---
        enrolled_outer_frame = ttk.Frame(paned_window, padding=0)
        enrolled_frame = ttk.LabelFrame(enrolled_outer_frame, text="Enrolled Courses", padding=(10, 5))
        enrolled_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        paned_window.add(enrolled_outer_frame)

        cols_enrolled = ('id', 'name', 'instructor', 'schedule', 'credits')
        self.enrolled_tree = ttk.Treeview(enrolled_frame, columns=cols_enrolled, show='headings', selectmode='browse')
        self.enrolled_tree.heading('id', text='ID', anchor=tk.W)
        self.enrolled_tree.heading('name', text='Name', anchor=tk.W)
        self.enrolled_tree.heading('instructor', text='Instructor', anchor=tk.W)
        self.enrolled_tree.heading('schedule', text='Schedule', anchor=tk.W)
        self.enrolled_tree.heading('credits', text='Credits', anchor=tk.CENTER)

        self.enrolled_tree.column('id', width=80, stretch=False)
        self.enrolled_tree.column('name', width=250)
        self.enrolled_tree.column('instructor', width=150)
        self.enrolled_tree.column('schedule', width=120)
        self.enrolled_tree.column('credits', width=70, anchor=tk.CENTER)

        self.enrolled_tree.pack(fill=tk.BOTH, expand=True)
        self.enrolled_tree.bind('<<TreeviewSelect>>', self.on_enrolled_course_select)

        drop_button = ttk.Button(enrolled_outer_frame, text="Drop", command=self.drop_selected_course, style="TButton", width=10)
        drop_button.pack(pady=5, fill=tk.X)

        # Set initial sash position to divide space evenly
        controller.root.update_idletasks()  # Ensure the window is fully rendered before setting sash position
        paned_window.sash_place(0, controller.root.winfo_width() // 2, 0)  # Divide the window into two equal halves

        # --- Status Label at the bottom ---
        self.status_label = self.create_status_label(content_frame)
        self.status_label.pack(pady=(10, 0), fill=tk.X)

        # Add a button to view the timetable
        timetable_button = ttk.Button(content_frame, text="View Timetable", command=lambda: controller.show_frame("TimetableScreen"), style="TButton")
        timetable_button.pack(pady=(10, 0), fill=tk.X)

        # Initial data load will happen in refresh_data
        self.refresh_data()

    def refresh_data(self):
        if self.controller.current_student_id:
            student_id = self.controller.current_student_id
            try:
                student = self.system.students[student_id]
                self.student_info_label.config(text=f"Student: {student.name} ({student_id})")
                enrolled_courses = self.system.get_student_courses(student_id)
                self.current_student_courses_ids = {course.course_id for course in enrolled_courses}
                total_credits = sum(course.credits for course in enrolled_courses)
                self.credits_label.config(text=f"Credits: {total_credits}")

                available_courses = self.system.get_available_courses()

                # Populate Available Courses Treeview
                for item in self.available_tree.get_children():
                    self.available_tree.delete(item)
                for course in available_courses:
                    enrollment_status = f"{len(course.enrolled_students)}/{course.max_students}"
                    if course.course_id not in self.current_student_courses_ids:
                        self.available_tree.insert('', tk.END, values=(
                            course.course_id, course.name, course.instructor,
                            f"{course.schedule[0]} {course.schedule[1]}-{course.schedule[2]}",
                            enrollment_status, course.credits
                        ))

                # Populate Enrolled Courses Treeview
                for item in self.enrolled_tree.get_children():
                    self.enrolled_tree.delete(item)
                for course in enrolled_courses:
                    self.enrolled_tree.insert('', tk.END, values=(
                        course.course_id, course.name, course.instructor,
                        f"{course.schedule[0]} {course.schedule[1]}-{course.schedule[2]}",
                        course.credits
                    ))
                self.clear_status()

            except ValueError as e:
                self.controller.set_status("CourseScreen", str(e))
            except Exception as e:
                self.controller.set_status("CourseScreen", f"Error refreshing data: {e}")
        else:
            self.student_info_label.config(text="Student: Not Logged In")
            self.credits_label.config(text="Credits: 0")
            for item in self.available_tree.get_children():
                self.available_tree.delete(item)
            for item in self.enrolled_tree.get_children():
                self.enrolled_tree.delete(item)

    def on_available_course_select(self, event):
        selected_item = self.available_tree.focus()
        if selected_item:
            self.selected_available_course = self.available_tree.item(selected_item)['values'][0] # Get course ID
        else:
            self.selected_available_course = None

    def on_enrolled_course_select(self, event):
        selected_item = self.enrolled_tree.focus()
        if selected_item:
            self.selected_enrolled_course = self.enrolled_tree.item(selected_item)['values'][0] # Get course ID
        else:
            self.selected_enrolled_course = None

    def enroll_selected_course(self):
        if not self.controller.current_student_id:
            self.controller.set_status("CourseScreen", "Please log in to enroll in courses.")
            return
        if not self.selected_available_course:
            self.controller.set_status("CourseScreen", "Please select a course to enroll in.")
            return
        try:
            self.system.enroll_student(self.controller.current_student_id, self.selected_available_course)
            self.refresh_data()
            self.selected_available_course = None
        except ValueError as e:
            self.controller.set_status("CourseScreen", str(e))
        except Exception as e:
            self.controller.set_status("CourseScreen", f"Error enrolling in course: {e}")

    def drop_selected_course(self):
        if not self.controller.current_student_id:
            self.controller.set_status("CourseScreen", "Please log in to drop courses.")
            return
        if not self.selected_enrolled_course:
            self.controller.set_status("CourseScreen", "Please select a course to drop.")
            return
        try:
            self.system.drop_course(self.controller.current_student_id, self.selected_enrolled_course)
            self.refresh_data()
            self.selected_enrolled_course = None
        except ValueError as e:
            self.controller.set_status("CourseScreen", str(e))
        except Exception as e:
            self.controller.set_status("CourseScreen", f"Error dropping course: {e}")

class TimetableScreen(BaseScreen):
    """Screen to display the student's timetable."""
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.create_header("Student Timetable")

        # Timetable content frame
        timetable_frame = ttk.Frame(self.content_area, padding=(10, 10))
        timetable_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview for timetable
        cols = ('day', 'time', 'course', 'instructor', 'credits')
        self.timetable_tree = ttk.Treeview(timetable_frame, columns=cols, show='headings', selectmode='none')
        self.timetable_tree.heading('day', text='Day', anchor=tk.W)
        self.timetable_tree.heading('time', text='Time', anchor=tk.W)
        self.timetable_tree.heading('course', text='Course', anchor=tk.W)
        self.timetable_tree.heading('instructor', text='Instructor', anchor=tk.W)
        self.timetable_tree.heading('credits', text='Credits', anchor=tk.CENTER)

        self.timetable_tree.column('day', width=100, stretch=False)
        self.timetable_tree.column('time', width=150)
        self.timetable_tree.column('course', width=200)
        self.timetable_tree.column('instructor', width=150)
        self.timetable_tree.column('credits', width=70, anchor=tk.CENTER)

        self.timetable_tree.pack(fill=tk.BOTH, expand=True)

        # Back button to return to the enrollment page
        back_button = ttk.Button(timetable_frame, text="Back to Enrollment", command=lambda: controller.show_frame("CourseScreen"), style="TButton")
        back_button.pack(pady=10)

    def refresh_data(self):
        """Refresh the timetable data."""
        if self.controller.current_student_id:
            student_id = self.controller.current_student_id
            try:
                student = self.system.students[student_id]
                enrolled_courses = self.system.get_student_courses(student_id)

                # Clear existing timetable data
                for item in self.timetable_tree.get_children():
                    self.timetable_tree.delete(item)

                # Define the order of days
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

                # Sort courses by day (using the defined order) and time
                sorted_courses = sorted(
                    enrolled_courses,
                    key=lambda course: (day_order.index(course.schedule[0]), course.schedule[1])
                )

                # Populate timetable with sorted courses
                for course in sorted_courses:
                    day, start_time, end_time = course.schedule
                    self.timetable_tree.insert('', tk.END, values=(
                        day,
                        f"{start_time} - {end_time}",
                        course.name,
                        course.instructor,
                        course.credits
                    ))

                self.clear_status()
            except Exception as e:
                self.controller.set_status("TimetableScreen", f"Error loading timetable: {e}")
        else:
            self.controller.set_status("TimetableScreen", "No student logged in.")

if __name__ == "__main__":
    root = tk.Tk()
    enrollment_system = EnrollmentSystem()
    app = RegistrationApp(root, enrollment_system)
    root.mainloop()