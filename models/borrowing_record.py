from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import datetime, date
import logging

_logger = logging.getLogger(__name__)


class BorrowingRecord(models.Model):
    _name = 'library.borrowing.record'
    _description = 'Library Borrowing Record'
    _order = 'borrow_date desc'

    # Basic Fields
    sequence = fields.Char(string='Record Number', readonly=True, copy=False, default='New')
    member_id = fields.Many2one('library.member', string='Member', required=True, ondelete='restrict')
    member_name = fields.Char(related='member_id.name', string='Member Name', readonly=True)
    book_id = fields.Many2one('library.book', string='Book', required=True, ondelete='restrict')
    book_title = fields.Char(related='book_id.title', string='Book Title', readonly=True)
    librarian_id = fields.Many2one('library.librarian', string='Processed by Librarian', required=True, ondelete='restrict')
    
    # Date Fields
    borrow_date = fields.Date(string='Borrow Date', required=True, default=fields.Date.today)
    expected_return_date = fields.Date(string='Expected Return Date', required=True)
    actual_return_date = fields.Date(string='Actual Return Date', readonly=True)
    
    # Status and Fine Fields
    status = fields.Selection([
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue')
    ], string='Status', default='borrowed', required=True)
    
    days_overdue = fields.Integer(string='Days Overdue', compute='_compute_days_overdue', store=True, readonly=False)
    fine_amount = fields.Float(string='Fine Amount (RM)', default=0.0, readonly=True)
    fine_per_day = fields.Float(string='Fine Per Day (RM)', default=5.0)
    notes = fields.Text(string='Notes')

    @api.depends('expected_return_date', 'actual_return_date', 'status')
    def _compute_days_overdue(self):
        """Calculate days overdue for borrowed and overdue books"""
        for record in self:
            if record.status in ['borrowed', 'overdue']:
                # For borrowed and overdue books, calculate based on today's date
                reference_date = fields.Date.today()
                if record.expected_return_date and reference_date > record.expected_return_date:
                    delta = reference_date - record.expected_return_date
                    record.days_overdue = delta.days
                else:
                    record.days_overdue = 0
            elif record.status == 'returned' and record.actual_return_date:
                # For returned books, calculate based on actual return date
                if record.actual_return_date > record.expected_return_date:
                    delta = record.actual_return_date - record.expected_return_date
                    record.days_overdue = delta.days
                else:
                    record.days_overdue = 0
            else:
                record.days_overdue = 0

    @api.depends('expected_return_date', 'status', 'actual_return_date')
    def _update_overdue_status(self):
        """Update status to overdue if past expected return date"""
        for record in self:
            if record.status == 'borrowed' and record.expected_return_date:
                if fields.Date.today() > record.expected_return_date:
                    record.status = 'overdue'

    @api.model
    def create(self, vals):
        """Create borrowing record with validations"""
        # Auto-generate sequence
        if not vals.get('sequence') or vals.get('sequence') == 'New':
            sequence_obj = self.env['ir.sequence']
            vals['sequence'] = sequence_obj.next_by_code('library.borrowing.record') or 'New'
        
        # Validate member borrow limit
        if vals.get('member_id'):
            member = self.env['library.member'].browse(vals['member_id'])
            current_borrowed = self.search_count([
                ('member_id', '=', vals['member_id']),
                ('status', '=', 'borrowed')
            ])
            if current_borrowed >= member.max_borrow_limit:
                raise ValidationError(
                    f'Member "{member.name}" has reached the borrowing limit of {member.max_borrow_limit} books.'
                )
        
        # Validate book availability
        if vals.get('book_id'):
            book = self.env['library.book'].browse(vals['book_id'])
            if book.available_copies < 1:
                raise ValidationError(f'Book "{book.title}" is not available for borrowing.')
        
        # Set status to overdue if past expected return date
        if vals.get('expected_return_date'):
            expected_date_str = vals['expected_return_date']
            if isinstance(expected_date_str, str):
                expected_date = fields.Date.from_string(expected_date_str)
            else:
                expected_date = expected_date_str
            
            if expected_date and expected_date < fields.Date.today():
                vals['status'] = 'overdue'
        
        record = super(BorrowingRecord, self).create(vals)
        
        # Trigger recomputation of member's current borrowed count
        if record.member_id:
            record.member_id._recompute_field('current_borrowed')
        
        return record

    def write(self, vals):
        """Override write to update member borrowed count"""
        result = super(BorrowingRecord, self).write(vals)
        
        # Trigger recomputation of member's current borrowed count if status changed
        if 'status' in vals:
            for record in self:
                if record.member_id:
                    record.member_id._recompute_field('current_borrowed')
        
        return result

    def unlink(self):
        """Override unlink to prevent deletion of unreturned books"""
        for record in self:
            if record.status in ['borrowed', 'overdue']:
                raise ValidationError(
                    f'Cannot delete borrowing record "{record.sequence}" '
                    f'for "{record.member_name} - {record.book_title}". '
                    f'The book has not been returned yet (Status: {record.status.title()}). '
                    f'Please return the book first before deleting this record.'
                )
        return super(BorrowingRecord, self).unlink()

    def action_return_book(self):
        """Process book return and calculate fines"""
        self.ensure_one()
        
        if self.status == 'returned':
            raise ValidationError('This book has already been returned.')
        
        return_date = fields.Date.today()
        fine_amount = 0.0
        
        # Calculate fine if overdue
        if return_date > self.expected_return_date:
            days_overdue = (return_date - self.expected_return_date).days
            fine_amount = days_overdue * self.fine_per_day
        
        self.write({
            'actual_return_date': return_date,
            'status': 'returned',
            'fine_amount': fine_amount
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Book Returned',
                'message': f'Book returned successfully. Fine: RM {fine_amount:.2f}',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_extend_due_date(self):
        """Extend the expected return date"""
        self.ensure_one()
        
        if self.status != 'borrowed':
            raise ValidationError('Can only extend due date for borrowed books.')
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Extend Due Date',
            'res_model': 'library.borrowing.record',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'extend_due_date': True}
        }

    @api.constrains('expected_return_date', 'borrow_date')
    def _check_return_date(self):
        """Validate that expected return date is after borrow date"""
        for record in self:
            if record.expected_return_date and record.borrow_date:
                if record.expected_return_date <= record.borrow_date:
                    raise ValidationError('Expected return date must be after the borrow date.')

    @api.constrains('actual_return_date', 'borrow_date')
    def _check_actual_return_date(self):
        """Validate that actual return date is not before borrow date"""
        for record in self:
            if record.actual_return_date and record.borrow_date:
                if record.actual_return_date < record.borrow_date:
                    raise ValidationError('Actual return date cannot be before the borrow date.')

    def name_get(self):
        """Display record as 'Member - Book (Status)'"""
        result = []
        for record in self:
            name = f'{record.member_name} - {record.book_title} ({record.status.title()})'
            result.append((record.id, name))
        return result

    @api.model
    def update_overdue_records(self):
        """Cron job method to update overdue records"""
        overdue_records = self.search([
            ('status', '=', 'borrowed'),
            ('expected_return_date', '<', fields.Date.today())
        ])
        overdue_records.write({'status': 'overdue'})
        return True

    @api.model
    def cron_calculate_overdue_fines(self):
        """
        Scheduled cron job that runs daily to:
        1. Check all borrowed records past due date
        2. Calculate fines for overdue books (RM 5 per day)
        3. Update the fine amount and status automatically
        """
        try:
            # Find all borrowed records that are past their expected return date
            overdue_records = self.search([
                ('status', '=', 'borrowed'),
                ('expected_return_date', '<', fields.Date.today())
            ])
            
            total_updated = 0
            total_fines_calculated = 0.0
            
            for record in overdue_records:
                # Calculate days overdue
                days_overdue = (fields.Date.today() - record.expected_return_date).days
                
                # Calculate fine amount
                fine_amount = days_overdue * record.fine_per_day
                
                # Update record status, fine, and days overdue
                record.write({
                    'status': 'overdue',
                    'fine_amount': fine_amount,
                    'days_overdue': days_overdue
                })
                
                total_updated += 1
                total_fines_calculated += fine_amount
                
                _logger.info(
                    f'Updated overdue record {record.sequence}: '
                    f'{record.member_name} - {record.book_title}, '
                    f'Days overdue: {days_overdue}, Fine: RM {fine_amount:.2f}'
                )
            
            # Also check for records that are already overdue but need fine updates
            existing_overdue = self.search([
                ('status', '=', 'overdue'),
                ('expected_return_date', '<', fields.Date.today())
            ])
            
            for record in existing_overdue:
                # Recalculate fine for existing overdue records
                days_overdue = (fields.Date.today() - record.expected_return_date).days
                new_fine_amount = days_overdue * record.fine_per_day
                
                # Update fine amount and days overdue if changed
                if record.fine_amount != new_fine_amount or record.days_overdue != days_overdue:
                    record.write({
                        'fine_amount': new_fine_amount,
                        'days_overdue': days_overdue
                    })
                    total_updated += 1
                    total_fines_calculated += new_fine_amount
            
            _logger.info(
                f'Overdue fine calculation completed successfully. '
                f'Records updated: {total_updated}, '
                f'Total fines calculated: RM {total_fines_calculated:.2f}'
            )
            
            return True
            
        except Exception as e:
            _logger.error(f'Error in cron_calculate_overdue_fines: {str(e)}')
            return False

    def action_test_cron_fine_calculation(self):
        """Manual action to test cron fine calculation"""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Cron Test',
                'message': f'Fine calculation completed. Check logs for details.',
                'type': 'info',
                'sticky': False,
            }
        }