# Library Management System - Test Cases v2.0

## 📋 System Overview

This document contains comprehensive test cases for the Library Management System built on Odoo 18.0. The system consists of four main models: Member, Book, Borrowing Record, and Librarian management with complete integration and real-time calculations.

## 🔍 Code Analysis Summary

### Member Model Features
- **Auto-generated sequences**: LM0001, LM0002...
- **Phone uniqueness validation**: Prevents duplicate registrations
- **Status-based borrow limits**: Active: 10, Inactive: 5, Pending: 5
- **Real-time borrowing statistics**: Current borrowed, total fines, overdue count
- **Computed fields with search capability**: All statistics searchable

### Book Model Features
- **ISBN uniqueness validation**: Prevents duplicate books
- **Real-time availability calculation**: Updates based on active borrowings
- **Category-based classification**: 7 categories with color coding
- **Borrowing history tracking**: Complete borrowing lifecycle

### Borrowing Model Features
- **Auto-generated sequences**: BR00001, BR00002...
- **Fine calculation**: RM 5.00 per day overdue
- **Status management**: Borrowed/Returned/Overdue with automatic updates
- **Date validations**: Comprehensive constraint checking
- **Member limit enforcement**: Prevents over-borrowing
- **Librarian assignment**: Track which librarian processed each transaction

### Librarian Model Features ✨ **NEW in v2.0**
- **Employee ID validation**: LIB001, LIB002... format enforcement
- **Department management**: Circulation, Reference, Cataloging, Administration
- **Position hierarchy**: Assistant, Librarian, Senior Librarian, Head Librarian
- **Years of service calculation**: Automatic computation based on hire date
- **Performance tracking**: Managed borrowings count and history
- **Contact validation**: Email and phone format validation
- **Access control**: Active/inactive status management

---

# 🧪 Comprehensive Test Cases

## Test Category 1: Member Management

### Test 1.1: Member Registration & Auto-Generation

**Objective**: Verify member creation with auto-generated sequence and status-based limits

**Test Steps**:
1. Navigate to Members → Create
2. Fill in member details:
   - Name: "John Doe"
   - Email: "john@email.com"
   - Phone: "012-345-6789"
   - Status: Active
3. Save the record

**Expected Results**:
- ✅ Member Number: LM0001 (auto-generated)
- ✅ Max Borrow Limit: 10 (because status = Active)
- ✅ Current Borrowed: 0
- ✅ Progress Bar: 0%
- ✅ Join Date: Today's date

**Test Data**:
```
Name: John Doe
Email: john@email.com
Phone: 012-345-6789
Status: Active
Expected Sequence: LM0001
Expected Limit: 10
```

### Test 1.2: Phone Number Uniqueness Validation

**Objective**: Verify phone number uniqueness constraint

**Test Steps**:
1. Attempt to create second member with same phone "012-345-6789"
2. Fill in different name and email
3. Try to save

**Expected Results**:
- ❌ **Error Message**: "Phone number '012-345-6789' is already registered to member: John Doe (LM0001). Please use a different phone number or contact administrator if this is an error."
- ❌ Record should not be created

### Test 1.3: Status-Based Borrow Limits

**Objective**: Verify automatic borrow limit assignment based on member status

**Test Steps**:
1. Create member with Status: Active
2. Create member with Status: Inactive  
3. Create member with Status: Pending
4. Change existing member from Active to Inactive
5. Verify limit updates in real-time

**Expected Results**:
- ✅ Active member: Max Borrow Limit = 10
- ✅ Inactive member: Max Borrow Limit = 5
- ✅ Pending member: Max Borrow Limit = 5
- ✅ Status change: Limit updates automatically (Active→Inactive: 10→5)

**Test Data**:
```
Member 1: Status=Active → Limit=10
Member 2: Status=Inactive → Limit=5
Member 3: Status=Pending → Limit=5
```

### Test 1.4: Member Statistics Computation

**Objective**: Verify real-time calculation of member statistics

**Test Steps**:
1. Create member and note initial statistics
2. Create borrowing records
3. Return some books with fines
4. Check Statistics tab

**Expected Results**:
- ✅ Total Books Borrowed: Updates automatically
- ✅ Total Fines: Sum of all fines (RM)
- ✅ Overdue Books Count: Current overdue books
- ✅ Returned Books Count: All returned books
- ✅ Progress bar shows correct percentage

---

## Test Category 2: Book Management

