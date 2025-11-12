from odoo import fields, models, api
from odoo.exceptions import ValidationError
import re


class Librarian(models.Model):
    _name = 'library.librarian'
    _description = 'Library Librarian'
    _sql_constraints = [
        ('unique_employee_id', 'UNIQUE(employee_id)', 'Employee ID must be unique! This employee ID is already registered.')
    ]

    name = fields.Char(string='Name', required=True)
    employee_id = fields.Char(string='Employee ID', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone Number')
    hire_date = fields.Date(string='Hire Date', default=fields.Date.today, required=True)
    active = fields.Boolean(string='Active', default=True)
    
    # Additional fields for better management
    department = fields.Selection([
        ('circulation', 'Circulation'),
        ('reference', 'Reference'),
        ('cataloging', 'Cataloging'),
        ('administration', 'Administration')
    ], string='Department', default='circulation')
    
    position = fields.Selection([
        ('librarian', 'Librarian'),
        ('senior_librarian', 'Senior Librarian'),
        ('head_librarian', 'Head Librarian'),
        ('assistant', 'Library Assistant')
    ], string='Position', default='librarian')
    
    # Computed fields
    years_of_service = fields.Float(string='Years of Service', compute='_compute_years_of_service', store=True)
    managed_borrowings = fields.One2many('library.borrowing.record', 'librarian_id', string='Managed Borrowings')
    total_managed_borrowings = fields.Integer(string='Total Managed Borrowings', compute='_compute_statistics')
    
    @api.depends('hire_date')
    def _compute_years_of_service(self):
        """Calculate years of service based on hire date"""
        for librarian in self:
            if librarian.hire_date:
                today = fields.Date.today()
                delta = today - librarian.hire_date
                librarian.years_of_service = round(delta.days / 365.25, 1)
            else:
                librarian.years_of_service = 0
    
    @api.depends('managed_borrowings')
    def _compute_statistics(self):
        """Compute statistics for librarian performance"""
        for librarian in self:
            librarian.total_managed_borrowings = len(librarian.managed_borrowings)
    
    @api.constrains('employee_id')
    def _check_employee_id_format(self):
        """Validate employee ID format"""
        for record in self:
            if record.employee_id:
                # Check if employee ID follows a pattern (e.g., LIB001, LIB002)
                if not re.match(r'^LIB\d{3,}$', record.employee_id):
                    raise ValidationError(
                        f"Employee ID '{record.employee_id}' must follow the format 'LIBxxx' where xxx is a number (e.g., LIB001, LIB123)."
                    )
    
    @api.constrains('email')
    def _check_email_format(self):
        """Validate email format"""
        for record in self:
            if record.email:
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, record.email):
                    raise ValidationError(
                        f"Please enter a valid email address. '{record.email}' is not a valid email format."
                    )
    
    # Phone validation commented out to allow international formats
    # @api.constrains('phone')
    # def _check_phone_format(self):
    #     """Validate phone number format"""
    #     for record in self:
    #         if record.phone:
    #             # Allow various phone formats: +60123456789, 0123456789, 123456789
    #             phone_pattern = r'^(\+?6?0?)(\d{8,10})$'
    #             if not re.match(phone_pattern, record.phone.replace('-', '').replace(' ', '')):
    #                 raise ValidationError(
    #                     f"Please enter a valid phone number. '{record.phone}' is not a valid phone format."
    #                 )
    
    @api.constrains('hire_date')
    def _check_hire_date(self):
        """Validate hire date is not in the future"""
        for record in self:
            if record.hire_date and record.hire_date > fields.Date.today():
                raise ValidationError(
                    "Hire date cannot be in the future. Please enter a valid hire date."
                )
    
    def name_get(self):
        """Custom name display: Name (Employee ID)"""
        result = []
        for librarian in self:
            name = f"{librarian.name} ({librarian.employee_id})"
            result.append((librarian.id, name))
        return result
    
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, order=None):
        """Allow searching by name or employee ID"""
        if args is None:
            args = []
        
        if name:
            # Search by name or employee ID
            domain = [
                '|',
                ('name', operator, name),
                ('employee_id', operator, name)
            ]
            return self._search(domain + args, limit=limit, order=order)
        
        return super()._name_search(name=name, args=args, operator=operator, limit=limit, order=order)
    
    def action_view_managed_borrowings(self):
        """Action to view borrowings managed by this librarian"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Borrowings Managed by {self.name}',
            'res_model': 'library.borrowing.record',
            'view_mode': 'list,form',
            'domain': [('librarian_id', '=', self.id)],
            'context': {'default_librarian_id': self.id}
        }
    
    def toggle_active(self):
        """Toggle active status of librarian"""
        for librarian in self:
            librarian.active = not librarian.active
    
    @api.model
    def get_available_librarians(self):
        """Get list of active librarians for assignment"""
        return self.search([('active', '=', True)])