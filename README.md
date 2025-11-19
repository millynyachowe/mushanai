# Mushanai E-commerce Platform

An innovative eCommerce solution designed to promote local brands, build communities, and support tangible development projects. The platform connects customers, vendors, raw material suppliers, and ministries to foster sustainable buying, encourage local production, and drive economic growth.

## Features

### For Customers
- **Project Voting**: Contribute to community projects with every purchase
- **Default Voting Logic**: Automatic allocation to most popular project, with option to override
- **Customer Portal**: 
  - View purchased items with status and delivery updates
  - Track voted projects with funding progress and milestones
  - View abandoned carts and quick checkout
  - Social media points for sharing quality posts (admin-approved)
  - Loyalty program with points redemption

### For Vendors
- **Basic Dashboard**: Sales analytics, abandoned cart views
- **Advanced Dashboard**: Access to accounting, sales, inventory modules
- **Multi-company Integration**: Manage multiple business entities
- **Shared Logistics**: Collaborate with other vendors for cost-effective deliveries
- **Job Posting**: Integrated job board for recruitment
- **Cash Receipt Management**: Record walk-in client payments
- **Suppliers Access**: View raw material listings and descriptions

### For Raw Material Suppliers
- **Manual Management**: Admin-added supplier profiles
- **Material Listings**: Detailed descriptions with sustainability and origin information
- **Hidden Portal**: Secure access via Suppliers module

### For Ministries & Government
- **Analytics Dashboard**:
  - View vendor job postings
  - Track community project progress
  - Analyze material usage in manufacturing
  - Monitor search trends and unavailable items (skill gap identification)
  - Evaluate local brand growth and revenue
  - Access manufacturing skill shortage insights
- **Promotion Features**: Promote local products made from locally sourced materials

### For Administrators
- **Comprehensive Management**: Oversee all platform aspects
- **User Management**: Vendor and customer registrations
- **Social Media Approval**: Approve/reject customer posts for points
- **Fiscalization**: ZIMRA integration for fiscal compliance
- **Payment Systems**: EcoCash, TeleCash, and other mobile money platforms
- **Loyalty Management**: Points and rewards administration
- **Featured Products**: Approve and highlight products on homepage

## Technology Stack

- **Backend**: Django 4.2.25
- **API Framework**: Django REST Framework 3.16.1
- **Image Processing**: Pillow 11.3.0
- **CORS**: django-cors-headers 4.9.0
- **Database**: SQLite (development) / PostgreSQL (production recommended)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd mushanai
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**:
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
mushanai/
├── accounts/          # User management and authentication
├── customers/         # Customer-specific features and dashboards
├── vendors/           # Vendor portals and analytics
├── suppliers/         # Raw material suppliers management
├── ministries/        # Ministry dashboards and analytics
├── projects/          # Community projects and voting
├── products/          # Product catalog and inventory
├── orders/            # Shopping carts and orders
├── logistics/         # Shared delivery and route optimization
├── loyalty/           # Loyalty program and rewards
├── payments/          # Payment processing and fiscalization
└── mushanaicore/      # Main project settings
```

## Key Models

- **User**: Custom user model with user types (Customer, Vendor, Supplier, Ministry, Admin)
- **Product**: Product catalog with local material tracking
- **Order**: Orders with project voting integration
- **CommunityProject**: Community development projects
- **LoyaltyAccount**: Points tracking and rewards
- **PaymentTransaction**: Payment processing with fiscalization
- **DeliveryGroup**: Shared logistics coordination

## Development

### Environment Variables

Create a `.env` file (not included in repository) for sensitive settings:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `DATABASE_URL`: Database connection string
- Payment gateway credentials
- ZIMRA fiscalization credentials

### Running Tests

```bash
python manage.py test
```

## Deployment Considerations

- Use PostgreSQL for production
- Configure proper media file storage (S3, Azure Blob, etc.)
- Set up proper CORS settings
- Configure payment gateway credentials
- Set up ZIMRA fiscalization integration
- Enable HTTPS
- Configure proper static file serving

## Contributing

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Submit a pull request

## License

[Add your license here]

## Support

For support and inquiries, please contact [your contact information]