### Test 2.1: Book Creation & ISBN Validation

**Objective**: Verify book creation with proper field validation

**Test Steps**:
1. Navigate to Books → Create
2. Fill in book details:
   - Title: "Python Programming"
   - Author: "John Author"
   - ISBN: "978-1234567890"
   - Category: Technology
   - Total Copies: 5
3. Save the record

**Expected Results**:
- ✅ Book created successfully
- ✅ Available Copies: 5 (same as total initially)
- ✅ Category shows with primary badge (Technology)
- ✅ Book appears in kanban view with proper layout

**Test Data**:
```
Title: Python Programming
Author: John Author
ISBN: 978-1234567890
Category: Technology
Total Copies: 5
Expected Available: 5
```

### Test 2.2: ISBN Uniqueness Validation

**Objective**: Verify ISBN uniqueness constraint

**Test Steps**:
1. Attempt to create another book with same ISBN "978-1234567890"
2. Use different title and author
3. Try to save

**Expected Results**:
- ❌ **Error Message**: "A book with ISBN 978-1234567890 already exists: 'Python Programming' by John Author."
- ❌ Record should not be created

### Test 2.3: Real-Time Availability Calculation

**Objective**: Verify available copies update based on borrowings

**Test Steps**:
1. Note initial Available Copies: 5
2. Create a borrowing record for this book
3. Check book's available copies
4. Return the book
5. Check available copies again

**Expected Results**:
- ✅ After borrowing: Available Copies decreases (5 → 4)
- ✅ Book list view shows updated availability
- ✅ After return: Available Copies increases (4 → 5)
- ✅ Kanban view progress bar updates

### Test 2.4: Category Color Coding

**Objective**: Verify category-based color coding in views

**Test Steps**:
1. Create books in different categories
2. Check list view and kanban view

**Expected Results**:
- ✅ Fiction: Info badge (blue)
- ✅ Science: Success badge (green)
- ✅ History: Warning badge (yellow)
- ✅ Technology: Primary badge (blue)
- ✅ Other categories: Secondary badge (gray)

---

## Test Category 3: Librarian Management ✨ **NEW in v2.0**

### Test 3.1: Librarian Registration & Employee ID Validation

**Objective**: Verify librarian creation with proper employee ID format validation

**Test Steps**:
1. Navigate to Librarians → Create
2. Fill in librarian details:
   - Name: "Sarah Wilson"
   - Employee ID: "LIB001"
   - Email: "sarah.wilson@library.com"
   - Phone: "012-987-6543"
   - Department: Circulation
   - Position: Librarian
3. Save the record

**Expected Results**:
- ✅ Librarian created successfully
- ✅ Years of Service: 0.0 (new hire)
- ✅ Active status: True (default)
- ✅ Total Managed Borrowings: 0 (initial)

**Test Data**:
```
Name: Sarah Wilson
Employee ID: LIB001
Email: sarah.wilson@library.com
Phone: 012-987-6543
Department: Circulation
Position: Librarian
Expected Years of Service: 0.0
```

### Test 3.2: Employee ID Format Validation

**Objective**: Verify employee ID follows LIB### pattern

**Test Steps**:
1. Try creating librarian with Employee ID: "INVALID001"
2. Try creating librarian with Employee ID: "LIB"
3. Try creating librarian with Employee ID: "LIB001" (valid)

**Expected Results**:
- ❌ **Error Message 1**: "Employee ID 'INVALID001' must follow the format 'LIBxxx' where xxx is a number (e.g., LIB001, LIB123)."
- ❌ **Error Message 2**: "Employee ID 'LIB' must follow the format 'LIBxxx' where xxx is a number (e.g., LIB001, LIB123)."
- ✅ **Valid**: "LIB001" should be accepted

### Test 3.3: Employee ID Uniqueness Validation

**Objective**: Verify employee ID uniqueness constraint

**Test Steps**:
1. Create first librarian with Employee ID: "LIB001"
2. Attempt to create second librarian with same Employee ID: "LIB001"
3. Try to save

**Expected Results**:
- ❌ **Error Message**: "Employee ID must be unique! This employee ID is already registered."
- ❌ Second record should not be created

### Test 3.4: Email & Phone Format Validation

**Objective**: Verify contact information format validation

**Test Steps**:
1. Try invalid email: "invalid-email"
2. Try invalid phone: "123"
3. Try valid formats

