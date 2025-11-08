# Huong Duong (Sunflower) Project

Huong Duong is an e-commerce web application built to support a social-enterprise initiative selling handmade knitted and crocheted crafts created by people with disabilities. The site connects artisans with customers, provides an accessible shopping experience, and helps create sustainable income and dignity for contributors.

## Table of Contents
- [Mission](#mission)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Demo / Screenshots](#demo--screenshots)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Run Locally](#run-locally)
- [Usage](#usage)
- [How to Support the Artisans](#how-to-support-the-artisans)
- [Accessibility & Social Impact](#accessibility--social-impact)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Mission
To empower people with disabilities by creating a marketplace for handcrafted yarn-based products. Huong Duong promotes economic inclusion, preserves handicraft skills, and raises awareness about the abilities and potential of artisans with disabilities.

## Key Features
- Product catalog with categories and search
- Product pages with photos, descriptions, price, and artisan profile
- Shopping cart and checkout flow
- Vendor / artisan profiles and stories
- Admin dashboard for product and order management
- Order tracking and email notifications
- Basic analytics for sales and impact reporting
- Accessibility features: keyboard navigation, ARIA labels, readable contrast
- Responsive layout for desktop and mobile
- (Optional) Multi-language support

## Tech Stack
Replace these with the actual stack used in the repository:
- Frontend: React / Vue / plain HTML + CSS (replace as appropriate)
- Backend: Node.js + Express / Django / Laravel / Flask (replace as appropriate)
- Database: PostgreSQL / MySQL / SQLite / MongoDB (replace)
- Authentication: JWT / OAuth / Session-based (replace)
- Payments: Stripe / PayPal (optional)
- Deployment: Vercel / Netlify / Heroku / Docker

## Demo / Screenshots
Add screenshots or a link to a live demo here:
- Live demo: https://your-live-site.example.com (replace)
- Screenshots: /docs/screenshots/*.png (add files to the repo)

## Getting Started

### Prerequisites
- Git
- Node.js and npm (if using Node)
- Python + pip (if using Django/Flask)
- Docker (optional)
- A database server (Postgres, MySQL, or SQLite for local development)

### Installation
Clone the repository:
```bash
git clone https://github.com/VNthcong520712/Huong-Duong_project.git
cd Huong-Duong_project
```

Install dependencies (example for Node.js):
```bash
# from project root
npm install
```

Or for a Python/Django project:
```bash
python -m venv venv
source venv/bin/activate  # macOS / Linux
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file in the project root and add required environment variables. Example variables (customize for your stack):
```
# Example
PORT=3000
DATABASE_URL=postgres://user:password@localhost:5432/huongduong
SECRET_KEY=replace_with_a_secure_key
STRIPE_SECRET_KEY=sk_test_xxx
SMTP_HOST=smtp.example.com
SMTP_USER=example@example.com
SMTP_PASS=supersecret
```

### Run Locally

For Node.js / Express (example):
```bash
npm run dev          # or: npm start
```

For a Django project:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Or using Docker Compose if a docker-compose.yml is provided:
```bash
docker-compose up --build
```

Open http://localhost:3000 or http://127.0.0.1:8000 in your browser (depending on the port).

## Usage
- Browse products and artisan profiles
- Add items to cart and checkout
- Admins can add products, manage orders, and view simple impact metrics
- Use the artisan profile pages to learn about each maker and their story

## How to Support the Artisans
- Purchase items from the shop
- Share the project on social media
- Donate materials or funds
- Volunteer time to help with training, product photography, or order fulfillment
- Partner with local businesses to showcase and sell products offline

## Accessibility & Social Impact
This project aims to be accessible and inclusive:
- Semantic HTML and ARIA attributes
- Keyboard navigable UI
- Clear focus states and high color contrast
- Simple language and readable layout to accommodate different needs

The social impact goal is to provide predictable income, upskill artisans, and increase community awareness about disability inclusion.

## Contributing
Contributions are welcome. Suggested workflow:
1. Fork the repository
2. Create a feature branch: git checkout -b feature/your-feature
3. Make changes and add tests
4. Commit and push: git push origin feature/your-feature
5. Open a Pull Request explaining the change and its purpose

Please follow the coding standards used in the project and include a short description of your changes in the PR.

## License
This repository is offered under the MIT License. Replace with the correct license file if different.

## Contact
Project owner: VNthcong520712  
GitHub: https://github.com/VNthcong520712
