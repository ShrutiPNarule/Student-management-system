# Reports Feature - User Guide

## 📊 Overview
The Reports feature allows **Admin** and **Superadmin** users to generate customized student reports in PDF format with advanced filtering capabilities.

---

## 🎯 Quick Start

### Step 1: Navigate to Reports
```
1. Login to the application as Admin or Superadmin
2. Click "📊 Reports" in the main navigation menu
3. You'll see the Reports filter page
```

### Step 2: Apply Filters (Optional)
```
Choose any of the 10 available filters or leave them blank
- All filters are OPTIONAL
- Combine multiple filters for more specific results
- Leave filters blank to include all values
```

### Step 3: Generate Report
```
Click "Generate PDF Report" button
PDF will automatically download to your device
```

---

## 📋 Filter Guide

### Academic Performance Filters
| Filter | Range | Usage Example |
|--------|-------|---------------|
| **10th Marks (Min)** | 0-100 | Find students with 10th marks ≥ 80 |
| **10th Marks (Max)** | 0-100 | Find students with 10th marks ≤ 95 |
| **12th Marks (Min)** | 0-100 | Find students with 12th marks ≥ 75 |
| **12th Marks (Max)** | 0-100 | Find students with 12th marks ≤ 98 |

### Institution Filters
| Filter | Type | Usage Example |
|--------|------|---------------|
| **School** | Dropdown | Select from all registered schools |
| **College** | Dropdown | Select from all registered colleges |
| **School Board** | Dropdown | CBSE, ICSE, State Board, etc. |
| **College Type** | Dropdown | Engineering, Arts, Commerce, etc. |

### Geographic Filter
| Filter | Type | Usage Example |
|--------|------|---------------|
| **State** | Dropdown | Maharashtra, Karnataka, Delhi, etc. |

### Status Filter
| Filter | Options | Usage Example |
|--------|---------|---------------|
| **Current Status** | Dropdown | Active, Inactive, Graduated, Dropped |

---

## 🔍 Common Use Cases

### Case 1: Find Top Performers
**Goal:** Identify students scoring >85 in both 10th and 12th

**Steps:**
1. Set "10th Marks (Minimum)" = 85
2. Set "12th Marks (Minimum)" = 85
3. Click "Generate PDF Report"

**Output:** List of high-performing students with all details

---

### Case 2: School-Wise Analysis
**Goal:** Generate report for a specific school

**Steps:**
1. Select "School" from dropdown
2. Click "Generate PDF Report"

**Output:** All students from that school with their marks and status

---

### Case 3: Regional Analysis
**Goal:** Analyze students from a specific state and board

**Steps:**
1. Select "State" from dropdown
2. Select "School Board" from dropdown
3. Click "Generate PDF Report"

**Output:** Students from that region with the specified board

---

### Case 4: College-Wise Report
**Goal:** Get students enrolled in a specific college

**Steps:**
1. Select "College" from dropdown
2. Click "Generate PDF Report"

**Output:** All students from that college with enrollment details

---

### Case 5: Status-Based Analysis
**Goal:** Find all active students

**Steps:**
1. Select "Current Status" = "Active"
2. Click "Generate PDF Report"

**Output:** All currently active students

---

### Case 6: Complex Filter Combination
**Goal:** High performers from a specific school in a state

**Steps:**
1. Set "10th Marks (Minimum)" = 80
2. Select "School" = "Desired School"
3. Select "State" = "Desired State"
4. Click "Generate PDF Report"

**Output:** Filtered students matching all criteria

---

## 📄 PDF Report Details

### What's Included in Each Report
```
✓ Report Title & Generated Date/Time
✓ Applied Filters Summary
✓ Student Table with Columns:
  - Name
  - Email
  - Phone
  - 10th Marks
  - 12th Marks
  - School Name
  - College Name
  - Current Status
✓ Total Record Count
✓ Professional Formatting
```

### File Format
- **Format:** PDF (Portable Document Format)
- **Filename:** `student_report_YYYYMMDD_HHMMSS.pdf`
- **Example:** `student_report_20251223_143025.pdf`