**Expected Results**:
- ❌ **Email Error**: "Please enter a valid email address. 'invalid-email' is not a valid email format."
- ❌ **Phone Error**: "Please enter a valid phone number. '123' is not a valid phone format."
- ✅ Valid formats should be accepted

### Test 3.5: Years of Service Calculation

**Objective**: Verify automatic years of service computation

**Test Steps**:
1. Create librarian with Hire Date: 2 years ago
2. Check Years of Service field
3. Update hire date and verify recalculation

**Expected Results**:
- ✅ Years of Service: ~2.0 (based on hire date)
- ✅ Updates automatically when hire date changes
- ✅ Displayed with 1 decimal precision

### Test 3.6: Department & Position Management

**Objective**: Verify department and position field functionality

**Test Steps**:
1. Create librarians in different departments
2. Assign different positions
3. Use search filters

**Expected Results**:
- ✅ Department options: Circulation, Reference, Cataloging, Administration
- ✅ Position options: Assistant, Librarian, Senior Librarian, Head Librarian
- ✅ Search filters work for department and position
- ✅ Kanban view displays department/position badges

### Test 3.7: Librarian Performance Tracking

**Objective**: Verify managed borrowings tracking

**Test Steps**:
1. Create librarian
2. Assign librarian to borrowing records
3. Check managed borrowings count
4. Use "View Managed Borrowings" action

**Expected Results**:
- ✅ Total Managed Borrowings: Updates automatically
- ✅ Managed Borrowings tab: Shows assigned borrowing records
- ✅ "View Managed Borrowings" button: Opens filtered list
- ✅ Statistics show in stat button

---

## Test Category 4: Borrowing Operations

### Test 4.1: Valid Borrowing Process with Librarian Assignment

**Objective**: Verify complete borrowing workflow with librarian tracking

**Test Steps**:
1. Navigate to Borrowing Records → Create
2. Fill in borrowing details:
   - Member: John Doe
   - Book: Python Programming  
   - Librarian: Sarah Wilson (LIB001)
   - Expected Return Date: 7 days from today
3. Save the record

**Expected Results**:
- ✅ Record Number: BR00001 (auto-generated)
- ✅ Status: Borrowed
- ✅ Librarian: Sarah Wilson assigned
- ✅ Member's Current Borrowed: 0 → 1
- ✅ Member's Progress Bar: 10% (1/10)
- ✅ Book's Available Copies: 5 → 4
- ✅ Librarian's Managed Borrowings: 0 → 1

**Test Data**:
```
Member: John Doe (LM0001)
Book: Python Programming
Librarian: Sarah Wilson (LIB001)
Expected Return: Today + 7 days
Expected Sequence: BR00001
```

### Test 4.2: Borrowing Limit Validation

**Objective**: Verify member borrowing limit enforcement

**Test Steps**:
1. Create 10 borrowing records for John Doe (Active member, limit = 10)
2. Attempt to create 11th borrowing record
3. Try to save

**Expected Results**:
- ❌ **Error Message**: "Member 'John Doe' has reached the borrowing limit of 10 books."
- ❌ 11th record should not be created
- ✅ First 10 records should be successful

### Test 4.3: Book Availability Validation

**Objective**: Verify book availability checking

**Test Steps**:
1. Borrow all 5 copies of Python Programming
2. Attempt to create 6th borrowing for same book
3. Try to save

**Expected Results**:
- ❌ **Error Message**: "Book 'Python Programming' is not available for borrowing."
- ❌ 6th borrowing should not be created
- ✅ Book shows 0 available copies

### Test 4.4: Return Button Visibility

**Objective**: Verify return button shows for borrowed and overdue books

**Test Steps**:
1. Create borrowing record with future return date (Status: Borrowed)
2. Create borrowing record with past return date (Status: Overdue)
3. Return a book (Status: Returned)
4. Check button visibility

**Expected Results**:
- ✅ Borrowed status: Return button visible
- ✅ Overdue status: Return button visible
- ❌ Returned status: Return button hidden

---

## Test Category 5: Return Process & Fine Calculation

### Test 5.1: On-Time Return

**Objective**: Verify return process without fines

**Test Steps**:
1. Open borrowing record with future due date
2. Click "Return Book" button
3. Verify all updates

**Expected Results**:
- ✅ Status: Borrowed → Returned
- ✅ Actual Return Date: Today's date
- ✅ Fine Amount: RM 0.00
- ✅ Success notification: "Book returned successfully. Fine: RM 0.00"
- ✅ Book's Available Copies: +1
- ✅ Member's Current Borrowed: -1
- ✅ Progress bar updates

