from odoo import fields, models, api
from odoo.exceptions import ValidationError

class Book(models.Model):
    _name = 'library.book'
    _description = 'Book in the library'
    _sql_constraints = [
        ('unique_isbn', 'UNIQUE(isbn)', 'ISBN must be unique! This ISBN is already registered.')
    ]

    title = fields.Char(string='Title', required=True)
    author = fields.Char(string='Author', required=True)
    isbn = fields.Char(string='ISBN', required=True)
    category = fields.Selection([
        ('fiction', 'Fiction'),
        ('non_fiction', 'Non-Fiction'),
        ('science', 'Science'),
        ('history', 'History'),
        ('biography', 'Biography'),
        ('technology', 'Technology'),
        ('other', 'Other')
    ], string='Category', required=True)
    total_copies = fields.Integer(string='Total Copies', required=True, default=1)
    available_copies = fields.Integer(string='Available Copies', compute='_compute_available_copies', store=True)
    borrowing_record_ids = fields.One2many('library.borrowing.record', 'book_id', string='Borrowing Records')
    image = fields.Binary(string='Book Cover')
    publication_year = fields.Integer(string='Publication Year')
    publisher = fields.Char(string='Publisher')
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)

    @api.depends('total_copies', 'borrowing_record_ids.status')
    def _compute_available_copies(self):
        for book in self:
            # Count both borrowed and overdue records as unavailable
            unavailable_count = len(book.borrowing_record_ids.filtered(lambda r: r.status in ['borrowed', 'overdue']))
            book.available_copies = max(0, book.total_copies - unavailable_count)

    @api.constrains('isbn')
    def _check_isbn_unique(self):
        """Ensure ISBN is unique across all books"""
        for book in self:
            if book.isbn:
                existing_book = self.search([
                    ('isbn', '=', book.isbn),
                    ('id', '!=', book.id)
                ], limit=1)
                if existing_book:
                    raise ValidationError(
                        f'A book with ISBN {book.isbn} already exists: "{existing_book.title}" by {existing_book.author}.'
                    )

    def action_view_borrowing_records(self):
        """Open borrowing records for this book"""
        return {
            'name': f'Borrowing Records - {self.title}',
            'type': 'ir.actions.act_window',
            'res_model': 'library.borrowing.record',
            'view_mode': 'list,form',
            'domain': [('book_id', '=', self.id)],
            'context': {'default_book_id': self.id}
        }