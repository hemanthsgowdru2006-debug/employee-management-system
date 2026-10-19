import os
from datetime import date
from functools import wraps
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()
login_manager = LoginManager()

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), default="")
    employees = db.relationship("Employee", back_populates="department")

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    phone = db.Column(db.String(30), default="")
    designation = db.Column(db.String(120), default="")
    salary = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    joining_date = db.Column(db.Date, nullable=False, default=date.today)
    department_id = db.Column(db.Integer, db.ForeignKey("department.id"), nullable=True)
    department = db.relationship("Department", back_populates="employees")

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-only-change-this-secret"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///employee_management.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config: app.config.update(test_config)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id): return db.session.get(Admin, int(user_id))

    def protected(fn):
        @wraps(fn)
        @login_required
        def wrapper(*args, **kwargs): return fn(*args, **kwargs)
        return wrapper

    @app.get("/")
    def index():
        return redirect(url_for("dashboard" if current_user.is_authenticated else "login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated: return redirect(url_for("dashboard"))
        if request.method == "POST":
            admin = Admin.query.filter_by(username=request.form.get("username", "").strip()).first()
            if admin and admin.check_password(request.form.get("password", "")):
                login_user(admin)
                flash("Welcome back!", "success")
                return redirect(url_for("dashboard"))
            flash("Invalid username or password.", "danger")
        return render_template("login.html")

    @app.post("/logout")
    @protected
    def logout():
        logout_user()
        return redirect(url_for("login"))

    @app.get("/dashboard")
    @protected
    def dashboard():
        return render_template("dashboard.html", employee_count=Employee.query.count(),
            department_count=Department.query.count(),
            latest_employees=Employee.query.order_by(Employee.id.desc()).limit(5).all())

    @app.get("/employees")
    @protected
    def employees():
        search = request.args.get("q", "").strip()
        query = Employee.query
        if search:
            pattern = f"%{search}%"
            query = query.filter(db.or_(Employee.name.ilike(pattern), Employee.email.ilike(pattern),
                                        Employee.designation.ilike(pattern)))
        return render_template("employees.html", employees=query.order_by(Employee.id.desc()).all(), search=search)

    @app.route("/employees/new", methods=["GET", "POST"])
    @app.route("/employees/<int:employee_id>/edit", methods=["GET", "POST"])
    @protected
    def employee_form(employee_id=None):
        employee = db.session.get(Employee, employee_id) if employee_id else Employee()
        if employee_id and not employee:
            flash("Employee not found.", "warning")
            return redirect(url_for("employees"))
        departments = Department.query.order_by(Department.name).all()
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            try:
                salary = float(request.form.get("salary") or 0)
                joining = date.fromisoformat(request.form.get("joining_date") or date.today().isoformat())
                dept_text = request.form.get("department_id", "").strip()
                dept_id = int(dept_text) if dept_text else None
                if salary < 0: raise ValueError
            except (ValueError, TypeError):
                flash("Enter valid salary, date, and department values.", "danger")
                return render_template("employee_form.html", employee=employee, departments=departments)
            if not name or "@" not in email:
                flash("Enter a name and valid email.", "danger")
                return render_template("employee_form.html", employee=employee, departments=departments)
            duplicate = Employee.query.filter(Employee.email == email, Employee.id != employee.id).first()
            if duplicate:
                flash("That email is already registered.", "danger")
                return render_template("employee_form.html", employee=employee, departments=departments)
            employee.name, employee.email = name, email
            employee.phone = request.form.get("phone", "").strip()
            employee.designation = request.form.get("designation", "").strip()
            employee.salary, employee.joining_date, employee.department_id = salary, joining, dept_id
            db.session.add(employee)
            db.session.commit()
            flash("Employee saved successfully.", "success")
            return redirect(url_for("employees"))
        return render_template("employee_form.html", employee=employee, departments=departments)

    @app.post("/employees/<int:employee_id>/delete")
    @protected
    def delete_employee(employee_id):
        employee = db.session.get(Employee, employee_id)
        if employee:
            db.session.delete(employee)
            db.session.commit()
            flash("Employee deleted.", "success")
        return redirect(url_for("employees"))

    @app.route("/departments", methods=["GET", "POST"])
    @protected
    def departments():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            description = request.form.get("description", "").strip()
            if not name:
                flash("Department name is required.", "danger")
            elif Department.query.filter(db.func.lower(Department.name) == name.lower()).first():
                flash("Department already exists.", "warning")
            else:
                db.session.add(Department(name=name, description=description))
                db.session.commit()
                flash("Department added.", "success")
            return redirect(url_for("departments"))
        return render_template("departments.html", departments=Department.query.order_by(Department.name).all())

    @app.post("/departments/<int:department_id>/delete")
    @protected
    def delete_department(department_id):
        department = db.session.get(Department, department_id)
        if department:
            for employee in department.employees: employee.department_id = None
            db.session.delete(department)
            db.session.commit()
            flash("Department deleted; employees were retained.", "success")
        return redirect(url_for("departments"))

    @app.get("/health")
    def health():
        try:
            db.session.execute(db.text("SELECT 1"))
            return jsonify(status="ok", database="connected"), 200
        except Exception:
            db.session.rollback()
            return jsonify(status="error", database="unavailable"), 503

    with app.app_context():
        db.create_all()
        if Admin.query.count() == 0:
            admin = Admin(username=os.getenv("ADMIN_USERNAME", "admin"))
            admin.set_password(os.getenv("ADMIN_PASSWORD", "Admin123!"))
            db.session.add(admin)
            if Department.query.count() == 0:
                db.session.add_all([Department(name="Engineering"), Department(name="Human Resources"),
                                    Department(name="Finance")])
            db.session.commit()
    return app

app = create_app()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