### Test 5.2: Overdue Return with Fine Calculation

**Objective**: Verify fine calculation for overdue returns

**Test Steps**:
1. Create borrowing with Expected Return Date: 3 days ago
2. Click "Return Book" button
3. Verify fine calculation

**Expected Results**:
- ✅ Status: Borrowed → Returned
- ✅ Days Overdue: 3
- ✅ Fine Amount: RM 15.00 (3 days × RM 5.00)
- ✅ Success notification: "Book returned successfully. Fine: RM 15.00"
- ✅ Member's Total Fines: +RM 15.00

**Test Data**:
```
Expected Return: Today - 3 days
Return Date: Today
Days Overdue: 3
Fine Per Day: RM 5.00
Expected Fine: RM 15.00
```

### Test 5.3: Automatic Overdue Status

**Objective**: Verify automatic status updates for overdue books

**Test Steps**:
1. Create borrowing with Expected Return Date: Yesterday
2. Check status automatically

**Expected Results**:
- ✅ Status should automatically be: Overdue
- ✅ Days Overdue: 1
- ✅ Record appears in "Overdue" filter

### Test 5.4: Prevent Double Return

**Objective**: Verify prevention of returning already returned books

**Test Steps**:
1. Return a book (status = Returned)
2. Try to click "Return Book" again

**Expected Results**:
- ❌ **Error Message**: "This book has already been returned."
- ❌ No changes to record

---

## Test Category 6: UI Features & Views

### Test 6.1: Librarian Kanban View Layout

**Objective**: Verify librarian kanban card layout and information display

**Test Steps**:
1. Navigate to Librarians → Kanban view
2. Check card layout for active and inactive librarians
3. Verify information display

**Expected Results**:
- ✅ Name and Employee ID: Prominently displayed
- ✅ Department badge: Color-coded
- ✅ Position badge: Hierarchical display
- ✅ Email and phone: With icons
- ✅ Managed borrowings count: Bottom left
- ✅ Active status toggle: Bottom right
- ✅ Inactive librarians: Grayed out display

### Test 6.2: List View Color Coding

**Objective**: Verify visual indicators in list views

**Visual Tests**:
1. **Members**: Create member at borrowing limit
2. **Books**: Create book with 0 availability  
3. **Borrowing Records**: Check status badges
4. **Librarians**: Check active/inactive status

**Expected Results**:
- ✅ Members at limit: ORANGE/WARNING highlight
- ✅ Books with 0 availability: RED/DANGER highlight  
- ✅ Borrowing status badges:
   - Borrowed: Blue/Info badge
   - Returned: Green/Success badge
   - Overdue: Red/Danger badge
- ✅ Inactive librarians: Muted/Gray display

### Test 6.3: Filter Functionality

**Objective**: Verify all search filters work correctly

**Test Steps**:
1. **Members filters**:
   - Apply "Active Members" filter
   - Apply "Members at Limit" filter
   - Apply "Members with Overdue Books" filter

2. **Books filters**:
   - Apply "Available Books" filter
   - Apply category filters (Fiction, Science, etc.)

3. **Borrowing Records filters**:
   - Apply status filters (Borrowed, Returned, Overdue)
   - Apply "With Fines" filter
   - Apply date-based filters

4. **Librarians filters** ✨ **NEW**:
   - Apply "Active" filter
   - Apply department filters (Circulation, Reference, etc.)
   - Apply position filters (Librarian, Senior Librarian, etc.)
   - Apply "This Year Hires" filter
   - Apply "Long Service (5+ Years)" filter

**Expected Results**:
- ✅ All filters show correct subset of records
- ✅ Multiple filters can be combined
- ✅ Clear filters returns to full list

### Test 6.4: Integration Buttons & Actions

**Objective**: Verify cross-model navigation and actions

**Test Steps**:
1. **Member form** → Click "New Borrowing"
2. **Book form** → Click "View Borrowing Records"
3. **Borrowing record** → Click "Return Book"
4. **Librarian form** → Click "View Managed Borrowings" ✨ **NEW**
5. **Librarian form** → Click "Activate/Deactivate" ✨ **NEW**

