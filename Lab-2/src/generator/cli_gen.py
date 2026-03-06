import csv
import os
import argparse
import random
from faker import Faker

fake = Faker()

def generate_google_play_data(output_path, num_rows):
    """Генерує випадкові дані для Google Play Store на основі діаграми класів."""
    
    categories = ["Games", "Productivity", "Finance", "Social", "Education", "Tools"]
    
    fieldnames = [
        'app_id', 'title', 'category', 'current_version', 'avg_rating', 
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

            for i in range(num_rows):
                is_free = random.choice([True, False])
                price = 0.0 if is_free else round(random.uniform(0.99, 49.99), 2)
                
                writer.writerow({
                    'app_id': fake.uuid4(),
                    'title': fake.catch_phrase(),
                    'category': random.choice(categories),
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
        
        print(f"✅ Успішно згенеровано {num_rows} рядків у файл: {output_path}")

    except Exception as e:
        print(f"❌ Помилка під час генерації: {e}")

def main():
    parser = argparse.ArgumentParser(description="Генератор даних для Google Play Store Lab.")
    parser.add_argument(
        '--count', 
        type=int, 
        default=1000, 
        help="Кількість рядків для генерації (мінімум 1000 за ТЗ)."
    )
    parser.add_argument(
        '--output', 
        type=str, 
        default='Lab-2/data/google_play_data.csv', 
        help="Шлях до вихідного CSV файлу."
    )

    args = parser.parse_args()

    if args.count < 1000:
        print("⚠️ Увага: Завдання вимагає мінімум 1000 рядків. Встановлюю 1000.")
        args.count = 1000

    generate_google_play_data(args.output, args.count)

if __name__ == "__main__":
    main()