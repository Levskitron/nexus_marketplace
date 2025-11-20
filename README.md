# Nexus Marketplace  
*A PC Parts & Gaming Marketplace — HND Final Project*

The **Nexus Marketplace** is the final project for the **HND Professional Practice in Software Development** module.  
It is a full-stack web application designed for users to:

- Buy and sell **PC parts**
- Browse and purchase **games and accessories**
- Request **build services**, including:
  - Custom prebuilts
  - PC repairs
  - Upgrades
  - Hardware consultation

This project is built collaboratively by a 5-member development team, combining backend engineering, frontend design, and professional workflow practices.

---

## 👥 Team Members

### **Tristan Duffy — Team Leader & Front-End Developer**
- N/A  

### **Levi Mair — Full Stack Developer**
- Backend architecture  
- Database design & integration  
- Initial project setup & GitHub repository management  
- Blueprint structure and HTML base template implementation  

### **Aidan Gibb — Front-End Developer**
- N/A 

### **Imdad Chaklader — Front-End Developer**
- N/A 

### **Nathan Morgan — Front-End Developer**
- N/A 

---

## 🛠️ Tech Stack

### **Backend**
- **Python 3**
- **Flask**
- **Flask-SQLAlchemy** 
- **Flask-WTF / WTForms**
- **Werkzeug**

### **Database**
- SQLite

### **Frontend**
- HTML5  
- CSS3
- Jinja2  
- JavaScript

### **Other Tools**
- Git & GitHub
- Visual Studio Code

---

## 📁 Project Structure
```
nexus_marketplace/
│
├── app.py
├── models.py
├── forms.py
├── database.py
├── config.py
├── requirements.txt
├── .gitignore
│
├── blueprints/
│ ├── auth/
│ ├── home/
│ ├── shop/
│ └── account/
│
├── templates/
│ ├── base.html
│ ├── components/
│ ├── auth/
│ ├── home/
│ ├── shop/
│ └── account/
│
├── static/
│ ├── css/
│ ├── js/
│ └── images/
│
├── instance/
│ └── nexus.db
```

--- 

## 🚀 How to Run the Project Locally

1. Install dependencies:
   ```pip install -r requirements.txt```

2. Run the Flask app:
   ```python app.py```

3. Open your browser and visit:
   ```http://127.0.0.1:5000/```

---

## 📜 License

This project is licensed under the **PolyForm Noncommercial License 1.0.0**.

This means:

- You may **use**, **modify**, and **share** the project freely  
- You may **not** use the project for any **commercial purposes**  
- This includes selling, offering paid services, or using it within a commercial product  

For full details, see the license text:  
https://polyformproject.org/licenses/noncommercial/1.0.0/