### Styling
- Clean, professional design
- Header color: Dark blue (#1a3a52)
- Alternating row colors for readability
- Proper table formatting with borders

---

## 🎮 Button Guide

| Button | Action | Result |
|--------|--------|--------|
| **📊 Generate PDF Report** | Submit filters | Downloads PDF with filtered data |
| **🔄 Clear Filters** | Reset all fields | Clears all filter selections |

---

## ⚙️ Navigation

### Where to Find Reports
```
Top Navigation Bar
├── Home (All users)
├── Add Student (Admin only)
├── 📊 Reports (Admin & Superadmin)
├── 📋 Approvals (Superadmin only)
├── 👥 Change Roles (Superadmin only)
├── Recycle Bin (Auditor only)
├── Activity Logs (Auditor only)
└── [User Email] (Profile menu)
```

---

## 💾 Saving & Sharing Reports

### Save PDF
```
1. After PDF downloads, it's saved to your Downloads folder
2. Move or save to your preferred location
3. Rename if needed (keep .pdf extension)
```

### Share Reports
```
1. Save the PDF file
2. Email or share using your preferred method
3. Recipients can open with any PDF reader
```

### Print Reports
```
1. Open PDF in your PDF reader
2. Use Print function (Ctrl+P)
3. Select your printer and print
```

---

## 🔒 Access Control

### Who Can Access Reports?
- ✅ **Admin** - Full access to all reports and filters
- ✅ **Superadmin** - Full access to all reports and filters
- ❌ **Student** - No access (permission denied)
- ❌ **Auditor** - No access (permission denied)

### Login Required
- You must be logged in to access reports
- Your role determines available features
- Session expires after 30 minutes of inactivity

---

## ❓ FAQ

**Q: Can I combine multiple filters?**
A: Yes! All filters work together with AND logic. Use multiple filters for specific results.

**Q: What if I want all students?**
A: Leave all filters blank and click "Generate PDF Report".

**Q: Why does my dropdown show "All Options"?**
A: This means no specific filter is applied - all values are included.

**Q: Can I edit the PDF after download?**
A: PDFs are read-only. Export data is frozen at report generation time.

**Q: How large can reports be?**
A: Reports can include hundreds/thousands of students. PDF size depends on record count.

**Q: Can I schedule reports?**
A: Currently, reports must be generated manually. Scheduled reports coming soon.

**Q: What if no students match my filters?**
A: The PDF will show "No students found matching the selected filters."

**Q: Can I download multiple formats?**
A: Currently, only PDF format is supported.

---

## 🚀 Tips & Tricks

### Tip 1: Use Mark Ranges
Instead of exact marks, use Min/Max ranges:
```
10th Min: 70
10th Max: 85
(Shows students with marks between 70-85)
```

### Tip 2: Combine School + Board
Get specific school results with filtering:
```
Select School: XYZ School
(All students from that school)
```

### Tip 3: Geographic Analysis
Use State + Board for regional analysis:
```
State: Karnataka
Board: CBSE
(All CBSE students from Karnataka)
```

### Tip 4: Status Monitoring
Check student status regularly:
```
Current Status: Active
(All currently active enrolled students)
```

### Tip 5: Performance Analysis
Identify high performers:
```
10th Min: 85
12th Min: 85
(Consistent top performers)
```

---

## ⚠️ Important Notes

1. **Data Accuracy:** Reports reflect current database state
2. **Performance:** Large reports (10000+ records) may take a few seconds
3. **Privacy:** Reports contain sensitive student information - handle securely
4. **Backup:** Always keep important reports saved
5. **Updates:** Filter options update automatically when data is added

---

## 📞 Support

**For Issues:**
1. Ensure you're logged in as Admin/Superadmin
2. Check if required filter options exist in database
3. Try clearing filters and generating full report
4. Check browser console (F12) for error messages

**For Questions:**
1. Refer to "Help Section" on Reports page
2. Check this guide
3. Contact system administrator

---

**Last Updated:** December 23, 2025
**Version:** 1.0
