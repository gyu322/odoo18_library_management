# Library Management System

A comprehensive library management system for Odoo 18.0 that provides core functionality for managing books, members, and borrowing records.

## Features

### =Ú Book Management
- Book catalog with title, author, ISBN, publisher information
- Stock management with available/total copies tracking
- Book categories and search functionality
- Automatic availability updates

### =e Member Management  
- Member registration with contact details
- Member status management (Active/Inactive/Pending)
- Borrowing limit controls based on member status
- Member statistics and borrowing history
- Automated member status review

### =Ö Borrowing Records
- Complete borrowing workflow (borrow ’ return)
- Automatic overdue detection and fine calculation
- Due date tracking and notifications
- Borrowing history and statistics
- Automated cron jobs for status updates

### =h=¼ Librarian Management
- Librarian profiles with roles and permissions
- Department and position tracking
- Integration with borrowing workflow

## Installation

### Prerequisites
- Odoo 18.0
- Python 3.8+

### Steps
1. Clone this repository to your Odoo addons directory:
   ```bash
   cd /path/to/odoo/addons
   git clone https://github.com/yourusername/library_management_1.git
   ```

2. Restart your Odoo server

3. Go to Apps ’ Update Apps List

4. Search for "Library Management System" and install

## Configuration

### Initial Setup
1. Create librarian records in **Library ’ Configuration ’ Librarians**
2. Add book categories if needed
3. Configure member statuses and borrowing limits

### Automated Tasks
The module includes automated cron jobs:
- **Daily**: Update overdue records and calculate fines
- **Weekly**: Review member statuses

## Usage

### For Administrators
- Manage books, members, and librarians through the main menu
- Monitor borrowing statistics and overdue books
- Configure system parameters

### For Librarians  
- Process book borrowing and returns
- Manage member accounts
- Handle fine calculations

## Technical Details

### Models
- `library.book` - Book catalog
- `library.member` - Member management
- `library.borrowing.record` - Borrowing transactions
- `library.librarian` - Staff management

### Key Features
- Automated sequence generation
- Smart constrains and validations
- Computed fields for statistics
- Email notifications (ready for extension)

## API & Extensions

This module is designed to be extended. Key extension points:

### Inheritable Models
All models support inheritance for adding custom fields and methods.

### Portal Integration Ready
Models include computed fields and methods that can be used by portal extensions.

### Mail Integration Ready  
Core models inherit from `mail.thread` for activity tracking.

## Support

For issues and feature requests, please use the GitHub issue tracker.

## License

This module is licensed under LGPL-3.0.

## Version History

### 1.0.0
- Initial release
- Core library management functionality
- Member and book management
- Borrowing workflow with fines

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.