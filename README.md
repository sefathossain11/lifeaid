# LifeAid 🚑

### Empowering Hospitals, Patients, and Healthcare Professionals 🌟

LifeAid is a dynamic online platform designed to streamline hospital operations and enhance patient care by enabling seamless tracking, monitoring, and sharing of health records. Patients can easily connect with doctors, book appointments, purchase medicines, and even pay for laboratory tests through an integrated system. 💊💉

> **This is a Software Engineering project for B.Sc. in Computer Science and Engineering (CSE).**

---

## 🌟 Features

### **Users**: 
- **Patients**
- **Doctors**
- **Hospital Admins**
- **Lab Workers**
- **Pharmacists**

### **Patient Features** 🩺
1. Search hospitals and departments, view doctor profiles.
2. Book appointments and receive email confirmations. 📩
3. Pay for appointments and laboratory tests (cart system included). 💳
4. Chat with appointed doctors. 💬
5. View and download prescriptions and test reports (PDF format).
6. Search for and purchase medicines online with a secure payment system. 🛒
7. Provide reviews for doctors. ⭐

### **Doctor Features** 👨‍⚕️
1. Manage profiles and upload credentials.
2. Register with hospitals and get verified by admins.
3. Accept or reject patient appointments with email notifications.
4. Create and view prescriptions and patient reports.
5. Chat with patients. 💬

### **Hospital Admin Features** 🏥
1. Dashboard for managing operations.
2. Approve or reject doctor registrations.
3. Add, edit, or delete hospitals, departments, lab workers, and pharmacists.

### **Lab Worker Features** 🧪
1. Create and manage patient reports.
2. Add, edit, or view lab tests for hospitals.

### **Pharmacist Features** 💊
1. Manage medicines (add/edit/delete).
2. Process and track medicine orders.

---

## 🚀 Tools & Technologies

### **Programming Language and Libraries**
- Django (Python web framework) 🐍
- Bootstrap, JavaScript, Ajax
- Django REST Framework (DRF)

### **Database**
- SQLite 🗄️

### **APIs & Libraries**
- [Mailtrap](https://mailtrap.io/) - For email testing 📧
- [SSLCommerz](https://sslcommerz.com/) - Payment gateway integration 💳
- Django PDF library - Generate PDF documents 🖨️
- Django Channels - Enable real-time chat functionality 💬
- [xhtml2pdf](https://xhtml2pdf.readthedocs.io/) - For PDF creation 📄
- Ngrok - HTTP tunneling for testing 🌐

---

## 🛠️ Installation and Setup

1. **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Activate environment
    ```

2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set up environment variables**:
    - Copy `.env.example` to `.env`.
    - Add your credentials (Mailtrap, SSLCommerz, etc.) and a secret key.

4. **Migrate the database**:
    ```bash
    python manage.py migrate
    ```

5. **Run the server**:
    ```bash
    python manage.py runserver
    ```

---

## 📂 Folder Structure
```
LifeAid/
├── manage.py
├── db.sqlite3
├── requirements.txt
├── .env.example
├── LifeAidApp/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│       └── ...
└── static/
    └── ...
```

---

## 💡 Key Highlights

- **User-Friendly Interface**: Optimized for accessibility and responsiveness. 📱
- **Secure Transactions**: Integrated with SSLCommerz for secure payments. 🔒
- **Scalable Architecture**: Built with Django REST Framework for modularity and scalability. 🔗
- **Real-Time Communication**: Chat functionality powered by Django Channels. 💬
- **PDF Support**: Generate prescriptions and reports on the go. 🖨️

---

## 🤝 Contribution Guidelines

1. Fork the repository.
2. Clone your forked repository.
3. Create a feature branch.
4. Commit your changes.
5. Push your branch and create a pull request.

---

<!-- ## 📸 Screenshots

### **Home Page**
![Home Page](https://user-images.githubusercontent.com/64092765/191188204-39dc320f-ec0f-4634-a8db-4735fd89cec9.png)

### **Patient Dashboard**
![Patient Dashboard](https://user-images.githubusercontent.com/64092765/191187372-0ea1bc75-aeee-4d2a-8624-27877d213753.png)

### **Doctor Dashboard**
![Doctor Dashboard](https://user-images.githubusercontent.com/64092765/191187476-aae75261-0298-4d13-bc19-d2db8918c1f6.png)

-->

---

## 🙌 Acknowledgments

Special thanks to:
- **Team Members** for their dedication and hard work.
- **Mentors and Professors** for their guidance.
- Open-source libraries and tools that made this project possible.

---

### 🌟 Let’s Build a Better Healthcare System Together!
