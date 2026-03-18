from flask import render_template, request, redirect, url_for, flash
from app import app, service
import uuid
@app.route('/')
def index():
    categories = service.get_all_categories()
    developers = service.get_all_developers()
    stats = service.get_statistics()
    
    return render_template('dashboard.html', 
                           categories=categories, 
                           developers=developers, 
                           stats=stats)

@app.route('/apps')
def list_apps():
    category_id = request.args.get('category_id')
    search_query = request.args.get('query', '').strip()
    
    if category_id:
        apps = service.get_apps_by_category(category_id)
        cat = next((c for c in service.get_all_categories() if str(c.category_id) == str(category_id)), None)
        title = f"Категорія: {cat.name}" if cat else "Додатки"
    else:
        apps = service.get_all_apps()
        title = "Всі додатки системи"
    
    if search_query:
        apps = [a for a in apps if search_query.lower() in a.title.lower()]
        title = f"Пошук: '{search_query}'"
        
    return render_template('index.html', 
                           apps=apps, 
                           title=title, 
                           stats=f"Знайдено: {len(apps)} шт.")

@app.route('/app/<string:app_id>')
def details(app_id):
    target_app = service.get_app_by_id(app_id)
    if not target_app:
        return "Додаток не знайдено", 404
    
    return render_template('details.html', app=target_app)


@app.route('/app/edit/<string:app_id>', methods=['GET', 'POST'])
def edit_app(app_id):
    target_app = service.get_app_by_id(app_id)
    
    if request.method == 'POST':
        new_data = {
            'title': request.form['title'],
            'price': request.form.get('price', 0)
        }
        service.update_application(app_id, new_data)

        flash(f"Зміни в '{new_data['title']}' збережено!", "info")

        return redirect(url_for('index'))
    
    return render_template('app_form.html', 
                           app=target_app,
                           categories=service.get_all_categories(),
                           developers=service.get_all_developers())




@app.route('/transactions')
def transactions():
    transactions = service._repository.get_all_transactions() 
    return render_template('transactions.html', transactions=transactions)


@app.route('/developer/<int:dev_id>')
def developer_profile(dev_id):
    developers = service.get_all_developers()
    dev = next((d for d in developers if d.user_id == dev_id), None)
    
    if not dev:
        return "Розробника не знайдено", 404
        
    return render_template('dev_details.html', dev=dev)

@app.route('/developers')
def list_developers():
    devs = service.get_all_developers()
    return render_template('dev_list.html', developers=devs)

@app.route('/developer/create', methods=['GET', 'POST'])
def create_developer():
    if request.method == 'POST':
        data = {
            'company_name': request.form['company_name'],
            'email': request.form['email'],
            'dev_key': request.form['dev_key'] or str(uuid.uuid4())[:16]
        }
        service.create_developer(data)
        return redirect(url_for('list_developers'))
    
    return render_template('dev_form.html')


@app.route('/app/purchase/<string:app_id>', methods=['POST'])
def purchase(app_id):
    role = request.args.get('role', 'admin')
    target_app = service.get_app_by_id(app_id)
    service.simulate_purchase(target_app)
    
    return redirect(url_for('details', app_id=app_id, role=role))

@app.route('/app/<string:app_id>/review', methods=['POST'])
def add_review(app_id):
    role = request.args.get('role', 'admin')
    data = {
        'app_id': app_id,
        'stars': int(request.form.get('stars', 5)),
        'comment': request.form.get('comment', '')
    }
    service.add_user_review(data)
    
    return redirect(url_for('details', app_id=app_id, role=role))

@app.route('/app/create', methods=['GET', 'POST'])
def create():
    role = request.args.get('role', 'admin')
    if request.method == 'POST':
        data = {
            'title': request.form['title'],
            'is_free': request.form['is_free'] == 'true',
            'category_id': request.form['category_id'],
            'developer_id': request.form['developer_id'],
            'price': request.form.get('price', 0)
        }
        service.create_application(data)

        flash(f"Додаток '{data['title']}' успішно створено!", "success")

        return redirect(url_for('index', role=role))
    
    return render_template('app_form.html', 
                           categories=service.get_all_categories(),
                           developers=service.get_all_developers())

@app.route('/app/delete/<string:app_id>')
def delete(app_id):
    role = request.args.get('role', 'admin')
    service.delete_application(app_id)

    flash("Додаток було видалено із системи.", "warning") 

    return redirect(url_for('index', role=role))

@app.route('/user/create', methods=['GET', 'POST'])
def create_user():
    role = request.args.get('role', 'admin')
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if role == 'customer':
            data = {
                'email': email,
                'password': password,
                'payment_method': request.form['payment_method']
            }
            success, message = service.create_customer(data)
        else:
            data = {
                'email': email,
                'password': password,
                'company_name': request.form['company_name'],
                'dev_key': request.form.get('dev_key') or str(uuid.uuid4())[:12]
            }
            success, message = service.create_developer(data)

        if success:
            flash(message, "success")
            return redirect(url_for('list_developers' if role != 'customer' else 'index'))
        else:
            flash(message, "danger")
            return render_template('user_form.html', role=role)
            
    return render_template('user_form.html', role=role)
