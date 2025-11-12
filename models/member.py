from odoo import fields, models, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class Member(models.Model):
    _name = 'library.member'
    _description = 'Library Member'
    _sql_constraints = [
        ('unique_phone', 'UNIQUE(phone)', 'Phone number must be unique! This phone number is already registered.')
    ]

    sequence = fields.Char(string='Member Number', readonly=True, copy=False, default='New')
    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone Number', required=True)
    join_date = fields.Date(string='Join Date', required=True, default=fields.Date.today)
    max_borrow_limit = fields.Integer(string='Maximum Borrow Limit', default=5)
    current_borrowed = fields.Integer(string='Currently Borrowed', compute='_compute_current_borrowed', store=True)
    member_status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending')
    ], string='Member Status', default='active', required=True)

    # Additional fields for views
    borrowing_ids = fields.One2many('library.borrowing.record', 'member_id', string='Borrowing Records')
    borrow_limit_progress = fields.Float(string='Borrow Limit Progress', compute='_compute_borrow_limit_progress')
    total_books_borrowed = fields.Integer(string='Total Books Borrowed', compute='_compute_statistics',
                                          search='_search_total_books_borrowed')
    total_fines = fields.Float(string='Total Fines', compute='_compute_statistics', search='_search_total_fines')
    overdue_books_count = fields.Integer(string='Overdue Books', compute='_compute_statistics',
                                         search='_search_overdue_books_count')
    returned_books_count = fields.Integer(string='Returned Books', compute='_compute_statistics',
                                          search='_search_returned_books_count')

    @api.depends('borrowing_ids', 'borrowing_ids.status')
    def _compute_current_borrowed(self):
        for member in self:
            member.current_borrowed = len(member.borrowing_ids.filtered(lambda b: b.status == 'borrowed'))

    @api.depends('current_borrowed', 'max_borrow_limit')
    def _compute_borrow_limit_progress(self):
        for member in self:
            if member.max_borrow_limit > 0:
                member.borrow_limit_progress = (member.current_borrowed / member.max_borrow_limit) * 100
            else:
                member.borrow_limit_progress = 0

    @api.constrains('phone')
    def _check_phone_unique(self):
        for record in self:
            if record.phone:
                # Check if another active member has the same phone number
                existing_member = self.search([
                    ('phone', '=', record.phone),
                    ('id', '!=', record.id),
                    ('member_status', '!=', 'inactive')
                ], limit=1)
                if existing_member:
                    raise ValidationError(
                        f"Phone number '{record.phone}' is already registered to member: {existing_member.name} ({existing_member.sequence}). "
                        "Please use a different phone number or contact administrator if this is an error."
                    )

    @api.onchange('member_status')
    def _onchange_member_status(self):
        """Update borrow limit when member status changes in the form"""
        if self.member_status == 'active':
            self.max_borrow_limit = 10
        elif self.member_status == 'inactive':
            self.max_borrow_limit = 5
        elif self.member_status == 'pending':
            self.max_borrow_limit = 5

    @api.constrains('member_status', 'current_borrowed')
    def _check_status_change_borrowing_limit(self):
        """Validate member status change based on current borrowed books"""
        for record in self:
            if record.member_status == 'inactive' and record.current_borrowed > 5:
                raise ValidationError(
                    f'Cannot change member "{record.name}" to Inactive status. '
                    f'Member currently has {record.current_borrowed} borrowed books, '
                    f'but Inactive members can only have maximum 5 books. '
                    f'Please ensure member returns {record.current_borrowed - 5} books before changing status.'
                )
            elif record.member_status == 'pending' and record.current_borrowed > 5:
                raise ValidationError(
                    f'Cannot change member "{record.name}" to Pending status. '
                    f'Member currently has {record.current_borrowed} borrowed books, '
                    f'but Pending members can only have maximum 5 books. '
                    f'Please ensure member returns {record.current_borrowed - 5} books before changing status.'
                )

    def write(self, vals):
        """Update borrow limit when member status is saved"""
        result = super(Member, self).write(vals)
        if 'member_status' in vals:
            for record in self:
                if record.member_status == 'active':
                    record.max_borrow_limit = 10
                elif record.member_status == 'inactive':
                    record.max_borrow_limit = 5
                elif record.member_status == 'pending':
                    record.max_borrow_limit = 5
        return result

    @api.model
    def create(self, vals):
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('library.member') or 'New'

        # Set initial borrow limit based on member status
        if vals.get('member_status') == 'active':
            vals['max_borrow_limit'] = 10
        elif vals.get('member_status') == 'pending':
            vals['max_borrow_limit'] = 5
        elif vals.get('member_status') == 'inactive':
            vals['max_borrow_limit'] = 5
        # For 'pending' or no status, use default value (5)

        return super(Member, self).create(vals)

    @api.depends('borrowing_ids', 'borrowing_ids.status', 'borrowing_ids.fine_amount')
    def _compute_statistics(self):
        for member in self:
            borrowings = member.borrowing_ids
            member.total_books_borrowed = len(borrowings)
            member.total_fines = sum(borrowings.mapped('fine_amount'))
            member.overdue_books_count = len(borrowings.filtered(lambda b: b.status == 'overdue'))
            member.returned_books_count = len(borrowings.filtered(lambda b: b.status == 'returned'))

    def action_new_borrowing(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Borrowing',
            'res_model': 'library.borrowing.record',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_member_id': self.id}
        }

    def check_borrow_limit(self):
        """Check if member can borrow more books"""
        if self.current_borrowed >= self.max_borrow_limit:
            raise ValidationError(
                f'Member "{self.name}" has reached the borrowing limit of {self.max_borrow_limit} books.'
            )

    # Search methods for computed fields
    def _search_total_books_borrowed(self, operator, value):
        """Search method for total_books_borrowed field"""
        members = self.search([])
        members._compute_statistics()
        if operator == '=':
            member_ids = [m.id for m in members if m.total_books_borrowed == value]
        elif operator == '>':
            member_ids = [m.id for m in members if m.total_books_borrowed > value]
        elif operator == '<':
            member_ids = [m.id for m in members if m.total_books_borrowed < value]
        elif operator == '>=':
            member_ids = [m.id for m in members if m.total_books_borrowed >= value]
        elif operator == '<=':
            member_ids = [m.id for m in members if m.total_books_borrowed <= value]
        else:
            member_ids = []
        return [('id', 'in', member_ids)]

    def _search_total_fines(self, operator, value):
        """Search method for total_fines field"""
        members = self.search([])
        members._compute_statistics()
        if operator == '=':
            member_ids = [m.id for m in members if m.total_fines == value]
        elif operator == '>':
            member_ids = [m.id for m in members if m.total_fines > value]
        elif operator == '<':
            member_ids = [m.id for m in members if m.total_fines < value]
        elif operator == '>=':
            member_ids = [m.id for m in members if m.total_fines >= value]
        elif operator == '<=':
            member_ids = [m.id for m in members if m.total_fines <= value]
        else:
            member_ids = []
        return [('id', 'in', member_ids)]

    def _search_overdue_books_count(self, operator, value):
        """Search method for overdue_books_count field"""
        members = self.search([])
        members._compute_statistics()
        if operator == '=':
            member_ids = [m.id for m in members if m.overdue_books_count == value]
        elif operator == '>':
            member_ids = [m.id for m in members if m.overdue_books_count > value]
        elif operator == '<':
            member_ids = [m.id for m in members if m.overdue_books_count < value]
        elif operator == '>=':
            member_ids = [m.id for m in members if m.overdue_books_count >= value]
        elif operator == '<=':
            member_ids = [m.id for m in members if m.overdue_books_count <= value]
        else:
            member_ids = []
        return [('id', 'in', member_ids)]

    def _search_returned_books_count(self, operator, value):
        """Search method for returned_books_count field"""
        members = self.search([])
        members._compute_statistics()
        if operator == '=':
            member_ids = [m.id for m in members if m.returned_books_count == value]
        elif operator == '>':
            member_ids = [m.id for m in members if m.returned_books_count > value]
        elif operator == '<':
            member_ids = [m.id for m in members if m.returned_books_count < value]
        elif operator == '>=':
            member_ids = [m.id for m in members if m.returned_books_count >= value]
        elif operator == '<=':
            member_ids = [m.id for m in members if m.returned_books_count <= value]
        else:
            member_ids = []
        return [('id', 'in', member_ids)]

    @api.model
    def cron_review_member_status(self):
        """
        Weekly cron job to review and update member statuses based on activity:
        1. Check members with overdue books for potential status changes
        2. Review inactive members who might need reactivation
        3. Log member status summary for admin review
        """
        try:
            # Get all members with overdue books
            members_with_overdue = self.search([
                ('overdue_books_count', '>', 0),
                ('member_status', '=', 'active')
            ])
            
            # Get inactive members with no recent activity
            inactive_members = self.search([
                ('member_status', '=', 'inactive'),
                ('current_borrowed', '=', 0)
            ])
            
            # Get pending members who might be ready for activation
            pending_members = self.search([
                ('member_status', '=', 'pending')
            ])
            
            # Log summary for admin review
            _logger.info(
                f'Weekly Member Status Review:'
                f'\n- Active members with overdue books: {len(members_with_overdue)}'
                f'\n- Inactive members: {len(inactive_members)}'
                f'\n- Pending members: {len(pending_members)}'
                f'\n- Total members: {len(self.search([]))}'
            )
            
            # Optional: Auto-update logic (can be customized based on business rules)
            # For example, members with 3+ overdue books might be marked as pending
            high_overdue_members = members_with_overdue.filtered(lambda m: m.overdue_books_count >= 3)
            if high_overdue_members:
                _logger.warning(
                    f'Members with 3+ overdue books requiring attention: '
                    f'{", ".join(high_overdue_members.mapped("name"))}'
                )
            
            return True
            
        except Exception as e:
            _logger.error(f'Error in cron_review_member_status: {str(e)}')
            return False
