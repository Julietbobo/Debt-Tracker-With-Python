#  Debt Tracker – Personal Project Summary

## 💡 Project Overview  
Developed a full-stack debt tracking web application using **Python (Streamlit)** and **MySQL** to help small-scale vendors (e.g., mama mbogas, shopkeepers) record, track, and manage customer debts. Connected the app (hosted on Streamlit Community Cloud) to a MySQL database server deployed on Google Cloud Virtual Machine, enabling secure login, debt recording, real-time payment tracking, and interactive dashboards.

---

## ⚙️ Tech stack
- **Python** – Main programming language for logic and backend connection
- **Streamlit** – For building the interactive web interface
- **pandas** – Used for processing SQL results and displaying data
- **MySQL** – Backend database for users, debts, and payments and a trigger for deleting debtors who clear their debts
- **bcrypt** – For secure password encryption
- **Google Cloud Platform (GCP)** – Hosted on Compute Engine (VM instance)

**MySQL Tables:**
- `users`: stores first name, last name, phone number, hashed password
- `debts`: records customer name, product, total, paid/unpaid amount, date
- `payments`: logs customer payments linked to specific debts

---

## Key Functionalities
-  User registration & login with password hashing (`bcrypt`)
-  Add, edit, delete, and view debts (CRUD)
-  Real-time debt and payment updates
-  Dashboard with KPIs: total debt, paid amounts, active debtors
-  Data displayS using `pandas.DataFrame` for readability
-  Session handling using `st.session_state`

---

## Technical Highlights
- Connected to **MySQL** using `mysql.connector` with secure, parameterized queries
- Performed SQL queries with aggregation (`SUM`, `COUNT`, `GROUP BY`) for KPIs
- Cleaned and presented SQL data using **pandas** for real-time UI updates
- Deployed the app on a **Google Cloud VM**, with port configuration and firewall settings
- Modularized app features into navigable pages using session routing

---

## Challenges & Limitations
-  **Concurrency**: Streamlit handles single-threaded users, which limits scalability
-  **Performance**: Multiple real-time SQL queries caused lag on GCP's free-tier VM
-  **Session Complexity**: Maintaining login state and navigation required careful `st.session_state` logic
-  **No role-based access**: All users had the same level of access
-  **Manual Hosting**: Required configuring GCP instance, firewall rules, and VM runtime setup

---

## Skills Demonstrated
-  **Database design** and schema creation (normalized tables)
-  **SQL for analysis** – joins, grouping, aggregation
-  **Backend integration** – secure Python ↔ MySQL connection
-  **Data processing with pandas** – transforming and displaying real-time results


---

## Project Outcomes
- Built and deployed a working app that mimics real-world debt tracking
- Practiced full-stack development from schema design to frontend UI
- Strengthened **MySQL, pandas**, and **Streamlit** skills in a practical, real-use case
- Gained hands-on experience deploying web apps via **Google Cloud Platform**

---