**Expected Results**:
- ✅ "New Borrowing": Opens borrowing form with member pre-filled
- ✅ "View Borrowing Records": Shows borrowing history for that book
- ✅ "Return Book": Processes return and calculates fines
- ✅ "View Managed Borrowings": Shows librarian's assigned borrowings
- ✅ "Activate/Deactivate": Toggles librarian status

---

## Test Category 7: Search & Grouping

### Test 7.1: Search Functionality

**Objective**: Verify search capabilities across all models

**Test Steps**:
1. **Members**: Search by name, member number, email
2. **Books**: Search by title, author, ISBN
3. **Borrowing Records**: Search by record number, member, book
4. **Librarians** ✨ **NEW**: Search by name, employee ID, email

**Expected Results**:
- ✅ All search fields return relevant results
- ✅ Partial matches work correctly
- ✅ Case-insensitive search
- ✅ Librarian search works for both name and employee ID

### Test 7.2: Group By Functionality

**Objective**: Verify grouping options work correctly

**Test Steps**:
1. **Members**: Group by Join Date, Member Status
2. **Books**: Group by Category, Author, Publisher
3. **Borrowing Records**: Group by Status, Member, Book
4. **Librarians** ✨ **NEW**: Group by Department, Position, Active Status, Hire Date

**Expected Results**:
- ✅ Records grouped correctly
- ✅ Group headers show count
- ✅ Groups can be expanded/collapsed
- ✅ Librarian grouping shows department hierarchy

---

## Test Category 8: Data Integrity & Constraints

### Test 8.1: Required Field Validation

**Objective**: Verify required fields are enforced

**Test Steps**:
1. Try creating member without name, email, or phone
2. Try creating book without title, author, ISBN, or category
3. Try creating borrowing without member, book, or expected return date
4. Try creating librarian without name or employee ID ✨ **NEW**

**Expected Results**:
- ❌ All attempts should fail with field requirement errors
- ❌ Records should not be created

### Test 8.2: Relationship Integrity

**Objective**: Verify foreign key relationships are maintained

**Test Steps**:
1. Try deleting member who has borrowing records
2. Try deleting book that has borrowing records
3. Try deleting librarian who has managed borrowing records ✨ **NEW**

**Expected Results**:
- ❌ Deletion should be prevented (ondelete='restrict')
- ❌ Appropriate error messages shown
- ✅ Librarian deletion should set borrowing records' librarian_id to null (ondelete='set null')

### Test 8.3: Date and Format Validations

**Objective**: Verify date and format constraints

**Test Steps**:
1. **Librarian hire date**: Try setting future date
2. **Librarian email**: Try invalid email format
3. **Librarian phone**: Try invalid phone format
4. **Borrowing dates**: Try invalid date combinations

**Expected Results**:
- ❌ Future hire date: "Hire date cannot be in the future."
- ❌ Invalid email: "Please enter a valid email address."
- ❌ Invalid phone: "Please enter a valid phone number."
- ❌ Invalid borrowing dates: Appropriate date validation errors

---

## ✅ Success Criteria Checklist

### Basic Functionality
- [ ] All four menus load (Members, Books, Borrowing Records, Librarians) ✨ **UPDATED**
- [ ] CRUD operations work on all models
- [ ] Auto-generation works (LM0001, BR00001, LIB001...) ✨ **UPDATED**
- [ ] Navigation between related records works

### Validations
- [ ] Phone uniqueness enforced (Members)
- [ ] ISBN uniqueness enforced (Books)
- [ ] Employee ID uniqueness and format enforced (Librarians) ✨ **NEW**
- [ ] Email and phone format validation (Librarians) ✨ **NEW**
- [ ] Borrowing limits respected
- [ ] Book availability checked
- [ ] Date validations work
- [ ] Required fields enforced

### Real-Time Calculations
- [ ] Available copies update automatically
- [ ] Member statistics compute correctly
- [ ] Librarian years of service compute correctly ✨ **NEW**
- [ ] Librarian managed borrowings count updates ✨ **NEW**
- [ ] Progress bars show accurate percentages
- [ ] Fine calculations are correct (RM 5.00/day)
- [ ] Status updates trigger cascade changes

### UI Features
- [ ] Color coding works (orange for at-limit, red for unavailable, gray for inactive)
- [ ] All filters function properly
- [ ] Librarian filters work (department, position, hire date, service years) ✨ **NEW**
- [ ] Buttons trigger correct actions
- [ ] Kanban view displays properly (including librarian cards) ✨ **UPDATED**
- [ ] Search functionality works
- [ ] Grouping options work

