# CourseRegistration_System
A desktop application built with **Python** and **Tkinter** for managing student course registration.

---

## Features

* **Student Management**: Add new students and log in with an existing student ID and name.
* **Course Browsing**: View a list of all available courses, including details like instructor, schedule, and credit hours.
* **Enrollment & Dropping**: Easily enroll in and drop courses with real-time feedback.
* **Validation & Conflict Checking**: The system prevents enrollment in full courses, detects schedule conflicts, and ensures students do not exceed the maximum credit limit (18 credits) or fall below the minimum (9 credits) after dropping.
* **Personal Timetable**: A dedicated screen to view a clear, organized timetable of all registered courses.
* **Data Persistence**: All student, course, and enrollment data is saved to and loaded from local CSV files, so information is retained between sessions.

---

## How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2. Run the Application

```bash
python "Course registration app.py"
```

> The application will create a `data/` folder and pre-populate it with hypothetical course data if no data files exist.

---

## File Structure

```
Course registration app.py    # Main application file containing all logic and GUI
data/                        # Directory automatically created to store all data
 ├─ students.csv             # Stores student IDs and names
 ├─ courses.csv              # Stores course details, including schedule, capacity, and credits
 └─ enrollments.csv          # Stores links between students and enrolled courses
```

---

## Dependencies

* Python's built-in **tkinter** library.
* No external packages required.

---

