import csv
import os
import argparse
import random
from faker import Faker

fake = Faker()

def generate_realistic_app_info(category):
    """Генерує реалістичну назву та опис залежно від категорії."""
    prefixes = {
        "Games": ["Epic", "Legend of", "Shadow", "Extreme", "Pixel", "Space", "Candy", "Angry", "Mega"],
        "Productivity": ["Smart", "Focus", "Easy", "Quick", "Pro", "Ultra", "Simple", "Cloud", "Daily"],
        "Finance": ["Safe", "Wallet", "Penny", "Gold", "Crypto", "Budget", "Tax", "Money", "Pocket"],
        "Social": ["Chat", "Connect", "Live", "Circle", "Link", "Vibe", "Talk", "Snap", "Friends"],
        "Education": ["Learn", "Academy", "Master", "Skill", "Quiz", "Brain", "Word", "Study", "Lingua"],
        "Tools": ["Turbo", "Cleaner", "Secure", "Master", "Fix", "Power", "Scan", "Guard", "Battery"]
    }
    
    suffixes = {
        "Games": ["Quest", "Saga", "Run", "Battle", "World", "Arena", "Hero", "Clicker", "Empire"],
        "Productivity": ["Task", "Editor", "Notes", "Planner", "Manager", "Do", "Organizer", "Flow"],
        "Finance": ["Pay", "Track", "Finance", "Vault", "Saver", "Invest", "Coin", "Bank", "Cash"],
        "Social": ["Messenger", "Network", "Social", "Stream", "Me", "Post", "Gram", "Hub", "Space"],
        "Education": ["Guide", "Language", "Tutor", "Course", "Lab", "Helper", "Study", "Cards"],
        "Tools": ["Utility", "Guard", "Tool", "Helper", "Boost", "App", "Expert", "Scanner", "Pro"]
    }

    cat_pref = random.choice(prefixes.get(category, ["My"]))
    cat_suff = random.choice(suffixes.get(category, ["App"]))
    
    formats = [
        f"{cat_pref} {fake.first_name()}", 
        f"{fake.last_name()} {cat_suff}",  
        f"{cat_pref} {cat_suff}",          
        f"{fake.color_name().capitalize()} {cat_suff}", 
        f"{cat_pref} {fake.word().capitalize()}"        
    ]
    title = random.choice(formats)
    
    description = f"Welcome to {title}! This is the ultimate {category} solution. {fake.paragraph(nb_sentences=2)}"
    
    return title, description

def generate_google_play_data(output_path, num_rows):
    categories = ["Games", "Productivity", "Finance", "Social", "Education", "Tools"]
    
    fieldnames = [
        'app_id', 'title', 'description', 'category', 'current_version', 'avg_rating', 
        'is_free', 'price', 'currency', 'contains_ads',
        'dev_id', 'dev_name', 'dev_email', 'company_name', 'dev_key',
        'version_tag', 'release_notes', 'upload_date',
        'review_author', 'review_comment', 'review_stars'
    ]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for _ in range(num_rows):
                category = random.choice(categories)
                title, description = generate_realistic_app_info(category)
                
                is_free = random.choice([True, False])
                price = 0.0 if is_free else round(random.uniform(0.99, 49.99), 2)
                
                writer.writerow({
                    'app_id': fake.uuid4(),
                    'title': title,
                    'description': description, 
                    'category': category,
                    'current_version': f"{random.randint(1, 12)}.{random.randint(0, 9)}",
                    'avg_rating': round(random.uniform(1.0, 5.0), 1),
                    'is_free': is_free,
                    'price': price,
                    'currency': 'USD' if not is_free else '',
                    'contains_ads': random.choice([True, False]),
                    
                    'dev_id': fake.uuid4(),
                    'dev_name': fake.name(),
                    'dev_email': fake.company_email(),
                    'company_name': fake.company(),
                    'dev_key': fake.sha256()[:16],
                    
                    'version_tag': f"v{random.randint(1, 5)}",
                    'release_notes': fake.sentence(),
                    'upload_date': fake.date_this_year().isoformat(),
                    
                    'review_author': fake.user_name(),
                    'review_comment': fake.text(max_nb_chars=100),
                    'review_stars': random.randint(1, 5)
                })
        
        print(f"✅ Успішно згенеровано {num_rows} рядків у: {output_path}")

    except Exception as e:
        print(f"❌ Помилка: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=1000)
    parser.add_argument('--output', type=str, default='data/google_play_data.csv')
    args = parser.parse_args()
    generate_google_play_data(args.output, args.count)