### Integration
- [ ] Member ↔ Borrowing relationship works
- [ ] Book ↔ Borrowing relationship works
- [ ] Librarian ↔ Borrowing relationship works ✨ **NEW**
- [ ] Status changes trigger updates across models
- [ ] Statistics update in real-time
- [ ] Cross-model navigation works

### Performance
- [ ] Views load quickly with sample data
- [ ] Computed fields calculate efficiently (including years of service) ✨ **UPDATED**
- [ ] Search operations are responsive
- [ ] No memory leaks or errors in browser console

---

## 🚨 Common Issues & Troubleshooting

### Issue 1: Module Won't Upgrade
**Symptoms**: XML parsing errors, field not found errors
**Solutions**: 
- Check XML syntax in all view files
- Verify all field names match model definitions
- Ensure proper XML declaration at file start
- Check for missing librarian_id field in borrowing records ✨ **NEW**

### Issue 2: Computed Fields Not Updating
**Symptoms**: Statistics don't update, progress bars wrong
**Solutions**:
- Check @api.depends decorators
- Verify field dependencies are correct
- Use _recompute_field() instead of invalidate_cache() for Odoo 18 ✨ **UPDATED**

### Issue 3: Validation Errors Not Showing
**Symptoms**: Duplicate records created, invalid data saved
**Solutions**:
- Check @api.constrains methods
- Verify ValidationError imports
- Test with various data scenarios
- Check employee ID regex pattern for librarians ✨ **NEW**

### Issue 4: UI Features Not Working
**Symptoms**: Colors not showing, buttons not working
**Solutions**:
- Check decoration-* attributes in XML
- Verify button method names match model methods
- Test with different browsers
- Verify librarian kanban template syntax ✨ **NEW**

### Issue 5: Return Button Disappearing ✨ **NEW**
**Symptoms**: Return button not visible after creating borrowing record
**Solutions**:
- Check button invisible condition: should be `status not in ['borrowed', 'overdue']`
- Verify automatic overdue status logic in create method
- Test with different expected return dates

---

## 📊 Test Execution Log Template

```
Test Date: ___________
Tester: ___________
Environment: Odoo 18.0
Module Version: 2.0.0

Test Results:
[ ] Test 1.1: Member Registration - PASS/FAIL
[ ] Test 1.2: Phone Uniqueness - PASS/FAIL
[ ] Test 1.3: Status-Based Limits - PASS/FAIL
[ ] Test 2.1: Book Creation - PASS/FAIL
[ ] Test 2.2: ISBN Uniqueness - PASS/FAIL
[ ] Test 3.1: Librarian Registration - PASS/FAIL ✨ NEW
[ ] Test 3.2: Employee ID Format - PASS/FAIL ✨ NEW
[ ] Test 3.3: Employee ID Uniqueness - PASS/FAIL ✨ NEW
[ ] Test 3.4: Email & Phone Validation - PASS/FAIL ✨ NEW
[ ] Test 3.5: Years of Service - PASS/FAIL ✨ NEW
[ ] Test 4.1: Valid Borrowing - PASS/FAIL
[ ] Test 4.4: Return Button Visibility - PASS/FAIL ✨ NEW
[ ] Test 5.1: Return Process - PASS/FAIL
[ ] Test 5.2: Fine Calculation - PASS/FAIL
[ ] Test 6.1: Librarian Kanban - PASS/FAIL ✨ NEW
[ ] Test 6.2: UI Color Coding - PASS/FAIL
[ ] Test 6.3: Filter Functionality - PASS/FAIL

Overall Result: PASS/FAIL
Notes: ___________
```

---

## 📝 Version History

- **v1.0** (2025-10-29): Initial test case documentation
  - Comprehensive coverage of Member, Book, and Borrowing Record features
  - Integration testing scenarios
  - UI and UX validation tests
  - Performance and data integrity checks

- **v2.0** (2025-10-30): Librarian module integration ✨ **NEW**
  - Added complete librarian management test cases
  - Updated borrowing workflow to include librarian assignment
  - Enhanced validation testing for employee ID formats
  - Added performance tracking and departmental management tests
  - Updated UI tests to include librarian views and navigation
  - Fixed return button visibility issues
  - Updated troubleshooting guide with Odoo 18 specific solutions

---

**Document Status**: Ready for Testing
**Last Updated**: 2025-10-30
**Next Review**: After v2.1 system updates